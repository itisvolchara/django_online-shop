from django.contrib.auth import get_user_model
from celery import shared_task
from django.core.mail import send_mail
from onlineshop import settings

@shared_task(bind=True)
def send_order_email(self, user_id, shopping_cart, order_sum, order_id):
    #operations

    User = get_user_model()
    user = User.objects.get(id=user_id)


    mail_subject="Спасибо за покупку!"
    message=f"{user.username}, большое спасибо за покупку! Ваш заказ: \n"
    for name in shopping_cart:
        message += f'{name}\n'

    message += f'\nИтоговая сумма: {order_sum}\n'
    message += f'\nНомер заказа: {order_id}'

    to_email=user.email

    print(message)
    print(to_email)

    send_mail(
        subject= mail_subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[to_email],
        fail_silently=True,
    )

    return "Done"

@shared_task(bind=True)
def send_thankyou_email(self, user_id):
    #operations

    mail_subject="Ещё раз благодарим за покупку!"
    message="С удовольствием узнаем Ваши мысли по поводу улучшения нашего сервиса!"

    User = get_user_model()
    user = User.objects.get(id=user_id)

    to_email = user.email
    send_mail(
        subject= mail_subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[to_email],
        fail_silently=True,
    )

    return "Done"

@shared_task(bind=True)
def send_newsletters(self):
    User = get_user_model()
    users = User.objects.exclude(email='volcharaodnonogy@gmail.com')


    mail_subject = "Напоминаем о себе!"
    message = "Не забывайте о нас! Мы всё ещё открыты!"

    to_email = [user.email for user in users]
    send_mail(
        subject=mail_subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=to_email,
        fail_silently=True,
    )

    return "Done"