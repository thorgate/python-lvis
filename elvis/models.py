import hashlib
import json

from django.utils.encoding import force_bytes

from .enums import Priority, TransportOrderStatus


class FilterItem(object):
    def __init__(self, field, value):
        self.Field = field
        self.Value = value


class SortItem(object):
    def __init__(self, column, direction):
        self.SortColumn = column
        self.SortDirection = direction


class ElvisModel(object):
    def __init__(self, **kwargs):
        dict_data = kwargs.get('dict_data', None)
        if dict_data:
            self.__dict__ = dict_data
            self._already_loaded = True
        else:
            self._already_loaded = False


# noinspection PyPep8Naming
class AdditionalProperty(ElvisModel):
    def __init__(self, **kwargs):
        super(AdditionalProperty, self).__init__(**kwargs)
        if not self._already_loaded:
            self.TypeId = kwargs.get('type_id')
            self.Value = kwargs.get('value')

            self.ExtensionData = None


# noinspection PyPep8Naming
class Address(ElvisModel):
    def __init__(self, **kwargs):
        super(Address, self).__init__(**kwargs)
        if not self._already_loaded:
            self.AddressAdditionalInformation = kwargs.get('address_additional_information')
            self.CityBorough = kwargs.get('city_borough')
            self.County = kwargs.get('county')
            self.EHAK = kwargs.get('ehak')
            self.NearAddress = kwargs.get('near_address')
            self.RuralDistrict = kwargs.get('rural_district')


# noinspection PyPep8Naming
class Pack(ElvisModel):
    def __init__(self, **kwargs):
        super(Pack, self).__init__(**kwargs)

        if not self._already_loaded:
            self.Factor = kwargs.get('factor')
            self.Width = kwargs.get('width')
            self.Heidht = kwargs.get('height')
            self.Length = kwargs.get('length')
            self.Number = kwargs.get('number')
            self.VehicleType = kwargs.get('vehicle_type')

            self.ExtensionData = None


# noinspection PyPep8Naming
class TimberAssortment(ElvisModel):
    def __init__(self, **kwargs):
        super(TimberAssortment, self).__init__(**kwargs)

        if not self._already_loaded:
            self.Amount = kwargs.get('amount')
            self.Description = kwargs.get('description')
            self.TimberAssortmentTypeId = kwargs.get('assortment_type')

            self.Id = kwargs.get('timber_assortment_id', None)

            # Load Packs
            packs = kwargs.get('packs', [])
            if isinstance(packs, Pack):
                packs = [packs, ]

            assert not list(filter(lambda x: not isinstance(x, Pack), packs))
            self.Packs = packs

            self.ExtensionData = None
        else:
            # Load received assortments
            packs = self.Packs
            self.Packs = []

            if packs:
                for pack in packs:
                    self.Packs.append(Pack(dict_data=pack))

        assert self.Amount is not None, 'TimberAssortment::Amount cant be None'


# noinspection PyPep8Naming
class Certificate(ElvisModel):
    def __init__(self, **kwargs):
        super(Certificate, self).__init__(**kwargs)

        if not self._already_loaded:
            self.CertificateNumber = kwargs.get('certificate_number')
            self.TypeId = kwargs.get('type_id')
            self.ExtensionData = None


# noinspection PyPep8Naming
class TimberBatch(ElvisModel):
    def __init__(self, **kwargs):
        super(TimberBatch, self).__init__(**kwargs)

        if not self._already_loaded:
            self.Appropriation = kwargs.get('appropriation')  # string
            self.Assortments = kwargs.get('assortments')  # TimberAssortment[]
            self.Certificates = kwargs.get('certificates')  # Certificate[]
            self.Description = kwargs.get('description')  # string

            self.CadastralNumber = kwargs.get('cadastral_number')  # string

            self.DocDate = kwargs.get('doc_date')  # DateTime
            self.DocNumber = kwargs.get('doc_number')  # string

            self.HoldingBaseId = kwargs.get('holding_base_id')  # int
            self.Id = kwargs.get('batch_id', None)  # int or None
            self.ForestNotice = kwargs.get('forest_notice', None)  # string or None

            self.PreviousOwnerAddress = kwargs.get('prev_owner_address')  # string
            self.PreviousOwnerCode = kwargs.get('prev_owner_code')  # string
            self.PreviousOwnerName = kwargs.get('prev_owner_name')  # string

            self.Quarter = kwargs.get('quarter')  # string
            self.RegisteredImmovableNumber = kwargs.get('reg_immovable_number')  # string

            self.ExtensionData = None
        else:
            assortments = self.Assortments
            certs = self.Certificates
            self.Assortments = []
            self.Certificates = []

            for item in assortments:
                self.Assortments.append(TimberAssortment(dict_data=item))
            for item in certs:
                self.Certificates.append(Certificate(dict_data=item))


