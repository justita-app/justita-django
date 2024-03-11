from django.shortcuts import render , redirect , HttpResponse
from django.contrib import messages
from django.http import JsonResponse , HttpResponseNotFound
from social.models import OnlineCounseling
from django.conf import settings
from social.forms import CounselingSelectLawyerForm
from django.contrib.auth.decorators import login_required
from social.utils import day_to_string_persian , customize_datetime_format , send_online_counseilng_payment_verified
from social.payment import send_request , verify_paument
from social.models import OnlineCounselingRoom
from lawyers.models import Lawyer


lawyer_pictures = {
    'Alireza_Atashzaran' : '/media/team/Alireza_atashzaran.webp',
    'Mohammad_Nobari' : '/media/team/Mohammad_nobari.webp',
    'Arghavan_Mansuri' : '/media/team/Arghavan_mansuri.webp',
    'Atmish_Jahanshahi' : '/media/team/Atmish_Jahanshahi.webp',
    'Niloofar_Shahab' : '/media/team/niloofar_shahab.webp',
    'None' : '/media/team/justita-team.png'
}


def OnlineCounselingView(request):

    if request.user.is_authenticated :
        if OnlineCounseling.objects.filter(client=request.user , payment_status = 'undone').exists() :
            order = OnlineCounseling.objects.filter(client=request.user , payment_status='undone').last()
        else :

            order = OnlineCounseling(client=request.user)
    else :
            order = OnlineCounseling()

    order.save()
    
    return redirect('online-counseling:select-lawyer' , identity=order.identity)


def OnlineCounselingSelectLawyerView(request, identity):
    form = CounselingSelectLawyerForm()
    if not OnlineCounseling.objects.filter(identity=identity , payment_status='undone').exists():
        return HttpResponseNotFound("چنین درخواستی در سایت ثبت نشده است")

    lawyers = Lawyer.objects.filter(verified=True).all()
    if request.method == 'POST' :
        form = CounselingSelectLawyerForm(request.POST)
        if form.is_valid():
            online_counseling_object = OnlineCounseling.objects.get(identity=identity)
            lawyer = form.cleaned_data.get('lawyer_name')
            online_counseling_object.lawyer = lawyer
            online_counseling_object.save()
            return redirect('online-counseling:chat-preview' , identity=identity)

        else :
            messages.error(request , form.errors)
    
    args = {
        'form' : form,
        'selected_lawyer' : OnlineCounseling.objects.get(identity=identity).lawyer,
        'price_from' : int(settings.PRICING.get('online')),
        'lawyers' : lawyers,
    }

    return render(request , 'online-counseling/select-lawyer.html' , args)


def OnlineCounselingChatPreviewView(request , identity) :
    if not OnlineCounseling.objects.filter(identity=identity , payment_status='undone').exists():
        return HttpResponseNotFound("چنین درخواستی در سایت ثبت نشده است")

    online_counseling_object = OnlineCounseling.objects.get(identity=identity)
    args = {
        'identity' : identity,
        'lawyer' : online_counseling_object.get_lawyer_display(),
        'lawyer_profile' : lawyer_pictures.get(online_counseling_object.lawyer , '/media/team/default.png'),
        'created_time' : customize_datetime_format(online_counseling_object.created_at)['time'],
        'payment_aount' : online_counseling_object.get_price(),
    }

    return render(request , 'online-counseling/chat-preview.html' , args)


@login_required
def OnlineCounselingPaymentStartView(request , identity) :
    if not OnlineCounseling.objects.filter(identity=identity , payment_status='undone').exists():
        return HttpResponseNotFound("چنین درخواستی در سایت ثبت نشده است")

    online_counseling_object = OnlineCounseling.objects.get(identity=identity)
    if not online_counseling_object.client :
        online_counseling_object.client = request.user
        online_counseling_object.save()

    price = online_counseling_object.get_price()
    callback_url = settings.HOSTADDRESS + '/social/online-counseling/verify-payment'
    response = send_request(price , 'درخواست مشاوره آنلاین' , callback_url)
    
    if response.get('status') :
        online_counseling_object.payment_id = response.get('authority')
        online_counseling_object.amount_paid = price
        online_counseling_object.save()
        return redirect(response.get('url'))

    return HttpResponse("<h1>خطایی رخ داد لطفا بعدا تلاش کنید</h1>")
    

def OnlineCounselingPaymentVerifyView(request) :
    authority = request.GET.get('Authority', '')
    if not OnlineCounseling.objects.filter(payment_id=authority).exists():
        return HttpResponse("<h1>چنین تراکنشی در سایت وجود ندارد</h1>")

    online_counseling_object = OnlineCounseling.objects.get(payment_id=authority)

    response = verify_paument(amount=online_counseling_object.amount_paid , authority=authority)

    if response.get('status') :
        online_counseling_object.payment_status = 'ok'
        online_counseling_object.ref_id = response.get('ref_id')
        online_counseling_object.save()

        if not OnlineCounselingRoom.objects.filter(online_counseling=online_counseling_object).exists():

            online_counseling_room = OnlineCounselingRoom(online_counseling=online_counseling_object , status='open')
            online_counseling_room.save()
            # send message to user
            phone_number = online_counseling_object.client.username
            lawyer = online_counseling_object.get_lawyer_display()
            name = online_counseling_object.client.get_full_name()

            send_online_counseilng_payment_verified(phone_number=phone_number , lawyer=lawyer , name=name)

        else :
            online_counseling_room = OnlineCounselingRoom.objects.get(online_counseling=online_counseling_object)
            
        args = {
            'identity' : online_counseling_room.identity
        }
        return render(request , 'online-counseling/done.html' , args)

    else :
        online_counseling_object.payment_status = 'failed'
        online_counseling_object.save()
        return render(request , 'online-counseling/failed.html')

