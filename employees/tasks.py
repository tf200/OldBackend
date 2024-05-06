from django.conf import settings

from system.models import Notification


def send_login_credentials(user, username, password):
    subject = "Your new account"
    message = f"Hello,\n\nYour account has been created.\nUsername: {username}\nPassword: {password}\n\nPlease change your password upon first login."

    notification = Notification.objects.create(
        title="Login credentials",
        event=Notification.EVENTS.LOGIN_SEND_CREDENTIALS,
        content="Login credentials are sent to your contacts (e.g email).",
        receiver=user,
        metadata={"user_id": user.id},
    )

    notification.notify(
        email_title=subject, email_content=message
    )  # send email as well as SMS (in the future)