# noinspection PyPep8Naming
class Warehouse(ElvisModel):
    def __init__(self, **kwargs):
        super(Warehouse, self).__init__(**kwargs)

        if not self._already_loaded:
            self.Id = kwargs.get('warehouse_id', None)  # string
            self.Name = kwargs.get('name')  # string
            self.Code = kwargs.get('code')  # string

            self.ContactEmail = kwargs.get('contact_email')  # string
            self.ContactName = kwargs.get('contact_name')  # string
            self.ContactPhone = kwargs.get('contact_phone')  # string

            self.Description = kwargs.get('description')  # string
            self.Appropriation = kwargs.get('appropriation')  # string
            self.Quarter = kwargs.get('quarter')  # string

            self.IsDry = kwargs.get('is_dry')  # bool or None
            self.IsParallelLoading = kwargs.get('is_parallel_loading')  # bool or None

            self.LambertEstX = kwargs.get('lambert_est_x')  # double or None
            self.LambertEstY = kwargs.get('lambert_est_y')  # double or None

            assert isinstance(kwargs.get('address'), Address)
            self.Address = kwargs.get('address')

            self.ForestDistrictId = kwargs.get('forest_district_id')  # int or None

            additional_properties = kwargs.get('additional_properties', [])
            if isinstance(additional_properties, AdditionalProperty):
                additional_properties = [additional_properties, ]

            assert not list(filter(lambda x: not isinstance(x, AdditionalProperty), additional_properties))
            self.AdditionalProperties = additional_properties
        else:
            if not isinstance(self.Address, Address):
                self.Address = Address(dict_data=self.Address)

            props = self.AdditionalProperties
            self.AdditionalProperties = []

            if props:
                for item in props:
                    self.AdditionalProperties.append(AdditionalProperty(dict_data=item))


# noinspection PyPep8Naming
class TimberWarehouse(Warehouse):

    def __init__(self, **kwargs):

        super(TimberWarehouse, self).__init__(**kwargs)

        #if not self._ElvisModel_already_loaded:
        if not self._already_loaded:
            self.CadastralNumber = kwargs.get('cadastral_number')
            self.IsActive = kwargs.get('is_active')
            self.IsPublic = kwargs.get('is_public')

            timber_batches = kwargs.get('timber_batches')
            if isinstance(timber_batches, TimberBatch):
                timber_batches = [timber_batches, ]

            assert not list(filter(lambda x: not isinstance(x, TimberBatch), timber_batches))
            self.TimberBatches = timber_batches

            self.Type = kwargs.get('warehouse_type')  # WarehouseType

            self.ExtensionData = None
            self.Version = kwargs.get('version', None)  # Note: byte array
        else:
            batches = self.TimberBatches
            self.TimberBatches = []

            for batch in batches:
                self.TimberBatches.append(TimberBatch(dict_data=batch))


# noinspection PyPep8Naming
class WaybillStatusChangeLog(ElvisModel):
    def __init__(self, **kwargs):

        super(WaybillStatusChangeLog, self).__init__(**kwargs)

        if not self._already_loaded:
            self.ChangedBy = kwargs.get('changed_by')
            self.ChangedOn = kwargs.get('changed_on')
            self.Status = kwargs.get('status')

            self.ExtensionData = None


