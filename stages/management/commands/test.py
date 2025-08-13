from django.core.management.commands.test import Command as TestCommand
from django.test.utils import override_settings


class Command(TestCommand):
    def handle(self, *args, **options):
        with override_settings(
            PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"],
        ):
            return super().handle(*args, **options)
