import dataclasses

import pytest

import znfields


def getter_01(self, name):
    return f"{name}:{self.__dict__[name]}"


def setter_01(self, name, value):
    if not isinstance(value, float):
        raise ValueError(f"Value {value} is not a float")
    self.__dict__[name] = value


def stringify_list(self, name):
    content = self.__dict__[name]
    self.__dict__[name] = [str(x) for x in content]
    # Can not return a copy to append to, but must be the same object
    return self.__dict__[name]


@dataclasses.dataclass
class SetterGetterNoInit(znfields.Base):
    parameter: float = znfields.field(getter=getter_01, setter=setter_01, init=False)


@dataclasses.dataclass
class Example1(znfields.Base):
    parameter: float = znfields.field(getter=getter_01)


@dataclasses.dataclass
class Example1WithDefault(znfields.Base):
    parameter: float = znfields.field(getter=getter_01, default=1)


@dataclasses.dataclass
class Example1WithDefaultFactory(znfields.Base):
    parameter: list = znfields.field(getter=stringify_list, default_factory=list)


def test_example1():
    example = Example1(parameter=1)
    assert example.parameter == "parameter:1"

    exampe_w_default = Example1WithDefault()
    assert exampe_w_default.parameter == "parameter:1"


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
        znfields.field(getter=getter_01, metadata="Hello")


@dataclasses.dataclass
class Example3(znfields.Base):
    parameter: float = znfields.field(getter=getter_01, metadata={"category": "test"})


def test_example3():
    example = Example3(parameter=1)
    assert example.parameter == "parameter:1"

    field = dataclasses.fields(example)[0]
    assert field.metadata == {
        "category": "test",
        znfields.ZNFIELDS_GETTER_TYPE: getter_01,
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


def test_default_factory():
    example = Example1WithDefaultFactory()
    assert example.parameter == []
    example.parameter.append(1)
    assert example.parameter == ["1"]


def test_getter_setter_no_init():
    example = SetterGetterNoInit()
    with pytest.raises(ValueError):
        example.parameter = "text"

    example.parameter = 3.14
    assert example.parameter == "parameter:3.14"


@dataclasses.dataclass
class ParentClass(znfields.Base):
    parent_field: str = znfields.field(getter=getter_01)


@dataclasses.dataclass
class ChildClass(ParentClass):
    child_field: str = znfields.field(getter=getter_01)


def test_inherited_getter():
    instance = ChildClass(parent_field="parent", child_field="child")
    assert instance.parent_field == "parent_field:parent"
    assert instance.child_field == "child_field:child"


def test_setter_validation():
    example = SetterGetterNoInit()

    with pytest.raises(ValueError):
        example.parameter = "invalid value"

    with pytest.raises(KeyError):
        # dict is not set, getter raises KeyError instead of AttributeError
        assert example.parameter is None

    example.parameter = 2.71
    assert example.parameter == "parameter:2.71"


@dataclasses.dataclass
class NoDefaultField(znfields.Base):
    parameter: float = znfields.field(getter=getter_01, setter=setter_01)


def test_no_default_field():
    with pytest.raises(TypeError):
        NoDefaultField()  # should raise because no default is provided
    obj = NoDefaultField(parameter=1.23)
    assert obj.parameter == "parameter:1.23"


@dataclasses.dataclass
class CombinedGetterSetter(znfields.Base):
    parameter: float = znfields.field(getter=getter_01, setter=setter_01)


def test_combined_getter_setter():
    obj = CombinedGetterSetter(parameter=2.5)
    assert obj.parameter == "parameter:2.5"
    obj.parameter = 3.5
    assert obj.parameter == "parameter:3.5"

    with pytest.raises(ValueError):
        obj.parameter = "invalid value"


@dataclasses.dataclass
class Nested(znfields.Base):
    inner_field: float = znfields.field(getter=getter_01)


@dataclasses.dataclass
class Outer(znfields.Base):
    outer_field: Nested = dataclasses.field(default_factory=lambda: Nested(1.0))


def test_nested_dataclass():
    obj = Outer()
    assert obj.outer_field.inner_field == "inner_field:1.0"
