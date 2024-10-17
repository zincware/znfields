import dataclasses
import functools
from typing import Any, Callable, Optional


class _ZNFIELDS_GETTER_TYPE:
    """Sentinel class to identify the getter type."""

    pass


class _ZNFIELDS_SETTER_TYPE:
    """Sentinel class used to identify the setter type."""

    pass


# Sentinels to identify the getter and setter types
ZNFIELDS_GETTER_TYPE = _ZNFIELDS_GETTER_TYPE()
ZNFIELDS_SETTER_TYPE = _ZNFIELDS_SETTER_TYPE()


class Base:
    """Base class to extend dataclasses with custom getter and setter behavior
    through field metadata.

    Methods
    -------
    __getattribute__(name: str) -> Any
        Overrides the default behavior of attribute access to allow for
        custom getter functionality defined via field metadata.
    __setattr__(name: str, value: Any) -> None
        Overrides the default behavior of attribute assignment to allow for
        custom setter functionality defined via field metadata.
    """

    def __getattribute__(self, name: str) -> Any:
        """Overrides the default behavior of attribute access.

        Allow for custom getter functionality defined via field metadata.

        Raises
        ------
        TypeError: If the class is not a dataclass.
        """
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
        """Overrides the default behavior of attribute assignment.

        Allow for custom setter functionality defined via field metadata.

        Raises
        ------
        TypeError: If the class is not a dataclass.
        """
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
    """Wrapper around `dataclasses.field` to allow for defining custom
    getter and setter functions via metadata.

    Attributes
    ----------
    getter : Optional[Callable[[Any, str], Any]]
        A function that takes the instance and attribute name as arguments
        and returns the value of the attribute.
    setter : Optional[Callable[[Any, str, Any], None]]
        A function that takes the instance, attribute name, and value as
        arguments and sets the value of the attribute.

    Returns
    -------
    dataclasses.Field
        A field object with custom getter and setter functionality defined
        via metadata.

    Raises
    ------
    TypeError: If the metadata is not a dictionary.
    """
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
        if "metadata" in kwargs:
            if not isinstance(kwargs["metadata"], dict):
                raise TypeError(
                    f"metadata must be a dict, not {type(kwargs['metadata'])}"
                )
            kwargs["metadata"][ZNFIELDS_SETTER_TYPE] = setter
        else:
            kwargs["metadata"] = {ZNFIELDS_SETTER_TYPE: setter}
    return dataclasses.field(**kwargs)