# noinspection PyPep8Naming
class Shipment(ElvisModel):
    def __init__(self, **kwargs):

        super(Shipment, self).__init__(**kwargs)

        if not self._already_loaded:
            assert isinstance(kwargs.get('warehouse'), Warehouse)
            self.Warehouse = kwargs.get('warehouse')

            timber_batches = kwargs.get('timber_batches')
            if isinstance(timber_batches, TimberBatch):
                timber_batches = [timber_batches, ]

            assert not list(filter(lambda x: not isinstance(x, TimberBatch), timber_batches))
            self.TimberBatches = timber_batches

            self.ExtensionData = None
        else:
            if not isinstance(self.Warehouse, Warehouse):
                self.Warehouse = Warehouse(dict_data=self.Warehouse)

            batches = self.TimberBatches
            self.TimberBatches = []

            for batch in batches:
                self.TimberBatches.append(TimberBatch(dict_data=batch))


# noinspection PyPep8Naming
class Person(ElvisModel):
    def __init__(self, **kwargs):
        super(Person, self).__init__(**kwargs)

        if not self._already_loaded:
            self.EMail = kwargs.get('email')
            self.Firstname = kwargs.get('firstname')
            self.Lastname = kwargs.get('lastname')
            self.PersonCode = kwargs.get('person_code')
            self.Phone = kwargs.get('phone')

            self.ExtensionData = None


# noinspection PyPep8Naming
class AuthorizedPerson(Person):
    def __init__(self, **kwargs):
        super(AuthorizedPerson, self).__init__(**kwargs)

        if not self._already_loaded:
            assert isinstance(kwargs.get('address'), Address)
            self.Address = kwargs.get('address')
            self.AuthorizationBase = kwargs.get('authorization_base')
        else:
            if not isinstance(self.Address, Address):
                self.Address = Address(dict_data=self.Address)


# noinspection PyPep8Naming
class Party(ElvisModel):
    def __init__(self, **kwargs):
        super(Party, self).__init__(**kwargs)

        if not self._already_loaded:
            self.Code = kwargs.get('code')
            self.Email = kwargs.get('email')
            self.Name = kwargs.get('name')
            self.Phone = kwargs.get('phone')

            self.ExtensionData = None


# noinspection PyPep8Naming
class TimberOwner(Party):
    def __init__(self, **kwargs):
        super(TimberOwner, self).__init__(**kwargs)

        if not self._already_loaded:
            self.Address = kwargs.get('address')

            self.AuthorizedPerson = kwargs.get('authorized_person')
            if self.AuthorizedPerson is not None:
                assert isinstance(self.AuthorizedPerson, AuthorizedPerson)

        else:
            if not isinstance(self.AuthorizedPerson, AuthorizedPerson):
                self.AuthorizedPerson = AuthorizedPerson(dict_data=self.AuthorizedPerson)


# noinspection PyPep8Naming
class TimberReceiver(Party):
    def __init__(self, **kwargs):
        super(TimberReceiver, self).__init__(**kwargs)

        if not self._already_loaded:
            self.ContactEmail = kwargs.get('contact_email')
            self.ContactName = kwargs.get('contact_name')
            self.ContactPhone = kwargs.get('contact_phone')

            self.Address = kwargs.get('address')
            if self.Address is not None:
                assert isinstance(self.Address, Address)
            self.AuthorizationBase = kwargs.get('authorization_base')

            additional_properties = kwargs.get('additional_properties', [])
            if isinstance(additional_properties, AdditionalProperty):
                additional_properties = [additional_properties, ]

            assert not list(filter(lambda x: not isinstance(x, AdditionalProperty), additional_properties))
            self.AdditionalProperties = additional_properties
        else:
            if not isinstance(self.Address, Address):
                self.Address = Address(dict_data=self.Address)

            props = self.AdditionalProperties
            self.AdditionalProperties = []

            if props:
                for item in props:
                    self.AdditionalProperties.append(AdditionalProperty(dict_data=item))


