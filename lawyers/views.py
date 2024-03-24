from django.shortcuts import render
from lawyers.forms import LawyerPersonalForm, LawyerVerificationForm, LawyerConsultationPriceForm, LawyerUpdateForm
from django.shortcuts import render , redirect
from django.contrib import messages
from django.http import HttpRequest, Http404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from lawyers.models import Lawyer, ConsultationPrice, Warning, Comment, Transaction
from lawyers.utils import lawyer_only
from social.models import ( CallCounseling , OnlineCounselingRoom , OnlineCounselingRoomMessage , FreeCounselingRoom , FreeCounselingRoomMessage
    , ComplaintRoom , ComplaintRoomMessage, ContractRoom , ContractRoomMessage , LegalPanel , LegalPanelMessage, SupportRoom , OnlineCounseling)
from social.utils import day_to_string_persian , customize_datetime_format , send_comment_req ,send_call_acc
from django.db.models import Max, Case , When , F, Avg
from itertools import chain
from operator import attrgetter
from django.db import models
from django.utils import timezone




@lawyer_only
@login_required
def settings(request):
    lawyer = Lawyer.objects.filter(username=request.user.username).first()
    return render(request, 'lawyers-settings.html', {'lawyer': lawyer})



@lawyer_only
@login_required
def verification(request):
    lawyer = Lawyer.objects.filter(username=request.user.username).first()
    form = LawyerVerificationForm(instance=lawyer)

    if request.method == 'POST':
        if not lawyer.verified:
            form = LawyerVerificationForm(request.POST, request.FILES, instance=lawyer)
            if form.is_valid():
                form.save()

                return redirect(reverse('lawyers:settings'))
            else:
                messages.error(request, form.errors)
        else:
            messages.error(request, 'Data cannot be changed.')

    return render(request, 'verification.html', {'form': form})


@lawyer_only
@login_required
def personal_settings(request):
    lawyer = Lawyer.objects.filter(username=request.user.username).first()
    form = LawyerPersonalForm(instance=lawyer)

    if request.method == 'POST':
        if not lawyer.verified:
            form = LawyerPersonalForm(request.POST, request.FILES, instance=lawyer)
            if form.is_valid():
                form.save()

                return redirect(reverse('lawyers:settings'))
            else:
                messages.error(request, form.errors)
        else:
            messages.error(request, 'Data cannot be changed.')

    return render(request, 'personal-settings.html', {'form': form})


@lawyer_only
@login_required
def pricings(request):
    lawyer = Lawyer.objects.filter(username=request.user.username).first()
    comments = Comment.objects.filter(lawyer=lawyer).all()
    avg_score = comments.aggregate(Avg('score'))

    if not ConsultationPrice.objects.filter(lawyer=lawyer).exists():
        consultation_price = ConsultationPrice(lawyer=lawyer)
        consultation_price.save()
    else:
        consultation_price = ConsultationPrice.objects.filter(lawyer=lawyer).first()

    consultation_price_form = LawyerConsultationPriceForm(instance=consultation_price)
    lawyer_update_form = LawyerUpdateForm(instance=lawyer)

    if request.method == 'POST':
        consultation_price_form = LawyerConsultationPriceForm(request.POST, instance=consultation_price)
        lawyer_update_form = LawyerUpdateForm(request.POST, request.FILES, instance=lawyer)
        if consultation_price_form.is_valid() and lawyer_update_form.is_valid():
            consultation_price_form.save()
            lawyer_update_form.save()

            return redirect(reverse('lawyers:pricings'))
        else:
            messages.error(request, consultation_price_form.errors)
            messages.error(request, lawyer_update_form.errors)

    return render(request, 'pricings.html', {'consultation_price_form': consultation_price_form,
                                             'lawyer_update_form': lawyer_update_form,
                                             'lawyer': lawyer,
                                             'comments': comments,
                                             'avg_score': avg_score['score__avg']})


@lawyer_only
@login_required
def financial(request):
    lawyer = Lawyer.objects.filter(username=request.user.username).first()
    transactions = Transaction.objects.filter(lawyer=lawyer).all()

    return render(request, 'financial.html', {'transactions': transactions, 'lawyer': lawyer})


