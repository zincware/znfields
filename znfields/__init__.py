import dataclasses
import functools
from typing import Any, Callable, Optional
from typing import Any, Callable, Optional, Type, TypeVar, Union, overload, Protocol, Generic
import dataclasses


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

T = TypeVar("T")
Self = TypeVar("Self", bound="Base")

class GetterSetter(Protocol[T]):
    """Protocol to enforce correct typing for descriptors."""

    @overload
    def __get__(self, instance: None, owner: type) -> "GetterSetter[T]": ...
    
    @overload
    def __get__(self, instance: Self, owner: Type[Self]) -> T: ...
    
    def __get__(self, instance: Optional[Self], owner: Type[Self]) -> Union[T, "GetterSetter[T]"]: ...
    
    def __set__(self, instance: Self, value: T) -> None: ...


class ZnField(Generic[T], GetterSetter[T]):
    """A type-safe descriptor for ZnTrack fields."""

    def __init__(
        self,
        *,
        getter: Optional[Callable[[Any, str], T]] = None,
        setter: Optional[Callable[[Any, str, T], None]] = None,
        **kwargs,
    ):
        self.getter = getter
        self.setter = setter
        self.field = dataclasses.field(**kwargs)

    def __set_name__(self, owner: type, name: str):
        """Store the attribute name."""
        self.name = name

    def __get__(self, instance: Optional[Self], owner: Type[Self]) -> Union[T, "ZnField[T]"]:
        if instance is None:
            return self  # Access via class
        value = instance.__dict__[self.name]
        return self.getter(instance, self.name) if self.getter else value

    def __set__(self, instance: Self, value: T) -> None:
        if self.setter:
            self.setter(instance, self.name, value)
        else:
            instance.__dict__[self.name] = value


# ✅ Correct type preservation
def field(
    *,
    getter: Optional[Callable[[Any, str], T]] = None,
    setter: Optional[Callable[[Any, str, T], None]] = None,
    **kwargs,
) -> ZnField[T]:
    """Return a descriptor that preserves type information."""
    return ZnField(getter=getter, setter=setter, **kwargs)
