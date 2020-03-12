from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import Any

from rest_framework import serializers

from rest_typed_views.param_settings import ParamSettings
from rest_typed_views.utils import (
    parse_complex_type,
    parse_enum_annotation,
    parse_list_annotation,
)
from rest_typed_views.validators import (
    DefaultValidator,
    PydanticValidator,
    TypeSystemValidator,
    MarshMallowValidator,
)


class ValidatorFactory(object):
    @classmethod
    def make_string_validator(cls, settings: ParamSettings):
        if settings.regex:
            return serializers.RegexField(
                settings.regex,
                default=settings.default,
                max_length=settings.max_length,
                min_length=settings.min_length,
            )

        if settings.format is None:
            return serializers.CharField(
                default=settings.default,
                max_length=settings.max_length,
                min_length=settings.min_length,
                trim_whitespace=settings.trim_whitespace,
            )

        if settings.format == "email":
            return serializers.EmailField(
                default=settings.default,
                max_length=settings.max_length,
                min_length=settings.min_length,
            )

        if settings.format == "slug":
            return serializers.SlugField(
                default=settings.default,
                max_length=settings.max_length,
                min_length=settings.min_length,
            )

        if settings.format == "url":
            return serializers.URLField(
                default=settings.default,
                max_length=settings.max_length,
                min_length=settings.min_length,
            )

        if settings.format == "uuid":
            return serializers.UUIDField(default=settings.default)

        if settings.format == "file_path":
            return serializers.FilePathField(
                default=settings.default,
                path=settings.path,
                match=settings.match,
                recursive=settings.recursive,
                allow_files=settings.allow_files,
                allow_folders=settings.allow_folders,
            )

        if settings.format == "ipv6":
            return serializers.IPAddressField(default=settings.default, protocol="IPv6")

        if settings.format == "ipv4":
            return serializers.IPAddressField(default=settings.default, protocol="IPv4")

        if settings.format == "ip":
            return serializers.IPAddressField(default=settings.default, protocol="both")

    @classmethod
    def make_list_validator(cls, item_type: Any, settings: ParamSettings):
        options = {
            "min_length": settings.min_length,
            "max_length": settings.max_length,
            "allow_empty": settings.allow_empty,
            "default": settings.default,
        }
        if item_type is not Any:
            options["child"] = ValidatorFactory.make(
                item_type, settings.child or ParamSettings()
            )

        return serializers.ListField(**options)

    @classmethod
    def make(cls, annotation: Any, settings: ParamSettings):
        if annotation is bool:
            return serializers.BooleanField(default=settings.default)

        if annotation is str:
            return cls.make_string_validator(settings)

        if annotation is int:
            return serializers.IntegerField(
                default=settings.default,
                max_value=settings.max_value,
                min_value=settings.min_value,
            )

        if annotation is float:
            return serializers.FloatField(
                default=settings.default,
                max_value=settings.max_value,
                min_value=settings.min_value,
            )

        if annotation is Decimal:
            return serializers.DecimalField(
                default=settings.default,
                max_digits=settings.max_digits,
                decimal_places=settings.decimal_places,
                coerce_to_string=settings.coerce_to_string,
                localize=settings.localize,
                rounding=settings.rounding,
                max_value=settings.max_value,
                min_value=settings.min_value,
            )

        if annotation is datetime:
            return serializers.DateTimeField(
                default=settings.default,
                input_formats=settings.input_formats,
                default_timezone=settings.default_timezone,
            )

        if annotation is date:
            return serializers.DateField(
                default=settings.default, input_formats=settings.input_formats
            )

        if annotation is time:
            return serializers.TimeField(
                default=settings.default, input_formats=settings.input_formats
            )

        if annotation is timedelta:
            return serializers.DurationField(default=settings.default)

        is_enum_type, values = parse_enum_annotation(annotation)

        if is_enum_type:
            return serializers.ChoiceField(choices=values)

        is_list_type, item_type = parse_list_annotation(annotation)

        if is_list_type:
            return cls.make_list_validator(item_type, settings)

        is_complex_type, package = parse_complex_type(annotation)

        if is_complex_type and package == "pydantic":
            return PydanticValidator(annotation)

        if is_complex_type and package == "typesystem":
            return TypeSystemValidator(annotation)

        if is_complex_type and package == "marshmallow":
            return MarshMallowValidator(annotation)

        return DefaultValidator(default=settings.default)