# noinspection PyPep8Naming
class TimberReceiverDestination(ElvisModel):
    def __init__(self, **kwargs):
        super(TimberReceiverDestination, self).__init__(**kwargs)

        if not self._already_loaded:
            assert isinstance(kwargs.get('destination'), Warehouse)
            self.Destination = kwargs.get('destination')

            assert isinstance(kwargs.get('receiver'), TimberReceiver)
            self.Receiver = kwargs.get('receiver')

            self.ExtensionData = None
        else:
            if not isinstance(self.Destination, Warehouse):
                self.Destination = Warehouse(dict_data=self.Destination)

            if not isinstance(self.Receiver, TimberReceiver):
                self.Receiver = TimberReceiver(dict_data=self.Receiver)


# noinspection PyPep8Naming
class Vehicle(ElvisModel):
    def __init__(self, **kwargs):
        super(Vehicle, self).__init__(**kwargs)

        if not self._already_loaded:
            self.Model = kwargs.get('model')
            self.RegistrationNumber = kwargs.get('registration_number')

            self.ExtensionData = None


# noinspection PyPep8Naming
class Transport(ElvisModel):
    def __init__(self, **kwargs):
        super(Transport, self).__init__(**kwargs)

        if not self._already_loaded:
            assert isinstance(kwargs.get('driver'), Person)
            self.Driver = kwargs.get('driver')

            assert isinstance(kwargs.get('trailer'), Vehicle)
            self.Trailer = kwargs.get('trailer')

            assert isinstance(kwargs.get('van'), Vehicle)
            self.Van = kwargs.get('van')

            self.ExtensionData = None
        else:
            if not isinstance(self.Driver, Person):
                self.Driver = Person(dict_data=self.Driver)

            if not isinstance(self.Trailer, Vehicle):
                self.Trailer = Vehicle(dict_data=self.Trailer)

            if not isinstance(self.Van, Vehicle):
                self.Van = Vehicle(dict_data=self.Van)


# noinspection PyPep8Naming
class Transporter(ElvisModel):
    def __init__(self, **kwargs):
        super(Transporter, self).__init__(**kwargs)

        if not self._already_loaded:
            self.CompanyRegistrationNumber = kwargs.get('company_registration_number')
            self.ContactEmail = kwargs.get('contact_email')
            self.ContactName = kwargs.get('contact_name')
            self.ContactPhone = kwargs.get('contact_phone')

            self.ExtensionData = None

            additional_properties = kwargs.get('additional_properties', [])
            if isinstance(additional_properties, AdditionalProperty):
                additional_properties = [additional_properties, ]

            assert not list(filter(lambda x: not isinstance(x, AdditionalProperty), additional_properties))
            self.AdditionalProperties = additional_properties
        else:
            props = self.AdditionalProperties
            self.AdditionalProperties = []

            if props:
                for item in props:
                    self.AdditionalProperties.append(AdditionalProperty(dict_data=item))


# noinspection PyPep8Naming
class WaybillTransporter(Transporter):

    def __init__(self, **kwargs):
        super(WaybillTransporter, self).__init__(**kwargs)

        if not self._already_loaded:
            assert isinstance(kwargs.get('transport'), Transport)
            self.Transport = kwargs.get('transport')
        else:
            if not isinstance(self.Transport, Transport):
                self.Transport = Transport(dict_data=self.Transport)


