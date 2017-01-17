from django.core.mail import send_mail

from api.celeryconf import app


@app.task(queue='registration_email')
def send_registration_email(username, email):
    # TODO: вынести в шаблон
    return send_mail('Регистрация на Anon FL',
                     '{0}, добро пожаловать на сайт Anon FL'.format(username),
                     'autechregescom@gmail.com',
                     [email],
                     fail_silently=False)
