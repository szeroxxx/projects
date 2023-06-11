import json
import os
import xml.etree.ElementTree as ET

from django.contrib.contenttypes.models import ContentType
from django.db import connection
from post_office.models import EmailTemplate

from accounts.models import ContentPermission, MainMenu, PagePermission
from attachment.models import FileType
from auditlog.models import AuditAction
from base.factory.factory_data import FactoryDemoData, FactoryMasterData
from base.models import AppReport, Currency, CurrencyRate, DMI_queries, DocNumber, ShippingService, SysParameter, TaskScheduler, Template_Form
from crm.models import CampaignType, Stage

# from clients.models import Client
from financial.models import InvoiceStatus, PaymentDifferenceType, PaymentMode, TaxRule
from hrm.models import AcademicQualification, LeaveType
from inventory.models import Location, MoveType, Warehouse
from logistics.models import InspectionType, ShipMethod
from messaging.models import NotificationEvent, SubscribeNotification
from partners.models import Country, LeadSource, LeadStatus, PaymentTerm, State
from production.models import AssemblyPrepStep, UnitOfCapacity, UnitOfCost
from products.models import UnitOfMeasure
from purchasing.models import OrderStatus as PurchaseOrderStatus
from sales.models import OrderStatus as SalesOrderStatus
from sparrow.dbengine import DBEngine
from task.models import TaskType


class EmailTemplateMasterFactory(object):
    @staticmethod
    def create_email_template():
        email_template_data = FactoryMasterData.EMAIL_TEMPLATE
        for data in email_template_data:
            file_name = data["template"]
            app_name = "base"
            folder_name = "factory"
            temp_name = "templates"

            file_path = os.path.join(app_name, folder_name, temp_name, file_name)
            tree = ET.parse(file_path)

            root = tree.getroot()

            for i, element in enumerate(root.getiterator("template")):
                name = element.find("name").text
                description = element.find("description").text
                subject = element.find("subject").text
                html_content = element.find("html_content").text

            email_template = EmailTemplate.objects.filter(name=name).first()

            if email_template is None:
                email_template = EmailTemplate.objects.create(name=name, description=description, subject=subject, html_content=html_content)

                email_template.description = description
                email_template.subject = subject
                email_template.html_content = html_content
                email_template.save()


class NotificationEventFactory(object):
    @staticmethod
    def create_notification_event():
        ne_data = FactoryMasterData.NOTIFICATION_EVENT
        for data in ne_data:
            file_name = data["email_template"]
            app_name = "base"
            folder_name = "factory"
            temp_name = "templates"

            file_path = os.path.join(app_name, folder_name, temp_name, file_name)
            tree = ET.parse(file_path)

            root = tree.getroot()

            for i, element in enumerate(root.getiterator("template")):
                name = element.find("name").text
            template_id = EmailTemplate.objects.filter(name=name).first().id
            notifiction_event = NotificationEvent.objects.filter(name=data["name"]).first()
            if notifiction_event is None:
                contenttype = ContentType.objects.filter(app_label=data["app_label"], model=data["model"]).values("id").first()
                notifiction_event = NotificationEvent.objects.create(
                    name=data["name"],
                    group=data["group"],
                    model_id=contenttype["id"],
                    action=data["action"],
                    subject=data["subject"],
                    is_active=data["is_active"],
                    created_by_id=data["created_by_id"],
                    created_on=data["created_on"],
                    template_id=template_id,
                )
                notifiction_event.text = data["text"]
                notifiction_event.save()


class SubscribeNotificationFactory(object):
    @staticmethod
    def create_subscribe_notification():
        sn_data = FactoryMasterData.SUBSCRIBE_NOTIFICATION
        for data in sn_data:
            notification_event = NotificationEvent.objects.filter(name=data["event"]).values("id").first()
            sub_notification = SubscribeNotification.objects.filter(event_id=notification_event["id"]).first()
            if sub_notification is None:
                sub_notification = SubscribeNotification.objects.create(
                    event_id=notification_event["id"], user_id=data["user_id"], created_by_id=data["created_by_id"], created_on=data["created_on"],
                )
                sub_notification.by_email = data["by_email"]
                sub_notification.in_system = data["in_system"]
                sub_notification.by_sms = data["by_sms"]
                sub_notification.save()


