import znfields
import pytest

def getter(self, name):
    return f"{name}:{self.__dict__[name]}"

def setter(self, name, value):
    if not isinstance(value, float):
        raise ValueError(f"Value {value} is not a float")
    self.__dict__[name] = value

@znfields.dataclass
class MyNode:
    value: float = znfields.field(getter=getter, setter=setter)

def test_decorated():
    node = MyNode(value=3.14)
    assert node.value == "value:3.14"
    with pytest.raises(ValueError):
        node.value = 42