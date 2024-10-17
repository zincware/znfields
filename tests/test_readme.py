import dataclasses

import pytest

import znfields


def getter(self, name):
    return f"{name}:{self.__dict__[name]}"


def setter(self, name, value):
    if not isinstance(value, float):
        raise ValueError(f"Value {value} is not a float")
    self.__dict__[name] = value


@dataclasses.dataclass
class MyModel(znfields.Base):
    parameter: float = znfields.field(getter=getter, setter=setter)


def test_readme():
    model = MyModel(parameter=3.14)
    assert model.parameter == "parameter:3.14"
    with pytest.raises(ValueError):
        model.parameter = 42
