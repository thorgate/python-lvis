#coding:utf-8
import base64
from copy import copy
import json
import requests
from datetime import datetime
from decimal import Decimal

from django.utils.encoding import force_text

from .enums import (WarehouseType, AssortmentType, TransportOrderRoleContext, WaybillRoleContext)
from .models import (FilterItem, SortItem, Address, ElvisModel, TransportOrderListPage, TransportOrder, TransportOrderStatusInfo,
                     TimberWarehouse, Waybill, WaybillStatusInfo, WaybillListPage, TimberAssortment, FineMeasurementFile)


class ElvisException(Exception):
    def __init__(self, message, raw):
        self.message = message
        self.raw = raw

    def __str__(self):
        return "ElvisException %s: %s" % (self.message, self.raw)


class ElvisEncoder(json.JSONEncoder):
    ELVIS_OBJECTS = (
        FilterItem,
        SortItem,
        WarehouseType,
        Address,
        ElvisModel
    )

    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)

        if isinstance(obj, datetime):
            return '/Date(%d)/' % ((obj - datetime(1970, 1, 1)).total_seconds() * 1000)

        if not isinstance(obj, ElvisEncoder.ELVIS_OBJECTS):
            return super(ElvisEncoder, self).default(obj)

        ret = copy(obj.__dict__)

        if isinstance(obj, FineMeasurementFile):
            del ret['Data']

        if 'Id' in ret and ret['Id'] is None:
            del ret['Id']

        if '_already_loaded' in ret:
            del ret['_already_loaded']

        return ret


