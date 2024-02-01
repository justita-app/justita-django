from django.shortcuts import render , redirect
from django.contrib.auth import get_user_model , logout , login , authenticate
from django.contrib import messages
from .forms import UserLoginForm , RegisterForm , SmsVerificationForm , ChangeInformationForm , changePhoneNumberForm
from .utils import random_digit , send_verification_code, check_phonenumber
from accounts.models import SmsVerificationCode , UserRegistrationIdentity
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse


def SmsVerifyView(request, phone_number ,*args, **kwargs):
    form = SmsVerificationForm()
    next_url = request.GET.get('next', None)
    if request.method == "GET":
        if not check_phonenumber(phone_number) :
            return redirect('accounts:login')

        # if there were some code and not expired return to page with last code time out else create a new code with 60 timeout
        if SmsVerificationCode.objects.filter(phone_number=phone_number).exists():
            last_code = SmsVerificationCode.objects.filter(phone_number=phone_number).order_by('-created_at').first()
            if last_code.is_expired():
                send_verification_code(phone_number=phone_number)
                return render(request, 'sms-verify.html', {'phone_number': phone_number, 'timeout': 60})
            else:
                return render(request, 'sms-verify.html', {'phone_number': phone_number, 'timeout': last_code.timeout_time()})

        # send a sms if there was no sms code exist
        send_verification_code(phone_number=phone_number)
        return render(request, 'sms-verify.html', {'phone_number': phone_number, 'timeout': 60})

    elif request.method == "POST":
            form = SmsVerificationForm(request.POST)
            if form.is_valid():
                User = get_user_model()
                if not get_user_model().objects.filter(username=phone_number).exists():
                    user_identity = UserRegistrationIdentity(phone_number=phone_number)
                    user_identity.save()

                    redirect_url = f'{reverse("accounts:register", args=[user_identity.identity])}?next={next_url}' if next_url else f'{reverse("accounts:register", args=[user_identity.identity])}'
                    return redirect(redirect_url)

                user = get_user_model().objects.get(username=phone_number)
                login(request, user)

                redirect_url = request.GET.get('next', None) or reverse('base:home')
                return redirect(redirect_url)

    for field, errors in form.errors.items():
        for error in errors:
            messages.error(request, error)

    return render(request, "sms-verify.html", {'form': form, 'phone_number': phone_number, 'timeout': 0})


def LoginView(request ,*args, **kwargs):

    form = UserLoginForm()
    next_url = request.GET.get('next', None)
    if request.method == "POST":

        form = UserLoginForm(request.POST)

        if  form.is_valid() :
            phone_number = form.cleaned_data.get("phone_number")

            redirect_url = f'{reverse("accounts:sms-verify", args=[phone_number])}?next={next_url}' if next_url else f'{reverse("accounts:sms-verify", args=[phone_number])}'

            return redirect(redirect_url)
        else :
            messages.error(request , form.errors)

    args = {
        'form': form
    }

    return render(request , 'login.html' , args) 


def RegisterView(request , identity ,*args, **kwargs):
    form = RegisterForm()

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            identity_code = UserRegistrationIdentity.objects.filter(identity=identity).order_by('-created_at').first()
            if identity_code and identity_code.is_valid() :
                form.instance.username = identity_code.phone_number
                user = form.save()
                login(request, user)

                # Redirect the user to the specified 'next' parameter or the default home page
                redirect_url = request.GET.get('next', None) or reverse('base:home')
                return redirect(redirect_url)

            return redirect('accounts:login')
        else:
            messages.error(request, form.errors)

    args = {'form': form}
    return render(request, 'register.html', args)


def LogoutView(request):
    logout(request)
    return redirect('social:home')


@login_required
def AccountView(request) :
    user = request.user
    form = ChangeInformationForm(instance=user)
    
    if request.method == "POST" :
        form = ChangeInformationForm(request.POST ,instance=user)
        if form.is_valid() :
            form.save()
        else:
            messages.error(request , form.errors)

    args = {'form' : form}
    return render(request , 'account.html' , args)


@login_required
def ChangePhoneNumberView(request ,*args, **kwargs):
    user = request.user
    form = changePhoneNumberForm()

    if request.method == "POST":

        form = changePhoneNumberForm(request.POST)

        if  form.is_valid() :
            phone_number = form.cleaned_data.get("phone_number")

            return redirect("accounts:change-phonenumber_validation" , phone_number=phone_number)
        else :
            messages.error(request , form.errors)

    args = {
        'form': form
    }

    return render(request , 'get-phonenumber.html' , args)


@login_required
def ChangePhoneNumberVerificationView(request , phone_number):
    form = SmsVerificationForm()
    user = request.user
    if request.method == "GET":
        if not check_phonenumber(phone_number) :
            return redirect('accounts:change-phonenumber')

        if get_user_model().objects.filter(username=phone_number).exists():
            return redirect('accounts:change-phonenumber')

        # if there were some code and not expired return to page with last code time out else create a new code with 60 timeout
        if SmsVerificationCode.objects.filter(phone_number=phone_number).exists():
            last_code = SmsVerificationCode.objects.filter(phone_number=phone_number).order_by('-created_at').first()
            if last_code.is_expired():
                send_verification_code(phone_number=phone_number)
                return render(request, 'change-phonenumber_verify.html', {'phone_number': phone_number, 'timeout': 60})
            else:
                return render(request, 'change-phonenumber_verify.html', {'phone_number': phone_number, 'timeout': last_code.timeout_time()})

        # send a sms if there was no sms code exist
        send_verification_code(phone_number=phone_number)
        return render(request, 'change-phonenumber_verify.html', {'phone_number': phone_number, 'timeout': 60})

    elif request.method == "POST":
            form = SmsVerificationForm(request.POST)
            if form.is_valid():
                new_phoneNumber = form.cleaned_data.get("phone_number")
                user.username = new_phoneNumber 
                user.save()
                return redirect('accounts:home')
            else:
                messages.error(request , form.errors)

    for field, errors in form.errors.items():
        for error in errors:
            messages.error(request, error)

    return render(request, "change-phonenumber_verify.html", {'form': form, 'phone_number': phone_number, 'timeout': 0})