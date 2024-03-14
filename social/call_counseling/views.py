from django.shortcuts import render , redirect , HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse , HttpResponseNotFound
from social.models import CallCounseling , CallCounselingFiles
from social.forms import (CounselingSelectLawyerForm , CallCounselingSubjectTimeForm ,
    CallCounselingDescriptionTimeForm , CallCounselingFileUploadForm)
from social.utils import day_to_string_persian , customize_datetime_format , send_call_counseilng_payment_verified
from django.conf import settings
from social.payment import send_request , verify_paument
from django.core import serializers
from django.utils import timezone
import json , datetime
from lawyers.models import Lawyer , ConsultationPrice


lawyer_pictures = {
    'Alireza_Atashzaran' : '/media/team/Alireza_atashzaran.webp',
    'Mohammad_Nobari' : '/media/team/Mohammad_nobari.webp',
    'Arghavan_Mansuri' : '/media/team/Arghavan_mansuri.webp',
    'Atmish_Jahanshahi' : '/media/team/Atmish_Jahanshahi.webp',
    'Niloofar_Shahab' : '/media/team/niloofar_shahab.webp',
    'None' : '/media/team/justita-team.png'
}


def CallCounselingView(request):
    if request.user.is_authenticated :
        if CallCounseling.objects.filter(client=request.user , payment_status='undone').exists():
            order = CallCounseling.objects.filter(client=request.user , payment_status = 'undone').last()
        else :
            order = CallCounseling(client=request.user)
            order.save()

    else :
        order = CallCounseling()
        order.save()
    
    return redirect('call-counseling:select-lawyer' , identity=order.identity)


def CallCounselingSelectLawyerView(request, identity):
    form = CounselingSelectLawyerForm()
    if not CallCounseling.objects.filter(identity=identity , payment_status='undone').exists():
        return HttpResponseNotFound("چنین درخواستی در سایت ثبت نشده است")

    lawyers = Lawyer.objects.filter(verified=True).all()
    if request.method == 'POST' :
        form = CounselingSelectLawyerForm(request.POST)
        if form.is_valid():
            call_counseling_object = CallCounseling.objects.get(identity=identity)
            lawyer = form.cleaned_data.get('lawyer_name')
            call_counseling_object.lawyer = lawyer
            call_counseling_object.save()
            return redirect('call-counseling:subject-time' , identity=identity)

        else :
            messages.error(request , form.errors)
    
    args = {
        'form' : form,
        'selected_lawyer' : CallCounseling.objects.get(identity=identity).lawyer,
        'price_from' : int(settings.PRICING.get('20')),
        'lawyers' : lawyers,
    }

    return render(request , 'call-counseling/select-lawyer.html' , args)


def CallCounselingSubjectTimeView(request , identity) :
    if not CallCounseling.objects.filter(identity=identity , payment_status='undone').exists():
        return HttpResponseNotFound("چنین درخواستی در سایت ثبت نشده است")

    form = CallCounselingSubjectTimeForm()


    if request.method == "POST" :
        form = CallCounselingSubjectTimeForm(request.POST)
        if form.is_valid():
            time = form.cleaned_data.get("time")
            subject = form.cleaned_data.get("subject")
            call_counseling = CallCounseling.objects.get(identity=identity)
            call_counseling.call_time = time
            call_counseling.subject = subject
            call_counseling.save()
            return redirect('call-counseling:description' , identity=identity)
        else :
            messages.error(request , form.errors)
        
    call_counseling_object = CallCounseling.objects.get(identity=identity)
    consultation_price = ConsultationPrice.objects.get(lawyer=call_counseling_object.lawyer)
    args = {
        'form' : form,
        'identity' : identity,
        'subject' : call_counseling_object.subject,
        'time' : call_counseling_object.call_time,
        'price20' : int(int(settings.PRICING.get('20') )/1000),
        'price30' : int(int(settings.PRICING.get('30') )/1000),
        'price45' : int(int(settings.PRICING.get('45') )/1000),
        
        'ten_min_price' : int(int(consultation_price.ten_min_price) / 1000),
        'fifteen_min_price' : int(int(consultation_price.fifteen_min_price) / 1000),
        'thirty_min_price' : int(int(consultation_price.thirty_min_price) / 1000),
        'online_price' : int(int(consultation_price.online_price) / 1000),
    }
    return render(request , 'call-counseling/subject-time.html' , args)


def CallCounselingDescriptioinView(request , identity) :
    if not CallCounseling.objects.filter(identity=identity , payment_status='undone').exists():
        return HttpResponseNotFound("چنین درخواستی در سایت ثبت نشده است")

    form = CallCounselingDescriptionTimeForm()

    if request.method == "POST" :
        form = CallCounselingDescriptionTimeForm(request.POST)

        if form.is_valid():
            time = form.cleaned_data.get("time")
            date = form.cleaned_data.get("date")
            description = form.cleaned_data.get("description")

            call_counseling = CallCounseling.objects.get(identity=identity)
            call_counseling.Reservation_time = time
            call_counseling.Reservation_day = date
            call_counseling.description = description
            call_counseling.save()

            return redirect('call-counseling:order-detail' , identity=identity)
        else :
            messages.error(request , form.errors)
    
    call_counseling_object = CallCounseling.objects.get(identity=identity)
    reservation_time = call_counseling_object.Reservation_time.strftime('%H:%M:%S') if call_counseling_object.Reservation_time else None
    reservation_day = call_counseling_object.Reservation_day if call_counseling_object.Reservation_day else datetime.date.today()
    date_string = day_to_string_persian(reservation_day)

    args = {
        'form' : form,
        'identity' : identity,
        'description' : call_counseling_object.description ,
        'time' : reservation_time ,
        'day' : date_string ,
    }
    return render(request , 'call-counseling/description.html' , args)


