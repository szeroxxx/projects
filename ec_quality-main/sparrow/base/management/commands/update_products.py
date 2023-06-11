from django.core.management.base import BaseCommand

from tenant_schemas.utils import schema_context
import logging

from django.db import transaction
from products.models import Product
from xlrd import open_workbook

from inventory.models import StockStatus


class Command(BaseCommand):
    help = "Update generic and ec stock."

    def handle(self, *args, **options):
        with schema_context("ec"):
            try:
                """
                0 -> Product name
                1 -> Description
                2 -> SKU
                3 -> QTY
                4 -> Unit
                5 -> Article number
                Box no -> 6

                """
                # [u'RC0603JR-0747RL', u'RES SMD 47 OHM 5% 1/10W 0603', u'603-RC0603JR-0747RL', 4933L, u'PCS', u'PM00388', 7L]
                with transaction.atomic():
                    from inventory import inventory_view
                    from products.products_view import create_product

                    wb = open_workbook("C:\\Users\\admin\\Desktop\\inventroy_update.xlsx")
                    sheet = wb.sheets()[0]

                    # book = openpyxl.load_workbook("", read_only=True)
                    # sheet = book.active
                    row_count = sheet.nrows
                    column_count = sheet.ncols
                    for row in range(1, row_count):
                        row_data = []
                        for col in range(1, column_count):
                            value = sheet.cell(row, col).value
                            if value:
                                row_data.append(value)
                            else:
                                row_data.append("")
                        print(row_data, "row_data")
                        product_name = str(row_data[0])
                        # desc = row_data[1]
                        # sku = row_data[2]
                        qty = int(row_data[2])
                        # unit = row_data[4]
                        # article_num = row_data[5]
                        product = Product.objects.filter(name=product_name.strip()).first()
                        exist_products = []
                        if product:
                            print(product_name, qty)
                            # product.name = product_name
                            # product.description_purchase = desc
                            # product.save()
                            exist_products.append(product.id)
                            move_type = None
                            final_qty = 0
                            stock_qty = 0
                            inventory_stock_obj = StockStatus.objects.filter(product_id=product.id).first()
                            if inventory_stock_obj:
                                current_qty = inventory_stock_obj.stock_on_hand
                            else:
                                current_qty = 0
                            import_qty = qty
                            # print(current_qty, 'current', import_qty, qty)
                            if current_qty != import_qty:
                                if import_qty > current_qty:
                                    stock_qty = import_qty
                                    try:
                                        final_qty = import_qty - current_qty
                                    except:
                                        print(product_name, "pro")
                                        final_qty = 0 - current_qty
                                    move_type = "Stock adjustment (+)"

                                elif import_qty < current_qty:
                                    final_qty = current_qty - import_qty
                                    stock_qty = import_qty
                                    move_type = "Stock adjustment (-)"

                            if final_qty > 0:
                                inventory_stock_obj.stock_on_hand = stock_qty
                                inventory_stock_obj.save()
                                inventory_view.generate_stock_move(product.id, final_qty, move_type, "", "", 1, None, "Product stock update")
                        else:
                            print("create")
                            new_product = create_product(1, " ", product_name, " ", False, True, "", None)
                            # new_product.internal_ref = article_num
                            new_product.save()
                            stock_obj = inventory_view.get_stock_status_obj(new_product.id, qty if qty else 0, "in")
                            inventory_view.update_stock_status([stock_obj])
                            exist_products.append(new_product.id)

                    # pro_ids = Product.objects.exclude(id__in = exist_products).values_list('id', flat = True)
                    # for pro_id in pro_ids:
                    #     move_type = None
                    #     final_qty = 0
                    #     stock_qty = 0
                    #     inventory_stock_obj = StockStatus.objects.filter(product_id = pro_id).first()
                    #     if inventory_stock_obj:
                    #         current_qty = inventory_stock_obj.stock_on_hand
                    #     else:
                    #         current_qty = 0
                    #     import_qty = 0
                    #     # print(current_qty, 'current', import_qty)
                    #     if current_qty != import_qty:
                    #         if import_qty > current_qty:
                    #             stock_qty = import_qty
                    #             final_qty = import_qty - current_qty
                    #             move_type = "Stock adjustment (+)"

                    #         elif import_qty < current_qty:
                    #             final_qty =  current_qty - import_qty
                    #             stock_qty = import_qty
                    #             move_type = "Stock adjustment (-)"

                    #     if final_qty > 0:
                    #         inventory_stock_obj.stock_on_hand = stock_qty
                    #         inventory_stock_obj.save()
                    #         inventory_view.generate_stock_move(pro_id, final_qty, move_type, 'Product update', '', 1, None)

            # except TypeError:
            #     # print(import_qty, "ipm")
            #     print(product_name)
            #     logging.exception("Something went wrong.")
            except Exception:
                logging.exception("Something went wrong.")
