# coding=utf-8
from django.core.management.base import BaseCommand
import psycopg2 as pg
from django.conf import settings
from django.contrib.auth.models import User
from django.db import transaction
import datetime
from tenant_schemas.utils import schema_context
from exception_log import manager
from django.http import HttpResponse, response

class Command(BaseCommand):    

    def handle(self, *args, **options):

        def insert_default_data(id, cursor):
            current_time= datetime.datetime.now()
            partners_country = [('Albania','AL','f'),('Algeria','DZ','f'),('American Samoa','AS','f'), ('Andorra','AD','f'),('Angola','AO','f'),('Anguilla','AI','f'),
            ('Antarctica','AQ','f'),('Antigua and Barbuda','AG','f'),('Argentina','AR','f'),('Armenia','AM','f'),('Aruba','AW','f'),('Australia','AU','f'),('Austria','AT','f'),('Azerbaijan','AZ','f'),('Bahamas','BS','f'),
            ('Bahrain','BH','f'),('Bangladesh','BD','f'),('Barbados','BB','f'),('Belarus','BY','f'),('Belgium','BE','f'),('Belize','BZ','f'),('Benin','BJ','f'),('Bermuda','BM','f'),('Bhutan','BT','f'),('Bolivia (Plurinational State of)','BO','f'),('Bonaire, Sint Eustatius and Saba','BQ','f'),('Bosnia and Herzegovina','BA','f'),('Botswana','BW','f'),
            ('Bouvet Island','BV','f'),('Brazil','BR','f'),('British Indian Ocean Territory','IO','f'),('Brunei Darussalam','BN','f'),('Bulgaria','BG','f'),('Burkina Faso','BF','f'),('Burundi','BI','f'),
            ('Cabo Verde','CV','f'),('Cambodia','KH','f'),('Cameroon','CM','f'),('Canada','CA','f'),('Cayman Islands','KY','f'),
            ('Central African Republic','CF','f'),('Chad','TD','f'),('Chile','CL','f'),('China','CN','f'),('Christmas Island','CX','f'),('Cocos (Keeling) Islands','CC','f'),
            ('Colombia','CO','f'),('Comoros','KM','f'),('Congo','CG','f'),('Congo (Democratic Republic of the)','CD','f'),('Cook Islands','CK','f'),
            ('Costa Rica','CR','f'),('Croatia','HR','f'),('Cuba','CU','f'),('Curaçao','CW','f'),('Cyprus','CY','f'),('Czechia','CZ','f'),
            ('Denmark','DK','f'),('Djibouti','DJ','f'),('Dominica','DM','f'),('Dominican Republic','DO','f'),('Ecuador','EC','f'),('Egypt','EG','f'),('El Salvador','SV','f'),('Equatorial Guinea','GQ','f'),('Eritrea','ER','f'),('Estonia','EE','f'),('Ethiopia','ET','f'),('Falkland Islands (Malvinas)','FK','f'),
            ('Faroe Islands','FO','f'),('Fiji','FJ','f'),('Finland','FI','f'),('France','FR','f'),('French Guiana','GF','f'),('French Polynesia','PF','f'),
            ('French Southern Territories','TF','f'),('Gabon','GA','f'),('Gambia','GM','f'),('Georgia','GE','f'),('Germany','DE','f'),('Ghana','GH','f'),('Gibraltar','GI','f'),('Greece','GR','f'),
            ('Greenland','GL','f'),('Grenada','GD','f'),('Guadeloupe','GP','f'),('Guam','GU','f'),('Guatemala','GT','f'),('Guernsey','GG','f'),('Guinea','GN','f'),('Guinea-Bissau','GW','f'),
            ('Guyana','GY','f'),('Haiti','HT','f'),('Heard Island and McDonald Islands','HM','f'),('Holy See','VA','f'),('Honduras','HN','f'),('Hong Kong','HK','f'),('Hungary','HU','f'),('Iceland','IS','f'),('India','IN','t'),('Indonesia','id','f'),
            ('Iran (Islamic Republic of)','IR','f'),('Iraq','IQ','f'),('Ireland','IE','f'),('Isle of Man','IM','f'),('Israel','IL','f'),('Italy','IT','f'),('Jamaica','JM','f'),('Japan','JP','f'),
            ('Jersey','JE','f'),('Jordan','JO','f'),('Kazakhstan','KZ','f'),('Kenya','KE','f'),('Kiribati','KI','f'),('Korea (Republic of)','KR','f'),('Kuwait','KW','f'),('Kyrgyzstan','KG','f'),('Latvia','LV','f'),('Lebanon','LB','f'),('Lesotho','LS','f'),('Liberia','LR','f'),('Libya','LY','f'),('Liechtenstein','LI','f'),
            ('Lithuania','LT','f'),('Luxembourg','LU','f'),('Macao','MO','f'),('Macedonia (the former Yugoslav Republic of)','MK','f'),('Madagascar','MG','f'),('Malawi','MW','f'),('Malaysia','MY','f'),('Maldives','MV','f'),('Mali','ML','f'),('Malta','MT','f'),('Marshall Islands','MH','f'),('Martinique','MQ','f'),('Mauritania','MR','f'),('Mauritius','MU','f'),('Mayotte','YT','f'),('Mexico','MX','f'),('Micronesia (Federated States of)','FM','f'),('Moldova (Republic of)','MD','f'),('Monaco','MC','f'),
            ('Mongolia','MN','f'),('Montenegro','ME','f'),('Montserrat','MS','f'),('Morocco','MA','f'),('Mozambique','MZ','f'),('Myanmar','MM','f'),('Namibia','NA','f'),
            ('Nauru','NR','f'),('Nepal','NP','f'),('Netherlands','NL','f'),('New Caledonia','NC','f'),('New Zealand','NZ','f'),('Nicaragua','NI','f'),('Niger','NE','f'),('Nigeria','NG','f'),('Niue','NU','f'),('Norfolk Island','NF','f'),('Northern Mariana Islands','MP','f'),
            ('Norway','NO','f'),('Oman','OM','f'),('Pakistan','PK','f'),('Palau','PW','f'),('Palestine, State of','PS','f'),('Panama','PA','f'),('Papua New Guinea','PG','f'),('Paraguay','PY','f'),('Peru','PE','f'),('Philippines','PH','f'),('Pitcairn','PN','f'),('Poland','PL','f'), ('Portugal','PT','f'),('Puerto Rico','PR','f'),('Qatar','QA','f'),('Réunion','RE','f'),('Romania','RO','f'),
            ('Russian Federation','RU','f'),('Rwanda','RW','f'),('Saint Barthélemy','BL','f'),('Saint Helena, Ascension and Tristan da Cunha','SH','f'),('Saint Kitts and Nevis','KN','f'),('Saint Lucia','LC','f'),('Saint Martin (French part)','MF','f'),('Saint Pierre and Miquelon','PM','f'),
            ('Saint Vincent and the Grenadines','VC','f'),('Samoa','WS','f'),('San Marino','SM','f'),('Sao Tome and Principe','ST','f'),('Saudi Arabia','SA','f'),('Senegal','SN','f'),('Serbia','RS','f'),('Seychelles','SC','f'),('Sierra Leone','SL','f'),('Singapore','SG','f'),
            ('Sint Maarten (Dutch part)','SX','f'),('Slovakia','SK','f'),('Slovenia','SI','f'),('Solomon Islands','SB','f'),('Somalia','SO','f'),('South Africa','ZA','f'),('South Georgia and the South Sandwich Islands','GS','f'),('South Sudan','SS','f'),('Spain','ES','f'),
            ('Sri Lanka','LK','f'),('Sudan','SD','f'),('Suriname','SR','f'),('Svalbard and Jan Mayen','SJ','f'),('Swaziland','SZ','f'),('Sweden','SE','f'),('Switzerland','CH','f'),
            ('Syrian Arab Republic','SY','f'),('Taiwan, Province of China[a]','TW','f'),('Tajikistan','TJ','f'),('Tanzania, United Republic of','TZ','f'),('Thailand','TH','f'),('Timor-Leste','TL','f'),('Togo','TG','f'),('Tokelau','TK','f'),
            ('Tonga','TO','f'),('Trinidad and Tobago','TT','f'),('Tunisia','TN','f'),('Turkey','TR','f'),('Turkmenistan','TM','f'),
            ('Turks and Caicos Islands','TC','f'),('Tuvalu','TV','f'),('Uganda','UG','f'),('Ukraine','UA','f'),('United Arab Emirates','AE','f'),('United Kingdom of Great Britain and Northern Ireland','GB','f'),('United States of America','US','f'),('United States Minor Outlying Islands','UM','f'),('Uruguay','UY','f'),
            ('Uzbekistan','UZ','f'),('Vanuatu','VU','f'),('Venezuela (Bolivarian Republic of)','VE','f'),('Viet Nam','VN','f'),('Virgin Islands (British)','VG','f'),('Virgin Islands (U.S.)','VI','f'),('Wallis and Futuna','WF','f'),('Western Sahara','EH','f'),('Yemen','YE','f'),('Zambia','ZM','f'),('Zimbabwe','ZW','f')]
            sql_country = '''INSERT INTO partners_country(name,code,has_state)values(%s,%s,%s)'''            
            cursor.executemany(sql_country , partners_country)            

            country_code = input("Enter country code: ")
            cursor.execute(''' select * from partners_country where code = '%s' ''' %(country_code))
            country_id = None
            for row in cursor.fetchall():                
                    country_id = row[0]

            if country_id == None:
                  raise ValueError('Invalid country code.')


            base_currency = input("Enter base currency code: ")
            currency_symbol = base_currency
            cursor.execute(''' INSERT INTO base_currency VALUES ('%s','%s','%s','%s','%s') '''%(1, base_currency, currency_symbol,'True','False' ))
            cursor.execute('''ALTER SEQUENCE base_currency_id_seq RESTART WITH 1''')
            currency_id = None
            cursor.execute(''' select * from base_currency''')
            for rows in cursor.fetchall():
                currency_id = rows[0]

            cursor.execute(''' INSERT INTO base_currencyrate VALUES ('%s','%s','%s','%s','%s','%s') '''%(1, 1, current_time, current_time, id, currency_id ))            
            cursor.execute('''ALTER SEQUENCE base_currencyrate_id_seq RESTART WITH 1''')

            cursor.execute(''' INSERT INTO partners_partner(
            name, comment, is_supplier, is_customer, email, is_company, 
            website, active, phone, mobile, fax, parent_id, created_by_id, 
            created_on, note, is_deleted, account_no, country_id, is_hc, 
            tax_no, tax_status, account_manager_id, is_prospect, 
            language, currency_id, company_img)
            VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')'''
            %('Company', '', 'False', 'False', 'info@company.me', 'False', '', 'False', '0', '0', '0', 0, 1, current_time, None, 'False', None, country_id , 'True', None, 'standard', id, 'False', None, currency_id, ''))

            cursor.execute(''' select * from partners_partner ''')
            partner_id = None
            for row in cursor.fetchall():
                partner_id = row[0]
            cursor.execute(''' INSERT INTO accounts_userprofile(partner_id, is_deleted, avatar, color_scheme, user_id, image_name, 
            user_type, purchase_plan_settings, ip_restriction)
            VALUES('%s','%s','%s','%s','%s','%s','%s','%s','%s')'''
            %(partner_id,'False', 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAQAAADZc7J/AAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAAAAmJLR0QAAKqNIzIAAAAJcEhZcwAADdcAAA3XAUIom3gAAAAHdElNRQfhCAQNCiRg6iEZAAABtElEQVRIx72Vv0tbURTHP+c2EYK0f4A4aDGh7VJ84tYpq8SpiFOMaUs3o27p5qKbQjc1PDU4uAbp2qlLh74ihLYQEDplFLo8iMXT4elrkpuouaJne+ee7+eeX5cn9LG9tObx8ICAQKqLjd5x0supsr+kG6TaXKGUCx9FbwVQ2T/WmR6hnwo5G/HIDhwr6VLPbDMnZ7WvN2awl9aTjuTbLZSX3b0wVgH5vnJIab7bZQHwuM68BwAMaDYguDY+uH+AVAn7ykOp3ghYbEi5n17K9ou48yqbTulBxs+uSSEny12FhLJcyK2Jnz3IaMel8cd2cmhVP/AE+Hbx7u13+zlXJs0uU8AfWW9tvj/vAGwnk595FWP/csRWsa3jvscK8yRix5fzbIS4BPibrFhF/5Qf+gvkmb7guXW6VVyNAf5TGgPv5AXp4ulVE0sOK20o/Z/C64HlscpAZYIRJ8BIZQIMmGknOZHSgIy7AmQcDOioK0BHowxSrgBJRRkkXAGaiMZ46gogWiSpO5dQBwPDNdwQ9eEaGJhrsSDNgW9vsjDXuvw31pqzOyhGHnObiZxpwKHOv/kN8A/pboEFiEa8pQAAACV0RVh0ZGF0ZTpjcmVhdGUAMjAxNy0wOC0wNFQxMzoxMDozNiswMjowMGQtmKcAAAAldEVYdGRhdGU6bW9kaWZ5ADIwMTctMDgtMDRUMTM6MTA6MzYrMDI6MDAVcCAbAAAAGXRFWHRTb2Z0d2FyZQB3d3cuaW5rc2NhcGUub3Jnm+48GgAAAABJRU5ErkJggg==', "bg_color:#364760,button_color:#1174da,link_color:#1174da", id, '', 1, None,'False'))


        schema = input("Enter schema name: ")        
        username = input("Enter Username: ")
        password = input("Enter Password: ")

        try:
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
        except Exception as e:
            print(str(e))
            # manager.create_from_exception(e)
            # logging.exception('Something went wrong.')
            # return HttpResponse(AppResponse.msg(0, str(e)), content_type='json')

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