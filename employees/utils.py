from authentication.models import CustomUser
from django.utils.text import slugify
import uuid

def generate_unique_username(first_name, last_name):
    base_username = slugify(f"{first_name}.{last_name}").lower()
    unique_username = base_username
    counter = 1
    while CustomUser.objects.filter(username=unique_username).exists():
        unique_suffix = str(uuid.uuid4())[:8]  # Use a short segment of UUID to ensure uniqueness
        unique_username = f"{base_username}.{unique_suffix}"
        counter += 1
    return unique_username