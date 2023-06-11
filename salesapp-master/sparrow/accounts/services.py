from accounts.models import Company

class CompanyService(object):

    @staticmethod
    def get_root_compnay_object():
        return Company.objects.filter().first()

    @staticmethod
    def get_root_compnay():
        return Company.objects.filter().values('id', 'company_img', 'name', 'email', 'mobile', 'phone', 'website', 'timezone', 'timezone_offset', 'daylight_offset', 'daylight_start', 'daylight_end').first()

class UserService(object):

    @staticmethod
    def get_theme_info(color_schemes):
        color_scheme_data = {
            'bg_color': '#2A3F54' ,
            'button_color': '#337ab7',
            'link_color': '#266EBB',
            'row_color': '#FFFFCC'
        }
        if color_schemes:
            color_schemes = color_schemes.split(",")
            for param in color_schemes:
                if param != "":
                    scheme_data = param.split(':')
                    color_scheme_data[scheme_data[0].strip()] = scheme_data[1].strip()

        return color_scheme_data

    def get_background_images_list():
        return [str(index) + '_b.jpg' for index in range(1, 11)]
        