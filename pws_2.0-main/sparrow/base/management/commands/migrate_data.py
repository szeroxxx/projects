# coding=utf-8
from django.core.management.base import BaseCommand
import psycopg2 as pg
from django.conf import settings
from django.contrib.auth.models import User
from django.db import transaction
import datetime
from tenant_schemas.utils import schema_context

class Command(BaseCommand):    

    def handle(self, *args, **options):

        def insert_default_data(id, cursor):
            current_time= datetime.datetime.now()
            partners_country = [('Albania','AL'),('Algeria','DZ'),('American Samoa','AS'), ('Andorra','AD'),('Angola','AO'),('Anguilla','AI'),
            ('Antarctica','AQ'),('Antigua and Barbuda','AG'),('Argentina','AR'),('Armenia','AM'),('Aruba','AW'),('Australia','AU'),('Austria','AT'),('Azerbaijan','AZ'),('Bahamas','BS'),
            ('Bahrain','BH'),('Bangladesh','BD'),('Barbados','BB'),('Belarus','BY'),('Belgium','BE'),('Belize','BZ'),('Benin','BJ'),('Bermuda','BM'),('Bhutan','BT'),('Bolivia (Plurinational State of)','BO'),('Bonaire, Sint Eustatius and Saba','BQ'),('Bosnia and Herzegovina','BA'),('Botswana','BW'),
            ('Bouvet Island','BV'),('Brazil','BR'),('British Indian Ocean Territory','IO'),('Brunei Darussalam','BN'),('Bulgaria','BG'),('Burkina Faso','BF'),('Burundi','BI'),
            ('Cabo Verde','CV'),('Cambodia','KH'),('Cameroon','CM'),('Canada','CA'),('Cayman Islands','KY'),
            ('Central African Republic','CF'),('Chad','TD'),('Chile','CL'),('China','CN'),('Christmas Island','CX'),('Cocos (Keeling) Islands','CC'),
            ('Colombia','CO'),('Comoros','KM'),('Congo','CG'),('Congo (Democratic Republic of the)','CD'),('Cook Islands','CK'),
            ('Costa Rica','CR'),('Croatia','HR'),('Cuba','CU'),('Curaçao','CW'),('Cyprus','CY'),('Czechia','CZ'),
            ('Denmark','DK'),('Djibouti','DJ'),('Dominica','DM'),('Dominican Republic','DO'),('Ecuador','EC'),('Egypt','EG'),('El Salvador','SV'),('Equatorial Guinea','GQ'),('Eritrea','ER'),('Estonia','EE'),('Ethiopia','ET'),('Falkland Islands (Malvinas)','FK'),
            ('Faroe Islands','FO'),('Fiji','FJ'),('Finland','FI'),('France','FR'),('French Guiana','GF'),('French Polynesia','PF'),
            ('French Southern Territories','TF'),('Gabon','GA'),('Gambia','GM'),('Georgia','GE'),('Germany','DE'),('Ghana','GH'),('Gibraltar','GI'),('Greece','GR'),
            ('Greenland','GL'),('Grenada','GD'),('Guadeloupe','GP'),('Guam','GU'),('Guatemala','GT'),('Guernsey','GG'),('Guinea','GN'),('Guinea-Bissau','GW'),
            ('Guyana','GY'),('Haiti','HT'),('Heard Island and McDonald Islands','HM'),('Holy See','VA'),('Honduras','HN'),('Hong Kong','HK'),('Hungary','HU'),('Iceland','IS'),('India','IN'),('Indonesia','id'),
            ('Iran (Islamic Republic of)','IR'),('Iraq','IQ'),('Ireland','IE'),('Isle of Man','IM'),('Israel','IL'),('Italy','IT'),('Jamaica','JM'),('Japan','JP'),
            ('Jersey','JE'),('Jordan','JO'),('Kazakhstan','KZ'),('Kenya','KE'),('Kiribati','KI'),('Korea (Republic of)','KR'),('Kuwait','KW'),('Kyrgyzstan','KG'),('Latvia','LV'),('Lebanon','LB'),('Lesotho','LS'),('Liberia','LR'),('Libya','LY'),('Liechtenstein','LI'),
            ('Lithuania','LT'),('Luxembourg','LU'),('Macao','MO'),('Macedonia (the former Yugoslav Republic of)','MK'),('Madagascar','MG'),('Malawi','MW'),('Malaysia','MY'),('Maldives','MV'),('Mali','ML'),('Malta','MT'),('Marshall Islands','MH'),('Martinique','MQ'),('Mauritania','MR'),('Mauritius','MU'),('Mayotte','YT'),('Mexico','MX'),('Micronesia (Federated States of)','FM'),('Moldova (Republic of)','MD'),('Monaco','MC'),
            ('Mongolia','MN'),('Montenegro','ME'),('Montserrat','MS'),('Morocco','MA'),('Mozambique','MZ'),('Myanmar','MM'),('Namibia','NA'),
            ('Nauru','NR'),('Nepal','NP'),('Netherlands','NL'),('New Caledonia','NC'),('New Zealand','NZ'),('Nicaragua','NI'),('Niger','NE'),('Nigeria','NG'),('Niue','NU'),('Norfolk Island','NF'),('Northern Mariana Islands','MP'),
            ('Norway','NO'),('Oman','OM'),('Pakistan','PK'),('Palau','PW'),('Palestine, State of','PS'),('Panama','PA'),('Papua New Guinea','PG'),('Paraguay','PY'),('Peru','PE'),('Philippines','PH'),('Pitcairn','PN'),('Poland','PL'), ('Portugal','PT'),('Puerto Rico','PR'),('Qatar','QA'),('Réunion','RE'),('Romania','RO'),
            ('Russian Federation','RU'),('Rwanda','RW'),('Saint Barthélemy','BL'),('Saint Helena, Ascension and Tristan da Cunha','SH'),('Saint Kitts and Nevis','KN'),('Saint Lucia','LC'),('Saint Martin (French part)','MF'),('Saint Pierre and Miquelon','PM'),
            ('Saint Vincent and the Grenadines','VC'),('Samoa','WS'),('San Marino','SM'),('Sao Tome and Principe','ST'),('Saudi Arabia','SA'),('Senegal','SN'),('Serbia','RS'),('Seychelles','SC'),('Sierra Leone','SL'),('Singapore','SG'),
            ('Sint Maarten (Dutch part)','SX'),('Slovakia','SK'),('Slovenia','SI'),('Solomon Islands','SB'),('Somalia','SO'),('South Africa','ZA'),('South Georgia and the South Sandwich Islands','GS'),('South Sudan','SS'),('Spain','ES'),
            ('Sri Lanka','LK'),('Sudan','SD'),('Suriname','SR'),('Svalbard and Jan Mayen','SJ'),('Swaziland','SZ'),('Sweden','SE'),('Switzerland','CH'),
            ('Syrian Arab Republic','SY'),('Taiwan, Province of China[a]','TW'),('Tajikistan','TJ'),('Tanzania, United Republic of','TZ'),('Thailand','TH'),('Timor-Leste','TL'),('Togo','TG'),('Tokelau','TK'),
            ('Tonga','TO'),('Trinidad and Tobago','TT'),('Tunisia','TN'),('Turkey','TR'),('Turkmenistan','TM'),
            ('Turks and Caicos Islands','TC'),('Tuvalu','TV'),('Uganda','UG'),('Ukraine','UA'),('United Arab Emirates','AE'),('United Kingdom of Great Britain and Northern Ireland','GB'),('United States of America','US'),('United States Minor Outlying Islands','UM'),('Uruguay','UY'),
            ('Uzbekistan','UZ'),('Vanuatu','VU'),('Venezuela (Bolivarian Republic of)','VE'),('Viet Nam','VN'),('Virgin Islands (British)','VG'),('Virgin Islands (U.S.)','VI'),('Wallis and Futuna','WF'),('Western Sahara','EH'),('Yemen','YE'),('Zambia','ZM'),('Zimbabwe','ZW')]
            sql_country = '''INSERT INTO partners_country(name,code)values(%s,%s)'''            
            cursor.executemany(sql_country , partners_country)

            accounts_mainmenu=[(1, 'EDA', '', 'fa fa-server', 1, 'True', 'False', '', id, None),
            (29, 'Logistics (in)', '', 'icon-truck', 6, 'True', 'False', '', id, None),
            (32, 'Logistics (out)', '', 'icon-wagon', 7, 'True', 'False', '', id, None),
            (37, 'Financial(In)', '', 'icon-EUR', 8, 'True', 'False', '', id, None),
            (41, 'Financial(Out)', '', 'icon-EUR-circle', 8, 'True', 'False', '', id, None),
            (45, 'Admin tools', '', 'icon-settings', 10, 'True', 'False', '', id, None),
            (156, 'Settings', '', 'fa fa-gear', 11, 'True', 'False', '', id, None),
            (160, 'Maintenances', '', 'icon-wrench-hammer', 12, 'True', 'False', '', id, None),
            (165, 'Reports', '', 'icon-funnel', 13, 'True', 'False', '', id, None),
            (171, 'Financial', '', 'icon-EUR', 10, 'True', 'False', '', id, None),
            (24, 'Production', '', 'icon-settings-2', 5, 'True', 'False', '', id, None),
            (194, 'Planning', '', 'icon-calendar-time', 4, 'True', 'False', '', id, None),
            (8, 'Sales', '', 'icon-bar-chart-up', 1, 'True', 'False', '', id, None),
            (14, 'Purchasing', '', 'icon-barcode-scan', 2, 'True', 'False', '', id, None),
            (20, 'Inventory', '', 'icon-layers-locked-2', 3, 'True', 'False', '', id, None),
            (205, 'Exchange rate', '#/exchangerate', '', 8, 'True', 'False', '', id, 45),
            (40, 'Payments', '#/financial/payments/customer', '', 3, 'True', 'False', '', id, 37),
            (9, 'Customers', '#/partners/partners/customer', '', 1, 'True', 'False', '', id, 8),
            (10, 'Products', '#/products/products/sale/', '', 2, 'True', 'False', '', id, 8),
            (11, 'Draft quotations', '#/sales/orders/draft/', '', 3, 'True', 'False', '', id, 8),
            (12, 'Quotations', '#/sales/orders/quotation/', '', 4, 'True', 'False', '', id, 8),
            (13, 'Orders', '#/sales/orders/sale/', '', 5, 'True', 'False', '', id, 8),
            (15, 'Suppliers', '#/partners/partners/supplier', '', 1, 'True', 'False', '', id, 14),
            (16, 'Products', '#/products/products/buy/', '', 2, 'True', 'False', '', id, 14),
            (17, 'Draft inquiries', '#/purchasing/orders/draftrfq/', '', 3, 'True', 'False', '', id, 14),
            (18, 'Quotations', '#/purchasing/orders/rfq/', '', 4, 'True', 'False', '', id, 14),
            (19, 'Purchase orders', '#/purchasing/orders/purchase/', '', 5, 'True', 'False', '', id, 14),
            (21, 'Stock moves', '#/inventory/stockmoves', '', 1, 'True', 'False', '', id, 20),
            (22, 'Inventory report', '#/inventory/inventory_report', '', 2, 'True', 'False', '', id, 20),
            (23, 'Stock status', '#/inventory/stock_status', '', 3, 'True', 'False', '', id, 20),
            (25, 'Manufacturing orders', '#/production/mfg_orders', '', 1, 'True', 'False', '', id, 24),
            (26, 'Bill of materials', '#/production/boms', '', 2, 'True', 'False', '', id, 24),
            (27, 'Routing', '#/production/routings', '', 3, 'True', 'False', '', id, 24),
            (30, 'Ready to receive', '#/logistics/to_be_receive/', '', 1, 'True', 'False', '', id, 29),
            (31, 'Receipts', '#/logistics/receipts/', '', 2, 'True', 'False', '', id, 29),
            (34, 'Inspections', '#/logistics/order_inspections/', '', 2, 'True', 'False', '', id, 32),
            (35, 'Ready to ship', '#/logistics/to_be_ship/', '', 3, 'True', 'False', '', id, 32),
            (36, 'Shipments', '#/logistics/shipments/', '', 4, 'True', 'False', '', id, 32),
            (38, 'Ready to invoice', '#/financial/ready_to_invoice', '', 1, 'True', 'False', '', id, 37),
            (39, 'Search invoice', '#/financial/invoices/customer', '', 2, 'True', 'False', '', id, 37),
            (48, 'System parameters', '#/sysparameters', '', 3, 'True', 'False', '', id, 45),
            (157, 'Users', '#/customer/users', '', 1, 'True', 'False', '', id, 156),
            (158, 'Company', '#/customer/company', '', 2, 'True', 'False', '', id, 156),
            (47, 'Company', '#/partners/company', '', 2, 'True', 'False', '', id, 45),
            (167, 'Sales report', '#/base/reports/1243453453', '', 1, 'True', 'False', '', id, 165),
            (172, 'Pending invoice', '#/customer/invoices/running', '', 1, 'True', 'False', '', id, 171),
            (161, 'Job schedules', '#/maintenances/jobentries', '', 2, 'True', 'False', '', id, 160),
            (163, 'Maintenance jobs', '#/maintenances/jobs', '', 3, 'True', 'False', '', id, 160),
            (173, 'History', '#/customer/invoices/history', '', 2, 'True', 'False', '', id, 171),
            (179, 'Search orders', '#/purchasing/orders/search/', '', 6, 'True', 'False', '', id, 14),
            (176, 'Maintenance Jobs', '#/base/reports/5282545256', '', 4, 'True', 'False', '', id, 165),
            (178, 'Search orders', '#/sales/orders/search/', '', 6, 'True', 'False', '', id, 8),
            (180, 'Search basket', '#/sales/orders/basket/', '', 7, 'True', 'False', '', id, 8),
            (159, 'Prospects', '#/sales/prospects', '', 8, 'True', 'False', '', id, 8),
            (184, 'Pricelist', '#/sales/pricelists', '', 9, 'True', 'False', '', id, 8),
            (185, 'Purchase plans', '#/purchasing/purchase_plans', '', 7, 'True', 'False', '', id, 14),
            (186, 'Operations', '#/production/operations/0/', '', 2, 'True', 'False', '', id, 24),
            (151, 'Traceability', '#/inventory/tracking_numbers/', '', 4, 'True', 'False', '', id, 20),
            (187, 'Pricelist', '#/purchasing/purchase_pricelists', '', 8, 'True', 'False', '', id, 14),
            (189, 'Machines', '#/production/machines', '', 6, 'True', 'False', '', id, 24),
            (181, 'Schedule', '#/production/schedule/0', '', 8, 'True', 'False', '', id, 24),
            (28, 'Work center', '#/production/workcenters', '', 5, 'True', 'False', '', id, 24),
            (192, 'MO cost report', '#/base/mo_cost_report', '', 1, 'True', 'False', '', id, 165),
            (193, 'Ready to invoice', '#/financial/ready_to_invoice/supplier', '', 1, 'True', 'False', '', id, 41),
            (195, 'Shifts', '#/production/shifts', '', 1, 'True', 'False', '', id, 194),
            (197, 'Workweeks', '#/production/workweeks', '', 5, 'True', 'False', '', id, 194),
            (198, 'Workweek shifts', '#/production/workweek_shifts', '', 6, 'True', 'False', '', id, 194),
            (42, 'Search supplier invoice', '#/financial/invoices/supplier', '', 2, 'True', 'False', '', id, 41),
            (191, 'Workers', '#/production/workers', '', 2, 'True', 'False', '', id, 194),
            (199, 'Holidays', '#/production/holidays', '', 3, 'True', 'False', '', id, 194),
            (196, 'Worker holidays', '#/production/worker_holidays', '', 4, 'True', 'False', '', id, 194),
            (149, 'Payments', '#/financial/payments/supplier', '', 3, 'True', 'False', '', id, 41),
            (200, 'Shift planning', '#/production/shift_planning', '', 7, 'True', 'False', '', id, 194),
            (203, 'External category', '#/products/external_categories', '', 9, 'True', 'False', '', id, 14),
            (204, 'External category', '#/products/external_categories', '', 10, 'True', 'False', '', id, 8),
            (202, 'Internal category', '#/products/internal_categories', '', 10, 'True', 'False', '', id, 14),
            (201, 'Internal category', '#/products/internal_categories', '', 11, 'True', 'False', '', id, 8),
            (46, 'Users', '#/accounts/users/admin', '', 1, 'True', 'False', '', id, 45),
            (2, 'Roles', '#/accounts/roles', '', 2, 'True', 'False', '', id, 45)]
            sql_menu ='''INSERT INTO accounts_mainmenu VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
            cursor.executemany(sql_menu, accounts_mainmenu)
            cursor.execute('''ALTER SEQUENCE accounts_mainmenu_id_seq RESTART WITH 205''')

            attachment_filetype =[(2, 'order_file', 'Order file', 'True'),
            (3, 'bom_file', 'Bom file', 'True')]
            sql3 = ''' INSERT INTO attachment_filetype VALUES(%s, %s, %s, %s)'''
            cursor.executemany(sql3,attachment_filetype)
            cursor.execute('''ALTER SEQUENCE attachment_filetype_id_seq RESTART WITH 3 ''')

            auditlog_auditaction = [(1, 'insert'),(2, 'update'), (3, 'delete')]
            sql4 = ''' INSERT INTO auditlog_auditaction VALUES(%s, %s)'''
            cursor.executemany(sql4,auditlog_auditaction)
            cursor.execute(''' ALTER SEQUENCE auditlog_auditaction_id_seq RESTART WITH 3''')

            base_docnumber= [ (7, 'TransferOrder', 'Doc Number for transfer order.', 'TO', 5, 1, 1, 'TO00001'),
            (13, 'Project', 'Doc Number for project.', 'PJ', 5, 1, 1, 'PJ00001'),
            (10, 'PurchaseOrder', 'Doc Number for purchase order.', 'PO', 5, 1, 1, 'PO00001'),
            (12, 'Invoice', 'Doc Number for invoice.', 'INV', 5, 1, 1, 'INV00001'),
            (14, 'SerialNumber', 'Doc Number for tracking serial.', '', 10, 1, 1, '0000000001'),
            (11, 'MfgOrder', 'Doc Number for Mfg order.', 'MO', 5, 1, 1, 'MO00001'),
            (6, 'SaleOrder', 'Doc Number for sale order.', 'SO', 5, 1, 1, 'SO00001'),
            (20, 'SaleReturn', 'Doc Number for return sale order.', 'SR', 5, 1, 1, 'SR00001'),
            (19, 'PurchaseReturn', 'Doc Number for return purchase order.', 'PR', 5, 1, 1, 'PR00001'),
            (18, 'PurchasePlan', 'Doc number for purchase plan', 'PP', 5, 1, 1, 'PP00001'),
            (15, 'SupInvoice', 'Doc number for supplier invoice', 'SINV', 5, 1, 1, 'SINV00001'),
            (16, 'JOBSCH', 'Job schedules', 'JS', 5, 1, 1, 'JS00001'),
            (17, 'JOBMAINT', 'Maintenance Job', 'MJ', 5, 1, 1, 'MJ00001'),
            (9, 'Inspection', 'Doc Number for Inspection report', 'QC', 5, 1, 1, 'QC00001'),
            (8, 'StockMove', 'Doc Number for Stock Moves', 'SM', 5, 1, 1, 'SM00001')]
            sql5 = ''' INSERT INTO base_docnumber VALUES(%s, %s, %s, %s, %s, %s, %s, %s) '''
            cursor.executemany(sql5,base_docnumber)
            cursor.execute(''' ALTER SEQUENCE base_docnumber_id_seq RESTART WITH 20''')
            
            base_shippingservice = [(1, 'FedEx', 'https://www.fedex.com/apps/fedextrack/?action=track&trackingnumber=#number#&cntry_code=us', '2017-06-09 07:44:31.385+00', id),
            (3, 'TNT', 'https://www.tnt.com/express/hu_hu/site/shipping-tools/tracking.html?cons=#number#&searchType=CON', '2017-07-12 06:49:38.523+00', id),
            (4, 'GLS', 'https://gls-group.eu/HU/hu/csomagkovetes?match=#number#', '2017-07-12 06:49:57.622+00', id),
            (2, 'UPS', 'https://wwwapps.ups.com/WebTracking/OnlineTool?loc=hu_HU&InquiryNumber=#number#', '2017-07-12 06:49:25.606+00', id)]
            sql6 = ''' INSERT INTO base_shippingservice VALUES(%s, %s, %s, %s, %s) '''
            cursor.executemany(sql6,base_shippingservice)
            cursor.execute(''' ALTER SEQUENCE base_shippingservice_id_seq RESTART WITH 4''')

            app_ecommerce = input("Do you want to enable ecommerce module(True/False)? ")
            app_production = input("Do you want to enable production module(True/False)? ")
            
            base_sysparameter = [(19, 'email_backend', 'Email Backend', 'django_smtp_ssl.SSLEmailBackend'),
            (20, 'email_host', 'Email host', ''),
            (21, 'email_host_user', 'Email host user', ''),
            (22, 'email_host_password', 'Email host password', ''),
            (24, 'email_use_tls', 'Email use tls', 'True'),
            (26, 'tax_rate', 'Default tax rate', '21'),
            (27, 'purchase_track', 'Default serialization for Purchase items (LOT/SERIAL)', 'LOT'),
            (28, 'prod_track', 'Default serialization for production items (LOT/SERIAL)', 'SERIAL'),
            (29, 'SMTP_SERVER', 'SMTP server IP or endpoint URL', 'smtp.gmail.com'),
            (30, 'bom_eda_data', 'Show EDA data in bom', 'False'),
            (32, 'weekoffs', 'List of week offs', 'Saturday,Sunday'),
            (34, 'app_production', 'If "True" to show production module', app_production),
            (31, 'ec_integration', 'Set "True" if ec service is integrated in sparrow.', 'False'),
            (33, 'app_eda', 'If "True" to show EDA module', 'True'),
            (2, 'usd_rate_to_base_currency', 'USD currency factor to base currency.', '0.94'),
            (3, 'supplier_price_update_rate', 'Supplier price will be updated if it is older then 3 days. Parameter value is in days.', '3'),
            (18, 'base_currency', 'Base currency of the system', 'EUR'),
            (4, 'mo_cpl_view', 'If "True" to show Production CPL module', 'False'),
            (5, 'final_inspection_code', 'Only one final operation in routing', 'FINISP'),
            (6, 'stock_selection', 'Stock sort by ascending when select LIFO(Last in First out) else default FIFO(First in First out).', 'LIFO'),
            (7, 'Indirect cost', 'Add below % cost value add into total cost.', '5'),
            (9, 'cost_m3_per_hour', 'per hour usage below value m3 material', '2'),
            (10, 'cost_ml_per_solderjoint', '1 solderjoint usage below value ml material', '0.2'),
            (11, 'cost_gram_per_solderjoint', '1 solderjoint use below value gram material', '0.1'),
            (12, 'cost_gram_per_dm2', '1 dm2 size use below value gram material', '0.64'),
            (13, 'workdays', 'Working days in a week', 'MO,TU,WE,TH,FR'),(8, 'decimalpoint', 'Decimal point for all calculations', '4'),
            (14, 'mpn_field', 'When selected name then MPN as a product name, if select internal_ref then MPN as a product internal reference, if select serial_num then MPN as a product artical number.', 'name'),
            (1, 'default_mo_routing', 'Set routing name to automatic set routing in ec mo generate', 'EC_MO_Route'),
            (15, 'company_code', 'Company code for template prefix', 'ec'),                        
            (35, 'app_ecommerce', 'If true show customer site view', app_ecommerce),
            (36, 'auto_generate_product_code', 'If value is true then product article number will be generated by system.', 'False'),]
            
            sql7 = ''' INSERT INTO base_sysparameter VALUES(%s, %s, %s, %s) '''
            cursor.executemany(sql7,base_sysparameter)
            cursor.execute(''' ALTER SEQUENCE base_sysparameters_id_seq RESTART WITH 36''')

            financial_paymentmode = [(1, 'Bank', 'False'),
            (2, 'Cash', 'False'),
            (3, 'Cheque', 'False'),
            (4, 'Credit card', 'False'),
            (5, 'Paypal', 'False'),
            (6, 'BT', 'False'),
            (7, 'COD', 'False'),
            (8, 'CBP', 'False')]
            sql8 = ''' INSERT INTO financial_paymentmode VALUES(%s, %s, %s) '''
            cursor.executemany(sql8,financial_paymentmode)
            cursor.execute(''' ALTER SEQUENCE financial_paymentmode_id_seq RESTART WITH 8''')

            financial_invoicestatus = [(1, 'Draft', 'False'),
            (2, 'Outstanding', 'False'),
            (3, 'Closed', 'False'),
            (4, 'Bad Debt', 'False'),
            (5, 'Legal Recovery', 'False')]
            sql9 = ''' INSERT INTO financial_invoicestatus VALUES(%s, %s, %s) '''
            cursor.executemany(sql9,financial_invoicestatus)
            cursor.execute(''' ALTER SEQUENCE financial_invoicestatus_id_seq RESTART WITH 5''')

            financial_paymentdifferencetype = [(1, 'OutStanding', 'False'),
            (2, 'Bank Charges', 'False'),
            (3, 'Discount', 'False'),
            (4, 'Write Off', 'False'),
            (5, 'Over Paid', 'False'),
            (6, 'Close', 'False')]
            sql10 = ''' INSERT INTO financial_paymentdifferencetype VALUES(%s, %s, %s) '''
            cursor.executemany(sql10,financial_paymentdifferencetype)
            cursor.execute(''' ALTER SEQUENCE financial_paymentdifferencetype_id_seq RESTART WITH 6''')

            financial_paymentterm = [(1, '15 days', 'False', 15),
            (2, '30 days', 'False', 30),
            (3, '60 days', 'False', 60)]
            sql11 = ''' INSERT INTO financial_paymentterm VALUES(%s, %s, %s, %s) '''
            cursor.executemany(sql11,financial_paymentterm)
            cursor.execute(''' ALTER SEQUENCE financial_paymentterm_id_seq RESTART WITH 3''')

            inventory_location = [(1, 'Stock', 'False'),
            (4, 'Supplier', 'False'),
            (5, 'Customer', 'False')]
            sql12 = ''' INSERT INTO inventory_location VALUES(%s, %s, %s) '''
            cursor.executemany(sql12,inventory_location)
            cursor.execute(''' ALTER SEQUENCE inventory_location_id_seq RESTART WITH 5''')

            inventory_movetype = [(1, 'Inward', 'False'),
            (2, 'Outward', 'False'),
            (3, 'Scrap', 'False'),
            (4, 'Produce', 'False'),
            (5, 'Consume', 'False'),
            (6, 'Stock adjustment (+)', 'False'),
            (7, 'Stock adjustment (-)', 'False'),
            (8, 'Material Issue', 'False')]
            sql13 = ''' INSERT INTO inventory_movetype VALUES(%s, %s, %s) '''
            cursor.executemany(sql13, inventory_movetype)
            cursor.execute(''' ALTER SEQUENCE inventory_movetype_id_seq RESTART WITH 8''')

            cursor.execute('''INSERT INTO inventory_warehouse VALUES (1, 'Company', 'False')''')
            cursor.execute(''' ALTER SEQUENCE inventory_warehouse_id_seq RESTART WITH 1''')

            cursor.execute(''' INSERT INTO logistics_shipmethod VALUES (1, 'Courier', 'False')''' )
            cursor.execute(''' ALTER SEQUENCE logistics_shipmethod_id_seq RESTART WITH 1''')

            purchasing_orderstatus = [(1, 'new', 'New', 'True'),
            (2, 'receive', 'Receive', 'True'),
            (3, 'ready_to_receive', 'Ready to receive', 'True'),
            (4, 'received', 'Received', 'True'),
            (5, 'done', 'Done', 'True'),
            (6, 'cancel', 'Cancel', 'True'),
            (8, 'po_return', 'Confirm return PO', 'True'),
            (9, 'confirmed', 'Quotation confirmed', 'True'),
            (7, 'draft_receipt', 'Draft receipt', 'True')]
            sql14 = ''' INSERT INTO purchasing_orderstatus VALUES(%s, %s, %s, %s) '''
            cursor.executemany(sql14, purchasing_orderstatus)
            cursor.execute(''' ALTER SEQUENCE purchasing_orderstatus_id_seq RESTART WITH 9''')

            sales_orderstatus =[(6, 'new', 'New', 'True'),
            (12, 'cancel', 'Cancel', 'True'),
            (8, 'produce', 'Produce', 'True'),
            (9, 'inspection', 'Inspection', 'True'),
            (13, 'completed', 'Completed', 'True'),
            (10, 'ship', 'Ready to ship', 'True'),
            (11, 'shipped', 'Shipped', 'True'),
            (15, 'so_return', 'Confirm return SO', 'True'),
            (7, 'confirmed', 'Confirmed', 'True'),
            (1, 'draft_shipment', 'Draft shipment', 'True')]
            sql15 = ''' INSERT INTO sales_orderstatus VALUES(%s, %s, %s, %s) '''
            cursor.executemany(sql15, sales_orderstatus)
            cursor.execute('''ALTER SEQUENCE sales_orderstatus_id_seq RESTART WITH 15''')
            rows = []
            cursor.execute(''' select * from auth_user''')
            for row in cursor.fetchall():
                rows.append(row)               

            cursor.execute('''INSERT INTO auth_group VALUES ('%s', '%s','%s','%s','%s')''' %(1, 'Admin','Master user permission',current_time, id))
            cursor.execute('''ALTER SEQUENCE auth_group_id_seq RESTART WITH 1''')

            rows = []
            cursor.execute(''' select * from auth_group''')
            for row in cursor.fetchall():
                rows.append(row)
            group_id = rows[0][0]
            menus_ids = []
            cursor.execute(''' select * from accounts_mainmenu''')
            for row in cursor.fetchall():
                menus_ids.append(row[0])

            for menu_id in menus_ids:
                cursor.execute('''INSERT INTO accounts_userrolepermission(created_on,created_by_id,menu_id,group_id) VALUES ('%s', '%s','%s','%s')''' %(current_time, id, menu_id, group_id))

            cursor.execute(''' INSERT INTO accounts_mainmenu_permission VALUES ('%s','%s','%s') '''%(1, id, group_id ))

            cursor.execute(''' INSERT INTO auth_user_groups VALUES ('%s','%s','%s') '''%(1, id, group_id ))

            base_currency = input("Enter base_currency: ")
            currency_symbol = base_currency
            cursor.execute(''' INSERT INTO base_currency VALUES ('%s','%s','%s','%s','%s') '''%(1, base_currency, currency_symbol,'True','False' ))
            cursor.execute('''ALTER SEQUENCE base_currency_id_seq RESTART WITH 1''')
            currency_id = None
            cursor.execute(''' select * from base_currency''')
            for rows in cursor.fetchall():
                currency_id = rows[0]

            cursor.execute(''' INSERT INTO base_currencyrate VALUES ('%s','%s','%s','%s','%s','%s') '''%(1, 1, current_time, current_time, id, currency_id ))
            cursor.execute('''ALTER SEQUENCE base_currencyrate_id_seq RESTART WITH 1''')
            cursor.execute(''' select * from partners_country ''')
            country_id = None
            for row in cursor.fetchall():
                if row[1] == 'India':
                    country_id = row[0]

            cursor.execute(''' INSERT INTO partners_partner(
            name, comment, is_supplier, is_customer, email, is_company, 
            website, active, phone, mobile, fax, parent_id, created_by_id, 
            created_on, note, is_deleted, account_no, country_id, is_hc, 
            tax_no, tax_status, discount, account_manager_id, is_prospect, 
            language, currency_id, company_img)
            VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')'''
            %('Company', None, 'False', 'False', 'info@company.me', 'False', '', 'False', '0', '0', '0', 0, 1, current_time, None, 'False', None, country_id , 'True', None, 'standard', 0 , id, 'False', None, currency_id, ''))

            cursor.execute(''' select * from partners_partner ''')
            partner_id = None
            for row in cursor.fetchall():
                partner_id = row[0]
            cursor.execute(''' INSERT INTO accounts_userprofile(partner_id, is_deleted, avatar, color_scheme, user_id, image_name, 
            user_type, purchase_plan_settings, ip_restriction)
            VALUES('%s','%s','%s','%s','%s','%s','%s','%s','%s')'''
            %(partner_id,'False', 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAQAAADZc7J/AAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAAAAmJLR0QAAKqNIzIAAAAJcEhZcwAADdcAAA3XAUIom3gAAAAHdElNRQfhCAQNCiRg6iEZAAABtElEQVRIx72Vv0tbURTHP+c2EYK0f4A4aDGh7VJ84tYpq8SpiFOMaUs3o27p5qKbQjc1PDU4uAbp2qlLh74ihLYQEDplFLo8iMXT4elrkpuouaJne+ee7+eeX5cn9LG9tObx8ICAQKqLjd5x0supsr+kG6TaXKGUCx9FbwVQ2T/WmR6hnwo5G/HIDhwr6VLPbDMnZ7WvN2awl9aTjuTbLZSX3b0wVgH5vnJIab7bZQHwuM68BwAMaDYguDY+uH+AVAn7ykOp3ghYbEi5n17K9ou48yqbTulBxs+uSSEny12FhLJcyK2Jnz3IaMel8cd2cmhVP/AE+Hbx7u13+zlXJs0uU8AfWW9tvj/vAGwnk595FWP/csRWsa3jvscK8yRix5fzbIS4BPibrFhF/5Qf+gvkmb7guXW6VVyNAf5TGgPv5AXp4ulVE0sOK20o/Z/C64HlscpAZYIRJ8BIZQIMmGknOZHSgIy7AmQcDOioK0BHowxSrgBJRRkkXAGaiMZ46gogWiSpO5dQBwPDNdwQ9eEaGJhrsSDNgW9vsjDXuvw31pqzOyhGHnObiZxpwKHOv/kN8A/pboEFiEa8pQAAACV0RVh0ZGF0ZTpjcmVhdGUAMjAxNy0wOC0wNFQxMzoxMDozNiswMjowMGQtmKcAAAAldEVYdGRhdGU6bW9kaWZ5ADIwMTctMDgtMDRUMTM6MTA6MzYrMDI6MDAVcCAbAAAAGXRFWHRTb2Z0d2FyZQB3d3cuaW5rc2NhcGUub3Jnm+48GgAAAABJRU5ErkJggg==', "bg_color:#364760,button_color:#1174da,link_color:#1174da", id, '', 1, None,'False'))

            cursor.execute(''' INSERT INTO products_unitofmeasure(name,is_active,created_on,created_by_id,code) VALUES('%s','%s','%s','%s','%s') '''%('Unit(s)','True',current_time,id,'unit'))            

        schema = input("Enter schema name: ")
        username = input("Enter Username: ")
        password = input("Enter Password: ")

        user_id = 0
        with schema_context(schema):
            user = User.objects.filter(username=username).first()
            if user != None:
                print("Process failed. User is already available. Verify other master tables in order to avoid dupicate data being inserted.")
                return

            user = User.objects.create_superuser(username=username, password=password, email="admin@admin.com")#,is_superuser=True, first_name=username, last_name=username, is_staff=True, is_active=True, date_joined=datetime.datetime.now())                                                
            user.save()
            user_id = user.id
        
        with transaction.atomic(): 
            if user_id == 0:
                print("Error occurred in creating user")
                return

            dbname = settings.DATABASES['default']['NAME']
            user = settings.DATABASES['default']['USER']
            password = settings.DATABASES['default']['PASSWORD']
            host = settings.DATABASES['default']['HOST']
            port = settings.DATABASES['default']['PORT']
            db = pg.connect(dbname=dbname,user=user,password=password,host=host,port=port)        
            cursor = db.cursor()
            
            cursor.execute("SET search_path TO " +schema )            

            insert_default_data(user_id, cursor)            

            db.commit()
            db.close()

            print("")
            print("Data migrated")

'''
delete from demo.auth_user CASCADE;
delete from demo.partners_country CASCADE; 
delete from demo.accounts_mainmenu  CASCADE; 
delete from demo.attachment_filetype  CASCADE; 
delete from demo.auditlog_auditaction  CASCADE; 
delete from demo.base_docnumber  CASCADE; 
delete from demo.base_shippingservice  CASCADE; 
delete from demo.base_sysparameter  CASCADE; 
delete from demo.financial_paymentmode  CASCADE; 
delete from demo.financial_invoicestatus  CASCADE; 
delete from demo.financial_paymentdifferencetype  CASCADE; 
delete from demo.financial_paymentterm  CASCADE; 
delete from demo.inventory_location  CASCADE; 
delete from demo.inventory_movetype  CASCADE; 
delete from demo.inventory_warehouse  CASCADE; 
delete from demo.logistics_shipmethod  CASCADE; 
delete from demo.purchasing_orderstatus  CASCADE; 
delete from demo.sales_orderstatus  CASCADE;
delete from demo.accounts_userrole  CASCADE;
delete from demo.accounts_userrolepermission  CASCADE;
delete from demo.accounts_mainmenu_permission CASCADE;
delete from demo.base_currency CASCADE;
delete from demo.base_currencyrate CASCADE;
delete from demo.accounts_userprofile CASCADE;
delete from demo.partners_partner CASCADE;
delete from demo.django_session  CASCADE;
delete from demo.products_unitofmeasure CASCADE;
''' 