class SalesMasterFactory(object):
    @staticmethod
    def create_sales_order_status():
        sales_order_status_data = FactoryMasterData.SALES_ORDER_STATUS
        for data in sales_order_status_data:
            sales_order_status = SalesOrderStatus.objects.filter(name=data["name"]).first()
            if sales_order_status is None:
                sales_order_status = SalesOrderStatus.objects.create(name=data["name"])
                sales_order_status.description = data["description"]
                sales_order_status.is_active = data["is_active"]
                sales_order_status.include_creditcheck = data["include_creditcheck"]
                sales_order_status.save()

    @staticmethod
    def create_sales_master():
        SalesMasterFactory.create_sales_order_status()


class PurchaseMasterFactory(object):
    @staticmethod
    def create_purchase_order_status():
        purchase_order_status_data = FactoryMasterData.PURCHASE_ORDER_STATUS
        for data in purchase_order_status_data:
            purchase_order_status = PurchaseOrderStatus.objects.filter(name=data["name"]).first()
            if purchase_order_status is None:
                purchase_order_status = PurchaseOrderStatus.objects.create(name=data["name"])
                purchase_order_status.description = data["description"]
                purchase_order_status.is_active = data["is_active"]
                purchase_order_status.save()

    @staticmethod
    def create_purchase_master():
        PurchaseMasterFactory.create_purchase_order_status()


class HrmMasterFactory(object):
    @staticmethod
    def create_academic_qualification():
        academic_qualification_data = FactoryMasterData.ACADEMIC_QUALIFICATION
        for data in academic_qualification_data:
            academic_qualification = AcademicQualification.objects.filter(name=data["name"]).first()
            if academic_qualification is None:
                academic_qualification = AcademicQualification.objects.create(name=data["name"], created_by_id=data["created_by_id"])
                academic_qualification.created_by_id = data["created_by_id"]
                academic_qualification.save()

    @staticmethod
    def create_leave_type():
        leave_type_data = FactoryMasterData.LEAVE_TYPE
        for data in leave_type_data:
            leave_type = LeaveType.objects.filter(name=data["name"]).first()
            if leave_type is None:
                leave_type = LeaveType.objects.create(name=data["name"])
                leave_type.days = data["days"]
                leave_type.save()

    @staticmethod
    def create_hrm_master():
        HrmMasterFactory.create_academic_qualification()
        HrmMasterFactory.create_leave_type()


