from django.shortcuts import render , HttpResponse , redirect
from django.http import HttpResponseForbidden
from social.models import ( CallCounseling , OnlineCounselingRoom , OnlineCounselingRoomMessage , FreeCounselingRoom , FreeCounselingRoomMessage
    , ComplaintRoom , ComplaintRoomMessage, ContractRoom , ContractRoomMessage , LegalPanel , LegalPanelMessage, SupportRoom)
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from social.utils import day_to_string_persian , customize_datetime_format
from django.db.models import Max, Case , When , F
from itertools import chain
from operator import attrgetter
from django.db import models


@login_required
def dashboardView(request) :
    if not request.user.is_superuser :
        return HttpResponseForbidden('شما نمیتوانید وارد این قسمت شوید.')

    if request.method == 'POST' :
        data = request.POST
        identity = data.get('identity' , None)
        if identity and CallCounseling.objects.filter(identity=identity).exists() :
            call_counseling_object = CallCounseling.objects.get(identity=identity)
            print(call_counseling_object.status)
            status = call_counseling_object.status
            changed_status = 'done' if status == 'undone' else 'undone'
            call_counseling_object.status = changed_status
            call_counseling_object.save()
            print(call_counseling_object.status)

    call_counseling = CallCounseling.objects.annotate(
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


@login_required
def supportRoomView(request) :
    if not request.user.is_superuser :
        return HttpResponseForbidden('شما نمیتوانید وارد این قسمت شوید.')

    support_rooms = SupportRoom.objects.annotate(last_message_created_at=Max('messages__created_at')).order_by('-last_message_created_at')

    args = {
        'support_rooms' : support_rooms
    }
    return render(request , 'support-room.html' , args)


@login_required
def ChatRoomsView(request) :
    if not request.user.is_superuser :
        return HttpResponseForbidden('شما نمیتوانید وارد این قسمت شوید.')


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

    online_counseling_chats = OnlineCounselingRoom.objects.annotate(last_message_created_at=Max('messages__created_at'))
    free_counseling_chats = FreeCounselingRoom.objects.annotate(last_message_created_at=Max('messages__created_at'))
    complaint_chats = ComplaintRoom.objects.annotate(last_message_created_at=Max('messages__created_at'))
    contract_chats = ContractRoom.objects.annotate(last_message_created_at=Max('messages__created_at'))
    legal_panle_chats = LegalPanel.objects.annotate(last_message_created_at=Max('messages__created_at'))

    

    all_chats = sorted(
        chain(online_counseling_chats, free_counseling_chats , complaint_chats , contract_chats , legal_panle_chats),
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