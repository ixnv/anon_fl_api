from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.views import APIView

from api.permissions import IsSuperUserOrReadOnly, IsOrderChatParticipant
from api.serializers import OrderListSerializer, OrderCreateSerializer, OrderAttachmentSerializer, \
    OrderCategorySerializer, \
    OrderDetailSerializer, OrderChatDetailSerializer, OrderChatMessageListSerializer, \
    AccountRegisterSerializer, TagSerializer
from api.models import Order, OrderAttachment, OrderCategory, OrderChat, OrderChatMessage, Tag, OrderTag


class AccountRegistrationView(generics.CreateAPIView):
    serializer_class = AccountRegisterSerializer


class AccountLoginView(APIView):
    serializer_class = AuthTokenSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key
        })


class OrderViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        category = self.request.query_params.get('category', None)
        if category and category.isdigit():
            return Order.objects.filter(category=category).select_related('category')

        tag_id = self.request.query_params.get('tag_id', None)
        if tag_id and tag_id.isdigit():
            return Order.objects.filter(order_tag__tag_id=tag_id)\
                .select_related('category').prefetch_related('order_tag')

        return Order.objects.select_related('category').prefetch_related('order_tag')

    def get_serializer_class(self):
        serializers = {
            'create': OrderCreateSerializer,
            'list': OrderListSerializer,
            'retrieve': OrderDetailSerializer,
            'update': OrderDetailSerializer,
            'partial_update': OrderDetailSerializer
        }

        return serializers[self.action]

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)


class TagCreateView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    serializer_class = TagSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        tag, created = Tag.objects.get_or_create(created_by=request.user, tag=serializer.validated_data['tag'])

        return Response({
            'tag': tag.tag
        })


class OrdersByTagListView(generics.ListAPIView):
    serializer_class = OrderListSerializer

    def get_queryset(self):

        return OrderTag.objects.select_related('order', 'tag')


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
    serializer_class = OrderListSerializer

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user)


class OrderContractorListViewSet(viewsets.ModelViewSet):
    serializer_class = OrderListSerializer

    def get_queryset(self):
        return Order.objects.filter(contractor=self.request.user)


class OrderChatDetailViewSet(viewsets.ModelViewSet):
    queryset = OrderChat.objects.all()
    serializer_class = OrderChatDetailSerializer
    permissions_classes = (IsOrderChatParticipant,)

    def retrieve(self, request, *args, **kwargs):
        queryset = OrderChat.objects.all()
        order_chat = get_object_or_404(queryset, order_id=self.kwargs['order_id'])
        serializer = OrderChatDetailSerializer(order_chat)
        return Response(serializer.data)


class OrderChatMessageListViewSet(viewsets.ModelViewSet):
    queryset = OrderChatMessage.objects.all()
    serializer_class = OrderChatMessageListSerializer
    permissions_classes = (IsOrderChatParticipant,)

    def perform_create(self, serializer):
        order_id = self.kwargs['order_id']
        try:
            order_chat = OrderChat.objects.get(order=order_id)
        except ObjectDoesNotExist:
            order_chat = OrderChat.objects.create(order_id=order_id)

        serializer.save(chat_id=order_chat.id, sender_id=self.request.user.pk)
