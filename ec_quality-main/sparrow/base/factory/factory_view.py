# MainMenuFactory,
import datetime
from time import time

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.http import HttpResponse
from sqlalchemy.sql import text
from tenant_schemas.utils import schema_context

from accounts.models import UserProfile
from accounts.services import UserService
from base.factory.master_factory import (
    AccountMasterFactory,
    AttachmentMasterFactory,
    AuditlogMasterFactory,
    BaseMasterFactory,
    CampaignMasterFactory,
    CurrencyRateFactory,
    EmailTemplateMasterFactory,
    FinancialMasterFactory,
    HrmMasterFactory,
    InspectionTypesFactory,
    InventoryFactory,
    LogisticsMasterFactory,
    NotificationEventFactory,
    PartnerMasterFactory,
    ProductionMasterFactory,
    ProductMasterFactory,
    PurchaseMasterFactory,
    SalesMasterFactory,
    SubscribeNotificationFactory,
    TaskMasterFactory,
)
from base.models import AppResponse, Currency

# from clients.models import Client

# MainMenuFactory,
from crm.factory import CampaignTemplateFactory, DealsFactory, MailCampaignFactory, PipelineFactory, SubscriberListFactory, SubscriberListLineFactory
from eda.factory import EdaFactory
from inventory.factory import LocationStructureFactory, StockStatusFactory
from partners.factory import AddressFactory, BankDetailFactory, ContactRelationFactory, PartnerFactory
from partners.models import Address, BankDetail, Country, Partner, State
from production.factory import FixedCostFactory  # MfgOrderFactory,
from production.factory import (
    LabourLevelFactory,
    MachineFactory,
    MfgBOMFactory,
    OperationFactory,
    ReworkIssueFactory,
    RoutingFactory,
    ShiftFactory,
    TimeAttributesFactory,
    UnplannedOperationFactory,
    WorkcenterFactory,
)

# from products.factory import CategoryMasterFactory, InternalCategoryFactory, LabelMasterFactory, ProductFactory, ProductGroupFormFactory, ProductGroupMasterFactory

# from purchasing.factory import PurchaseOrderFactory, PurchasePlanFactory, PurchaseRequisitionFactory
# from sales.factory import SalesOrderFactory, SalesPriceFactory
from sparrow.dbengine import DBEngine
from task.factory import TaskFactory


def init_database(domain_url, schema_name, demo_data):
    with schema_context("public"):
        start = time()
        max_id_query = "select max(id) + 1 from public.clients_client"
        today = datetime.date.today()
        subscription_expiration_date = datetime.date(year=today.year + 50, month=today.month, day=today.day)

        # with DBEngine().connect() as conn:
        #     schema_id = conn.execute(text(max_id_query)).fetchall()[0][0]
        #     demo_data = True if demo_data == "true" else False

        #     if domain_url is not None:
        #         schema_name = "sparrow_" + str(schema_id)
        #         # On tenant save, it applies all the migration on given schema
        #         tenant = Client(domain_url=domain_url, schema_name=schema_name, name=schema_name, subscription_expiration=subscription_expiration_date, on_trial=False)
        #         tenant.save()

    end = time()
    print("Elapsed time: {}".format(end - start))
    with schema_context("public"):
        if demo_data is True:
            print("Populating both master data and demo data ...")
            populate_master_data()
            populate_demo_data()
        else:
            print("Populating only master data ...")
            populate_master_data()
    return HttpResponse(AppResponse.msg(1, "done"), content_type="json")


