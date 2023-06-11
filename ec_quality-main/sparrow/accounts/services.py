import boto3
from django.conf import settings
from django.contrib.auth.models import User

from accounts.models import UserProfile

from . import profile_image_generator


class UserService(object):
    @staticmethod
    def get_theme_info(color_schemes):
        color_scheme_data = {"bg_color": "#2A3F54", "button_color": "#337ab7", "link_color": "#266EBB", "row_color": "#FFFFCC", "db_bg_color": "#F1F5F9"}
        if color_schemes:
            color_schemes = color_schemes.split(",")
            for param in color_schemes:
                if param != "":
                    scheme_data = param.split(":")
                    color_scheme_data[scheme_data[0].strip()] = scheme_data[1].strip()
        return color_scheme_data

    @staticmethod
    def create_user(first_name, last_name, email, is_superuser, is_staff, is_active, partner_id, ip_restriction, remark_type=None):
        user = User(first_name=first_name, last_name=last_name, email=email, username=email, is_superuser=is_superuser, is_staff=is_staff, is_active=is_active)
        user.save()

        # Create user profile
        profile_image = profile_image_generator.GenerateCharacters(first_name[0].upper() + "" + last_name[0].upper(), user.id)
        profile = UserProfile.objects.create(
            user=user,
            user_type=1,
            partner_id=partner_id,
            color_scheme=settings.DEFAULT_COLOR_SCHEME,
            profile_image=profile_image,
            ip_restriction=ip_restriction,
        )
        profile.save()
        return user

    @staticmethod
    def get_background_images_list(bucket_name):
        client = boto3.client("s3", aws_access_key_id=settings.AWS_ACCESS_KEY, aws_secret_access_key=settings.AWS_SECRET)
        response = client.list_objects(Bucket=bucket_name)
        bg_images_list = response.get("Contents", [])
        return bg_images_list
