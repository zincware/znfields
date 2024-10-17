[![zincware](https://img.shields.io/badge/Powered%20by-zincware-darkcyan)](https://github.com/zincware)
[![PyPI version](https://badge.fury.io/py/znfields.svg)](https://badge.fury.io/py/znfields)
[![Coverage Status](https://coveralls.io/repos/github/zincware/znfields/badge.svg?branch=main)](https://coveralls.io/github/zincware/znfields?branch=main)

# znfields

Provide a `getter` and `setter` for `dataclasses.fields` to allow e.g. for lazy
evaluation or field content validation.

```bash
pip install znfields
```

## Example

The `znfields.field` supports all arguments from `dataclasses.field` with the
additional `getter` argument.

```python
import dataclasses
import znfields

def getter(self, name) -> str:
    return f"{name}:{self.__dict__[name]}"

def setter(self, name, value) -> None:
    if not isinstance(value, float):
        raise ValueError(f"Value {value} is not a float")
    self.__dict__[name] = value

@dataclasses.dataclass
class MyModel(znfields.Base):
    parameter: float = znfields.field(getter=getter, setter=setter)
```
