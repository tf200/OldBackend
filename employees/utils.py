import uuid

from django.utils.text import slugify

from authentication.models import CustomUser


def generate_unique_username(first_name, last_name):
    base_username = slugify(f"{first_name}.{last_name}").lower()
    unique_username = base_username
    counter = 1
    while CustomUser.objects.filter(username=unique_username).exists():
        unique_suffix = str(uuid.uuid4())[:8]
        unique_username = f"{base_username}.{unique_suffix}"
        counter += 1
    return unique_username
