import jwt
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import PermissionDenied, NotAcceptable, NotFound, ParseError
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.views import APIView

from anon_fl import notify_api
from anon_fl import settings
from anon_fl.paginators import EnlargedResultsSetPagination
from api import models
from api.permissions import IsSuperUserOrReadOnly, IsOrderChatParticipant, IsOrderOwner
from api.serializers import OrderListSerializer, OrderCreateSerializer, OrderAttachmentSerializer, \
    OrderCategorySerializer, \
    OrderDetailSerializer, OrderChatDetailSerializer, OrderChatMessageListSerializer, \
    AccountRegisterSerializer, TagSerializer, OrderApplicationListSerializer, UserNotificationsSettingsDetailSerializer
from api.models import Order, OrderAttachment, OrderCategory, OrderChat, OrderChatMessage, Tag, OrderTag, \
    OrderApplication, UserNotificationsSettings


class AccountRegistrationView(generics.CreateAPIView):
    serializer_class = AccountRegisterSerializer


class AccountLoginView(APIView):
    serializer_class = AuthTokenSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        jwt.encode({'user_id': user.id}, settings.JWT_SECRET)
        return Response({
            'jwt': '',
            'token': token.key,
            'email': user.email,
            'username': user.username,
            'id': user.id
        })


class OrderViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        category = self.request.query_params.get('category', None)
        queryset = Order.objects.order_by('-updated_at') \
            .select_related('category').prefetch_related('order_tag')

        filter = {}

        # TODO: extract to ModelManager
        if category:
            filter['category__in'] = category.split(',')

        tag_id = self.request.query_params.get('tag_id', None)
        if tag_id and tag_id.isdigit():
            filter['order_tag__tag_id'] = tag_id

        return queryset.filter(**filter)

    def get_serializer_class(self):
        serializers = {
            'create': OrderCreateSerializer,
            'list': OrderListSerializer,
            'retrieve': OrderDetailSerializer,
            'update': OrderDetailSerializer,
            'partial_update': OrderDetailSerializer
        }

        return serializers[self.action]

    def get_permissions(self):
        if self.action == 'create':
            return (IsAuthenticated(),)

        if self.action in ['update', 'partial_update']:
            return (IsOrderOwner(),)

        if self.action == 'delete':
            return (IsSuperUserOrReadOnly(),)

        return (AllowAny(),)

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = (TokenAuthentication,)

    def get_permissions(self):
        if self.action == 'create':
            return (IsAuthenticated(),)
        if self.action in ['update', 'partial_update', 'delete']:
            return (IsSuperUserOrReadOnly(),)

        return (AllowAny(),)

    def get_queryset(self):
        if self.action == 'list':
            query = self.request.query_params.get('q')
            if query is not None:
                return Tag.objects.filter(tag__contains=query)

        return self.queryset

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        tag, created = Tag.objects.get_or_create(created_by=request.user, tag=serializer.validated_data['tag'])

        return Response({
            'id': tag.id,
            'tag': tag.tag
        })


class OrderAttachmentViewSet(viewsets.ModelViewSet):
    queryset = OrderAttachment.objects.all()
    serializer_class = OrderAttachmentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class OrderCategoryViewSet(viewsets.ModelViewSet):
    queryset = OrderCategory.objects.all()
    serializer_class = OrderCategorySerializer
    permission_classes = (IsSuperUserOrReadOnly,)

    # FIXME: move to serializer! smth like this: serializers.SerializerMethodField
    def finalize_response(self, request, response, *args, **kwargs):
        results = []

        for category in response.data['results']:
            if category['parent_id'] is None:
                category['subcategories'] = []
                results.append(category)
            else:
                parent_id = category['parent_id']
                parent = list(filter(lambda el: el['id'] == parent_id, results)).pop()
                index = results.index(parent)
                results[index]['subcategories'].append(category)

        response.data['results'] = results

        return super().finalize_response(request, response, *args, **kwargs)


class OrderCustomerListViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = OrderListSerializer

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user)


class OrderContractorListViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    serializer_class = OrderListSerializer

    def get_queryset(self):
        return Order.objects.filter(contractor=self.request.user)


class OrderChatDetailViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    queryset = OrderChat.objects.all()
    serializer_class = OrderChatDetailSerializer
    permissions_classes = (IsAuthenticated, IsOrderChatParticipant,)

    def retrieve(self, request, *args, **kwargs):
        queryset = OrderChat.objects.all()
        order_chat = get_object_or_404(queryset, order_id=self.kwargs['order_id'])
        serializer = OrderChatDetailSerializer(order_chat)
        return Response(serializer.data)


class OrderChatMessageListViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    serializer_class = OrderChatMessageListSerializer
    permissions_classes = (IsAuthenticated, IsOrderChatParticipant,)
    pagination_class = EnlargedResultsSetPagination

    def get_queryset(self):
        order_id = self.kwargs['order_id']

        order = Order.objects.get(id=order_id)
        if self.request.user.id not in [order.customer_id, order.contractor_id]:
            raise PermissionDenied

        chat = get_object_or_404(OrderChat.objects.all(), order_id=order_id)
        return OrderChatMessage.objects.filter(chat_id=chat.id).order_by('-id')

    def perform_create(self, serializer):
        order_id = self.kwargs['order_id']
        sender_id = self.request.user.id

        order = Order.objects.get(id=order_id)
        if sender_id not in [order.customer_id, order.contractor_id]:
            raise PermissionDenied

        order_chat = OrderChat.objects.get(order=order_id)
        serializer.save(chat_id=order_chat.id, sender_id=sender_id)

        order_chat.messages_count += 1
        order_chat.save()

        data = serializer.data
        data['order_title'], data['order_id'] = order.title, order.id
        receiver = list(filter(lambda _id: _id != sender_id, [order.contractor_id, order.customer_id]))
        notify_api.notify(receiver, order_chat.id, notify_api.ORDER_CHAT_NEW_MESSAGE, data)

    def read(self, request, *args, **kwargs):
        order_id = kwargs['order_id']
        order_chat = OrderChat.objects.get(order_id=order_id)
        OrderChatMessage.objects.filter(chat_id=order_chat.id).update(is_read=True)
        return Response({'status': 'ok'})


class OrderApplicationListViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    serializer_class = OrderApplicationListSerializer
    queryset = OrderApplication.objects.all()
    permission_classes = (IsAuthenticated, )

    def create(self, request, *args, **kwargs):
        """
        Customer applies for order
        """
        order_id = kwargs['order_id']
        applicant_id = self.request.user.id
        order = Order.objects.filter(id=order_id).get()

        if order.customer_id == applicant_id:
            return Response({'application': 'Cannot apply to own order'}, status=status.HTTP_409_CONFLICT)

        if not order:
            return Response({'order': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        if order.contractor_id is not None:
            return Response({'order': 'Order already has contractor. Applications are no longer accepted'},
                            status=status.HTTP_400_BAD_REQUEST)

        application, created = OrderApplication.objects.get_or_create(order_id=order_id, applicant_id=applicant_id)

        if not application:
            return ParseError

        serialized = OrderApplicationListSerializer(application).data
        serialized['order_title'] = order.title
        notify_api.notify([order.customer_id], order.id, notify_api.ORDER_APPLICATION_REQUEST_RECEIVED, serialized)
        return Response(serialized)

    def destroy(self, request, *args, **kwargs):
        """
        Customer withdraws application
        """
        order_id = kwargs['order_id']
        applicant_id = self.request.user.id

        try:
            application = OrderApplication.objects.get(applicant_id=applicant_id, order_id=order_id)
        except models.OrderApplication.DoesNotExist:
            raise NotFound

        if application.status == models.ApplicationStatus.ACCEPTED.value:
            raise NotAcceptable

        application.status = models.ApplicationStatus.WITHDRAWN.value
        application.save()

        return Response(OrderApplicationListSerializer(application).data)


class OrderApplicationStatusDetailView(generics.UpdateAPIView, generics.DestroyAPIView):
    authentication_classes = (TokenAuthentication,)

    def update(self, request, *args, **kwargs):
        """
        Customer accepts or declines application
        """
        order_id = kwargs['order_id']
        application_id = kwargs['pk']
        application_status = request.data.get('status')

        permitted_statuses = [models.ApplicationStatus.ACCEPTED.value, models.ApplicationStatus.DECLINED.value]
        order = Order.objects.get(id=order_id)
        if order.customer_id != self.request.user.pk \
                or application_status not in permitted_statuses \
                or order.contractor_id is not None:
            raise PermissionDenied

        application = OrderApplication.objects.get(id=application_id)

        if application_status == models.ApplicationStatus.ACCEPTED.value:
            order.status = models.OrderStatus.IN_PROCESS.value
            order.contractor_id = application.applicant_id
            order.save()

            OrderChat.objects.create(order_id=order_id)

        application.status = application_status
        application.save()

        if application.status == models.ApplicationStatus.ACCEPTED.value:
            key = notify_api.ORDER_APPLICATION_APPROVED
        else:
            key = notify_api.ORDER_APPLICATION_DECLINED

        serialized = OrderApplicationListSerializer(application).data
        serialized['order_title'] = order.title

        notify_api.notify([application.applicant_id], order.id, key, serialized)

        return Response(serialized)


class UserNotificationsSettingsViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    serializer_class = UserNotificationsSettingsDetailSerializer
    queryset = UserNotificationsSettings.objects.all()

    def retrieve(self, request, *args, **kwargs):
        settings = get_object_or_404(self.queryset, user_id=request.user.id)
        serializer = self.serializer_class(settings)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        settings = get_object_or_404(self.queryset, user_id=request.user.id)
        serializer = self.serializer_class(settings, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NotificationsMarkAsRead(APIView):
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        notify_api.read_notifications(request.user.id)
        return Response({'status': 'ok'})
