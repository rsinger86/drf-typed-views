from django.contrib.auth.models import User, Group
from django.core.management.base import BaseCommand
from rest_framework.authtoken.models import Token


class Command(BaseCommand):
    def handle(self, *args, **options):
        user = User.objects.filter(username="robert").first()
        admin = Group.objects.filter(name="admin").first()

        if user:
            user.delete()

        if not admin:
            admin = Group.objects.create(name="admin")

        user = User.objects.create_user(
            "robert",
            email="robertgsinger@gmail.com",
            first_name="Robert",
            last_name="Singer",
        )

        user.groups.add(admin)

        token = Token.objects.create(user=user)
        print("Token is: ", token.key)