class BaseMasterFactory(object):
    @staticmethod
    def create_doc_number():
        doc_number_data = FactoryMasterData.DOC_NUMBER
        for data in doc_number_data:
            doc_number = DocNumber.objects.filter(code=data["code"]).first()
            if doc_number is None:
                doc_number = DocNumber.objects.create(code=data["code"], length=data["length"])
                doc_number.desc = data["desc"]
                doc_number.prefix = data["prefix"]
                doc_number.length = data["length"]
                doc_number.increment = data["increment"]
                doc_number.nextint = data["nextint"]
                doc_number.nextnum = data["nextnum"]
                doc_number.save()

    @staticmethod
    def create_shipping_service():
        shipping_service_data = FactoryMasterData.SHIPPING_SERVICE
        for data in shipping_service_data:
            shipping_service = ShippingService.objects.filter(name=data["name"]).first()
            if shipping_service is None:
                shipping_service = ShippingService.objects.create(name=data["name"], created_by_id=data["created_by_id"])
                shipping_service.tracking_url = data["tracking_url"]
                shipping_service.created_by_id = data["created_by_id"]
                shipping_service.save()

    @staticmethod
    def create_currency():
        currency_data = FactoryMasterData.CURRENCY
        for data in currency_data:
            currency = Currency.objects.filter(name=data["name"]).first()
            if currency is None:
                currency = Currency.objects.create(name=data["name"], is_deleted=False)
            currency.symbol = data["symbol"]
            currency.is_base = data["is_base"]
            currency.is_deleted = data["is_deleted"]
            currency.save()

    @staticmethod
    def create_currency_rate():
        currency_rate_data = FactoryMasterData.CURRENCY_RATE
        for data in currency_rate_data:
            currency_rate = CurrencyRate.objects.filter(currency__symbol=data["currency_symbol"]).first()
            currency = Currency.objects.filter(symbol=data["currency_symbol"]).values("id").first()
            if currency_rate is None:
                currency_rate = CurrencyRate.objects.create(
                    currency_id=currency["id"], created_by_id=data["created_by_id"], factor=data["factor"], reference_date=data["reference_date"]
                )
                currency_rate.factor = data["factor"]
                currency_rate.currency_id = currency["id"]
                currency_rate.reference_date = data["reference_date"]
                currency_rate.expire_date = data["reference_date"].date().replace(year=data["reference_date"].date().year + 1)
                currency_rate.save()

    @staticmethod
    def create_system_parameter():
        # company_code = Client.objects.filter(schema_name="public").values("id").first()
        system_parameter_data = FactoryMasterData.SYSTEM_PARAMETER
        for data in system_parameter_data:
            sys_parameter = SysParameter.objects.filter(para_code=data["para_code"]).first()
            if sys_parameter is None:
                sys_parameter = SysParameter.objects.create(para_code=data["para_code"])
                sys_parameter.para_value = 1
                sys_parameter.descr = data["descr"]
                sys_parameter.save()

    @staticmethod
    def create_template_form():
        template_form_data = FactoryMasterData.TEMPLATE_FORM
        for data in template_form_data:
            template_form = Template_Form.objects.filter(name=data["name"], code=data["code"]).first()
            if template_form is None:
                template_form = Template_Form.objects.create(name=data["name"], code=data["code"])
                template_form.code = data["code"]
                template_form.is_active = data["is_active"]
                template_form.save()

    @staticmethod
    def create_task_scheduler():
        task_scheduler_data = FactoryMasterData.TASK_SCHEDULER
        for data in task_scheduler_data:
            task_scheduler = TaskScheduler.objects.filter(title=data["title"], url=data["url"]).first()
            if task_scheduler is None:
                task_scheduler = TaskScheduler.objects.create(title=data["title"], url=data["url"])
                task_scheduler.schedule = json.dumps(data["schedule"])
                task_scheduler.pattern = data["pattern"]
                task_scheduler.is_active = data["is_active"]
                task_scheduler.status = data["status"]
                task_scheduler.save()

    @staticmethod
    def create_postgres_funtion():
        file_name = "postgres_function.xml"
        app_name = "base"
        folder_name = "factory"
        temp_name = "templates"

        file_path = os.path.join(app_name, folder_name, temp_name, file_name)
        tree = ET.parse(file_path)

        root = tree.getroot()

        for i, element in enumerate(root.getiterator("Function")):
            for j, ord_elem in enumerate(element.getiterator("query")):
                sql = ord_elem.find("sql").text.replace("default.", "public" + ".")

                with DBEngine().connect() as conn:
                    conn.execute(sql)

    @staticmethod
    def create_dmi_query():
        dmi_query_data = FactoryMasterData.DMI_QUERY
        for data in dmi_query_data:
            file_name = data["template"]
            app_name = "base"
            folder_name = "factory"
            temp_name = "templates"

            file_path = os.path.join(app_name, folder_name, temp_name, file_name)
            tree = ET.parse(file_path)

            root = tree.getroot()

            for i, element in enumerate(root.getiterator("DMI")):
                for j, ord_elem in enumerate(element.getiterator("query")):
                    title = ord_elem.find("title").text
                    report_sql = ord_elem.find("report_sql").text
                    if report_sql is not None:
                        report_sql = report_sql.replace("default.", "public" + ".")
                    is_active = ord_elem.find("is_active").text
                    descr = ord_elem.find("descr").text
                    report_code = ord_elem.find("report_code").text
                    report_para = ord_elem.find("report_para").text
                    url = ord_elem.find("url").text
                    app_name = ord_elem.find("app_name").text

                    dmi_query = DMI_queries.objects.filter(title=title).first()

                    if dmi_query is None:
                        dmi_query = DMI_queries.objects.create(
                            title=title,
                            descr=descr,
                            report_code=report_code,
                            report_sql=report_sql,
                            report_para=report_para,
                            url=url,
                            is_active=is_active,
                            created_by_id=data["created_by_id"],
                        )
                        dmi_query.descr = descr
                        dmi_query.report_code = report_code
                        dmi_query.report_sql = report_sql
                        dmi_query.report_para = report_para
                        dmi_query.url = url
                        dmi_query.is_active = is_active
                        dmi_query.created_by_id = data["created_by_id"]
                        dmi_query.save()
                    app_report = AppReport.objects.filter(report__title=title, app=app_name).first()

                    if app_report is None:
                        AppReport.objects.create(report_id=dmi_query.id, app=app_name)

    @staticmethod
    def create_base_master():
        # BaseMasterFactory.create_doc_number()
        # BaseMasterFactory.create_shipping_service()
        # BaseMasterFactory.create_currency()
        # BaseMasterFactory.create_currency_rate()
        # BaseMasterFactory.create_task_scheduler()
        # BaseMasterFactory.create_template_form()
        # BaseMasterFactory.create_dmi_query()
        BaseMasterFactory.create_system_parameter()
        BaseMasterFactory.create_postgres_funtion()


