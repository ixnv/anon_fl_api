from django.contrib.auth.models import User
from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import NotAcceptable
from django.conf import settings

import jwt

from api import models
from api.models import Order, OrderAttachment, OrderCategory, OrderChat, OrderChatMessage, Tag, OrderTag, \
    OrderApplication, UserNotificationsSettings
from api.tasks import send_registration_email


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'username'
        )


class AccountRegisterSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()
    jwt = serializers.SerializerMethodField()

    def create(self, validated_data):
        try:
            user = User.objects.create(
                username=validated_data['username'],
                email=validated_data['email']
            )
        except IntegrityError:
            raise NotAcceptable(detail={'email': ['Пользователь с таким email уже существует']})

        user.set_password(validated_data['password'])
        user.save()

        Token.objects.get_or_create(user=user)

        # TODO: move this to signals
        send_registration_email.delay(validated_data['username'], validated_data['email'])
        UserNotificationsSettings.objects.create(user_id=user.id)
        return user

    def get_token(self, instance):
        token = Token.objects.get(user=instance.id)
        return token.key

    def get_jwt(self, instance):
        return jwt.encode({'user_id': instance.id}, settings.JWT_SECRET)

    class Meta:
        model = User
        fields = (
            'email', 'username', 'password', 'token', 'id', 'jwt'
        )
        extra_kwargs = {
            'password': {'write_only': True, 'required': True},
            'email': {'required': True},
            'username': {'required': True},
            'token': {'read_only': True},
            'id': {'read_only': True}
        }


class OrderCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderCategory
        fields = (
            'id', 'title', 'parent_id'
        )


class OrderAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderAttachment
        fields = (
            'filename', 'url'
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id', 'tag'
        )


class OrderTagSerializer(serializers.ModelSerializer):
    tag = TagSerializer()

    class Meta:
        model = OrderTag
        fields = (
            'tag',
        )


class OrderListSerializer(serializers.ModelSerializer):
    customer_id = serializers.ReadOnlyField(source='customer.id')
    category = OrderCategorySerializer()
    tags = serializers.SerializerMethodField('get_order_tags')
    contractor = serializers.SerializerMethodField('get_contractor_profile')
    customer = serializers.SerializerMethodField('get_customer_profile')

    def get_order_tags(self, instance):
        serialized_data = OrderTagSerializer(instance.order_tag.all(), many=True, read_only=True, context=self.context)
        return list(map((lambda tag: tag['tag']), serialized_data.data))

    def get_contractor_profile(self, instance):
        if instance.contractor is None or self.context['request'].user.id not in [instance.customer_id, instance.contractor.id]:
            return {}

        return {
            'id': instance.contractor.id, 'username': instance.contractor.username
        }

    def get_customer_profile(self, instance):
        return {
            'id': instance.customer.id, 'username': instance.customer.username
        }

    class Meta:
        model = Order
        fields = (
            'id', 'title', 'description', 'price', 'created_at', 'updated_at', 'category', 'customer_id', 'tags',
            'customer', 'contractor'
        )


class OrderCreateSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()

    def get_tags(self, instance):
        tags = self.context['request'].data['tags']
        # FIXME: what if passed tag does not exists in table?
        serializer = TagSerializer(data=tags, many=True)
        serializer.is_valid(raise_exception=True)
        OrderTag.objects.bulk_create(
            list(map(lambda tag: OrderTag(tag_id=tag['id'], order_id=instance.id), serializer.initial_data))
        )
        return tags

    def create(self, validated_data):
        order = Order.objects.create(**validated_data)
        return order

    class Meta:
        model = Order
        fields = (
            'id', 'title', 'description', 'price', 'created_at', 'category', 'tags'
        )


class OrderDetailSerializer(serializers.ModelSerializer):
    category = OrderCategorySerializer()
    attachments = OrderAttachmentSerializer(many=True)
    tags = serializers.SerializerMethodField('get_order_tags')
    application = serializers.SerializerMethodField()
    application_list = serializers.SerializerMethodField()
    contractor = serializers.SerializerMethodField('get_contractor_profile')
    customer = serializers.SerializerMethodField('get_customer_profile')

    def get_order_tags(self, instance):
        serialized_data = OrderTagSerializer(instance.order_tag.all(), many=True, read_only=True, context=self.context)
        return list(map((lambda tag: tag['tag']), serialized_data.data))

    def get_customer_profile(self, instance):
        return {'id': instance.customer.id, 'username': instance.customer.username}

    def get_contractor_profile(self, instance):
        if instance.contractor is None or self.context['request'].user.id not in [instance.customer_id, instance.contractor.id]:
            return {}

        return {'id': instance.contractor.id, 'username': instance.contractor.username}

    def get_application(self, instance):
        try:
            application = OrderApplication.objects.filter(order_id=instance.id, applicant_id=self.context['request'].user.pk).get()
        except OrderApplication.DoesNotExist:
            return {}

        serializer = OrderApplicationListSerializer(application)
        return serializer.data

    def get_application_list(self, instance):
        if self._context['request'].user.id != instance.customer_id:
            return []

        application_list = OrderApplication.objects\
            .filter(order_id=instance.id).exclude(status=models.ApplicationStatus.WITHDRAWN.value)\
            .select_related('applicant').all()

        serializer = OrderApplicationListSerializer(application_list, many=True)
        return serializer.data

    class Meta:
        model = Order
        fields = (
            'id', 'title', 'description', 'price', 'status', 'created_at', 'updated_at', 'category', 'customer_id',
            'attachments', 'tags', 'application', 'application_list', 'contractor', 'customer'
        )


class OrderChatDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderChat
        fields = (
            'id', 'messages_count'
        )


class OrderChatMessageListSerializer(serializers.ModelSerializer):
    chat_id = serializers.ReadOnlyField()
    is_read = serializers.ReadOnlyField()

    class Meta:
        model = OrderChatMessage
        fields = (
            'id', 'chat_id', 'message', 'is_read', 'sender_id', 'created_at'
        )


class OrderApplicationListSerializer(serializers.ModelSerializer):
    applicant = UserSerializer()

    class Meta:
        model = OrderApplication
        fields = (
            'id', 'order_id', 'applicant_id', 'created_at', 'status', 'applicant'
        )


class UserNotificationsSettingsDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNotificationsSettings
        fields = (
            'categories', 'notify_on_email'
        )
