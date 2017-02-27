import jwt
from django.conf import settings
import requests

BASE_URL = settings.NOTIFY_URL

ORDER_CHAT_NEW_MESSAGE = 'ORDER_CHAT_NEW_MESSAGE'
ORDER_APPLICATION_REQUEST_RECEIVED = 'ORDER_APPLICATION_REQUEST_RECEIVED'
ORDER_APPLICATION_APPROVED = 'ORDER_APPLICATION_APPROVED'
ORDER_APPLICATION_DECLINED = 'ORDER_APPLICATION_DECLINED'


def generate_jwt():
    return jwt.encode({}, settings.JWT_NOTIFY_SECRET)


def notify(user_ids, entity_id, key, data):
    return requests.post(BASE_URL + '/notify', json={
        'user_ids': user_ids,
        'entity_id': entity_id,
        'key': key,
        'data': data,
        'token': generate_jwt()
    })


def read_notifications(user_id):
    return requests.post(BASE_URL + '/notifications/read', json={
        'user_id': user_id,
        'token': generate_jwt()
    })
