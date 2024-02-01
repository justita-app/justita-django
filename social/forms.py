from dataclasses import fields
from django import forms
from django.core.exceptions import ValidationError
from social import jalali
import re
import datetime

class CounselingSelectLawyerForm(forms.Form) :
    lawyer_name = forms.CharField(max_length=32 , required=True)

    def clean(self):
        cleaned_data = super().clean()
        lawyer_name = cleaned_data.get("lawyer_name")
        lawyer_choices = [
            "Mohammad_Nobari",
            "Alireza_Atashzaran",
            "Arghavan_Mansuri",
            "Atmish_Jahanshahi",
            "Niloofar_Shahab",
        ]
        if not lawyer_name in lawyer_choices:
            raise ValidationError("وکیل مورد نظر یافت نشد ، لطفا وکیل را به درستی انتخاب کنید؛")
        
        return cleaned_data


class CallCounselingSubjectTimeForm(forms.Form) :
    subject = forms.CharField(max_length=32 , required=True)
    time = forms.CharField(max_length=3 , required=True)

    def clean(self):
        cleaned_data = super().clean()
        subject = cleaned_data.get("subject")
        time = cleaned_data.get("time")
        
        time_choices = [
            "20",
            "30",
            "45",
        ]
        if not time in time_choices:
            raise ValidationError("زمان انتخاب شده معتبر نیست")
        
        return cleaned_data


class CallCounselingDescriptionTimeForm(forms.Form) :
    date = forms.CharField(max_length=32 , required=True , error_messages={'required': 'وارد کردن تاریخ الزامی است'})
    time = forms.TimeField(required=True , error_messages={'required': 'وارد کردن زمان الزامی است'})
    description = forms.CharField(widget=forms.Textarea() , required=False)

    def clean(self):
        cleaned_data = super().clean()

        date = cleaned_data.get("date" , '')
        time = cleaned_data.get("time" , '')
        description = cleaned_data.get("description")

        if not re.search('^\d{4}\/\d{2}\/\d{2}$' , date) :
            raise ValidationError("تاریخ وارد شده اشتباه است.")

        date = date.split('/')
        j_date = jalali.Persian(date[0] , date[1] , date[2]).gregorian_datetime()

        if j_date < datetime.date.today() :
            raise ValidationError("تاریخ وارد شده نامعتبر است لطفا یک تاریخ معتبر انتخاب کنید.")
        cleaned_data['date'] = j_date

        return cleaned_data


class CallCounselingFileUploadForm(forms.Form):
    file = forms.FileField()