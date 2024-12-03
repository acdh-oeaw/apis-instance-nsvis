from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.models import Group
from django.dispatch import receiver


@receiver(user_logged_in)
def post_login(sender, user, request, **kwargs):
    g, _ = Group.objects.get_or_create(name="editors")
    user.groups.add(g)
