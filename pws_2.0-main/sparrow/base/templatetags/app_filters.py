import logging

from django import template

from base.util import Util

register = template.Library()


@register.filter
def get_formatted_decimal(value, arg):
    new_decimal = Util.decimal_to_str(arg, value)
    return new_decimal


@register.filter
def get_number_value(value, arg):
    if value is None:
        value = 0.00
    new_decimal = "%.0f" % value
    return new_decimal


@register.filter
def get_two_decimal_value(value, arg):
    if value is None or value == "":
        value = 0.00
    new_decimal = "%.2f" % value
    return new_decimal


@register.filter
def get_four_decimal_value(value, arg):
    if value is None:
        value = 0.0000
    new_decimal = "%.4f" % value
    return new_decimal


@register.filter
def get_currency(value, arg):
    currency = ""
    if "base_currency" in arg.session:
        currency = arg.session.get("base_currency")
    return currency + " " + value


@register.filter
def get_reserved_qty(dictionary, key):
    if dictionary.get(key)["reserved_qty"] > 0:
        return dictionary.get(key)["reserved_qty"]
    else:
        return 0


@register.filter
def get_formatted_decimal_pdf(value, arg):
    new_decimal = Util.decimal_to_str(None, value, arg)
    return new_decimal


@register.filter
def get_currency_pdf(value, arg):
    return arg + " " + value


@register.filter
def get_range(value):
    return range(0, value)


@register.filter
def get_serial_source(value):
    if value is None:
        return ""
    source = ""
    try:
        if value is not None:
            if value.mfgorder is not None:
                source = value.mfgorder.mfg_order_num
            if value.to_line is not None and value.to_line.order_line is not None:
                source = value.to_line.order_line.order.ordernum
            if value.to_line is not None and value.to_line.po_line is not None:
                source = value.to_line.po_line.order.ordernum
    except Exception:
        logging.exception("Something went wrong")
        source = ""
    return source


@register.filter
def get_formatted_string(value, arg):
    if isinstance(value, str):
        return value.lower().replace(" ", "_")
    return value


@register.filter
def break_for_loop(category_sequence, selected_category):
    url_string = ""
    for category in category_sequence:
        url_string += category["name"].lower().replace(" ", "-") + "-"
        if category["id"] == selected_category["id"]:
            break
    return url_string


@register.filter
def get_multiply_value(value, multiply_value):
    if value is not None:
        return value * multiply_value
    return ""


@register.filter
def get_two_factor_date(date):
    if date is not None:
        return date.strftime("%d %b")


@register.filter
def startswith_check(string):
    """for product images grouping"""
    if string.startswith("th"):
        return 0
    elif string.startswith("me"):
        return 1
    elif not string.startswith("th") and not string.startswith("me"):
        return 2


@register.filter
def get_local_time(utctime, showtime=False, time_format=None):
    new_time = Util.get_local_time(utctime, showtime, time_format)
    return new_time


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def get_short_string(arg, limit):
    if len(arg) >= limit:
        return arg[0 : limit - 2] + ".."
    return arg


@register.filter
def get_division(value, arg):
    division_value = value / arg
    if not isinstance(division_value, int) or division_value == 0:
        return 1
    return division_value


@register.filter
def get_name_string(value):
    return value.replace("'", "")


@register.filter
def get_float_value(value, arg):
    if value is None:
        value = 0.00
    new_decimal = float(value)
    return new_decimal


@register.filter
def replace(value, args):
    replace_data = args.split(",")
    return value.replace(replace_data[0][1:-1], replace_data[1][1:-1])
