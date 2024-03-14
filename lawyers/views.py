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
from social.utils import day_to_string_persian , customize_datetime_format
from django.db.models import Max, Case , When , F, Avg
from itertools import chain
from operator import attrgetter
from django.db import models


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
    warnings = Warning.objects.filter(lawyer=lawyer).all()
    comments = Comment.objects.filter(lawyer=lawyer).all()
    avg_score = comments.aggregate(Avg('score'))
    return render(request, 'lawyers.html', {'lawyer': lawyer,
                                            'warnings': warnings,
                                            'comments': comments,
                                            'avg_score': avg_score['score__avg']})


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
        identity = data.get('identity' , None)
        if identity and CallCounseling.objects.filter(identity=identity).exists() :
            call_counseling_object = CallCounseling.objects.get(identity=identity)
            
            status = call_counseling_object.status
            changed_status = 'done' if status == 'undone' else 'undone'
            call_counseling_object.status = changed_status
            call_counseling_object.save()
            

    call_counseling = CallCounseling.objects.filter(lawyer=lawyer.pk , payment_status='ok').annotate(
    has_reservation=Case(
        When(Reservation_day__isnull=False, Reservation_time__isnull=False, then=1),
        default=0,
        output_field=models.IntegerField(),
    )
    ).order_by('-has_reservation', 'Reservation_day', 'Reservation_time')

    args = {
        'call_counseling' : call_counseling
    }

    return render(request , 'call-counseling.html' , args)


@lawyer_only
@login_required
def ChatRoomsView(request) :
    lawyer = Lawyer.objects.filter(username=request.user.username).first()

    if request.method == 'POST' :
        data = request.POST
        print(data)
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
            print(my_object.status)
            return redirect('dashboard:chats')

    online_counseling_chats = OnlineCounselingRoom.objects.filter(online_counseling=OnlineCounseling.objects.filter(lawyer=lawyer.pk).first()).annotate(last_message_created_at=Max('messages__created_at'))
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
        elif isinstance(chat, ContractRoom):
            service_name = 'تنظیم قرارداد'
            lawyer = 'جاستیتا'
            url = f'/social/chat/contract/{chat.identity}'
            last_message_time = ContractRoomMessage.objects.filter(room=chat).last().created_at_persian() if ContractRoomMessage.objects.filter(room=chat).last() else chat.created_at_persian()
            last_message_time_en = ContractRoomMessage.objects.filter(room=chat).last().created_at if ContractRoomMessage.objects.filter(room=chat).last() else chat.created_at
        elif isinstance(chat , ComplaintRoom):
            service_name = 'تنظیم شکوائیه'
            lawyer = 'جاستیتا'
            url = f'/social/chat/complaint/{chat.identity}'
            last_message_time = ComplaintRoomMessage.objects.filter(room=chat).last().created_at_persian() if ComplaintRoomMessage.objects.filter(room=chat).last() else chat.created_at_persian()
            last_message_time_en = ComplaintRoomMessage.objects.filter(room=chat).last().created_at if ComplaintRoomMessage.objects.filter(room=chat).last() else chat.created_at
        elif isinstance(chat , FreeCounselingRoom) :
            service_name = 'مشاوره رایگان'
            lawyer = 'جاستیتا'
            url = f'/social/chat/free-counseling/{chat.identity}'
            last_message_time = FreeCounselingRoomMessage.objects.filter(room=chat).last().created_at_persian() if FreeCounselingRoomMessage.objects.filter(room=chat).last() else chat.created_at_persian()
            last_message_time_en = FreeCounselingRoomMessage.objects.filter(room=chat).last().created_at if FreeCounselingRoomMessage.objects.filter(room=chat).last() else chat.created_at
        else :
            service_name = 'وکالت آنلاین'
            lawyer = chat.get_lawyer_display()
            url = f'/social/chat/legal-panel/{chat.identity}'
            last_message_time = LegalPanelMessage.objects.filter(room=chat).last().created_at_persian() if LegalPanelMessage.objects.filter(room=chat).last() else chat.created_at_persian()
            last_message_time_en = LegalPanelMessage.objects.filter(room=chat).last().created_at if LegalPanelMessage.objects.filter(room=chat).last() else chat.created_at

        chats.append({
            'created_at': customize_datetime_format(chat.created_at),
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

    return render(request , 'chat-rooms.html' , args)

@lawyer_only
@login_required
def messanger(request):

    return render(request , 'messanger.html')


    