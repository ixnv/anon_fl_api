# anon_fl_api

RESTful backend for freelance service. Made exclusively for learning purposes.

Stack: django-rest-framework, docker-compose (containers: postgres, nginx, gunicorn, redis, celery), ansible for deploying, and little bit of celery (simple registration email sending)

Other linked projects:
frontend (react + redux) - https://github.com/tiezo/anon_fl_frontend
notifications service (node + websockets + mongodb) - https://github.com/tiezo/anon_fl_notifications

## Testing
```
$ ./manage.py test
```
## На русском

Незамудренное RESTful API сервиса биржи фриланса. Написнао для целей изучения django-rest-framework (надстройка над Django для автоматизации рутинного создания views для rest api)

Использовано: django-rest-framework, docker-compose (контейнеры: postgres, nginx, gunicorn, redis, celery), ansible для деплоя, и немного celery (отправка email при регистрации)

Связанные проекты:
фронтэнд (клиентское приложение на react + redux) - https://github.com/tiezo/anon_fl_frontend
сервис оповещений (сервис на node + websockets и mongodb) - https://github.com/tiezo/anon_fl_notifications