class ProductionMasterFactory(object):
    @staticmethod
    def create_unit_of_capacity():
        unit_of_capacity_data = FactoryMasterData.UNIT_OF_CAPACITY
        for data in unit_of_capacity_data:
            unit_of_capacity = UnitOfCapacity.objects.filter(name=data["name"]).first()
            if unit_of_capacity is None:
                unit_of_capacity = UnitOfCapacity.objects.create(name=data["name"], created_by_id=data["created_by_id"])
                unit_of_capacity.code = data["code"]
                unit_of_capacity.created_by_id = data["created_by_id"]
                unit_of_capacity.save()

    @staticmethod
    def create_unit_of_cost():
        unit_of_cost_data = FactoryMasterData.UNIT_OF_COST
        for data in unit_of_cost_data:
            unit_of_cost = UnitOfCost.objects.filter(name=data["name"], code=data["code"]).first()
            if unit_of_cost is None:
                unit_of_cost = UnitOfCost.objects.create(name=data["name"], code=data["code"], created_by_id=data["created_by_id"])
                unit_of_cost.is_active = data["is_active"]
                unit_of_cost.created_by_id = data["created_by_id"]
                unit_of_cost.save()

    @staticmethod
    def create_assembly_prep_step():
        assembly_prep_step_data = FactoryMasterData.ASSEMBLY_PREP_STEP
        for data in assembly_prep_step_data:
            assembly_prep_step = AssemblyPrepStep.objects.filter(name=data["name"]).first()
            if assembly_prep_step is None:
                assembly_prep_step = AssemblyPrepStep.objects.create(name=data["name"])
                assembly_prep_step.code = data["code"]
                assembly_prep_step.save()

    @staticmethod
    def create_production_master():
        ProductionMasterFactory.create_unit_of_capacity()
        ProductionMasterFactory.create_unit_of_cost()
        ProductionMasterFactory.create_assembly_prep_step()


class LogisticsMasterFactory(object):
    @staticmethod
    def create_ship_method():
        ship_method_data = FactoryMasterData.SHIP_METHOD
        for data in ship_method_data:
            ship_method = ShipMethod.objects.filter(name=data["name"]).first()
            if ship_method is None:
                ship_method = ShipMethod.objects.create(name=data["name"])
                ship_method.is_deleted = data["is_deleted"]
                ship_method.save()

    @staticmethod
    def create_logistics_master():
        LogisticsMasterFactory.create_ship_method()


