from django.conf.urls import url

from api.views import OrderViewSet, OrderAttachmentViewSet, OrderCategoryViewSet, OrderContractorListViewSet, \
    OrderCustomerListViewSet, OrderChatMessageListViewSet, OrderChatDetailViewSet, AccountRegistrationView, \
    AccountLoginView, TagCreateView, OrdersByTagListView

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
    'post': 'create'
})


urlpatterns = [
    url(r'^account/register', AccountRegistrationView.as_view(), name='account-register'),
    url(r'^account/login', AccountLoginView.as_view(), name='account-login'),

    url(r'^orders/$', order_list, name='order-list'),
    url(r'^orders/(?P<pk>[0-9]+)/$', order_detail, name='order-detail'),
    url(r'^orders/contractor/$', order_contractor_list, name='order-contractor-list'),
    url(r'^orders/customer/$', order_customer_list, name='order-customer-list'),

    url(r'^orders/tags/$', TagCreateView.as_view(), name='tag-create'),
    url(r'^orders/tags/(?P<pk>[0-9]+)$', OrdersByTagListView.as_view(), name='orders-by-tag-list'),

    url(r'^orders/categories/$', order_category_list, name='order-category-list'),
    url(r'^orders/categories/(?P<pk>[0-9]+)/$', order_category_detail, name='order-category-detail'),

    url(r'^orders/(?P<order_id>[0-9]+)/chat/$', order_chat_detail, name='order-chat-list'),
    url(r'^orders/(?P<order_id>[0-9]+)/chat/messages/$', order_chat_messages_list, name='order-chat-messages-list')
]