# noinspection PyPep8Naming
class Waybill(ElvisModel):
    def __init__(self, **kwargs):
        super(Waybill, self).__init__(**kwargs)

        if not self._already_loaded:
            self.AltNumber = kwargs.get('alt_number')
            self.Description = kwargs.get('description')
            self.IsDisputed = kwargs.get('is_disputed', False)
            self.Number = kwargs.get('number')
            self.Status = kwargs.get('status')

            self.TransportOrderNumber = kwargs.get('transport_order_number')

            self.PreJourneyLength = kwargs.get('pre_journey_length', None)
            self.TotalJourneyLength = kwargs.get('total_journey_length', None)

            self.Version = kwargs.get('version', None)  # Note: byte array
            self.ExtensionData = None

            # Timber owner
            if not isinstance(kwargs.get('timber_owner'), TimberOwner):
                from elvis.api import ElvisException
                raise ElvisException("ELVIS didn't return a proper way bill", raw={})
            self.TimberOwner = kwargs.get('timber_owner')

            # Timber receiver destination
            assert isinstance(kwargs.get('timber_receiver_destination'), TimberReceiverDestination)
            self.TimberReceiverDestination = kwargs.get('timber_receiver_destination')

            # Transporter
            assert isinstance(kwargs.get('transporter'), WaybillTransporter)
            self.Transporter = kwargs.get('transporter')

            # Load fine measurements
            fine_measurements = kwargs.get('fine_measurements')
            if fine_measurements:
                if isinstance(fine_measurements, TimberAssortment):
                    fine_measurements = [fine_measurements, ]

                assert not list(filter(lambda x: not isinstance(x, TimberAssortment), fine_measurements))
                self.FineMeasurements = fine_measurements

            # Load received assortments
            received_assortments = kwargs.get('received_assortments')
            if received_assortments:
                if isinstance(received_assortments, TimberBatch):
                    received_assortments = [received_assortments, ]

                assert not list(filter(lambda x: not isinstance(x, TimberBatch), received_assortments))
                self.ReceivedAssortments = received_assortments

            # Load status change logs
            status_change_logs = kwargs.get('status_change_logs')
            if status_change_logs:
                if isinstance(status_change_logs, WaybillStatusChangeLog):
                    status_change_logs = [status_change_logs, ]

                assert not list(filter(lambda x: not isinstance(x, WaybillStatusChangeLog), status_change_logs))
                self.StatusChangeLogs = status_change_logs

            # Load shipments
            shipments = kwargs.get('shipments')
            if shipments:
                if isinstance(shipments, Shipment):
                    shipments = [shipments, ]

                assert not list(filter(lambda x: not isinstance(x, Shipment), shipments))
                self.Shipments = shipments
        else:
            # Timber owner
            if not isinstance(self.TimberOwner, TimberOwner):
                self.TimberOwner = TimberOwner(dict_data=self.TimberOwner)

            # Timber receiver destination
            if not isinstance(self.TimberReceiverDestination, TimberReceiverDestination):
                self.TimberReceiverDestination = TimberReceiverDestination(dict_data=self.TimberReceiverDestination)

            # Transporter
            if not isinstance(self.Transporter, WaybillTransporter):
                self.Transporter = WaybillTransporter(dict_data=self.Transporter)

            # Load fine measurements
            fine_measurements = self.FineMeasurements
            self.FineMeasurements = []

            if fine_measurements:
                for fine_measurement in fine_measurements:
                    self.FineMeasurements.append(TimberAssortment(dict_data=fine_measurement))

            # Load received assortments
            received_assortments = self.ReceivedAssortments
            self.ReceivedAssortments = []

            if received_assortments:
                for received_assortment in received_assortments:
                    self.ReceivedAssortments.append(TimberBatch(dict_data=received_assortment))

            # Load status change logs
            status_change_logs = self.StatusChangeLogs
            self.StatusChangeLogs = []

            if status_change_logs:
                for item in status_change_logs:
                    self.StatusChangeLogs.append(WaybillStatusChangeLog(dict_data=item))

            # Load shipments
            shipments = self.Shipments
            self.Shipments = []

            if shipments:
                for item in shipments:
                    self.Shipments.append(Shipment(dict_data=item))


# noinspection PyPep8Naming
class WaybillListItem(ElvisModel):
    def __init__(self, **kwargs):
        super(WaybillListItem, self).__init__(**kwargs)

        if not self._already_loaded:
            self.Number = kwargs.get('number')
            self.AltNumber = kwargs.get('alt_number')

            self.OwnerCode = kwargs.get('owner_code')
            self.OwnerName = kwargs.get('owner_name')

            self.ReceiverCode = kwargs.get('receiver_code')
            self.ReceiverName = kwargs.get('receiver_name')

            self.Status = kwargs.get('status')

            self.TransportOrderNumber = kwargs.get('transport_order_number')

            self.TransporterCode = kwargs.get('transporter_code')
            self.TransporterName = kwargs.get('transporter_name')

            self.Version = kwargs.get('version', [])

            self.ExtensionData = None


