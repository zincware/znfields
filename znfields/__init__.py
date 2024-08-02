import dataclasses
import functools
from typing import Any, Callable, Optional

_GETTER = "znfields.getter"


class Base:
    def __getattribute__(self, name: str) -> Any:
        if name.startswith("__") and name.endswith("__"):
            return super().__getattribute__(name)
        if not dataclasses.is_dataclass(self):
            raise TypeError(f"{self} is not a dataclass")
        try:
            field = next(
                field for field in dataclasses.fields(self) if field.name == name
            )
        except StopIteration:
            return super().__getattribute__(name)
        lazy = field.metadata.get(_GETTER)
        if lazy:
            return lazy(self, name)
        return super().__getattribute__(name)


@functools.wraps(dataclasses.field)
def field(*, getter: Optional[Callable[[Any, str], Any]] = None, **kwargs):
    if getter is not None:
        if "metadata" in kwargs:
            if not isinstance(kwargs["metadata"], dict):
                raise TypeError(
                    f"metadata must be a dict, not {type(kwargs['metadata'])}"
                )
            kwargs["metadata"][_GETTER] = getter
        else:
            kwargs["metadata"] = {_GETTER: getter}
    return dataclasses.field(**kwargs)
