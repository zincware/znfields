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
