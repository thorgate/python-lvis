# coding=utf-8
from datetime import datetime
import uuid
import json

from elvis.api import ElvisClient, ElvisException, ElvisEncoder
from elvis.enums import (WarehouseType, WarehouseListItemSearchField, WarehouseListItemSortField, SortDirection, VehicleType, WaybillStatus,
                         WaybillRoleContext, WaybillListItemSearchField, WaybillListItemSortField, AssortmentType)
from elvis.models import (TimberAssortment, Certificate, TimberBatch, TimberWarehouse, Address, FilterItem, SortItem, Pack, Shipment,
                          Warehouse, AdditionalProperty, TimberOwner, AuthorizedPerson, TimberReceiverDestination, TimberReceiver,
                          WaybillTransporter, Transport, Person, Vehicle, Waybill, FineMeasurementFile)

import lvis_test_config


class ElvisProxyTest(object):

    def __init__(self):
        self.file_path = lvis_test_config.TEST_CERTIFICATE_PATH

        self.client = ElvisClient(lvis_test_config.PROXY_HOST_URL, lvis_test_config.TEST_CERTIFICATE_PERSON_CODE,
                                  certificate_pass=lvis_test_config.TEST_CERTIFICATE_PASSWORD)
        self.client.load_cert_from_file(self.file_path)

        self.warehouse_id = None
        self.waybill_id = None
        self.waybill = None

    def test_authorize(self):
        print("Ühenduse loomine ...")
        assert self.client.authorize()
        print("Ühenduse loomine õnnestus")

    def test_get_session_tag(self):
        print("Ühenduse sildi kontrollimine")

        original_token = self.client.session_token

        tag = self.client.get_session_tag()
        print('    Vaikimisi silt: %s - %s' % (tag, original_token))
        assert tag == 'default'
        print('    Vaikimisi silt on korrektne')

        print("    Valikulise sildi testimine: 'testing'")
        assert self.client.authorize('testing')

        tag = self.client.get_session_tag()
        new_token = self.client.session_token

        print('    Valikuline silt: %s - %s' % (tag, new_token))
        assert tag == 'testing'
        print('    Valikuline silt on korrektne')

        assert new_token != original_token
        print('    %s != %s: Success' % (original_token, new_token))

        print("Ühenduse sildi kontrollimine õnnestus")

    def test_assortment_types(self):
        print("Sortimendi tüüpide pärimine (elvise omad) ...")

        a_types = self.client.get_assortment_types(AssortmentType.ELVIS)

        print("Sortimendi tüüpide pärimine õnnestust (%d vastet)!" % len(a_types))

    def test_assortment_types_company(self):
        print("Sortimendi tüüpide pärimine (firma omad) ...")

        a_types = self.client.get_assortment_types(AssortmentType.COMPANY)

        print("Sortimendi tüüpide pärimine õnnestust (%d vastet)!" % len(a_types))

    def test_add_warehouse(self):
        print("Lao lisamine")

        the_id = str(uuid.uuid4()).replace('-', '').lower()

        assortments = [
            TimberAssortment(amount=12, description='Description', assortment_type=34)
        ]
        certificates = [
            Certificate(certificate_number='CertificateNumber', type_id=3001)
        ]

        timber_batch = TimberBatch(
            appropriation='Appropriation',
            cadastral_number='CadastralNumber',
            description='Description',
            doc_number='DocNumber',
            prev_owner_address='PreviousOwnerAddress',
            prev_owner_code='PreviousOwnerCode',
            prev_owner_name='PreviousOwnerName',
            reg_immovable_number='RegisteredImmovableNumber',
            quarter='Quarter',

            doc_date=datetime.now(),
            holding_base_id=6001,

            assortments=assortments,
            certificates=certificates,
        )

        warehouse = TimberWarehouse(
            cadastral_number='CadastralNumber',
            appropriation='Appropriation',
            name='Name_%s' % the_id,
            code=the_id[0:22],
            contact_email='ContactEmail',
            contact_name='ContactName',
            contact_phone='ContactPhone',
            description="Description",
            quarter="Quarter",
            is_active=True,
            is_public=True,
            is_dry=True,
            is_parallel_loading=True,
            lambert_est_x=6528248.6,
            lambert_est_y=536139.5,
            timber_batches=[
                timber_batch
            ],
            warehouse_type=WarehouseType.ForestEdge,
            forest_district_id=8001,
            address=Address(address_additional_information="AddressAdditionalInformation",
                            city_borough="CityBorough",
                            county="County",
                            ehak="EHAK",
                            near_address="NearAddress",
                            rural_district="RuralDistrict")
        )
        self.warehouse_id = self.client.insert_warehouse(warehouse)

        print("Lao sisestamine õnnestus! ID: %s" % self.warehouse_id)

    def test_get_warehouse(self):
        print("Lao lugemine (number = %d) ..." % self.warehouse_id)

        ware = self.client.get_warehouse(self.warehouse_id)

        print("Lao lugemine õnnestus %d!" % ware.Id)

    def test_search_warehouse(self):
        print("Ladude otsimine.")

        warehouse_search_res = self.client.search_warehouses(FilterItem(WarehouseListItemSearchField.IsPublic, True),
                                                             SortItem(WarehouseListItemSortField.Name,
                                                                      SortDirection.Asc),
                                                             0, 10, True)

        print("Ladude ostimine õnnestus! Leiti %d vastet." % warehouse_search_res.get('TotalCount', 0))

    def test_delete_warehouse(self):
        print("Lao %d kustutamine." % self.warehouse_id)

        if self.client.delete_warehouse(self.warehouse_id) is True:
            print("Lao kustutamine õnnestus!")

    def test_insert_waybill(self):
        print("Veoselehe sisestamine...")

        timber_batch = TimberBatch(
            appropriation="TestAppropriation",
            cadastral_number="14235",
            doc_date=datetime.now(),
            doc_number="TestDocNumberTestD",
            holding_base_id=6001,
            prev_owner_name="TestPreviousOwnerName",
            prev_owner_code="TestPreviousOwnerPhone",
            prev_owner_address="TestPreviousOwnerAddress",
            reg_immovable_number="TestRegisteredImmovableNumber",
            quarter="TestQuarter",

            certificates=[
                Certificate(
                    certificate_number="TestCertificateNumber",
                    type_id=3001
                )
            ],

            assortments=[
                TimberAssortment(
                    amount=5343,
                    assortment_type=34,
                ),
                TimberAssortment(
                    assortment_type=29,
                    amount=0,
                    packs=[
                        Pack(factor=1, height=2, length=3, number=5, vehicle_type=VehicleType.Van, width=4),
                        Pack(factor=1, height=2, length=3, number=5, vehicle_type=VehicleType.Trailer, width=4),
                    ]
                )
            ]
        )

        shipments = [
            Shipment(
                warehouse=Warehouse(
                    appropriation="TestAppropriation",
                    code="TestCode",
                    forest_district_id=8001,
                    lambert_est_x=1234,
                    lambert_est_y=4321,
                    name="TestName",
                    quarter="TestQuarter",
                    contact_email="TestContactEmail",
                    contact_name="TestContactName",
                    contact_phone="TestContactPhone",
                    description="TestDescription",

                    address=Address(
                        address_additional_information="TestAddressAdditionalInformation",
                        rural_district="TestRuralDistrict",
                        city_borough="TestCityBorough",
                        county="TestCounty",
                        ehak="TestEHAK",
                        near_address="TestNearAddress"
                    ),

                    additional_properties=AdditionalProperty(
                        type_id=25001,
                        value="SWhTestProp"
                    )
                ),

                timber_batches=[
                    timber_batch
                ]

            )
        ]

        timber_owner = TimberOwner(
            code="1111",
            email="TestEmail",
            name="TestName",
            phone="TestPhone",

            address=Address(
                address_additional_information="TestAddressAdditionalInformation",
                rural_district="TestRuralDistrict",
                city_borough="TestCityBorough",
                county="TestCounty",
                ehak="TestCounty",
                near_address="TestNearAddress"
            ),

            authorized_person=AuthorizedPerson(
                authorization_base="TestAuthorizationBase",
                email="TestEmail",
                firstname="TestFirstname",
                lastname="TestLastName",
                person_code="47101010033",
                phone="TestPhone",
                address=Address(
                    address_additional_information="TestAddressAdditionalInformation",
                    rural_district="TestRuralDistrict",
                    city_borough="TestCityBorough",
                    county="TestCounty",
                    ehak="TestEHAK",
                    near_address="TestNearAddress"
                )
            )
        )

        timber_receiver_destination = TimberReceiverDestination(
            destination=Warehouse(
                appropriation="TestAppropriation",
                code="3333",
                forest_district_id=8001,
                lambert_est_x=1234,
                lambert_est_y=4321,
                name="TestName",
                quarter="TestQuarter",
                contact_email="TestContactEmail",
                contact_name="TestContactName",
                contact_phone="TestContactPhone",
                description="TestDescription",
                address=Address(
                    address_additional_information="TestAddressAdditionalInformation",
                    rural_district="TestRuralDistrict",
                    city_borough="TestCityBorough",
                    county="TestCounty",
                    ehak="TestEHAK",
                    near_address="TestNearAddress"
                ),

                additional_properties=AdditionalProperty(
                    type_id=25001,
                    value="TrecWhTestProp"
                )
            ),
            receiver=TimberReceiver(
                code="1111",
                email="TestEmail",
                name="Metsaomandamise AS",
                phone="TestPhone",
                contact_email="TestContactEmail",
                contact_name="TestContactName",
                contact_phone="TestContactPhone",
                address=Address(
                    address_additional_information="TestAddressAdditionalInformation",
                    rural_district="TestRuralDistrict",
                    city_borough="TestCityBorough",
                    county="TestCounty",
                    ehak="TestEHAK",
                    near_address="TestNearAddress"
                ),

                additional_properties=AdditionalProperty(
                    type_id=25001,
                    value="TrecTestProp"
                )
            )
        )

        transporter = WaybillTransporter(
            contact_email="TestContactEmail",
            contact_name="TestContactName",
            contact_phone="TestContactPhone",
            company_registration_number="2222",

            transport=Transport(
                driver=Person(
                    email="TestEmail",
                    firstname="TestFirstname",
                    lastname="TestLastName",
                    person_code="47101010033",
                    phone="TestPhone"
                ),
                trailer=Vehicle(
                    model="TestTrailerModel",
                    registration_number="TestTrailerRegistrationNumber"
                ),
                van=Vehicle(
                    model="TestVanModel",
                    registration_number="TestVanRegistrationNumber"
                )
            ),

            additional_properties=AdditionalProperty(
                type_id=25001,
                value="TransTestProp"
            )
        )

        waybill = Waybill(
            alt_number='TestAltNumber123',
            pre_journey_length=123,
            total_journey_length=34123,
            status=WaybillStatus.Confirmed,
            transport_order_number="Test",
            shipments=shipments,
            timber_owner=timber_owner,
            timber_receiver_destination=timber_receiver_destination,
            transporter=transporter,
        )

        self.waybill_id = self.client.insert_waybill(waybill)

        print("Veoselehe sisestamine õnnestus %s!" % str(self.waybill_id))

    def test_get_waybill(self):
        print("Veoselehe lugemine (number = %s) ..." % self.waybill_id)

        self.waybill = self.client.get_waybill(self.waybill_id)
        print("Veoselehe lugemine õnnestus %s!" % str(self.waybill.Number))

    def test_set_waybill_status(self):
        print("Veoselehe (number = %s) staatuse muutmine %d -> %d ..." % (self.waybill.Number,
                                                                           self.waybill.Status,
                                                                           WaybillStatus.Unloaded))

        if self.client.set_waybill_status(self.waybill.Number, WaybillStatus.Unloaded, "Maha laetud.",
                                          None, 200, None, self.waybill.Version):
            print("Veosele staatuse muutmine õnnestus!")

    def test_get_waybill_status(self):
        print("Veoselehe (number = %s) staatuse pärimine..." % str(self.waybill.Number))
        status = self.client.get_waybill_status(self.waybill.Number)
        print("Veoselehe staatuse päring õnnestus, staatus on %s." % status.Status)

    def test_search_waybills(self):
        print("Veoselehtede otsimine ...")

        search_result = self.client.search_waybills(
            WaybillRoleContext.All,
            FilterItem(
                WaybillListItemSearchField.WaybillNumber,
                self.waybill.Number
            ),
            SortItem(
                WaybillListItemSortField.CreatedOn,
                SortDirection.Asc
            ),
            0, 10, True
        )

        print("Veoselehtede otsimine õnnestus! (%d tulemust)" % search_result.TotalCount)

    def test_reception_assortments(self):
        print("Vastuvõetud sortimendide lisamine ...", self.waybill.Shipments[0].TimberBatches[0].Id)

        for assortment in self.waybill.Shipments[0].TimberBatches[0].Assortments:
            reception_assortment_id = self.client.insert_reception_assortment(
                self.waybill.Shipments[0].TimberBatches[0].Id,
                assortment,
            )
            print("    Vastuvõetud sortimendi lisamine õnnestus (Id = %s)." % reception_assortment_id)

            print("    Vastuvõetud sortimendi kustutamine (id = %s) ..." % reception_assortment_id)
            if self.client.delete_reception_assortment(reception_assortment_id):
                print("    Vastuvõetud sortimendi kustutamine õnnestus!")

            else:
                raise Exception("    Vastuvõetud sortimendi kustutamine ebaõnnestus!")

            print("    Vastuvõetud sortimendi lisamine ...")
            reception_assortment_id2 = self.client.insert_reception_assortment(
                self.waybill.Shipments[0].TimberBatches[0].Id,
                assortment,
            )
            assert reception_assortment_id != reception_assortment_id2
            print("    Vastuvõetud sortimendi lisamine õnnestus (Id = %s)." % reception_assortment_id2)

    def test_fine_measurement_assortments(self):
        try:
            print("Täppismõõdetud sortimendi lisamine ...", self.waybill.Number)
            fine_measurement_id = self.client.insert_fine_measurement_assortment(
                self.waybill.Number,
                TimberAssortment(amount=12, description='Täppis andmed', assortment_type=3)
            )
            print("Täppismõõdetud sortimendi lisamine õnnestus (Id = %s)!" % fine_measurement_id)

        except ElvisException:
            status = self.client.get_waybill_status(self.waybill.Number)
            self.waybill.Status = status.Status
            self.waybill.Version = status.Version

            print("Veoselehe (number = %s) staatuse muutmine %d -> %d ..." % (self.waybill.Number,
                                                                               self.waybill.Status,
                                                                               WaybillStatus.Received))

            if self.client.set_waybill_status(self.waybill.Number, WaybillStatus.Received, "Vastuvõetud",
                                              None, 200, None, self.waybill.Version):
                print("Veosele staatuse muutmine õnnestus!")

        else:
            raise Exception('Täppismõõdetud sortimendi lisamine veoselehele mille staatus pole Received peaks ebaõnnestuma')

        print("Täppismõõdetud sortimendi lisamine ...", self.waybill.Number)
        fine_measurement_id = self.client.insert_fine_measurement_assortment(
            self.waybill.Number,
            TimberAssortment(amount=12, description='Täppis andmed', assortment_type=3)
        )
        print("Täppismõõdetud sortimendi lisamine õnnestus (Id = %s)!" % fine_measurement_id)

        print("Täppismõõdetud sortimendi kustutamine (id = %s) ..." % fine_measurement_id)
        if self.client.delete_fine_measurement_assortment(fine_measurement_id):
            print("Täppismõõdetud sortimendi kustutamine õnnestus!")

        else:
            raise Exception("Täppismõõdetud sortimendi kustutamine ebaõnnestus!")

        print("Täppismõõdetud sortimendi lisamine ...")
        fine_measurement_id2 = self.client.insert_fine_measurement_assortment(
            self.waybill.Number,
            TimberAssortment(amount=321, description='Täppis andmed 2', assortment_type=3)
        )
        assert fine_measurement_id != fine_measurement_id2
        print("Täppismõõdetud sortimendi lisamine õnnestus (Id = %s)!" % fine_measurement_id2)

    def test_fine_measurement_files(self):
        print("Täppismõõdetud faili lisamine ...")
        fine_measurement_file_id = self.client.insert_fine_measurement_file(
            self.waybill.Number,
            FineMeasurementFile(content_type='text/plain', data='Test tekstifail', description='Testimiseks lisatud', file_name='Test.txt'),
        )
        print("Täppismõõdetud faili lisamine õnnestus (id = %s)" % fine_measurement_file_id)

        print("Täppismõõdetud faili kustutamine (id = %s) ..." % fine_measurement_file_id)
        if self.client.delete_fine_measurement_file(fine_measurement_file_id):
            print("Täppismõõdetud faili kustutamine õnnestus!")

        else:
            raise Exception("Täppismõõdetud faili kustutamine ebaõnnestus!")