class InspectionTypesFactory(object):
    @staticmethod
    def create_inspection_type():
        inspection_type_data = FactoryMasterData.INSPECTION_TYPE
        for data in inspection_type_data:
            inspection_type = InspectionType.objects.filter(name=data["name"]).first()
            if inspection_type is None:
                inspection_type = InspectionType.objects.create(name=data["name"], created_by_id=data["created_by_id"])
                inspection_type.is_deleted = data["is_deleted"]
                inspection_type.created_by_id = data["created_by_id"]
                inspection_type.save()


class CampaignMasterFactory(object):
    @staticmethod
    def create_campaign_type():
        campaign_type_data = FactoryMasterData.CAMPAIGN_TYPE
        for data in campaign_type_data:
            campaign_type = CampaignType.objects.filter(name=data["name"]).first()
            if campaign_type is None:
                campaign_type = CampaignType.objects.create(name=data["name"], created_by_id=data["created_by_id"])
                campaign_type.description = data["description"]
                campaign_type.created_by_id = data["created_by_id"]
                campaign_type.save()

    @staticmethod
    def create_stage():
        stage_data = FactoryMasterData.STAGE
        for data in stage_data:
            stage = Stage.objects.filter(name=data["name"]).first()
            if stage is None:
                stage = Stage.objects.create(name=data["name"], sequence=data["sequence"])
                stage.sequence = data["sequence"]
                stage.save()

    @staticmethod
    def create_campaign_master():
        CampaignMasterFactory.create_campaign_type()
        CampaignMasterFactory.create_stage()


class AuditlogMasterFactory(object):
    @staticmethod
    def create_audit_action():
        audit_action_data = FactoryMasterData.AUDIT_ACTION
        for data in audit_action_data:
            audit_action = AuditAction.objects.filter(name=data["name"]).first()
            if audit_action is None:
                audit_action = AuditAction.objects.create(name=data["name"])
                audit_action.save()

    @staticmethod
    def create_audit_log_master():
        AuditlogMasterFactory.create_audit_action()


class FinancialMasterFactory(object):
    @staticmethod
    def create_invoice_status():
        invoice_status_data = FactoryMasterData.INVOICE_STATUS
        for data in invoice_status_data:
            invoice_status = InvoiceStatus.objects.filter(name=data["name"]).first()
            if invoice_status is None:
                invoice_status = InvoiceStatus.objects.create(name=data["name"])
                invoice_status.description = data["description"]
                invoice_status.is_deleted = data["is_deleted"]
                invoice_status.save()

    @staticmethod
    def create_payment_mode():
        payment_mode_data = FactoryMasterData.PAYMENT_MODE
        for data in payment_mode_data:
            payment_mode = PaymentMode.objects.filter(name=data["name"]).first()
            if payment_mode is None:
                payment_mode = PaymentMode.objects.create(name=data["name"])
                payment_mode.is_deleted = data["is_deleted"]
                payment_mode.save()

    @staticmethod
    def create_payment_difference_type():
        payment_difference_type_data = FactoryMasterData.PAYMENT_DIFFERENCE_TYPE
        for data in payment_difference_type_data:
            payment_difference_type = PaymentDifferenceType.objects.filter(name=data["name"], code=data["code"]).first()
            if payment_difference_type is None:
                payment_difference_type = PaymentDifferenceType.objects.create(name=data["name"], code=data["code"])
                payment_difference_type.is_deleted = data["is_deleted"]
                payment_difference_type.save()

    @staticmethod
    def create_tax_rule():
        tax_rule_data = FactoryMasterData.TAX_RULE
        for data in tax_rule_data:
            tax_rule = TaxRule.objects.filter(name=data["name"], code=data["code"]).first()
            if tax_rule is None:
                tax_rule = TaxRule.objects.create(name=data["name"], code=data["code"], created_by_id=data["created_by_id"])
                tax_rule.created_by_id = data["created_by_id"]
                tax_rule.save()

    @staticmethod
    def create_financial_master():
        FinancialMasterFactory.create_invoice_status()
        FinancialMasterFactory.create_payment_mode()
        FinancialMasterFactory.create_payment_difference_type()
        FinancialMasterFactory.create_tax_rule()


