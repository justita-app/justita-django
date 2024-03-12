from django.shortcuts import render , redirect , HttpResponse , Http404
from django.contrib.auth.decorators import login_required
from .utils import day_to_string_persian , customize_datetime_format
import datetime
from django.conf import settings
from django.core import serializers
from django.utils import timezone
from social.models import ( CallCounseling , OnlineCounseling , OnlineCounselingRoom 
, OnlineCounselingRoomMessage , FreeCounselingRoom , FreeCounselingRoomMessage , ComplaintRoom , ComplaintRoomMessage
, ContractRoom , ContractRoomMessage , LegalPanel , LegalPanelMessage , SupportRoom , SupportRoomMessage)
import json
from itertools import chain
from operator import attrgetter
from django.db.models import Value, CharField
from django.http import HttpResponseNotFound
from lawyers.models import Lawyer


lawyer_pictures = {
    'Alireza_Atashzaran' : '/media/team/Alireza_atashzaran.webp',
    'Mohammad_Nobari' : '/media/team/Mohammad_nobari.webp',
    'Arghavan_Mansuri' : '/media/team/Arghavan_mansuri.webp',
    'Atmish_Jahanshahi' : '/media/team/Atmish_Jahanshahi.webp',
    'Niloofar_Shahab' : '/media/team/niloofar_shahab.webp',
    'None' : '/media/team/justita-team.png'
}



def Home(request) :
    return render(request , 'services.html')


def LegalPanelView(request) :
    return render(request , 'legal-panel.html')


def OrdersView(request):
    if request.user.is_authenticated:
        user_call_counseling = CallCounseling.objects.filter(payment_status='ok', client=request.user)
        user_online_counseling = OnlineCounseling.objects.filter(payment_status='ok', client=request.user)
        
        # Combine and sort the orders
        all_orders = sorted(
            chain(user_call_counseling, user_online_counseling),
            key=attrgetter('created_at')
        )
        
        # Add a service name to each order
        modified_data = [
            {
                'created_at': customize_datetime_format(order.created_at),
                'amount_paid': order.amount_paid,
                'service_name': 'درخواست مشاوره تلفنی' if isinstance(order, CallCounseling) else 'درخواست مشاوره آنلاین',
            }
            for order in all_orders
        ]
    else:
        modified_data = []

    args = {
        'orders': modified_data
    }

    return render(request, 'orders.html', args)


