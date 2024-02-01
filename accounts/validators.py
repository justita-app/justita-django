from django.core.exceptions import ValidationError
import re

def phonenumber_validator(value):
    pattern = r'([0+]98|0)(9\d{9})$'

    if not re.match(pattern, value):
        raise ValidationError("شماره تلفن وارد شده صحیح نمی باشد.")


def validate_code(value):
    if not value.isdigit() or len(value) != 4:
        raise ValidationError('کد تایید باید یک عدد چهار رقمی باشد.')