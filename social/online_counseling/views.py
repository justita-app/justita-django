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
from lawyers.models import Lawyer, ConsultationPrice , Comment
from django.db.models import Avg


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

    lawyers = Lawyer.objects.filter(verified=True).all().order_by('office_address')
    for lawyer in lawyers:
        lawyer.comment_count = Comment.objects.filter(lawyer=lawyer).count()
        avg_score = Comment.objects.filter(lawyer=lawyer).aggregate(avg_score=Avg('score'))
        if avg_score['avg_score'] is not None:
            lawyer.avg_score = avg_score['avg_score']/2
        else:
            lawyer.avg_score=5.0
    
    consultation_prices = []
    for lawyer in lawyers:
        if ConsultationPrice.objects.filter(lawyer=lawyer).exists():
            consultation_price = ConsultationPrice.objects.filter(lawyer=lawyer).first().online_price
        else:
            consultation_price = None

        consultation_prices.append(consultation_price)

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
    
    lawyers = list(zip(lawyers, consultation_prices))
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

    for lawyer in Lawyer.objects.filter(verified=True).all():
        if lawyer.profile_image:
            lawyer_pictures[f'{lawyer.pk}'] = lawyer.profile_image.url
        else:
            lawyer_pictures[f'{lawyer.pk}'] = '/media/team/default.png'

    online_counseling_object = OnlineCounseling.objects.get(identity=identity)
    lawyer_license = Lawyer.objects.get(id = online_counseling_object.lawyer).licence_type
    lawyerf = Lawyer.objects.get(id = online_counseling_object.lawyer).first_name
    lawyerl = Lawyer.objects.get(id = online_counseling_object.lawyer).last_name
    args = {
        'identity' : identity,
        'lawyer' : online_counseling_object.get_lawyer_display(),
        'lawyer_profile' : lawyer_pictures.get(online_counseling_object.lawyer , '/media/team/default.png'),
        'created_time' : customize_datetime_format(online_counseling_object.created_at)['time'],
        'payment_aount' : online_counseling_object.get_price(),
        'lawyer_license':lawyer_license,
        'lawyerf' : lawyerf,
        'lawyerl': lawyerl
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
    lawyer_num = Lawyer.objects.get(id=online_counseling_object.lawyer).username
    
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

            send_online_counseilng_payment_verified(phone_number=phone_number , lawyer=lawyer , name=name , lawyer_num=lawyer_num)

        else :
            online_counseling_room = OnlineCounselingRoom.objects.get(online_counseling=online_counseling_object)
            
        args = {
            'identity' : online_counseling_room.identity,
           
        }
        
        return render(request , 'online-counseling/done.html' , args)

    else :
        online_counseling_object.payment_status = 'failed'
        online_counseling_object.save()
        return render(request , 'online-counseling/failed.html')

