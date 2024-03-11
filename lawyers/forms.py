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

            if not self.cleaned_data['licence_type'] in ['وکیل پایه یک کانون وکلای دادگستری', 'وکیل پایه یک مرکز وکلای قوه‌قضاییه',
                                                         'وکیل پایه دو مرکز وکلای قوه‌قضاییه', 'کارآموز وکالت کانون وکلای دادگستری',
                                                         'کاراموز وکالت مرکز وکلای قوه‌قضاییه', 'کارشناس رسمی دادگستری', 'کارشناس حقوقی']:
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
