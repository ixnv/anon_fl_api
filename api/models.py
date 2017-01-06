from django.db import models

ORDER_STATUS_CHOICES = (
    (0, 'NEW'),
    (1, 'PUBLISHED'),
    (2, 'IN_PROCESS'),
    (3, 'COMPLETED_WITH_SUCCESS'),
    (4, 'COMPLETED_WITH_FAIL')
)


class OrderCategory(models.Model):
    """
    Категория заказа
    """
    parent = models.ForeignKey("OrderCategory", related_name='subcategories', null=True)
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'order_category'


class Tag(models.Model):
    tag = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('auth.User', related_name='tag_creator')

    class Meta:
        db_table = 'tag'


class Order(models.Model):
    """
    Заказ
    """
    category = models.ForeignKey(OrderCategory, related_name='order_category')
    title = models.CharField(max_length=100)
    description = models.TextField()
    customer = models.ForeignKey('auth.User', related_name='order_customer', on_delete=models.CASCADE)
    contractor = models.ForeignKey('auth.User', related_name='order_contractor', null=True)
    status = models.IntegerField(choices=ORDER_STATUS_CHOICES, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'order'


class OrderTag(models.Model):
    tag = models.ForeignKey(Tag, related_name='order_tag_key')
    order = models.ForeignKey(Order, related_name='order_tag')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'order_tag'


class OrderAttachment(models.Model):
    """
    Приложение к заказу
    """
    order = models.ForeignKey(Order, related_name='attachments', on_delete=models.CASCADE)
    customer = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    filename = models.TextField()
    # sha1 hash
    hash = models.CharField(max_length=40)
    # max url length is 2000
    url = models.CharField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'order_attachment'


class OrderApplication(models.Model):
    """
    Отклик на заказ
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    applicant = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    class Meta:
        db_table = 'order_application'


class OrderChat(models.Model):
    """
    Чат заказчика с исполнителем
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    contractor_last_read_at = models.DateTimeField(null=True)
    customer_last_read_at = models.DateTimeField(null=True)
    messages_count = models.IntegerField(default=0)
    contractor_new_messages_count = models.IntegerField(default=0)
    customer_new_messages_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'order_chat'


class OrderChatMessage(models.Model):
    chat = models.ForeignKey(OrderChat, related_name='messages', on_delete=models.CASCADE)
    message = models.TextField()
    sender = models.ForeignKey('auth.User', related_name='order_chat_sender')
    is_read = models.BooleanField(default=False)

    class Meta:
        db_table = 'order_chat_message'


class OrderChatAttachment(models.Model):
    message = models.ForeignKey(OrderChatMessage, related_name='messages_attachments', on_delete=models.CASCADE)
    filename = models.TextField()
    # max url length is 2000
    url = models.CharField(max_length=2000)
    # sha1 hash
    hash = models.CharField(max_length=40)

    class Meta:
        db_table = 'order_chat_attachment'