class TaskMasterFactory(object):
    @staticmethod
    def create_task_type():
        task_type_data = FactoryMasterData.TASK_TYPE
        for data in task_type_data:
            task_type = TaskType.objects.filter(name=data["name"]).first()
            if task_type is None:
                task_type = TaskType.objects.create(name=data["name"], created_by_id=data["created_by_id"])
                task_type.code = data["code"]
                task_type.icon = data["icon"]
                task_type.created_by_id = data["created_by_id"]
                task_type.save()

    @staticmethod
    def create_task_master():
        TaskMasterFactory.create_task_type()


class ProductMasterFactory(object):
    @staticmethod
    def create_unit_of_measure():
        unit_of_measure_data = FactoryMasterData.UNIT_OF_MEASURE
        for data in unit_of_measure_data:
            unit_of_measure = UnitOfMeasure.objects.filter(name=data["name"]).first()
            if unit_of_measure is None:
                unit_of_measure = UnitOfMeasure.objects.create(name=data["name"], created_by_id=data["created_by_id"])
                unit_of_measure.code = data["code"]
                unit_of_measure.is_active = data["is_active"]
                unit_of_measure.created_by_id = data["created_by_id"]
                unit_of_measure.save()

    @staticmethod
    def create_product_master():
        ProductMasterFactory.create_unit_of_measure()


