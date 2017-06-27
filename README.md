# RESTful API

Simple RESTful API backend of freelance service. Made exclusively for learning purposes and demonstration of skills.

Stack: django-rest-framework, docker-compose (containers: postgreSQL, nginx, gunicorn, redis, celery), JWT for ISC authentication, ansible for deploying, and little bit of celery (simple registration email sending)

### Other linked projects:

frontend (react + redux) - https://github.com/tiezo/anon_fl_frontend

notifications service (node + websockets + mongodb) - https://github.com/tiezo/anon_fl_notifications

## Testing
```
$ ./manage.py test
```
## На русском

Незамудренное RESTful API сервиса биржи фриланса. Написнао для целей изучения django-rest-framework

Использовано: django-rest-framework, docker-compose (контейнеры: postgreSQL, nginx, gunicorn, redis, celery), JWT для авторизации между сервисами, ansible для деплоя, и немного celery (отправка email при регистрации)

### Связанные проекты:

фронтэнд (клиентское приложение на react + redux) - https://github.com/tiezo/anon_fl_frontend

сервис оповещений (сервис на node + websockets и mongodb) - https://github.com/tiezo/anon_fl_notifications