@lawyer_only
@login_required
def lawyers(request):
    lawyer = Lawyer.objects.filter(username=request.user.username).first()
    call_orders = CallCounseling.objects.filter(lawyer_model=request.user.username )
    warnings = Warning.objects.filter(lawyer=lawyer).all()
    comments = Comment.objects.filter(lawyer=lawyer).all()
    
    avg_score = Comment.objects.filter(lawyer=lawyer).aggregate(avg_score=Avg('score'))
    if avg_score['avg_score'] is not None:
        avg_score = avg_score['avg_score']/2
    else:
        avg_score=5


    call_counseling = CallCounseling.objects.filter(lawyer=lawyer.pk , payment_status='ok').count()
    online_counseling = OnlineCounseling.objects.filter(lawyer=lawyer.pk , payment_status='ok').count()

    
    return render(request, 'lawyers.html', {'lawyer': lawyer,
                                            'call_counseling' : call_counseling,
                                            'online_counseling' : online_counseling,
                                            'warnings': warnings,
                                            'comments': comments,
                                            'avg_score': avg_score})


@method_decorator(lawyer_only, name='dispatch')
@method_decorator(login_required, name='dispatch')
class UpdateStatus(APIView):
    def post(self, request: HttpRequest):
        def data_validation():
            data_is_valid = True

            if not is_online in ['false', 'true']:
                data_is_valid = False

            return data_is_valid

        lawyer = Lawyer.objects.filter(username=request.user.username).first()
        is_online = request.POST['is_online']

        data_is_valid = data_validation()
        if data_is_valid:
            lawyer.online = True if is_online == 'true' else False
            lawyer.save()

            return Response({'status': 'OK'}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Data was not valid."}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


@method_decorator(lawyer_only, name='dispatch')
@method_decorator(login_required, name='dispatch')
class UpdateProfile(APIView):
    def post(self, request: HttpRequest):
        def data_validation():
            data_is_valid = True

            if not profile_image:
                data_is_valid = False

            return data_is_valid

        lawyer = Lawyer.objects.filter(username=request.user.username).first()
        profile_image = request.FILES['profile_image']
        data_is_valid = data_validation()
        if data_is_valid:
            lawyer.profile_image.delete()
            lawyer.profile_image = profile_image
            lawyer.save()

            return Response({'status': 'OK', 'image_url': lawyer.profile_image.url}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Data was not valid."}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)



@lawyer_only
@login_required
def councilView(request) :
    lawyer = Lawyer.objects.filter(username=request.user.username).first()

    if request.method == 'POST' :
        data = request.POST
        if data.get('identifier' , None) == "StatusChanger":
            identity = data.get('identity' , None)
            if identity and CallCounseling.objects.filter(identity=identity).exists() :
                call_counseling_object = CallCounseling.objects.get(identity=identity)
                
                status = call_counseling_object.status
                changed_status = 'done' if status == 'undone' else 'undone'
                call_counseling_object.status = changed_status
                call_counseling_object.save()
                if call_counseling_object.status == "done":
                    lawyer.balance = lawyer.balance + int(call_counseling_object.amount_paid)/2
                    lawyer.save()
                send_comment_req(phone_number = call_counseling_object.client.username ,name= call_counseling_object.client.first_name , service='تلفنی' ,lawyer= f'{call_counseling_object.get_lawyer_display()}', link=f'justita.app/social/submit-review/?pk={call_counseling_object.identity}' )
       
        else:
            identity = data.get('identity' , None)
            if identity and CallCounseling.objects.filter(identity=identity).exists() :
                call_counseling_object = CallCounseling.objects.get(identity=identity)
                is_accepted = call_counseling_object.accepted
                call_counseling_object.accepted = True
                call_counseling_object.save()
                send_call_acc(phone_number=f'{call_counseling_object.client.username}' ,lawyer= f'{call_counseling_object.get_lawyer_display()}', time=call_counseling_object.Reservation_time.strftime("%H:%M:%S") , num=f'{Lawyer.objects.get(id = call_counseling_object.lawyer).username}')




            

    call_counseling = CallCounseling.objects.filter(lawyer=lawyer.pk , payment_status='ok').annotate(
    has_reservation=Case(
        When(Reservation_day__isnull=False, Reservation_time__isnull=False, then=1),
        default=0,
        output_field=models.IntegerField(),
    )
    ).order_by('-has_reservation', '-Reservation_day', '-Reservation_time')
    args = {
        'call_counseling' : call_counseling
    }

    return render(request , 'calls.html' , args)


@lawyer_only
@login_required
def ChatRoomsView(request) :
    lawyer = Lawyer.objects.filter(username=request.user.username).first()

    if request.method == 'POST' :
        data = request.POST
        service = data.get('service' , '')
        identity = data.get('identity' , '')

        if service == 'مشاوره رایگان' :
            object = FreeCounselingRoom
        elif service == 'مشاوره آنلاین' :
            object = OnlineCounselingRoom
        elif service == 'وکالت آنلاین' :
            object = LegalPanel
        elif service == 'تنظیم قرارداد' :
            object = ContractRoom
        elif service =='تنظیم شکوائیه' :
            object = ComplaintRoom
        else :
            object = None

        if object != None and object.objects.filter(identity=identity).exists():
            my_object = object.objects.get(identity=identity)
            new_status = 'open' if my_object.status == 'closed' else 'closed'
            my_object.status = new_status
            my_object.save()
            lawyer.balance = lawyer.balance + int(my_object.online_counseling.amount_paid)/2
            lawyer.save()
            # send_comment_req(phone_number = my_object.online_counseling.client.username ,name= my_object.online_counseling.client.first_name , service='آنلاین' ,lawyer= f'{my_object.online_counseling.get_lawyer_display()}', link=f'justita.app/social/submit-review/?pk={my_object.identity}' )
            return redirect('lawyers:chats')
    online_counselings = OnlineCounseling.objects.filter(lawyer=lawyer.pk , payment_status='ok')
    online_counseling_ids = online_counselings.values_list('id', flat=True)
    online_counseling_chats = OnlineCounselingRoom.objects.filter(online_counseling__id__in=online_counseling_ids)
    legal_panle_chats = LegalPanel.objects.filter(lawyer=lawyer.pk).annotate(last_message_created_at=Max('messages__created_at'))

    

    all_chats = sorted(
        chain(online_counseling_chats, legal_panle_chats),
        key=attrgetter('created_at'),
        reverse=True
    )


    chats = []

    for chat in all_chats:
        if isinstance(chat, OnlineCounselingRoom):
            service_name = 'مشاوره آنلاین'
            chat.client = chat.online_counseling.client
            lawyer = chat.online_counseling.get_lawyer_display() if chat.online_counseling else 'جاستیتا'
            url = f'/social/chat/online-counseling/{chat.identity}'
            last_message_time = OnlineCounselingRoomMessage.objects.filter(room=chat).last().created_at_persian() if OnlineCounselingRoomMessage.objects.filter(room=chat).last() else chat.created_at_persian()
            last_message_time_en = OnlineCounselingRoomMessage.objects.filter(room=chat).last().created_at if OnlineCounselingRoomMessage.objects.filter(room=chat).last() else chat.created_at
       
        chats.append({
            'created_at': customize_datetime_format(chat.created_at),
            'today' : timezone.now().date(),
            
            'client' : chat.client ,
            'status' : chat.status,
            'get_status_display' : chat.get_status_display,
            'identity' : chat.identity,
            'service_name': service_name,
            'url' : url , 
            'lawyer': lawyer if lawyer else 'جاستیتا',
            'last_message_time' : last_message_time,
            'last_message_time_en' : last_message_time_en
        })

    chats_sorted_by_last_message = sorted(chats, key=lambda x: x['last_message_time_en'], reverse=True)

    args = {
        'chats' : chats_sorted_by_last_message
    }

    return render(request , 'messanger.html' , args)


