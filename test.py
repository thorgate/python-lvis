# coding=utf-8
from datetime import datetime
import uuid

from elvis.api import ElvisClient
from elvis.enums import (WarehouseType, WarehouseListItemSearchField, WarehouseListItemSortField, SortDirection, VehicleType, WaybillStatus,
                         WaybillRoleContext, WaybillListItemSearchField, WaybillListItemSortField, AssortmentType)
from elvis.models import (TimberAssortment, Certificate, TimberBatch, TimberWarehouse, Address, FilterItem, SortItem, Pack, Shipment,
                          Warehouse, AdditionalProperty, TimberOwner, AuthorizedPerson, TimberReceiverDestination, TimberReceiver,
                          WaybillTransporter, Transport, Person, Vehicle, Waybill)


class ElvisProxyTest(object):

    def __init__(self):
        self.file_path = "test_cert.pfx"

        self.client = ElvisClient("http://54.194.211.213:9500/%s", "00000000000", certificate_pass='test')
        self.client.load_cert_from_file(self.file_path)

        self.warehouse_id = None
        self.waybill_id = None
        self.waybill = None

    def test_authorize(self):
        print("Ühenduse loomine ...")
        assert self.client.authorize()
        print("Ühenduse loomine õnnestus")

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

        print("Veoselehe sisestamine õnnestus %s!" % self.waybill_id)

    def test_get_waybill(self):
        print("Veoselehe lugemine (number = %s) ..." % self.waybill_id)

        self.waybill = self.client.get_waybill(self.waybill_id)
        print("Veoselehe lugemine õnnestus %s!" % self.waybill.Number)

    def test_set_waybill_status(self):
        print("Veoselehe (number = %s) staatuse muutmine %d -> %d ..." % (self.waybill.Number,
                                                                           self.waybill.Status,
                                                                           WaybillStatus.Unloaded))

        if self.client.set_waybill_status(self.waybill.Number, WaybillStatus.Unloaded, "Maha laetud.",
                                          None, 200, None, self.waybill.Version):
            print("Veosele staatuse muutmine õnnestus!")

    def test_get_waybill_status(self):
        print("Veoselehe (number = %s) staatuse pärimine..." % self.waybill.Number)
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


if __name__ == '__main__':

    test = ElvisProxyTest()

    # Start tests
    test.test_authorize()

    test.test_assortment_types()
    test.test_assortment_types_company()

    test.test_add_warehouse()
    test.test_get_warehouse()
    test.test_search_warehouse()
    test.test_delete_warehouse()

    test.test_insert_waybill()
    test.test_get_waybill()
    test.test_set_waybill_status()
    test.test_get_waybill_status()

    test.test_search_waybills()

    print("Testi lõpp!")