class AccountMasterFactory(object):
    @staticmethod
    def create_parent_menu():
        parent_menu_data = FactoryMasterData.PARENT_MENU
        for data in parent_menu_data:
            parent_menu = MainMenu.objects.filter(name=data["name"], url=data["url"]).first()

            if parent_menu is None:
                parent_menu = MainMenu.objects.create(name=data["name"], created_by_id=data["created_by_id"])
                parent_menu.url = data["url"] if "url" in data else ""
                parent_menu.icon = data["icon"] if "icon" in data else ""
                parent_menu.parent_id_id = None
                parent_menu.sequence = data["sequence"]
                parent_menu.is_active = data["is_active"]
                parent_menu.is_external = data["is_external"]
                parent_menu.is_master = data["is_master"]
                parent_menu.on_click = data["on_click"] if "on_click" in data else ""
                parent_menu.company_code = data["company_code"] if "company_code" in data else None
                parent_menu.menu_code = data["menu_code"] if "menu_code" in data else ""
                parent_menu.created_by_id = data["created_by_id"]
                parent_menu.launcher_add_url = data["launcher_add_url"] if "launcher_add_url" in data else ""
                parent_menu.launcher_menu = data["launcher_menu"] if "launcher_menu" in data else ""
                parent_menu.launcher_sequence = data["launcher_sequence"] if "launcher_sequence" in data else 1
                parent_menu.save()

            if "child_menus" in data:
                AccountMasterFactory.create_child_menu(parent_menu.id, data["child_menus"])

            if "content_permission" in data:
                AccountMasterFactory.create_content_permission(data["content_permission"], parent_menu.id)

    @staticmethod
    def create_child_menu(parent_id, child_menu_data):
        for data in child_menu_data:
            child_menu = MainMenu.objects.filter(name=data["name"], parent_id_id=parent_id).first()
            if child_menu is None:
                child_menu = MainMenu.objects.create(name=data["name"], created_by_id=data["created_by_id"], parent_id_id=parent_id)
                child_menu.url = data["url"] if "url" in data else ""
                child_menu.icon = data["icon"] if "icon" in data else ""
                child_menu.parent_id_id = parent_id if "parent_id" in data else None
                child_menu.sequence = data["sequence"]
                child_menu.is_active = data["is_active"]
                child_menu.is_external = data["is_external"]
                child_menu.is_master = data["is_master"]
                child_menu.on_click = data["on_click"] if "on_click" in data else ""
                child_menu.company_code = data["company_code"] if "company_code" in data else None
                child_menu.menu_code = data["menu_code"] if "menu_code" in data else ""
                child_menu.created_by_id = data["created_by_id"]
                child_menu.launcher_add_url = data["launcher_add_url"] if "launcher_add_url" in data else ""
                child_menu.launcher_menu = data["launcher_menu"] if "launcher_menu" in data else ""
                child_menu.launcher_sequence = data["launcher_sequence"] if "launcher_sequence" in data else 1
                child_menu.save()

            if "content_permission" in data:
                AccountMasterFactory.create_content_permission(data["content_permission"], child_menu.id)
            child_sub_menus = data["child_sub_menus"] if "child_sub_menus" in data else []
            AccountMasterFactory.create_child_sub_menu(child_menu.id, child_sub_menus)

    @staticmethod
    def create_child_sub_menu(child_menu_id, child_sub_menu_data):
        for data in child_sub_menu_data:
            child_sub_menu = MainMenu.objects.filter(name=data["name"], parent_id_id=child_menu_id).first()

            if child_sub_menu is None:
                child_sub_menu = MainMenu.objects.create(name=data["name"], created_by_id=data["created_by_id"])
                child_sub_menu.url = data["url"] if "url" in data else ""
                child_sub_menu.icon = data["icon"] if "icon" in data else ""
                child_sub_menu.parent_id_id = child_menu_id
                child_sub_menu.sequence = data["sequence"]
                child_sub_menu.is_active = data["is_active"]
                child_sub_menu.is_external = data["is_external"]
                child_sub_menu.is_master = data["is_master"]
                child_sub_menu.on_click = data["on_click"] if "on_click" in data else ""
                child_sub_menu.company_code = data["company_code"] if "company_code" in data else None
                child_sub_menu.menu_code = data["menu_code"] if "menu_code" in data else ""
                child_sub_menu.created_by_id = data["created_by_id"]
                child_sub_menu.launcher_add_url = data["launcher_add_url"] if "launcher_add_url" in data else ""
                child_sub_menu.launcher_menu = data["launcher_menu"] if "launcher_menu" in data else ""
                child_sub_menu.launcher_sequence = data["launcher_sequence"] if "launcher_sequence" in data else 1
                child_sub_menu.save()

            if "content_permission" in data:
                AccountMasterFactory.create_content_permission(data["content_permission"], child_sub_menu.id)

    @staticmethod
    def create_content_permission(content_permission_data, menu_id):
        for data in content_permission_data:
            content_permission = ContentPermission.objects.filter(content_group=data["content_group"], content_name=data["content_name"], sequence=data["sequence"]).first()

            if content_permission is None:
                content_permission = ContentPermission.objects.create(content_group=data["content_group"], content_name=data["content_name"], sequence=data["sequence"])
                content_permission.content_group = data["content_group"]
                content_permission.content_name = data["content_name"]
                content_permission.sequence = data["sequence"]
                content_permission.save()

            if "page_permissions" in data:
                AccountMasterFactory.create_page_permission(content_permission.id, menu_id, data["page_permissions"])

    @staticmethod
    def create_page_permission(content_id, menu_id, page_permission_data):
        for data in page_permission_data:
            page_permission = PagePermission.objects.filter(act_name=data["act_name"], act_code=data["act_code"], content_id=content_id, menu_id=menu_id).first()

            if page_permission is None:
                page_permission = PagePermission.objects.create(act_name=data["act_name"], act_code=data["act_code"], content_id=content_id, menu_id=menu_id)

                page_permission.act_name = data["act_name"]
                page_permission.act_code = data["act_code"]
                page_permission.save()


