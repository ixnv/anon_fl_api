from django.conf.urls import url

from api.views import OrderViewSet, OrderAttachmentViewSet, OrderCategoryViewSet, OrderContractorListViewSet, \
    OrderCustomerListViewSet, OrderChatMessageListViewSet, OrderChatDetailViewSet, AccountRegistrationView, \
    AccountLoginView, OrderApplicationListViewSet, TagViewSet, OrderApplicationStatusDetailView, \
    UserNotificationsSettingsViewSet, NotificationsMarkAsRead

order_list = OrderViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

order_detail = OrderViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

order_attachment_list = OrderAttachmentViewSet.as_view({
    'get': 'retrieve',
    'post': 'create'
})

order_attachment_detail = OrderAttachmentViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

order_category_list = OrderCategoryViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

order_category_detail = OrderCategoryViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

order_contractor_list = OrderContractorListViewSet.as_view({
    'get': 'list'
})

order_customer_list = OrderCustomerListViewSet.as_view({
    'get': 'list'
})

order_chat_detail = OrderChatDetailViewSet.as_view({
    'get': 'retrieve'
})

order_chat_messages_list = OrderChatMessageListViewSet.as_view({
    'get': 'list',
    'post': 'create',
    'put': 'read'
})

order_application_list = OrderApplicationListViewSet.as_view({
    'post': 'create',
    'delete': 'destroy'
})

tags_list = TagViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

user_notifications_settings_detail = UserNotificationsSettingsViewSet.as_view({
    'get': 'retrieve',
    'put': 'update'
})

urlpatterns = [
    url(r'^account/register', AccountRegistrationView.as_view(), name='account-register'),
    url(r'^account/login', AccountLoginView.as_view(), name='account-login'),

    url(r'^account/settings/notifications', user_notifications_settings_detail, name='account-settings-notifications'),

    url(r'^orders/$', order_list, name='order-list'),
    url(r'^orders/(?P<pk>[0-9]+)/$', order_detail, name='order-detail'),
    url(r'^orders/contractor/$', order_contractor_list, name='order-contractor-list'),
    url(r'^orders/customer/$', order_customer_list, name='order-customer-list'),

    url(r'^tags/$', tags_list, name='tag-list'),
    url(r'^tags/search$', tags_list, name='tag-search'),

    url(r'^orders/categories/$', order_category_list, name='order-category-list'),
    url(r'^orders/categories/(?P<pk>[0-9]+)/$', order_category_detail, name='order-category-detail'),

    url(r'^orders/(?P<order_id>[0-9]+)/applications/$', order_application_list, name='order-application-list'),
    url(r'^orders/(?P<order_id>[0-9]+)/applications/(?P<pk>[0-9]+)/status/$', OrderApplicationStatusDetailView.as_view(), name='order-application-status-detail'),

    url(r'^orders/(?P<order_id>[0-9]+)/chat/$', order_chat_detail, name='order-chat-list'),
    url(r'^orders/(?P<order_id>[0-9]+)/chat/messages/$', order_chat_messages_list, name='order-chat-messages-list'),

    url(r'notifications/mark_as_read', NotificationsMarkAsRead.as_view(), name='notifications-mark-as-read')
]