def ChatsView(request) :
    for lawyer in Lawyer.objects.filter(verified=True).all():
        if lawyer.profile_image:
            lawyer_pictures[f'{lawyer.pk}'] = lawyer.profile_image.url
        else:
            lawyer_pictures[f'{lawyer.pk}'] = '/media/team/default.png'

    if request.user.is_authenticated :
        online_counseling_chats = OnlineCounselingRoom.objects.filter(online_counseling__client=request.user)
        free_counseling_chats = FreeCounselingRoom.objects.filter(client=request.user)
        complaint_chats = ComplaintRoom.objects.filter(client=request.user)
        contract_chats = ContractRoom.objects.filter(client=request.user)
        legal_panle_chats = LegalPanel.objects.filter(client=request.user)
        
                # Combine and sort the orders
        all_chats = sorted(
            chain(online_counseling_chats, free_counseling_chats , complaint_chats , contract_chats , legal_panle_chats),
            key=attrgetter('created_at'),
            reverse=True
        )
        chats = []

        for chat in all_chats:
            if isinstance(chat, OnlineCounselingRoom):
                service_name = 'مشاوره آنلاین'
                lawyer = chat.online_counseling.get_lawyer_display() if chat.online_counseling else 'جاستیتا'
                lawyer_profile = lawyer_pictures.get(chat.online_counseling.lawyer , '/media/team/justita-team.png')
                url = f'/social/chat/online-counseling/{chat.identity}'
                last_message_time = OnlineCounselingRoomMessage.objects.filter(room=chat).last().created_at_persian() if OnlineCounselingRoomMessage.objects.filter(room=chat).last() else chat.created_at_persian()
            elif isinstance(chat, ContractRoom):
                service_name = 'تنظیم قرار داد'
                lawyer = 'جاستیتا'
                lawyer_profile = '/media/team/justita-team.png'
                url = f'/social/chat/contract/{chat.identity}'
                last_message_time = ContractRoomMessage.objects.filter(room=chat).last().created_at_persian() if ContractRoomMessage.objects.filter(room=chat).last() else chat.created_at_persian()
            elif isinstance(chat , ComplaintRoom):
                service_name = 'تنظیم شکوائیه'
                lawyer = 'جاستیتا'
                lawyer_profile = '/media/team/justita-team.png'
                url = f'/social/chat/complaint/{chat.identity}'
                last_message_time = ComplaintRoomMessage.objects.filter(room=chat).last().created_at_persian() if ComplaintRoomMessage.objects.filter(room=chat).last() else chat.created_at_persian()
            elif isinstance(chat , FreeCounselingRoom) :
                service_name = 'مشاوره رایگان'
                lawyer = 'جاستیتا'
                lawyer_profile = '/media/team/justita-team.png'
                url = f'/social/chat/free-counseling/{chat.identity}'
                last_message_time = FreeCounselingRoomMessage.objects.filter(room=chat).last().created_at_persian() if FreeCounselingRoomMessage.objects.filter(room=chat).last() else chat.created_at_persian()
            else :
                service_name = 'وکالت آنلاین'
                lawyer = chat.get_lawyer_display()
                lawyer_profile = lawyer_pictures.get(chat.lawyer , '/media/team/justita-team.png')
                url = f'/social/chat/legal-panel/{chat.identity}'
                last_message_time = LegalPanelMessage.objects.filter(room=chat).last().created_at_persian() if LegalPanelMessage.objects.filter(room=chat).last() else chat.created_at_persian()

            chats.append({
                'created_at': customize_datetime_format(chat.created_at),
                'marked': chat.marked,
                'status' : chat.status,
                'identity' : chat.identity,
                'service_name': service_name,
                'url' : url , 
                'lawyer': lawyer if lawyer else 'جاستیتا',
                'lawyer_profile' : lawyer_profile,
                'last_message_time' : last_message_time
            })

    else :
        chats = []

    if request.method == 'POST' :
        data = request.POST
        service = data.get('service' , '')
        identity = data.get('identity' , '')

        if service == 'مشاوره رایگان' :
            object = FreeCounselingRoom
        elif service == 'مشاوره آنلاین' :
            object = OnlineCounseling
        elif service == 'وکالت آنلاین' :
            object = LegalPanel
        elif service == 'تنظیم قرار داد' :
            object = ContractRoom
        elif service =='تنظیم شکوائیه' :
            object = ComplaintRoom
        else :
            object = None

        if object != None and object.objects.filter(identity=identity).exists():
            my_object = object.objects.get(identity=identity)
            my_object.marked = not my_object.marked
            my_object.save()
            return redirect('social:chats')

    args = {
        'chats' : chats
    }
    return render(request, 'chats.html' , args)


# chats pages views

@login_required
def OnlineCounselingRoomView(request , identity) :

    if (not request.user.is_superuser or not request.user.is_lawyer) and not OnlineCounselingRoom.objects.filter(identity=identity , online_counseling__client=request.user).exists():
        return HttpResponseNotFound("گفت و گو یافت نشد")

    for lawyer in Lawyer.objects.filter(verified=True).all():
        if lawyer.profile_image:
            lawyer_pictures[f'{lawyer.pk}'] = lawyer.profile_image.url
        else:
            lawyer_pictures[f'{lawyer.pk}'] = '/media/team/default.png'

    online_counseling_room = OnlineCounselingRoom.objects.get(identity=identity)
    room_messages = OnlineCounselingRoomMessage.objects.filter(room=online_counseling_room)

    args = {
        'identity' : identity,
        'lawyer' : online_counseling_room.online_counseling.get_lawyer_display(),
        'lawyer_profile' : lawyer_pictures.get(online_counseling_room.online_counseling.lawyer , '/media/team/default.png'),
        'created_time' : customize_datetime_format(online_counseling_room.created_at)['time'],
        'client' : online_counseling_room.online_counseling.client , 
        'messages' : room_messages,
        'status' : online_counseling_room.status
    }

    return render(request , 'chats/online-counseling.html' , args)


@login_required
def FreeCounselingView(request):
    if FreeCounselingRoom.objects.filter(client=request.user , status='open').exists():
        free_counseling_object = FreeCounselingRoom.objects.get(client=request.user , status='open')
    else :
        free_counseling_object = FreeCounselingRoom(client=request.user , status='open')
        free_counseling_object.save()
    return redirect('social:free-counseling-chat' , identity = free_counseling_object.identity)


@login_required
def FreeCounselingRoomView(request , identity) :

    if not request.user.is_superuser and not FreeCounselingRoom.objects.filter(identity=identity , client=request.user).exists():
        return HttpResponseNotFound("گفت و گو یافت نشد")

    free_counseling_room = FreeCounselingRoom.objects.get(identity=identity)
    room_messages = FreeCounselingRoomMessage.objects.filter(room=free_counseling_room)

    args = {
        'identity' : identity,
        'created_time' : customize_datetime_format(free_counseling_room.created_at)['time'],
        'client' : free_counseling_room.client , 
        'messages' : room_messages,
        'status' : free_counseling_room.status
    }

    return render(request , 'chats/free-counseling.html' , args)


