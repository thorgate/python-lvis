

class AssortmentType(object):
    ELVIS = 0
    COMPANY = 1


class Priority(object):
    Low = 11001
    Normal = 11002
    High = 11003


class WarehouseListItemSearchField(object):
    CompanyRegistrationNumber = 0
    UserId = 1
    Code = 2
    Name = 3
    TypeId = 4
    Address = 5
    ContactName = 6
    CreatedOnStart = 7
    CreatedOnEnd = 8
    IsActive = 9
    IsPublic = 10
    IsArchived = 11
    AssortmentName = 12
    HoldingBaseId = 13
    TimberBatchContractNumber = 14
    TimberBatchDocumentDate = 15
    WaybillNumber = 16
    WaybillNumberAlternate = 17
    TransportOrderNumber = 18
    TransportOrderNumberAlternate = 19
    WaybillStatusId = 20
    AdditionalPropertyTypeId = 21
    AdditionalProperty = 22


class TransportOrderListItemSearchField(object):
    GroupId = 0
    OwnerCode = 1
    RecieverCode = 2
    TransporterCode = 3
    DeadlineFrom = 4
    DeadlineTo = 5
    TransportOrderNumber = 6
    TransportOrderNumberAlternate = 7
    OwnerCompanyName = 8
    TransporterCompanyName = 9
    SourceWarehouseName = 10
    DestinationWarehouseName = 11
    IsDeleted = 12
    StatusId = 13
    IsArchived = 14
    ReportFilterDateFrom = 15
    ReportFilterDateTo = 16
    RecieverName = 17
    SourceWarehouseCodeOrName = 18
    DestinationWarehouseCodeOrName = 19
    AssortmentName = 20
    HoldingBaseId = 21
    TimberBatchContractNumber = 22
    TimberBatchDocumentDate = 23
    DriverName = 24
    VanRegistrationNumber = 25
    DriverPersonCode = 26
    VisibleToReceiver = 27
    AdditionalPropertyTypeId = 28
    AdditionalProperty = 29
    ContactType = 30
    ContactName = 31


class TransportOrderListItemSortField(object):
    Deadline = 0
    CreatedOn = 1
    OwnerName = 2
    DestinationWarehouseName = 3
    TransporterName = 4
    Number = 5


class WarehouseListItemSortField(object):
    Code = 0
    Name = 1
    TypeId = 2
    Address = 3
    ResponsiblePersonName = 4
    CreatedOn = 5


class SortDirection(object):
    Asc = 0
    Desc = 1


class TransportOrderRoleContext(object):
    Owner = 0
    Reciever = 1
    Transporter = 2


class WaybillRoleContext(object):
    Owner = 1
    Reciever = 2
    Transporter = 4
    All = 8


class WarehouseType(object):
    ForestEdge = 5001
    Middle = 5002
    End = 5003


class VehicleType(object):
    Van = 9001
    Trailer = 9002


class WaybillStatus(object):
    Composing = 7001
    Confirmed = 7002
    Unloaded = 7003
    Received = 7004
    Measured = 7005
    MeasurementConfirmed = 7006
    Finalized = 7007
    Cancelled = 7008


class WaybillListItemSearchField(object):
    OwnerCode = 0
    RecieverCode = 1
    RecieverName = 2
    TransporterCode = 3
    WaybillNumber = 4
    WaybillNumberAlternate = 5
    OwnerCompanyName = 6
    TransporterCompanyName = 7
    SourceWarehouseName = 8
    SourceWarehouseCodeOrName = 9
    DestinationWarehouseName = 10
    DestinationWarehouseCodeOrName = 11
    IsDeleted = 12
    StatusId = 13
    IsArchived = 14
    ReportFilterDateFrom = 15
    ReportFilterDateTo = 16
    CreatedOnStart = 17
    CreatedOnEnd = 18
    TransportOrderNumber = 19
    TransportOrderNumberAlternate = 20
    AssortmentName = 21
    HoldingBaseId = 22
    TimberBatchContractNumber = 23
    TimberBatchDocumentDate = 24
    DriverName = 25
    VanRegistrationNumber = 26
    TrailerRegistrationNumber = 27
    IsDisputed = 28
    DriverPersonCode = 29
    ReportCompanyName = 30
    AdditionalPropertyTypeId = 31
    AdditionalProperty = 32
    ContactType = 33
    ContactName = 34
    AuthorizedReceiverCode = 35
    NotInStatusId = 36
    Inspected = 37


class WaybillListItemSortField(object):
    CreatedOn = 0
    OwnerName = 1
    DestinationWarehouseName = 2
    TransporterName = 3
    Number = 4


class TransportOrderStatus(object):
    Composing = 4001
    Submitted = 4002
    Accepted = 4003
    Declined = 4004
    Finalized = 4005
    Cancelled = 4006