# noinspection PyPep8Naming
class TransportOrderListItem(ElvisModel):
    def __init__(self, **kwargs):
        super(TransportOrderListItem, self).__init__(**kwargs)

        if not self._already_loaded:
            self.Number = kwargs.get('number')
            self.AltNumber = kwargs.get('alt_number')

            self.OwnerCode = kwargs.get('owner_code')
            self.OwnerName = kwargs.get('owner_name')

            self.ReceiverCode = kwargs.get('receiver_code')
            self.ReceiverName = kwargs.get('receiver_name')

            self.TransporterCode = kwargs.get('transporter_code')
            self.TransporterName = kwargs.get('transporter_name')

            self.Deadline = kwargs.get('deadline', None)
            self.GroupId = kwargs.get('group_id')

            self.Version = kwargs.get('version', [])
            self.ExtensionData = None

            self.Status = kwargs.get('status')
            self.Priority = kwargs.get('priority')


# noinspection PyPep8Naming
class WaybillListPage(ElvisModel):
    def __init__(self, **kwargs):
        super(WaybillListPage, self).__init__(**kwargs)

        if not self._already_loaded:
            self.HasCount = kwargs.get('has_count')
            self.Skip = kwargs.get('skip')
            self.Take = kwargs.get('take')
            self.TotalCount = kwargs.get('total_count')

            self.ExtensionData = None

            # Load shipments
            items = kwargs.get('items', [])
            if isinstance(items, WaybillListItem):
                items = [items, ]

            assert not list(filter(lambda x: not isinstance(x, WaybillListItem), items))
            self.Items = items

        else:
            # Load items
            items = self.Items
            self.Items = []

            if items:
                for item in items:
                    self.Items.append(WaybillListItem(dict_data=item))


# noinspection PyPep8Naming
class TransportOrderListPage(ElvisModel):
    def __init__(self, **kwargs):
        super(TransportOrderListPage, self).__init__(**kwargs)

        if not self._already_loaded:
            self.HasCount = kwargs.get('has_count')
            self.Skip = kwargs.get('skip')
            self.Take = kwargs.get('take')
            self.TotalCount = kwargs.get('total_count')

            self.ExtensionData = None

            # Load shipments
            items = kwargs.get('items', [])
            if isinstance(items, TransportOrderListItem):
                items = [items, ]

            assert not list(filter(lambda x: not isinstance(x, TransportOrderListItem), items))
            self.Items = items

        else:
            # Load items
            items = self.Items
            self.Items = []

            if items:
                for item in items:
                    self.Items.append(TransportOrderListItem(dict_data=item))


# noinspection PyPep8Naming
class WaybillStatusInfo(ElvisModel):
    def __init__(self, **kwargs):
        super(WaybillStatusInfo, self).__init__(**kwargs)

        if not self._already_loaded:
            self.Number = kwargs.get('number')
            self.Status = kwargs.get('status')
            self.Version = kwargs.get('status', [])
            self.ExtensionData = None


# noinspection PyPep8Naming
class TransportOrderStatusInfo(ElvisModel):
    def __init__(self, **kwargs):
        super(TransportOrderStatusInfo, self).__init__(**kwargs)

        if not self._already_loaded:
            self.Number = kwargs.get('number')
            self.Status = kwargs.get('status')
            self.Version = kwargs.get('status', [])
            self.ExtensionData = None


# noinspection PyPep8Naming
class TransportOrderStatusChangeLog(WaybillStatusChangeLog):
    pass


# noinspection PyPep8Naming
class TransportOrderTransporter(Transporter):
    def __init__(self, **kwargs):
        super(TransportOrderTransporter, self).__init__(**kwargs)

        if not self._already_loaded:

            transports = kwargs.get('transports', [])
            if isinstance(transports, Transport):
                transports = [transports, ]

            assert transports
            assert not list(filter(lambda x: not isinstance(x, Transport), transports))
            self.Transports = transports

        else:
            transports = self.Transports
            self.Transports = []
            for transport in transports:
                if isinstance(transport, Transport):
                    self.Transports.append(transport)
                else:
                    self.Transports.append(Transport(dict_data=transport))

    def get_waybill_transporter(self, transport_hash):
        transport = None
        for t in self.Transports:
            if transport_hash == hashlib.md5("%s%s%s" % (t.Driver.PersonCode, t.Trailer.RegistrationNumber, t.Van.RegistrationNumber)).hexdigest():
                transport = t
                break
        assert transport

        from elvis.api import ElvisEncoder
        dict_data = json.loads(json.dumps(self, cls=ElvisEncoder))
        del dict_data['Transports']
        dict_data['Transport'] = transport
        waybill_transport_order = WaybillTransporter(dict_data=dict_data)

        return waybill_transport_order


