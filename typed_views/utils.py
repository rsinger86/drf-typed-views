from enum import Enum
from typing import Any, List, Tuple
import inspect


def parse_list_annotation(annotation) -> Tuple[bool, Any]:
    if "List[" in str(annotation):
        return True, annotation.__args__[0]
    return False, None


def parse_enum_annotation(annotation) -> Tuple[bool, List[Any]]:
    if inspect.isclass(annotation) and issubclass(annotation, Enum):
        return True, [_.value for _ in annotation]
    return False, []