@login_required
def ComplaintView(request):
    if ComplaintRoom.objects.filter(client=request.user , status='open').exists():
        complaint_object = ComplaintRoom.objects.get(client=request.user , status='open')
    else :
        complaint_object = ComplaintRoom(client=request.user , status='open')
        complaint_object.save()
    return redirect('social:complaint-room' , identity = complaint_object.identity)


@login_required
def ComplaintRoomView(request , identity) :

    if not request.user.is_superuser and not ComplaintRoom.objects.filter(identity=identity , client=request.user).exists():
        return HttpResponseNotFound("گفت و گو یافت نشد")

    complaint_room = ComplaintRoom.objects.get(identity=identity)
    room_messages = ComplaintRoomMessage.objects.filter(room=complaint_room)

    args = {
        'identity' : identity,
        'created_time' : customize_datetime_format(complaint_room.created_at)['time'],
        'client' : complaint_room.client , 
        'messages' : room_messages,
        'status' : complaint_room.status
    }

    return render(request , 'chats/complaint-room.html' , args)


@login_required
def ContractView(request):
    if ContractRoom.objects.filter(client=request.user , status='open').exists():
        contract_object = ContractRoom.objects.get(client=request.user , status='open')
    else :
        contract_object = ContractRoom(client=request.user , status='open')
        contract_object.save()
    return redirect('social:contract-room' , identity = contract_object.identity)


@login_required
def ContractRoomView(request , identity) :

    if not request.user.is_superuser and not ContractRoom.objects.filter(identity=identity , client=request.user).exists():
        return HttpResponseNotFound("گفت و گو یافت نشد")

    contract_room = ContractRoom.objects.get(identity=identity)
    room_messages = ContractRoomMessage.objects.filter(room=contract_room)

    args = {
        'identity' : identity,
        'created_time' : customize_datetime_format(contract_room.created_at)['time'],
        'client' : contract_room.client , 
        'messages' : room_messages,
        'status' : contract_room.status
    }

    return render(request , 'chats/contract-room.html' , args)


@login_required
def LegalPanelRoomStartView(request) :
    user = request.user
    if LegalPanel.objects.filter(client=user , status='open').exists():
        legal_panel_object = LegalPanel.objects.get(client=user , status='open')
    else :
        legal_panel_object = LegalPanel(client=user)
        legal_panel_object.save()

    return redirect('social:legal-panel-chat' , identity = legal_panel_object.identity)
    

@login_required
def LegalPanelRoomView(request , identity) :

    if (not request.user.is_superuser or not request.user.is_lawyer) and not LegalPanel.objects.filter(identity=identity , client=request.user).exists():
        return HttpResponseNotFound("گفت و گو یافت نشد")

    for lawyer in Lawyer.objects.filter(verified=True).all():
        if lawyer.profile_image:
            lawyer_pictures[f'{lawyer.pk}'] = lawyer.profile_image.url
        else:
            lawyer_pictures[f'{lawyer.pk}'] = '/media/team/default.png'

    legal_panel = LegalPanel.objects.get(identity=identity)
    room_messages = LegalPanelMessage.objects.filter(room=legal_panel)

    args = {
        'identity' : identity,
        'lawyer' : legal_panel.get_lawyer_display(),
        'lawyer_profile' : lawyer_pictures.get(legal_panel.lawyer , '/media/team/default.png'),
        'created_time' : customize_datetime_format(legal_panel.created_at)['time'],
        'client' : legal_panel.client , 
        'messages' : room_messages,
        'status' : legal_panel.status
    }

    return render(request , 'chats/legal-panel.html' , args)


@login_required
def SupportView(request):
    tickets = SupportRoom.objects.filter(user = request.user)

    if request.method == 'POST' :
        subject = request.POST.get('subject' , '')
        if subject != '' :
            _suppert_object = SupportRoom(subject=subject , user=request.user)
            _suppert_object.save()
            return redirect('social:support-room' , identity = _suppert_object.identity)

    args = {
        'tickets' : tickets
    }
    return render(request , 'social-support.html' , args)


@login_required
def SupportRoomView(request , identity):
    if not request.user.is_superuser and not SupportRoom.objects.filter(identity=identity , user=request.user).exists():
        return HttpResponseNotFound("گفت و گو یافت نشد")

    support_room = SupportRoom.objects.get(identity=identity)
    room_messages = SupportRoomMessage.objects.filter(room=support_room)

    args = {
        'identity' : identity,
        'created_time' : customize_datetime_format(support_room.created_at)['time'],
        'user' : support_room.user , 
        'messages' : room_messages,
    }

    return render(request , 'chats/support.html' , args)