# noinspection PyPep8Naming
class TransportOrder(ElvisModel):
    def __init__(self, **kwargs):
        super(TransportOrder, self).__init__(**kwargs)

        if not self._already_loaded:
            self.Number = kwargs.get('number')
            self.AltNumber = kwargs.get('alt_number')

            self.Deadline = kwargs.get('deadline', None)
            self.GroupId = kwargs.get('group_id')

            self.Status = kwargs.get('status', TransportOrderStatus.Composing)
            self.Priority = kwargs.get('priority', Priority.Normal)

            self.Description = kwargs.get('description')
            self.TransportContractNumber = kwargs.get('transport_contract_number')

            self.IsPartialOperationsAllowed = kwargs.get('is_partial_operations_allowed')
            self.IsVisibleToReceiver = kwargs.get('is_visible_to_receiver')

            self.Version = kwargs.get('version', [])

            self.ExtensionData = None

            # Timber owner
            if not isinstance(kwargs.get('timber_owner'), TimberOwner):
                from elvis.api import ElvisException
                raise ElvisException("ELVIS didn't return a proper transport order", raw={})
            self.TimberOwner = kwargs.get('timber_owner')

            # Timber receiver destination
            assert isinstance(kwargs.get('timber_receiver_destination'), TimberReceiverDestination)
            self.TimberReceiverDestination = kwargs.get('timber_receiver_destination')

            # Transporter
            assert isinstance(kwargs.get('transporter'), TransportOrderTransporter)
            self.Transporter = kwargs.get('transporter')

            # Load status change logs
            status_change_logs = kwargs.get('status_change_logs')
            if status_change_logs:
                if isinstance(status_change_logs, TransportOrderStatusChangeLog):
                    status_change_logs = [status_change_logs, ]

                assert not list(filter(lambda x: not isinstance(x, TransportOrderStatusChangeLog), status_change_logs))
                self.StatusChangeLogs = status_change_logs

            # Load shipments
            shipments = kwargs.get('shipments')
            if shipments:
                if isinstance(shipments, Shipment):
                    shipments = [shipments, ]

                assert not list(filter(lambda x: not isinstance(x, Shipment), shipments))
                self.Shipments = shipments
        else:
            # Timber owner
            if not isinstance(self.TimberOwner, TimberOwner):
                self.TimberOwner = TimberOwner(dict_data=self.TimberOwner)

            # Timber receiver destination
            if not isinstance(self.TimberReceiverDestination, TimberReceiverDestination):
                self.TimberReceiverDestination = TimberReceiverDestination(dict_data=self.TimberReceiverDestination)

            # Transporter
            if not isinstance(self.Transporter, TransportOrderTransporter):
                self.Transporter = TransportOrderTransporter(dict_data=self.Transporter)

            # Load status change logs
            status_change_logs = self.StatusChangeLogs
            self.StatusChangeLogs = []

            if status_change_logs:
                for item in status_change_logs:
                    self.StatusChangeLogs.append(TransportOrderStatusChangeLog(dict_data=item))

            # Load shipments
            shipments = self.Shipments
            self.Shipments = []

            if shipments:
                for item in shipments:
                    self.Shipments.append(Shipment(dict_data=item))


# noinspection PyPep8Naming
class FineMeasurementFile(ElvisModel):

    def __init__(self, **kwargs):
        super(FineMeasurementFile, self).__init__(**kwargs)

        if not self._already_loaded:
            self.Description = kwargs.get('description')
            self.ContentType = kwargs.get('content_type')
            self.FileName = kwargs.get('file_name')

            self.Data = force_bytes(kwargs.get('data'))

            self.ExtensionData = None

        else:
            self.Data = force_bytes(self.Data)
