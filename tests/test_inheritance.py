import znfields
import dataclasses

def getter(self, name):
    return f"{name}:{self.__dict__[name]}"

def setter(self, name, value):
    if not isinstance(value, float):
        raise ValueError(f"Value {value} is not a float")
    self.__dict__[name] = value

@znfields.dataclass
class MyNodeOverwrite(znfields.Base):
    value: float = znfields.field(getter=getter, setter=setter)

    def __getattribute__(self, name: str) -> znfields.Any:
        if name == "value":
            return 42
        return super().__getattribute__(name)
    


def test_MyNodeOverwrite():
    x = MyNodeOverwrite(value=3.14)
    assert x.value == 42