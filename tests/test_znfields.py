import dataclasses
import znfields
import pytest


def example1_parameter_getter(self, name):
    return f"{name}:{self.__dict__[name]}"


@dataclasses.dataclass
class Example1(znfields.Base):
    parameter: float = znfields.field(getter=example1_parameter_getter)


def test_example1():
    example = Example1(parameter=1)
    assert example.parameter == "parameter:1"


def test_example1_with_update():
    example = Example1(parameter=1)
    assert example.parameter == "parameter:1"
    example.parameter = 2
    assert example.parameter == "parameter:2"


@dataclasses.dataclass
class Example2(znfields.Base):
    parameter: float = znfields.field()


def test_example2():
    example = Example2(parameter=1)
    assert example.parameter == 1


def test_wrong_metadata():
    with pytest.raises(TypeError):
        znfields.field(getter=example1_parameter_getter, metadata="Hello")


@dataclasses.dataclass
class Example3(znfields.Base):
    parameter: float = znfields.field(
        getter=example1_parameter_getter, metadata={"category": "test"}
    )


def test_example3():
    example = Example3(parameter=1)
    assert example.parameter == "parameter:1"

    field = dataclasses.fields(example)[0]
    assert field.metadata == {
        "category": "test",
        znfields.ZNFIELDS_GETTER_TYPE: example1_parameter_getter,
    }


def test_dataclass_field_without_getter():
    @dataclasses.dataclass
    class DataClassWithoutGetter(znfields.Base):
        field_without_getter: int = 42

    obj = DataClassWithoutGetter()
    assert obj.field_without_getter == 42


def test_dataclass_field_with_getter():
    def getter(instance, name: str):
        return f"lazy_{name}"

    @dataclasses.dataclass
    class DataClassWithGetter(znfields.Base):
        field_with_getter: int = znfields.field(getter=getter, default=0)

    obj = DataClassWithGetter()
    assert obj.field_with_getter == "lazy_field_with_getter"


def test_non_existent_attribute():
    @dataclasses.dataclass
    class DataClass(znfields.Base):
        existing_field: int = 42

    obj = DataClass()
    with pytest.raises(AttributeError):
        _ = obj.non_existent_field


def test_not_a_dataclass():
    class NotADataclass(znfields.Base):
        regular_field: str = "regular"

    instance = NotADataclass()
    with pytest.raises(TypeError):
        _ = instance.regular_field


def test_lazy_loading():
    def lazy_getter(instance, name):
        return f"lazy value for {name}"

    @dataclasses.dataclass
    class MyDataClass(znfields.Base):
        regular_field: str
        lazy_field: str = znfields.field(default=None, getter=lazy_getter)

    instance = MyDataClass(regular_field="regular")
    assert instance.regular_field == "regular"
    assert instance.lazy_field == "lazy value for lazy_field"


def test_no_lazy_loading():
    @dataclasses.dataclass
    class MyDataClass(znfields.Base):
        regular_field: str
        lazy_field: str = "default"

    instance = MyDataClass(regular_field="regular")
    assert instance.regular_field == "regular"
    assert instance.lazy_field == "default"


def test_metadata_must_be_dict():
    with pytest.raises(TypeError):
        znfields.field(metadata="not a dict", getter=lambda instance, name: None)
