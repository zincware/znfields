# lazyfields

Provide a `getter` for `dataclasses.fields` to allow e.g. for lazy evaluation.

```bash
pip install lazyfields
```

## Example

```python
import dataclasses
import lazyfields

def example1_parameter_getter(self, name):
    return f"{name}:{self.__dict__[name]}"

@dataclasses.dataclass
class Example3(lazyfields.Base):
    parameter: float = lazyfields.field(getter=example1_parameter_getter)
```
