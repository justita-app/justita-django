from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from accounts.models import User
from PIL import Image


class Lawyer(User):
    agreement_signed = models.BooleanField(default=False)
    online = models.BooleanField(default=False)

    verified = models.BooleanField(default=False)
    balance = models.IntegerField(default=0)

    IBAN_number = models.CharField(max_length=50, null=True, blank=True)
    licence_number = models.CharField(max_length=6, null=True, blank=True)
    introduction_code = models.CharField(max_length=64, default=None, null=True)
    subset_introduction_code = models.CharField(max_length=64, default=None, null=True, blank=True) # The introduction code that lawyer use it when registration
    profile_image = models.ImageField(upload_to="profile_images", null=True, blank=True)
    licence_image = models.ImageField(upload_to="licence_images", null=True, blank=True)
    gender = models.CharField(max_length=1, null=True, blank=True) # M  for Male, F for Female
    bio = models.CharField(max_length=512, null=True, blank=True)
    work_address = models.CharField(max_length=256, null=True, blank=True)
    office_address = models.CharField(max_length=256, null=True, blank=True)
    city_working = models.CharField(max_length=64 , default="" , blank=True)
    address = models.CharField(max_length=256, null=True, blank=True)
    national_code = models.CharField(max_length=20, null=True, blank=True)
    id_card_image = models.ImageField(upload_to="id_card_images", null=True, blank=True)
    licence_type = models.CharField(max_length=100, null=True, blank=True)
    last_degree = models.CharField(max_length=100, null=True, blank=True)

    def get_name(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = _("lawyer")
        verbose_name_plural = _("lawyers")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.profile_image:
            img = Image.open(self.profile_image.path) # Open image

            # resize image
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size) # Resize image
                img.save(self.profile_image.path) # Save it again and override the larger image


class ConsultationPrice(models.Model):
    lawyer = models.OneToOneField(Lawyer, on_delete=models.CASCADE, null=False)
    ten_min_price = models.IntegerField(default=15, blank=True, null=True)
    fifteen_min_price = models.IntegerField(default=30, blank=True, null=True)
    thirty_min_price = models.IntegerField(default=45, blank=True, null=True)
    online_price = models.IntegerField(default=100, blank=True, null=True)


class Comment(models.Model):
    lawyer = models.ForeignKey(Lawyer, on_delete=models.CASCADE, null=False)
    order_id = models.CharField(max_length=64 , default="" , blank=True)
    score = models.IntegerField() # 1 to 10
    description = models.CharField(max_length=512, null=True, blank=True)


class Transaction(models.Model):
    lawyer = models.ForeignKey(Lawyer, on_delete=models.CASCADE, null=False)
    amount = models.IntegerField()
    IBAN_number = models.CharField(max_length=50, null=True, blank=True)
    transaction_date = models.DateTimeField(default=timezone.now)


class Warning(models.Model):
    lawyer = models.ForeignKey(Lawyer, on_delete=models.CASCADE, null=False)
    level = models.IntegerField() # 1 to 4
    description = models.CharField(max_length=512, null=True, blank=True)
