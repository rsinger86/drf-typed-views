import inspect
import operator
from enum import Enum
from functools import reduce
from typing import Any, List, Optional, Tuple

from pydantic import BaseModel as PydanticBaseModel
from typesystem import Schema as TypeSystemSchema


def parse_list_annotation(annotation) -> Tuple[bool, Any]:
    if "List[" in str(annotation):
        return True, annotation.__args__[0]
    return False, None


def parse_enum_annotation(annotation) -> Tuple[bool, List[Any]]:
    if inspect.isclass(annotation) and issubclass(annotation, Enum):
        return True, [_.value for _ in annotation]
    return False, []


def parse_complex_type(annotation) -> Tuple[bool, Optional[str]]:
    if inspect.isclass(annotation) and issubclass(annotation, PydanticBaseModel):
        return True, "pydantic"
    if inspect.isclass(annotation) and issubclass(annotation, TypeSystemSchema):
        return True, "typesystem"
    return False, None


def get_nested_value(dic: dict, path: str) -> Any:
    try:
        return reduce(operator.getitem, path.split("."), dic)
    except (TypeError, KeyError, ValueError):
        return None
