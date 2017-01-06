from django.contrib.auth.models import User
from rest_framework import serializers
from api.models import Order, OrderAttachment, OrderCategory, OrderChat, OrderChatMessage, Tag, OrderTag


class AccountRegisterSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()

        return user

    class Meta:
        model = User
        fields = (
            'email', 'username', 'password'
        )
        extra_kwargs = {
            'password': {'write_only': True}
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

    def get_order_tags(self, instance):
        serialized_data = OrderTagSerializer(instance.order_tag.all(), many=True, read_only=True, context=self.context)
        return list(map((lambda tag: tag['tag']), serialized_data.data))

    class Meta:
        model = Order
        fields = (
            'id', 'title', 'description', 'created_at', 'updated_at', 'category', 'customer_id', 'tags'
        )


class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = (
            'id', 'title', 'description', 'created_at', 'updated_at', 'category', 'customer'
        )


class OrderDetailSerializer(serializers.ModelSerializer):
    category = OrderCategorySerializer()
    attachments = OrderAttachmentSerializer(many=True)

    class Meta:
        model = Order
        fields = (
            'id', 'title', 'description', 'created_at', 'updated_at', 'category', 'customer_id', 'attachments'
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
            'id', 'chat_id', 'message', 'is_read', 'sender_id'
        )


