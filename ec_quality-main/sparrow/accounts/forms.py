from django import forms
from django.core.files.images import get_image_dimensions

from .models import Group, User


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "password"]


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ["name"]


display_row = [
    ("10", "10"),
    ("25", "25"),
    ("50", "50"),
    ("100", "100"),
    ("200", "200"),
    ("300", "300"),
    ("400", "400"),
    ("500", "500"),
]
menu = [(True, "Launcher menu"), (False, "Left menu")]


class ProfileForm(forms.Form):
    first_name = forms.CharField(label="First Name", max_length=100, required=True)
    last_name = forms.CharField(label="Last Name", max_length=100, required=True)
    email = forms.EmailField(label="Email", required=False, widget=forms.TextInput(attrs={"readonly": "readonly"}))
    password = forms.CharField(label="New Password", widget=forms.PasswordInput, max_length=30, required=False)
    confirm_password = forms.CharField(label="Confirm Password", widget=forms.PasswordInput, max_length=30, required=False)
    avatar = forms.FileField(label="Display picture", help_text="max. 1 megabytes", required=False)
    display_row = forms.IntegerField(label="Display row", widget=forms.Select(choices=display_row))
    default_page = forms.CharField(
        label="Default page",
        max_length=250,
        required=False,
        help_text="This will be your default page after login. Input page URL from address bar for the page you want to load. (e.g. http://servername/b/#/purchasing/dashboard/)",
    )
    menu_launcher = forms.BooleanField(label="Menu navigation", widget=forms.RadioSelect(choices=menu, attrs={"id": "menu_launcher"}), initial=True, required=False)

    def clean_avatar(self):
        avatar = self.cleaned_data["avatar"]

        try:
            w, h = get_image_dimensions(avatar)

            # validate dimensions
            max_width = max_height = 1000
            if w > max_width or h > max_height:
                raise forms.ValidationError("Please use an image that is %s x %s pixels or smaller." % (max_width, max_height))

            # validate content type
            main, sub = avatar.content_type.split("/")
            if not (main == "image" and sub in ["jpeg", "pjpeg", "gif", "png"]):
                raise forms.ValidationError("Please use a JPEG, GIF or PNG image.")

            # validate file size
            if len(avatar) > (1000 * 1024):
                raise forms.ValidationError("Avatar file size may not exceed 1024k.")
            return avatar

        except (AttributeError, TypeError):
            """
            Handles case when we are updating the user profile
            and do not supply a new avatar
            """
            pass
            return avatar


class CreateUserForm(forms.Form):
    first_name = forms.CharField(label="First Name", max_length=100, required=True, widget=forms.TextInput(attrs={"required": ""}))
    last_name = forms.CharField(label="Last Name", max_length=100, required=True, widget=forms.TextInput(attrs={"required": ""}))
    email = forms.EmailField(label="Email", required=False, widget=forms.TextInput(attrs={"readonly": "readonly"}))
    password = forms.CharField(label="New Password", widget=forms.PasswordInput, max_length=30, required=False)
    confirm_password = forms.CharField(label="Confirm Password", widget=forms.PasswordInput, max_length=30, required=False)


class PasswrecoveryForm(forms.Form):
    email = forms.EmailField(
        label="Enter your email address and we will send you a link to reset your password.",
        required=True,
        max_length=200,
        widget=forms.EmailInput(attrs={"placeholder": "Email"}),
    )


class ResetPwdForm(forms.Form):
    password = forms.CharField(label="New Password", widget=forms.PasswordInput, min_length=6, max_length=30, required=False)
    confirm_password = forms.CharField(label="Confirm Password", widget=forms.PasswordInput, min_length=6, max_length=30, required=False)

    def clean(self):
        cleaned_data = super(ResetPwdForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("password and confirm_password does not match")


# class UserRoleForm(forms.ModelForm):

#     class Meta:
#         model = UserRole
#         fields = [ 'name', 'desc']
