from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync , sync_to_async
from social.models import (OnlineCounselingRoom , OnlineCounselingRoomMessage , FreeCounselingRoom , 
    FreeCounselingRoomMessage , ComplaintRoom , ComplaintRoomMessage , ContractRoom ,ContractRoomMessage ,LegalPanel , LegalPanelMessage , 
    SupportRoom , SupportRoomMessage)
from django.core.files.base import ContentFile
import json , base64
from django.core.serializers.json import DjangoJSONEncoder
from social.utils import (customize_datetime_format , send_new_message_available_onlin_counseling , send_new_message_available_free_counseling ,
    send_new_message_available_complaint_counseling , send_new_message_available_contract_counseling)
from django.conf import settings


class OnlineCounselingConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        self.identity = self.scope["url_route"]["kwargs"]["identity"]
        self.room_group_name = f"online_counseling_{self.identity}"
        self.user = self.scope['user']

        is_authenticated = self.user.is_authenticated
        is_valid_room = True if self.user.is_superuser else await sync_to_async(OnlineCounselingRoom.objects.filter(identity=self.identity, online_counseling__client=self.user).exists)()

        if is_authenticated and is_valid_room:
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            self.room = await sync_to_async(OnlineCounselingRoom.objects.get)(identity=self.identity)
            await self.accept()
        else:
            await self.disconnect(403)


    async def disconnect(self, close_code):
        # Leave room group
        self.connected_clients.discard(self.user.username)
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        # pass


    async def receive(self, text_data):

        room = await sync_to_async(OnlineCounselingRoom.objects.get)(identity=self.identity)
        if room.status == 'closed':
            return

        text_data_json = json.loads(text_data)
        data = text_data_json["data"]
        message = data.get('message', '')
        file_data = data.get('file', None)

        sender = self.user
        room = self.room

        if file_data:
            # Handle the file
            file_content = file_data.get('content', '')
            file_name = file_data.get('file_name', '')

            # Decode base64 and create a ContentFile
            file_content = base64.b64decode(file_content)
            content_file = ContentFile(file_content, name=file_name)

            # Create a message with both message and file
            message_instance = await sync_to_async(OnlineCounselingRoomMessage.objects.create)(
                room=room,
                message=message,
                file=content_file,
                sender=sender
            )

        else:
            # Handle the case without a file
            message_instance = await sync_to_async(OnlineCounselingRoomMessage.objects.create)(
                room=room,
                message=message,
                sender=sender
            )

        client = await sync_to_async(lambda: room.online_counseling.client)()
        from_client = message_instance.sender == client
        # Notify the group about the new message
        await self.channel_layer.group_send(
            self.room_group_name, {
                "type": "chat.message",
                "message": message_instance.message,
                "from_client" : from_client , 
                "created_at": customize_datetime_format(message_instance.created_at)["time"],
                "file_url": message_instance.file.url if message_instance.file else None , 
            }
        )

        if not from_client :
            link = settings.HOSTADDRESS + '/social/chat/online-counseling/' + self.identity
            name = client.get_full_name()
            send_new_message_available_onlin_counseling(phone_number=client.username , name=name, link=link)


    async def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "message": message,
            "created_at": event["created_at"],
            "file_url": event["file_url"],
            "from_client" : event["from_client"]
        }, cls=DjangoJSONEncoder))


class FreeCounselingConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        self.identity = self.scope["url_route"]["kwargs"]["identity"]
        self.room_group_name = f"free_counseling_{self.identity}"
        self.user = self.scope['user']

        is_authenticated = self.user.is_authenticated
        is_valid_room = True if self.user.is_superuser else await sync_to_async(FreeCounselingRoom.objects.filter(identity=self.identity, client=self.user).exists)()

        if is_authenticated and is_valid_room:
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            self.room = await sync_to_async(FreeCounselingRoom.objects.get)(identity=self.identity)
            await self.accept()
        else:
            await self.disconnect(403)


    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        # pass


    async def receive(self, text_data):

        room = await sync_to_async(FreeCounselingRoom.objects.get)(identity=self.identity)
        if room.status == 'closed':
            return

        text_data_json = json.loads(text_data)
        data = text_data_json["data"]
        message = data.get('message', '')

        sender = self.user
        room = self.room
        client = await sync_to_async(lambda: room.client)()
        message_instance = await sync_to_async(FreeCounselingRoomMessage.objects.create)(
            room=room,
            message=message,
            sender=sender
        )

        from_client = message_instance.sender == client

        await self.channel_layer.group_send(
            self.room_group_name, {
                "type": "chat.message",
                "message": message_instance.message,
                "from_client" : from_client , 
                "created_at": customize_datetime_format(message_instance.created_at)["time"],
            }
        )

        if not from_client :
            link = settings.HOSTADDRESS + '/social/chat/free-counseling/' + self.identity
            send_new_message_available_free_counseling(phone_number=client.username , name=client.get_full_name(), link=link)


    async def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "message": message,
            "from_client" : event["from_client"],
            "created_at": event["created_at"],
        }, cls=DjangoJSONEncoder))


class ComplaintRoomConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        self.identity = self.scope["url_route"]["kwargs"]["identity"]
        self.room_group_name = f"complaint_{self.identity}"
        self.user = self.scope['user']

        is_authenticated = self.user.is_authenticated
        is_valid_room = True if self.user.is_superuser else await sync_to_async(ComplaintRoom.objects.filter(identity=self.identity, client=self.user).exists)()

        if is_authenticated and is_valid_room:
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            self.room = await sync_to_async(ComplaintRoom.objects.get)(identity=self.identity)
            await self.accept()
        else:
            await self.disconnect(403)


    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        # pass


    async def receive(self, text_data):

        room = await sync_to_async(ComplaintRoom.objects.get)(identity=self.identity)
        if room.status == 'closed':
            return

        text_data_json = json.loads(text_data)
        data = text_data_json["data"]
        message = data.get('message', '')
        file_data = data.get('file', None)

        sender = self.user
        room = self.room

        if file_data:
            # Handle the file
            file_content = file_data.get('content', '')
            file_name = file_data.get('file_name', '')

            # Decode base64 and create a ContentFile
            file_content = base64.b64decode(file_content)
            content_file = ContentFile(file_content, name=file_name)

            # Create a message with both message and file
            message_instance = await sync_to_async(ComplaintRoomMessage.objects.create)(
                room=room,
                message=message,
                file=content_file,
                sender=sender
            )

        else:
            # Handle the case without a file
            message_instance = await sync_to_async(ComplaintRoomMessage.objects.create)(
                room=room,
                message=message,
                sender=sender
            )

        client = await sync_to_async(lambda: room.client)()
        from_client = message_instance.sender == client

        await self.channel_layer.group_send(
            self.room_group_name, {
                "type": "chat.message",
                "message": message_instance.message,
                "from_client" : from_client , 
                "created_at": customize_datetime_format(message_instance.created_at)["time"],
                "file_url": message_instance.file.url if message_instance.file else None
            }
        )

        if not from_client :
            link = settings.HOSTADDRESS + '/social/chat/complaint/' + self.identity
            send_new_message_available_complaint_counseling(phone_number=client.username , name=client.get_full_name() , link=link)


    async def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "message": message,
            "created_at": event["created_at"],
            "file_url": event["file_url"],
            "from_client" : event["from_client"]
        }, cls=DjangoJSONEncoder))


class ContractRoomConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        self.identity = self.scope["url_route"]["kwargs"]["identity"]
        self.room_group_name = f"contract_{self.identity}"
        self.user = self.scope['user']

        is_authenticated = self.user.is_authenticated
        is_valid_room = True if self.user.is_superuser else await sync_to_async(ContractRoom.objects.filter(identity=self.identity, client=self.user).exists)()

        if is_authenticated and is_valid_room:
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            self.room = await sync_to_async(ContractRoom.objects.get)(identity=self.identity)
            await self.accept()
        else:
            await self.disconnect(403)


    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        # pass


    async def receive(self, text_data):

        room = await sync_to_async(ContractRoom.objects.get)(identity=self.identity)
        if room.status == 'closed':
            return

        text_data_json = json.loads(text_data)
        data = text_data_json["data"]
        message = data.get('message', '')
        file_data = data.get('file', None)

        sender = self.user
        room = self.room

        if file_data:
            # Handle the file
            file_content = file_data.get('content', '')
            file_name = file_data.get('file_name', '')

            # Decode base64 and create a ContentFile
            file_content = base64.b64decode(file_content)
            content_file = ContentFile(file_content, name=file_name)

            # Create a message with both message and file
            message_instance = await sync_to_async(ContractRoomMessage.objects.create)(
                room=room,
                message=message,
                file=content_file,
                sender=sender
            )

        else:
            # Handle the case without a file
            message_instance = await sync_to_async(ContractRoomMessage.objects.create)(
                room=room,
                message=message,
                sender=sender
            )

        client = await sync_to_async(lambda: room.client)()
        from_client = message_instance.sender == client

        await self.channel_layer.group_send(
            self.room_group_name, {
                "type": "chat.message",
                "message": message_instance.message,
                "from_client" : from_client , 
                "created_at": customize_datetime_format(message_instance.created_at)["time"],
                "file_url": message_instance.file.url if message_instance.file else None
            }
        )

        if not from_client :
            link = settings.HOSTADDRESS + '/social/chat/contract/' + self.identity
            send_new_message_available_contract_counseling(phone_number=client.username , name=client.get_full_name() , link=link)


    async def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "message": message,
            "created_at": event["created_at"],
            "file_url": event["file_url"],
            "from_client" : event["from_client"]
        }, cls=DjangoJSONEncoder))


class LegalPanelConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        self.identity = self.scope["url_route"]["kwargs"]["identity"]
        self.room_group_name = f"legal_panel_{self.identity}"
        self.user = self.scope['user']

        is_authenticated = self.user.is_authenticated
        is_valid_room = True if self.user.is_superuser else await sync_to_async(LegalPanel.objects.filter(identity=self.identity, client=self.user).exists)()

        if is_authenticated and is_valid_room:
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            self.room = await sync_to_async(LegalPanel.objects.get)(identity=self.identity)
            await self.accept()
        else:
            await self.disconnect(403)


    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        # pass


    async def receive(self, text_data):

        room = await sync_to_async(LegalPanel.objects.get)(identity=self.identity)
        if room.status == 'closed':
            return

        text_data_json = json.loads(text_data)
        data = text_data_json["data"]
        message = data.get('message', '')
        file_data = data.get('file', None)

        sender = self.user
        room = self.room

        if file_data:
            # Handle the file
            file_content = file_data.get('content', '')
            file_name = file_data.get('file_name', '')

            # Decode base64 and create a ContentFile
            file_content = base64.b64decode(file_content)
            content_file = ContentFile(file_content, name=file_name)

            # Create a message with both message and file
            message_instance = await sync_to_async(LegalPanelMessage.objects.create)(
                room=room,
                message=message,
                file=content_file,
                sender=sender
            )

        else:
            # Handle the case without a file
            message_instance = await sync_to_async(LegalPanelMessage.objects.create)(
                room=room,
                message=message,
                sender=sender
            )

        client = await sync_to_async(lambda: room.client)()
        from_client = message_instance.sender == client
        # Notify the group about the new message
        await self.channel_layer.group_send(
            self.room_group_name, {
                "type": "chat.message",
                "message": message_instance.message,
                "from_client" : from_client , 
                "created_at": customize_datetime_format(message_instance.created_at)["time"],
                "file_url": message_instance.file.url if message_instance.file else None
            }
        )

        if not from_client :
            link = settings.HOSTADDRESS + '/social/chat/legal-panel/' + self.identity
            send_new_message_available_legal_pannel(phone_number=client.username , name=client.get_full_name() , link=link)


    async def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "message": message,
            "created_at": event["created_at"],
            "file_url": event["file_url"],
            "from_client" : event["from_client"]
        }, cls=DjangoJSONEncoder))


class SupportRoomConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        self.identity = self.scope["url_route"]["kwargs"]["identity"]
        self.room_group_name = f"support_room_{self.identity}"
        self.user = self.scope['user']

        is_authenticated = self.user.is_authenticated
        is_valid_room = True if self.user.is_superuser else await sync_to_async(SupportRoom.objects.filter(identity=self.identity, user=self.user).exists)()

        if is_authenticated and is_valid_room:
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            self.room = await sync_to_async(SupportRoom.objects.get)(identity=self.identity)
            await self.accept()
        else:
            await self.disconnect(403)


    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        # pass


    async def receive(self, text_data):

        text_data_json = json.loads(text_data)
        data = text_data_json["data"]
        message = data.get('message', '')
        file_data = data.get('file', None)

        sender = self.user
        room = self.room

        if file_data:
            # Handle the file
            file_content = file_data.get('content', '')
            file_name = file_data.get('file_name', '')

            # Decode base64 and create a ContentFile
            file_content = base64.b64decode(file_content)
            content_file = ContentFile(file_content, name=file_name)

            # Create a message with both message and file
            message_instance = await sync_to_async(SupportRoomMessage.objects.create)(
                room=room,
                message=message,
                file=content_file,
                sender=sender
            )

        else:
            # Handle the case without a file
            message_instance = await sync_to_async(SupportRoomMessage.objects.create)(
                room=room,
                message=message,
                sender=sender
            )

        user = await sync_to_async(lambda: room.user)()
        from_user = message_instance.sender == user
        # Notify the group about the new message
        await self.channel_layer.group_send(
            self.room_group_name, {
                "type": "chat.message",
                "message": message_instance.message,
                "from_user" : from_user , 
                "created_at": customize_datetime_format(message_instance.created_at)["time"],
                "file_url": message_instance.file.url if message_instance.file else None
            }
        )


    async def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "message": message,
            "created_at": event["created_at"],
            "file_url": event["file_url"],
            "from_user" : event["from_user"]
        }, cls=DjangoJSONEncoder))




