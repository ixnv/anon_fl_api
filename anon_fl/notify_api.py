from django.conf import settings
import requests

BASE_URL = settings.NOTIFY_URL

ORDER_CHAT_NEW_MESSAGE = 'ORDER_CHAT_NEW_MESSAGE'


def notify(user_ids, key, data):
    return requests.post(BASE_URL + '/notify', json={
        'user_ids': user_ids,
        'key': key,
        'data': data
    })
