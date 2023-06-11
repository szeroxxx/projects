# from dateutil import tz
from base.util import Util
from django.contrib.auth.models import Group, User
from finance_api.rest_config import FilePath
from numpy import source
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from accounts.models import UserProfile


class RolePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["id","name"]

class UserRoleSerializer(serializers.ModelSerializer):
    key_value = serializers.IntegerField(source="id")
    display_value = serializers.CharField(source="name")
    class Meta:
        model = Group
        fields = ("key_value","display_value")
class UpdateUserSerializer(serializers.ModelSerializer):
    role_ids = serializers.ListField(read_only=True)
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name","is_active","role_ids"]
class UserSerializer(serializers.ModelSerializer):
    role_ids = serializers.ListField(read_only=True)
    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=False)
    # user_id = 
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name","is_active","role_ids","password","password2"]
        
    def validate(self, attrs):
        if "password" in attrs and "password2" in  attrs:
            if attrs["password"] != attrs["password2"]:
                raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    def create(self, validated_data):
        user = User.objects.create(
        username=validated_data['username'],
        email=validated_data['email'],
        first_name=validated_data['first_name'],
        last_name=validated_data['last_name']
    )
        user.set_password(validated_data['password'])
        user.save()
        return user
class UserProfileSerializer(serializers.ModelSerializer):
    user__first_name = serializers.CharField(read_only=True)
    user__last_name = serializers.CharField(read_only=True)
    user__email = serializers.CharField(read_only=True)
    profile_image = FilePath(required=False)
    user = UserSerializer(required=False)
    class Meta:
        model = UserProfile
        fields = ["user","user_id","user__first_name","user__last_name","user__email","profile_image","theme","display_row","default_page"]

    def update(self,instance,validated_data):
        user_data = validated_data.pop("user")
        user_serializer = self.fields['user']
        user_data.pop("is_active")
        user_serializer.update(instance.user,user_data)
        # if "profile_image" in validated_data:
        #     Util.delete_old_file(instance.profile_image.path)
        return super().update(instance, validated_data)



class UserListSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user__first_name')
    last_name = serializers.CharField(source='user__last_name')
    username = serializers.CharField(source='user__username')
    # usergroup = serializers.CharField(source='user__usergroup__group__name')
    usergroup = serializers.CharField()
    id = serializers.IntegerField(source="user_id")


    class Meta:
        model = UserProfile
        fields = ["id","first_name", "last_name", "username","usergroup"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if  not "None" in representation["usergroup"]:
            representation["usergroup"] = representation["usergroup"].replace("]","").replace("[","").replace("'",'')
        else:
            representation["usergroup"] = None
        return representation