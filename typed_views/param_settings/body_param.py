from typing import Any

from typed_views.classes import Missing


class BodyParam(object):
    def __init__(self, default: Any = Missing):
        self.default = default