if __name__ == '__main__':
    test = ElvisProxyTest()

    # Start tests
    test.test_authorize()
    test.test_get_session_tag()

    if lvis_test_config.TESTING_RANGE:
        all_tests = lvis_test_config.TESTING_RANGE is True
        if not all_tests:
            if not isinstance(lvis_test_config.TESTING_RANGE, (list, tuple)):
                raise ValueError('TESTING RANGE MUST BE True or a list/tuple typed value')

        if not all_tests and lvis_test_config.TEST_LEVEL_WAYBILL not in lvis_test_config.TESTING_RANGE:
            if lvis_test_config.TEST_LEVEL_WAYBILL_ASSORTMENTS in lvis_test_config.TESTING_RANGE:
                print('Adding waybill to testing range since its needed for other tests.')
                lvis_test_config.TESTING_RANGE.append(lvis_test_config.TEST_LEVEL_WAYBILL)

        if all_tests or lvis_test_config.TEST_LEVEL_ASSORTMENTS in lvis_test_config.TESTING_RANGE:
            print('Testing assortments')
            test.test_assortment_types()
            test.test_assortment_types_company()

        if all_tests or lvis_test_config.TEST_LEVEL_WAREHOUSE in lvis_test_config.TESTING_RANGE:
            print('Testing warehouses')
            test.test_add_warehouse()
            test.test_get_warehouse()
            test.test_search_warehouse()
            test.test_delete_warehouse()

        if all_tests or lvis_test_config.TEST_LEVEL_WAYBILL in lvis_test_config.TESTING_RANGE:
            print('Testing waybills')

            test.test_insert_waybill()
            test.test_get_waybill()
            test.test_set_waybill_status()
            test.test_get_waybill_status()

            test.test_search_waybills()

            if all_tests or lvis_test_config.TEST_LEVEL_WAYBILL_ASSORTMENTS in lvis_test_config.TESTING_RANGE:
                test.test_reception_assortments()
                test.test_fine_measurement_assortments()
                test.test_fine_measurement_files()

    print("Testi lõpp!")
