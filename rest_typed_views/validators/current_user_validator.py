from typing import TYPE_CHECKING
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError

if TYPE_CHECKING:
    from rest_typed_views import ParamSettings


class CurrentUserValidator(object):
    def __init__(self, settings: "ParamSettings"):
        self.settings = settings

    def run_validation(self, user: User) -> User:
        if self.settings.member_of is not None:
            queryset = user.groups.all().filter(name=self.settings.member_of)

            if queryset.count() == 0:
                raise ValidationError(
                    f"User must be a member of the '{self.settings.member_of}' group"
                )

        if len(self.settings.member_of_any) > 0:
            queryset = user.groups.all().filter(name__in=self.settings.member_of_any)

            if queryset.count() == 0:
                raise ValidationError(
                    f"User must be a member of at least one of these groups: "
                    f"'{self.settings.member_of_any}'"
                )
        return user
