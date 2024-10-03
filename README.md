[![zincware](https://img.shields.io/badge/Powered%20by-zincware-darkcyan)](https://github.com/zincware)
[![PyPI version](https://badge.fury.io/py/znfields.svg)](https://badge.fury.io/py/znfields)
[![Coverage Status](https://coveralls.io/repos/github/zincware/znfields/badge.svg?branch=main)](https://coveralls.io/github/zincware/znfields?branch=main)

# znfields

Provide a `getter` for `dataclasses.fields` to allow e.g. for lazy evaluation.

```bash
pip install znfields
```

## Example

```python
import dataclasses
import znfields

def example1_parameter_getter(self, name):
    return f"{name}:{self.__dict__[name]}"

@dataclasses.dataclass
class Example3(znfields.Base):
    parameter: float = znfields.field(getter=example1_parameter_getter)
```