class ElvisClient(object):
    def __init__(self, api_url, person_code, certificate_pass="", session_token=None):
        self.api_url = api_url

        self.person_code = person_code
        self.certificate = None
        self.certificate_password = certificate_pass or ""
        self.session_token = session_token or None

        assert self.person_code, "Person code must be provided"

    def load_cert_from_fieldfile(self, fieldfile):
        try:
            fieldfile.open(mode='rb')
            self.certificate = force_text(base64.b64encode(fieldfile.read()), 'utf-8')
            fieldfile.close()
        except IOError:
            raise Exception("FieldFile %s is invalid" % fieldfile)

    def load_cert_from_file(self, file_path):
        try:
            with open(file_path, "rb") as fHandle:
                self.certificate = force_text(base64.b64encode(fHandle.read()), 'utf-8')
                fHandle.close()
        except IOError:
            raise Exception("File %s is invalid" % file_path)

    def load_cert_from_str(self, certificate_data):
        # Note: may need validation here?
        self.certificate = force_text(base64.b64encode(certificate_data), 'utf-8')

    def load_cert_from_base64str(self, certificate_data):
        # Note: may need validation here?
        self.certificate = certificate_data

    def __request(self, endpoint, method, attrs=None):

        func = requests.get
        if method.lower() == "post":
            func = requests.post

        headers = {
            'Content-type': 'application/json',
            'Accept': 'text/plain',
        }

        if self.session_token:
            headers['Authorization'] = self.session_token

        if method.lower() == "post":
            result = func(self.api_url % endpoint, data=json.dumps(attrs, cls=ElvisEncoder), headers=headers)
        else:
            result = func(self.api_url % endpoint, params=attrs, headers=headers)

        if result.status_code == 200:
            text = result.text

            try:
                return {
                    "Success": True,
                    "raw": json.loads(text),
                }
            except ValueError:
                return {
                    "Success": False,
                    "message": "not json",
                    "raw": text,
                }

        else:
            return {
                "Success": False,
                "message": "Bad status code: %d" % result.status_code,
                "raw": result.text,
            }

    # ENDPOINTS

    def server_info(self):
        assert self.session_token, "No valid session available"

        result = self.__request("GetInformation", "GET")

        if result["Success"] and result["raw"].get("GetInformationResult", None):
            return result["raw"]["GetInformationResult"]
        else:
            raise ElvisException("Server information not available, it was added in proxy version 1.1.*", raw=result)

    def authorize(self, session_tag='default'):
        assert self.certificate, "Certificate must be provided"

        result = self.__request("Authorize", "POST", {
            'code': self.person_code,
            'certificateData': self.certificate,
            'password': self.certificate_password,
            'connectionTag': session_tag,
        })

        if result["Success"] and result["raw"].get("AuthorizeResult", None) and result['raw']['AuthorizeResult'].get('Success'):
            auth_result = result["raw"].get("AuthorizeResult")
            self.session_token = auth_result["access_token"]
            return True
        else:
            raise ElvisException("Authorization failed:", result)

    def get_session_tag(self):
        assert self.session_token, "No valid session available"

        result = self.__request("getSessionTag", "GET", {})

        if result["Success"]:
            return result["raw"]['getSessionTagResult']
        else:
            raise ElvisException(result['message'], result['raw'])

    def get_assortment_types(self, assortment_type=AssortmentType.ELVIS):
        assert self.session_token, "No valid session available"
        assert assortment_type in [AssortmentType.ELVIS, AssortmentType.COMPANY], "Invalid assortment type"

        result = self.__request("getAssortmentTypes", "GET", {
            'assortment_type': assortment_type,
        })

        if result["Success"]:
            return result["raw"]['getAssortmentTypesResult']
        else:
            raise ElvisException(result['message'], result['raw'])

    def search_warehouses(self, filters, sorting, start=0, limit=10, show_count=False):
        assert self.session_token, "No valid session available"

        assert isinstance(filters, (list, tuple, FilterItem)), 'Filters must be a list or tuple'
        if isinstance(filters, FilterItem):
            filters = (filters, )

        assert not list(filter(lambda x: not isinstance(x, FilterItem), filters)), \
            'All filters must be instances of FilterItem'

        assert isinstance(sorting, (list, tuple, SortItem)), 'Sorting must be a list or tuple'
        if isinstance(sorting, SortItem):
            sorting = (sorting, )

        assert not list(filter(lambda x: not isinstance(x, SortItem), sorting)), \
            'All sorting rules must be instances of SortItem'

        assert filters and sorting, 'Need to add filters and sorting!'

        result = self.__request("SearchWarehouses", "POST", {
            'filters': filters,
            'sorting': sorting,
            'start': start,
            'limit': limit,
            'show_count': show_count,
        })

        if result["Success"]:
            return result["raw"]["SearchWarehousesResult"]
        else:
            raise ElvisException(result['message'], result['raw'])

    def insert_transport_order(self, transport_order):
        assert self.session_token, "No valid session available"

        assert isinstance(transport_order, TransportOrder), 'Invalid TransportOrder'

        result = self.__request("InsertTransportOrder", "POST", {
            'item': transport_order,
        })

        if result.get("Success", False):
            return result["raw"]['InsertTransportOrderResult']
        else:
            raise ElvisException(result['message'], result['raw'])

    def search_transport_orders(self, context, filters, sorting, start=0, limit=10, show_count=False):
        assert self.session_token, "No valid session available"

        assert context in TransportOrderRoleContext.__dict__.values(), 'Invalid context'

        assert isinstance(filters, (list, tuple, FilterItem)), 'Filters must be a list or tuple'
        if isinstance(filters, FilterItem):
            filters = (filters, )

        assert not list(filter(lambda x: not isinstance(x, FilterItem), filters)), \
            'All filters must be instances of FilterItem'

        assert isinstance(sorting, (list, tuple, SortItem)), 'Sorting must be a list or tuple'
        if isinstance(sorting, SortItem):
            sorting = (sorting, )

        assert not list(filter(lambda x: not isinstance(x, SortItem), sorting)), \
            'All sorting rules must be instances of SortItem'

        result = self.__request("SearchTransportOrders", "POST", {
            'context': context,
            'filters': filters,
            'sorting': sorting,
            'start': start,
            'limit': limit,
            'show_count': show_count,
        })

        if result.get("Success", False):
            return TransportOrderListPage(dict_data=result["raw"]["SearchTransportOrdersResult"])
        else:
            raise ElvisException(result['message'], result['raw'])

    def get_transport_order(self, transport_order_id):
        assert self.session_token, "No valid session available"

        result = self.__request("GetTransportOrder", "POST", {
            'transport_order_id': transport_order_id,
        })

        if result.get("Success", False):
            json_obj = result["raw"]["GetTransportOrderResult"]
            return TransportOrder(dict_data=json_obj)
        else:
            raise ElvisException(result['message'], result['raw'])

    def get_transport_order_status(self, transport_order_id):
        assert self.session_token, "No valid session available"

        result = self.__request("GetTransportOrderStatus", "POST", {
            'transport_order_id': transport_order_id
        })

        if result.get("Success", False):
            return TransportOrderStatusInfo(dict_data=result["raw"]["GetTransportOrderStatusResult"])
        else:
            raise ElvisException(result['message'], result['raw'])

    def set_transport_order_status(self, transport_order_id, status, feedback, version):
        assert self.session_token, "No valid session available"

        result = self.__request("SetTransportOrderStatus", "POST", {
            'transport_order_id': transport_order_id,
            'status': status,
            'feedback': feedback or "",
            'version': version or [],
        })

        if result.get("Success", False):
            return result["raw"]['SetTransportOrderStatusResult']
        else:
            raise ElvisException(result['message'], result['raw'])

    def insert_warehouse(self, warehouse):
        assert self.session_token, "No valid session available"

        assert isinstance(warehouse, TimberWarehouse), 'Invalid Warehouse'

        result = self.__request("InsertWarehouse", "POST", {
            'item': warehouse,
        })

        if result.get("Success", False):
            return result["raw"]['InsertWarehouseResult']
        else:
            raise ElvisException(result['message'], result['raw'])

    def get_warehouse(self, warehouse_id):
        assert self.session_token, "No valid session available"

        result = self.__request("GetWarehouse", "POST", {
            'warehouse_id': warehouse_id,
        })

        if result.get("Success", False):
            json_obj = result["raw"]["GetWarehouseResult"]
            return TimberWarehouse(dict_data=json_obj)
        else:
            raise ElvisException(result['message'], result['raw'])

    def delete_warehouse(self, warehouse_id):
        assert self.session_token, "No valid session available"

        result = self.__request("DeleteWarehouse", "POST", {
            'warehouse_id': warehouse_id,
        })

        if result.get("Success", False):
            return result["raw"]['DeleteWarehouseResult']
        else:
            raise ElvisException(result['message'], result['raw'])

    def insert_waybill(self, waybill):
        assert self.session_token, "No valid session available"

        assert isinstance(waybill, Waybill), 'Invalid Waybill'

        result = self.__request("InsertWaybill", "POST", {
            'item': waybill,
        })

        if result.get("Success", False):
            return result["raw"]["InsertWaybillResult"]
        else:
            raise ElvisException(result['message'], result['raw'])

    def get_waybill(self, waybill_id):
        assert self.session_token, "No valid session available"

        result = self.__request("GetWaybill", "POST", {
            'waybill_id': waybill_id
        })

        if result.get("Success", False):
            json_obj = result["raw"]["GetWaybillResult"]
            if json_obj is None:
                return None
            return Waybill(dict_data=json_obj)
        else:
            raise ElvisException(result['message'], result['raw'])

    def set_waybill_status(self, waybill_number, status, feedback, pre_journey_length,
                           total_journey_length, measurement_act_nr, version):
        assert self.session_token, "No valid session available"

        result = self.__request("SetWaybillStatus", "POST", {
            'waybillNumber': waybill_number,
            'status': status,
            'feedback': feedback,
            'preJorneyLength': pre_journey_length,
            'totalJourneyLength': total_journey_length,
            'measurementActNr': measurement_act_nr,
            'version': version,
        })

        if result.get("Success", False):
            return result["raw"]['SetWaybillStatusResult']
        else:
            raise ElvisException(result['message'], result['raw'])

    def get_waybill_status(self, waybill_id):
        assert self.session_token, "No valid session available"

        result = self.__request("GetWaybillStatus", "POST", {
            'waybill_id': waybill_id
        })

        if result.get("Success", False):
            return WaybillStatusInfo(dict_data=result["raw"]["GetWaybillStatusResult"])
        else:
            raise ElvisException(result['message'], result['raw'])

    def search_waybills(self, context, filters, sorting, start=0, limit=10, show_count=False):
        assert self.session_token, "No valid session available"

        assert context in WaybillRoleContext.__dict__.values(), 'Invalid context'

        assert isinstance(filters, (list, tuple, FilterItem)), 'Filters must be a list or tuple'
        if isinstance(filters, FilterItem):
            filters = (filters, )

        assert not list(filter(lambda x: not isinstance(x, FilterItem), filters)), \
            'All filters must be instances of FilterItem'

        assert isinstance(sorting, (list, tuple, SortItem)), 'Sorting must be a list or tuple'
        if isinstance(sorting, SortItem):
            sorting = (sorting, )

        assert not list(filter(lambda x: not isinstance(x, SortItem), sorting)), \
            'All sorting rules must be instances of SortItem'

        assert filters and sorting, 'Need to add filters and sorting!'

        result = self.__request("SearchWaybills", "POST", {
            'context': context,
            'filters': filters,
            'sorting': sorting,
            'start': start,
            'limit': limit,
            'show_count': show_count,
        })

        if result.get("Success", False):
            return WaybillListPage(dict_data=result["raw"]["SearchWaybillsResult"])
        else:
            raise ElvisException(result['message'], result['raw'])

    def insert_reception_assortment(self, timber_batch_id, timber_assortment):
        assert self.session_token, "No valid session available"

        assert isinstance(timber_assortment, TimberAssortment), 'Invalid TimberAssortment'

        result = self.__request("InsertReceptionAssortment", "POST", {
            'timber_batch_id': timber_batch_id,
            'assortment': timber_assortment,
        })

        if result.get("Success", False):
            return result["raw"]["InsertReceptionAssortmentResult"]
        else:
            raise ElvisException(result['message'], result['raw'])

    def delete_reception_assortment(self, reception_assortment_id):
        return self.__delete_function({'id': reception_assortment_id}, 'DeleteReceptionAssortment')

    def insert_fine_measurement_assortment(self, waybill_number, timber_assortment):
        assert self.session_token, "No valid session available"

        assert isinstance(timber_assortment, TimberAssortment), 'Invalid TimberAssortment'

        result = self.__request("InsertFineMeasurementAssortment", "POST", {
            'waybill_number': waybill_number,
            'assortment': timber_assortment,
        })

        if result.get("Success", False):
            val = result["raw"]["InsertFineMeasurementAssortmentResult"]

            if not val or val in ['0', 0]:
                raise ElvisException('InsertFineMeasurementAssortmentResult:: returned id 0', result['raw'])

            else:
                return val
        else:
            raise ElvisException(result['message'], result['raw'])

    def delete_fine_measurement_assortment(self, reception_assortment_id):
        return self.__delete_function({'id': reception_assortment_id}, 'DeleteFineMeasurementAssortment')

    def insert_fine_measurement_file(self, waybill_number, fine_measurement_file):
        assert self.session_token, "No valid session available"

        assert isinstance(fine_measurement_file, FineMeasurementFile), 'Invalid FineMeasurementFile'

        result = self.__request("InsertFineMeasurementFile", "POST", {
            'waybill_number': waybill_number,
            'file': fine_measurement_file,
            'file_data': force_text(base64.b64encode(fine_measurement_file.Data)),
        })

        if result.get("Success", False):
            return result["raw"]["InsertFineMeasurementFileResult"]
        else:
            raise ElvisException(result['message'], result['raw'])

    def delete_fine_measurement_file(self, fine_measurement_file_id):
        return self.__delete_function({'id': fine_measurement_file_id}, 'DeleteFineMeasurementFile')

    def __delete_function(self, params, endpoint):
        assert self.session_token, "No valid session available"

        result = self.__request(endpoint, "POST", params)

        if result.get("Success", False):
            return result["raw"]["%sResult" % endpoint]
        else:
            raise ElvisException(result['message'], result['raw'])
