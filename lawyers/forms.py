from django.forms import ModelForm
from django.core.exceptions import ValidationError
from lawyers.models import Lawyer, ConsultationPrice


class LawyerVerificationForm(ModelForm) :
    class Meta:
        model = Lawyer
        fields = ['national_code', 'id_card_image', 'city_working', 'licence_type',
                  'licence_number', 'licence_image', 'last_degree', 'office_address']

        def clean(self, *args, **kwargs):
            super().clean(*args, **kwargs)

            if not self.cleaned_data['licence_type'] in ['attorneys-icbar-first', 'attorneys-judiciary-first',
                                                         'attorneys-judiciary-second', 'trainee-icbar', 'Trainee-judiciary'
                                                         'judiciary_official_expert', 'legal-expert']:
                self.cleaned_data['licence_type'] = None

class LawyerPersonalForm(ModelForm) :
    class Meta:
        model = Lawyer
        fields = ['first_name', 'last_name', 'username', 'city',
                  'address', 'bio', 'gender']
    
    def clean(self, *args, **kwargs):
        super().clean(*args, **kwargs)

        if not self.cleaned_data['gender'] in ['M', 'F']:
            self.cleaned_data['gender'] = None


class LawyerConsultationPriceForm(ModelForm) :
    class Meta:
        model = ConsultationPrice
        fields = ['ten_min_price', 'fifteen_min_price', 'thirty_min_price', 'online_price']


class LawyerUpdateForm(ModelForm) :
    class Meta:
        model = Lawyer
        fields = ['IBAN_number', 'profile_image']