class PartnerMasterFactory(object):
    @staticmethod
    def create_country():
        country_data = FactoryMasterData.COUNTRY
        for data in country_data:
            country = Country.objects.filter(name=data["name"]).first()
            if country is None:
                country = Country.objects.create(name=data["name"])
                country.code = data["code"]
                country.has_state = data["has_state"]
                country.save()

    @staticmethod
    def create_state():
        state_data = FactoryMasterData.STATE
        for data in state_data:
            country = Country.objects.filter(name=data["country"]).values("id").first()
            state = State.objects.filter(name=data["name"], country_id=country["id"]).first()
            if state is None:
                state = State.objects.create(name=data["name"], country_id=country["id"])
                state.code = data["code"]
                state.save()

    @staticmethod
    def create_lead_status():
        lead_status_data = FactoryMasterData.LEAD_STATUS
        for data in lead_status_data:
            lead_status = LeadStatus.objects.filter(name=data["name"]).first()
            if lead_status is None:
                lead_status = LeadStatus.objects.create(name=data["name"], created_by_id=data["created_by_id"])
                lead_status.code = data["code"]
                lead_status.sequence = data["sequence"]
                lead_status.created_by_id = data["created_by_id"]
                lead_status.save()

    @staticmethod
    def create_lead_source():
        lead_source_data = FactoryMasterData.LEAD_SOURCE
        for data in lead_source_data:
            lead_source = LeadSource.objects.filter(name=data["name"]).first()
            if lead_source is None:
                lead_source = LeadSource.objects.create(name=data["name"], created_by_id=data["created_by_id"])
                lead_source.created_by_id = data["created_by_id"]
                lead_source.save()

    @staticmethod
    def create_payment_term():
        payment_term_data = FactoryMasterData.PAYMENT_TERM
        for data in payment_term_data:
            payment_term = PaymentTerm.objects.filter(name=data["name"]).first()
            if payment_term is None:
                payment_term = PaymentTerm.objects.create(name=data["name"])
                payment_term.days = data["days"]
                payment_term.paymentterm_type = data["paymentterm_type"]
                payment_term.is_deleted = data["is_deleted"]
                payment_term.save()

    @staticmethod
    def create_partner_master():
        PartnerMasterFactory.create_country()
        PartnerMasterFactory.create_state()
        PartnerMasterFactory.create_lead_status()
        PartnerMasterFactory.create_lead_source()
        PartnerMasterFactory.create_payment_term()


class AttachmentMasterFactory(object):
    @staticmethod
    def create_file_type():
        file_type_data = FactoryMasterData.FILE_TYPE
        for data in file_type_data:
            file_type = FileType.objects.filter(name=data["name"]).first()
            if file_type is None:
                file_type = FileType.objects.create(name=data["name"])
                file_type.code = data["code"]
                file_type.description = data["description"]
                file_type.is_active = data["is_active"]
                file_type.save()


class InventoryFactory(object):
    @staticmethod
    def create_move_type():
        move_type_data = FactoryMasterData.MOVE_TYPE
        for data in move_type_data:
            move_type = MoveType.objects.filter(name=data["name"]).first()
            if move_type is None:
                move_type = MoveType.objects.create(name=data["name"])
                move_type.code = data["code"]
                move_type.is_deleted = data["is_deleted"]
                move_type.save()

    @staticmethod
    def create_location():
        location_data = FactoryMasterData.LOCATION
        for data in location_data:
            location = Location.objects.filter(name=data["name"]).first()
            if location is None:
                location = Location.objects.create(name=data["name"])
                location.is_deleted = data["is_deleted"]
                location.save()

    @staticmethod
    def create_warehouse():
        warehouse_data = FactoryMasterData.WAREHOUSE
        for data in warehouse_data:
            warehouse = Warehouse.objects.filter(name=data["name"]).first()
            if warehouse is None:
                warehouse = Warehouse.objects.create(name=data["name"])
                warehouse.code = data["code"]
                warehouse.is_deleted = data["is_deleted"]
                warehouse.save()

    @staticmethod
    def create_inventory_master():
        InventoryFactory.create_move_type()
        InventoryFactory.create_location()
        InventoryFactory.create_warehouse()


class CurrencyRateFactory(object):
    @staticmethod
    def create_currency_rate():
        currency_rate_data = FactoryDemoData.CURRENCY_RATE
        for data in currency_rate_data:
            c_rate = CurrencyRate.objects.filter(currency__symbol=data["currency_symbol"]).first()
            if c_rate is None:
                currency = Currency.objects.filter(symbol=data["currency_symbol"]).values("id").first()
                c_rate = CurrencyRate.objects.create(
                    currency_id=currency["id"],
                    created_by_id=data["created_by_id"],
                    factor=data["factor"],
                    reference_date=data["reference_date"],
                    expire_date=data["reference_date"].date().replace(year=data["reference_date"].date().year + 1),
                )
