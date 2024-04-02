from celery import shared_task

from .models import GroupMembership


@shared_task
def update_group_memberships():
    for membership in GroupMembership.objects.all():
        if membership.is_active():
            membership.group.user_set.add(membership.user)
        else:
            membership.group.user_set.remove(membership.user)