def CallCounselingUploadFileView(request , identity):
    if request.method == 'POST':
        form = CallCounselingFileUploadForm(request.POST, request.FILES)

        if not CallCounseling.objects.filter(identity=identity , payment_status='undone').exists():
            return JsonResponse({{'success': False, 'errors': 'درخواستی با این شناسه ثبت نشده است.'}})

        if form.is_valid():
            uploaded_file = form.cleaned_data['file']
            
            call_counseling = CallCounseling.objects.get(identity=identity)
            new_instance = CallCounselingFiles(call_counseling=call_counseling , file=uploaded_file)
            new_instance.save()

            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        return JsonResponse({'success': False, 'errors': 'متد پشتیبانی نمیشود.'})


def CallCounselingDetailView(request , identity):

    if not CallCounseling.objects.filter(identity=identity , payment_status='undone').exists():
        return HttpResponseNotFound("چنین درخواستی در سایت ثبت نشده است")

    for lawyer in Lawyer.objects.filter(verified=True).all():
        if lawyer.profile_image:
            lawyer_pictures[f'{lawyer.pk}'] = lawyer.profile_image.url
        else:
            lawyer_pictures[f'{lawyer.pk}'] = '/media/team/default.png'

    call_counseling_object = CallCounseling.objects.get(identity=identity)
    reservation_day = call_counseling_object.Reservation_day
    date_string = day_to_string_persian(reservation_day)
    client_name =  call_counseling_object.client.get_full_name() if call_counseling_object.client else ''
    args = {
        'identity' : call_counseling_object.identity,
        'lawyer_picture' : lawyer_pictures.get(call_counseling_object.lawyer , '/media/team/default.png'),
        'subject' : call_counseling_object.subject,
        'lawyer' : call_counseling_object.get_lawyer_display() ,
        'client' : client_name,
        'reservation_day' : date_string ,
        'reservation_time' : call_counseling_object.Reservation_time.strftime('%H:%M:%S') ,
        'call_time' : call_counseling_object.call_time,
        'price' : call_counseling_object.get_price()
    }

    return render(request , 'call-counseling/order-details.html' , args)


@login_required
def CallCounselingPaymentStartView(request , identity) :
    if not CallCounseling.objects.filter(identity=identity , payment_status='undone').exists():
        return HttpResponseNotFound("چنین درخواستی در سایت ثبت نشده است")

    call_counseling_object = CallCounseling.objects.get(identity=identity)
    if not call_counseling_object.client :
        call_counseling_object.client = request.user
        call_counseling_object.save()

    price = call_counseling_object.get_price()
    callback_url = settings.HOSTADDRESS + '/social/call-counseling/verify-payment'
    response = send_request(price , 'درخواست مشاوره تلفنی' , callback_url)
    
    if response.get('status') :
        call_counseling_object.payment_id = response.get('authority')
        call_counseling_object.amount_paid = price
        call_counseling_object.save()
        return redirect(response.get('url'))

    return HttpResponse("<h1>خطایی رخ داد لطفا بعدا تلاش کنید</h1>")
    

def CallCounselingPaymentVerifyView(request) :
    authority = request.GET.get('Authority', '')
    if not CallCounseling.objects.filter(payment_id=authority).exists():
        return HttpResponse("<h1>چنین تراکنشی در سایت وجود ندارد</h1>")

    call_counseling_object = CallCounseling.objects.get(payment_id=authority)

    response = verify_paument(amount=call_counseling_object.amount_paid , authority=authority)

    args = {
        'time' : call_counseling_object.Reservation_time.strftime('%H:%M:%S'),
        'day' : day_to_string_persian(call_counseling_object.Reservation_day),
    }

    if response.get('status') :
        if response.get('code') == 100 :
            call_counseling_object.payment_status = 'ok'
            call_counseling_object.ref_id = response.get('ref_id')
            call_counseling_object.save()
            # send message to user
            phone_number = call_counseling_object.client.username
            name = call_counseling_object.client.get_full_name()
            date = day_to_string_persian(call_counseling_object.Reservation_day)
            time = call_counseling_object.Reservation_time.strftime("%H:%M:%S")

            send_call_counseilng_payment_verified(phone_number=phone_number, name=name , date=date , time=time)

        return render(request , 'call-counseling/done.html' , args)
    else :
        call_counseling_object.payment_status = 'failed'
        call_counseling_object.save()
        return render(request , 'call-counseling/failed.html' , args)