def populate_master_data():

    partner = Partner.objects.filter(is_hc=True).first()
    country = Country.objects.filter(name="India").first()
    if country is None:
        country = Country.objects.create(name="India", code="IN", has_state=True)
    if partner is None:
        partner = Partner.objects.create(is_hc=True)
    partner.name = "Pouros Inc"
    partner.email = "mllywarch6@ca.gov"
    partner.timezone = "America/Bogota"
    partner.phone = "863-379-6950"
    partner.mobile = "863-379-6950"
    partner.country_id = country.id
    cur = Currency.objects.filter(symbol="EUR").first()
    partner.currency = cur if cur is not None else Currency.objects.create(name="Euro", is_base=True, symbol="EUR", is_deleted=False)
    partner.save()
    address_types = [1, 2, 3]
    address = Address.objects.filter(partner_id=partner.id, address_type=1, is_deleted=False).first()
    bank_detail = BankDetail.objects.filter(bank_ac_no="254184521542", bank_name="BOB", partner_id=partner.id).first()

    state = State.objects.filter(name="Gujarat").first()
    if state is None:
        state = State.objects.create(name="Gujarat", code="24", country_id=country.id)

    if address is None:
        for address_type in address_types:
            Address.objects.create(
                partner_id=partner.id,
                street="6 Algoma Street",
                street2="Stoughton",
                zip=14614,
                city="Rochester",
                address_type=address_type,
                country_id=country.id,
                state_id=state.id,
            )

    if bank_detail is None:
        bank_detail = BankDetail.objects.create(bank_name="BOB", bank_ac_no="254184521542", partner_id=partner.id, bank_country_id=country.id)

    user = User.objects.filter(email="admin@admin.com").first()
    if user is None:
        user = UserService.create_user("Admin", "Admin", "admin@admin.com", True, True, True, partner.id, False)
        user.password = make_password("ispl123;")
        user.save()
    user_profile = UserProfile.objects.filter(user_id=user.id).first()
    user_profile.color_scheme = "bg_color:#363062,button_color:#4d4c7d,link_color:#4d4c7d,row_color:#fee2b3"
    user_profile.image_name = "4_b.jpg"
    user_profile.save()
    # populate master tables
    ProductionMasterFactory.create_production_master()
    LogisticsMasterFactory.create_logistics_master()
    CampaignMasterFactory.create_campaign_master()
    AuditlogMasterFactory.create_audit_log_master()
    FinancialMasterFactory.create_financial_master()
    AttachmentMasterFactory.create_file_type()
    # InventoryFactory.create_inventory_master()
    ProductMasterFactory.create_product_master()
    BaseMasterFactory.create_base_master()
    PurchaseMasterFactory.create_purchase_master()
    SalesMasterFactory.create_sales_master()
    AccountMasterFactory.create_parent_menu()
    PartnerMasterFactory.create_partner_master()
    AttachmentMasterFactory.create_file_type()
    # InventoryFactory.create_inventory_master()
    ProductMasterFactory.create_product_master()

    ProductionMasterFactory.create_production_master()
    LogisticsMasterFactory.create_logistics_master()
    CampaignMasterFactory.create_campaign_master()
    AuditlogMasterFactory.create_audit_log_master()
    FinancialMasterFactory.create_financial_master()
    TaskMasterFactory.create_task_master()
    EmailTemplateMasterFactory.create_email_template()
    NotificationEventFactory.create_notification_event()  # should be below emailtemplate
    SubscribeNotificationFactory.create_subscribe_notification()  # should be below NotificationEventFactory
    CurrencyRateFactory.create_currency_rate()
    PipelineFactory.create_pipeline()  # create pipeline always before deals
    return None


def populate_demo_data():
    # populate dependent tables
    CampaignTemplateFactory.create_campaign_template()
    # LabelMasterFactory.create_label_master()
    InspectionTypesFactory.create_inspection_type()  #
    # CategoryMasterFactory.create_category_master()
    LocationStructureFactory.create_location_structure()
    ###
    LabourLevelFactory.create_labour_level()
    ShiftFactory.create_shift()
    UnplannedOperationFactory.create_unplanned_operation_master()
    OperationFactory.create_operation_master()
    FixedCostFactory.create_fixed_cost()
    ReworkIssueFactory.create_rework_issue()
    ###
    MachineFactory.create_machine()
    HrmMasterFactory.create_hrm_master()
    # ProductGroupMasterFactory.create_product_group_master()
    PartnerFactory.create_partner()
    BankDetailFactory.create_bank_detail()
    ContactRelationFactory.create_contact_relation()
    AddressFactory.create_address()
    SubscriberListFactory.create_subscriber_list()

    # InternalCategoryFactory.create_internal_category()
    # ProductGroupFormFactory.create_product_group_form()
    # ProductFactory.create_product()
    StockStatusFactory.create_stockstatus()
    WorkcenterFactory.create_workcenter()

    MfgBOMFactory.create_bom()
    RoutingFactory.create_routing()
    # SalesOrderFactory.create_order()
    # PurchaseOrderFactory.create_purchase_order()
    # PurchasePlanFactory.create_purchaseplan()
    # PurchaseRequisitionFactory.create_purchase_requisition()
    # MfgOrderFactory.create_mfg_order()
    DealsFactory.create_deals()
    TimeAttributesFactory.create_time_attributes()
    SubscriberListLineFactory.create_subscriber_list()
    TaskFactory.create_task()
    MailCampaignFactory.create_mail_campaign()
    # SalesPriceFactory.create_sales_price()
    EdaFactory.create_category()
    EdaFactory.create_menufacturer()
    EdaFactory.create_document()
    EdaFactory.create_package()
    EdaFactory.create_part()

    # LeadFactory.create_lead()
    return None
