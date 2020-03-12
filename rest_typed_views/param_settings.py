from typing import Any, List, Optional

from rest_framework.fields import empty


class ParamSettings(object):
    param_type: Optional[str]
    default: Any
    source: Optional[str]
    min_value: Optional[int]
    max_value: Optional[int]
    input_formats: Optional[List[str]]
    format: Optional[str]
    regex: Optional[str]
    min_length: Optional[int]
    max_length: Optional[int]
    trim_whitespace: bool
    allow_blank: bool
    default_timezone: Optional[Any]
    choices: Optional[List[Any]]
    delimiter: str
    max_digits: Optional[int]
    decimal_places: Optional[int]
    rounding: Optional[str]
    coerce_to_string: bool
    localize: bool
    path: Optional[str]
    match: Optional[str]
    recursive: bool
    allow_files: bool
    allow_folders: bool
    protocol: str
    child: Optional["ParamSettings"]
    allow_empty: Optional[bool]
    member_of: Optional[str]
    member_of_any: List[str]

    def __init__(
        self,
        param_type: Optional[str] = None,
        default: Any = empty,
        source: str = None,
        min_value: int = None,
        max_value: int = None,
        input_formats: List[str] = None,
        format: str = None,
        regex: str = None,
        min_length: int = None,
        max_length: int = None,
        trim_whitespace: bool = True,
        allow_blank: bool = False,
        default_timezone=None,
        choices: List[Any] = None,
        delimiter: str = ",",
        # DecimalField args
        max_digits: int = None,
        decimal_places: int = None,
        rounding: str = None,
        coerce_to_string: bool = False,
        localize: bool = False,
        # FilePathField args
        path: str = None,
        match: str = None,
        recursive: bool = False,
        allow_files: bool = True,
        allow_folders: bool = False,
        # IPAddressField args
        protocol: str = "both",
        # ListField arg
        child: "ParamSettings" = None,
        allow_empty: bool = True,
        # Current user validator arg
        member_of: str = None,
        member_of_any: List[str] = [],
    ):
        self.param_type = param_type
        self.default = default
        self.source = source
        self.min_value = min_value
        self.max_value = max_value
        self.input_formats = input_formats
        self.format = format
        self.regex = regex
        self.min_length = min_length
        self.max_length = max_length
        self.trim_whitespace = trim_whitespace
        self.allow_blank = allow_blank
        self.default_timezone = default_timezone
        self.choices = choices
        self.delimiter = delimiter
        self.max_digits = max_digits
        self.decimal_places = decimal_places
        self.rounding = rounding
        self.coerce_to_string = coerce_to_string
        self.localize = localize
        self.path = path
        self.match = match
        self.recursive = recursive
        self.allow_files = allow_files
        self.allow_folders = allow_folders
        self.protocol = protocol
        self.child = child
        self.allow_empty = allow_empty
        self.member_of = member_of
        self.member_of_any = member_of_any

        if self.regex and self.format:
            raise Exception("Cannot set both 'regex' and 'format'")

        if self.protocol not in ("both", "IPv4", "IPv6"):
            raise Exception(
                "'protocol' (for validating IP addresses) must be one of: both, IPv4, IPv6"
            )

        if self.format is not None and self.format not in (
            "uuid",
            "email",
            "slug",
            "url",
            "ipv4",
            "ipv6",
            "file_path",
        ):
            raise Exception(
                "'format' must be one of: uuid, email, slug, url, ip_address, file_path"
            )

        if self.param_type and self.param_type not in (
            "body",
            "query_param",
            "path",
            "current_user",
            "header",
            # "cookie",
        ):
            raise Exception(
                "'param_type' must be one of: body, query_param, path, current_user, header"
            )
