import dataclasses
import functools
from typing import Any, Callable, Optional


class _ZNFIELDS_GETTER_TYPE:
    pass


class _ZNFIELDS_SETTER_TYPE:
    pass


ZNFIELDS_GETTER_TYPE = _ZNFIELDS_GETTER_TYPE()
ZNFIELDS_SETTER_TYPE = _ZNFIELDS_SETTER_TYPE()


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
        lazy = field.metadata.get(ZNFIELDS_GETTER_TYPE)
        if lazy:
            return lazy(self, name)
        return super().__getattribute__(name)

    def __setattr__(self, name: str, value: Any) -> None:
        if not dataclasses.is_dataclass(self):
            raise TypeError(f"{self} is not a dataclass")
        try:
            field = next(
                field for field in dataclasses.fields(self) if field.name == name
            )
        except StopIteration:
            return super().__setattr__(name, value)
        setter = field.metadata.get(ZNFIELDS_SETTER_TYPE)
        if setter:
            setter(self, name, value)
        else:
            super().__setattr__(name, value)


@functools.wraps(dataclasses.field)
def field(
    *,
    getter: Optional[Callable[[Any, str], Any]] = None,
    setter: Optional[Callable[[Any, str, Any], None]] = None,
    **kwargs,
) -> dataclasses.Field:
    if getter is not None:
        if "metadata" in kwargs:
            if not isinstance(kwargs["metadata"], dict):
                raise TypeError(
                    f"metadata must be a dict, not {type(kwargs['metadata'])}"
                )
            kwargs["metadata"][ZNFIELDS_GETTER_TYPE] = getter
        else:
            kwargs["metadata"] = {ZNFIELDS_GETTER_TYPE: getter}
    if setter is not None:
        if "init" in kwargs:
            if not kwargs["init"]:
                raise ValueError("init must be True")
        else:
            kwargs["init"] = True
        if "metadata" in kwargs:
            if not isinstance(kwargs["metadata"], dict):
                raise TypeError(
                    f"metadata must be a dict, not {type(kwargs['metadata'])}"
                )
            kwargs["metadata"][ZNFIELDS_SETTER_TYPE] = setter
        else:
            kwargs["metadata"] = {ZNFIELDS_SETTER_TYPE: setter}
    return dataclasses.field(**kwargs)
