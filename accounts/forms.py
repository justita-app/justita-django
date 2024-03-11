from dataclasses import fields
from django import forms
from django.forms import HiddenInput, ModelForm , Form
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.crypto import get_random_string
from accounts.validators import phonenumber_validator , validate_code
from accounts.models import SmsVerificationCode
from lawyers.models import Lawyer
import re


class SmsVerificationForm(Form):
    phone_number = forms.CharField(label= 'شماره تلفن', min_length=10 , max_length=14,required=True)
    code = forms.CharField(label='کد تایید', min_length=4 , max_length=4,required=True)

    def clean(self):
        cleaned_data = super().clean()
        phone_number = cleaned_data.get("phone_number")
        code = cleaned_data.get("code")

        if phone_number and code:
            sms_code = SmsVerificationCode.objects.filter(phone_number=phone_number , code=code).order_by('-created_at').first()
            if not sms_code :
                raise ValidationError("کد تایید اشتباه است.")
            if not sms_code or sms_code.is_expired():
                raise ValidationError("کد تایید متقضی شده است.")
        
        return cleaned_data


class UserLoginForm(Form):
    phone_number = forms.CharField(label='Phone Number', max_length=13, validators=[phonenumber_validator])

    def clean(self):
        cleaned_data = super().clean()
        phone_number = cleaned_data.get("phone_number", '')

        if not phone_number:
            return cleaned_data

        match = re.search(r'(9\d{9})$', phone_number)

        if match:
            cleaned_phone_number = '0' + match.group(1)
            self.cleaned_data['phone_number'] = cleaned_phone_number

            user = get_user_model().objects.filter(username=cleaned_phone_number)

            if user.exists() and not user.first().is_active:
                raise ValidationError("اکانت شما غیر فعال شده است.")

        return cleaned_data


class LawyerLoginForm(UserLoginForm):
    pass


class RegisterForm(ModelForm):
    
    class Meta:
        model = get_user_model()
        fields = ['username', 'first_name', 'last_name','city','introduction_method']

        labels = {
            'username' : 'شماره تلفن' ,
            'first_name': 'نام',
            'last_name': 'نام خانوادگی',
            'city': 'شهر',
            'introduction_method': 'نحوه آشنایی',
        }
        error_messages = {
            'first_name': {
                'required': 'وارد کردن نام اجباری است',
            },
            'last_name': {
                'required': 'وارد کردن نام خانوادگی اجباری است',
            },
            'introduction_method': {
                'required': 'وارد کردن نحوه آشنایی با جاستیتا اجباری است',
            },
        }

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)

        # Make the 'username' and 'city' fields not required
        self.fields['username'].required = False
        self.fields['city'].required = False


class LawyerRegisterForm(ModelForm):
    class Meta:
        model = Lawyer
        fields = ['username', 'first_name', 'last_name', 'city', 'introduction_method', 'subset_introduction_code', 'agreement_signed']

        labels = {
            'username' : 'شماره تلفن' ,
            'first_name': 'نام',
            'last_name': 'نام خانوادگی',
            'city': 'شهر',
            'introduction_method': 'نحوه آشنایی',
            'subset_introduction_code': 'کد معرفی',
        }
        error_messages = {
            'first_name': {
                'required': 'وارد کردن نام اجباری است',
            },
            'last_name': {
                'required': 'وارد کردن نام خانوادگی اجباری است',
            },
        }

    def __init__(self, *args, **kwargs):
        super(LawyerRegisterForm, self).__init__(*args, **kwargs)

        self.instance.introduction_code = get_random_string(length=6) # Not safe, change it later

        self.fields['agreement_signed'].required = True

        # Make the 'username' and 'city' and 'subset_introduction_code' fields not required
        self.fields['username'].required = False
        self.fields['city'].required = False
        self.fields['subset_introduction_code'].required = False


class ChangeInformationForm(ModelForm) :
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name','city']

        error_messages = {
            'first_name': {
                'required': 'وارد کردن نام اجباری است',
            },
            'last_name': {
                'required': 'وارد کردن نام خانوادگی اجباری است',
            }
        }

    def __init__(self, *args, **kwargs):
        super(ChangeInformationForm, self).__init__(*args, **kwargs)

        self.fields['city'].required = False

    def clean(self):
        super(ChangeInformationForm, self).clean()

        # Check if first name is empty
        if not self.cleaned_data['first_name']:
            raise ValidationError({'first_name': 'وارد کردن نام اجباری است'})

        # Check if last name is empty
        if not self.cleaned_data['last_name']:
            raise ValidationError({'last_name': 'وارد کردن نام خانوادگی اجباری است'})

        return self.cleaned_data


class changePhoneNumberForm(Form):
    phone_number = forms.CharField(label='Phone Number', max_length=13, validators=[phonenumber_validator])

    def clean(self):
        cleaned_data = super().clean()
        phone_number = cleaned_data.get("phone_number", '')

        if not phone_number:
            return cleaned_data

        match = re.search(r'(9\d{9})$', phone_number)

        if match:
            cleaned_phone_number = '0' + match.group(1)
            self.cleaned_data['phone_number'] = cleaned_phone_number

            user = get_user_model().objects.filter(username=cleaned_phone_number)

            if user.exists():
                raise ValidationError("این شماره همراه در حال حاضر در سایت ثبت نام شده است.")

        return cleaned_data