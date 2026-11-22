# LMLM Tensor — NumPy CPU Backend

A minimal LMLM-owned tensor abstraction backed by NumPy.

## Requirements

- Python 3.9+
- NumPy

Install NumPy:

```bash
python -m pip install numpy
```

## Quick start

```python
import numpy as np
from lmlm_tensor import Tensor, tensor

x = tensor([[1, 2], [3, 4]], dtype=np.float32)
y = Tensor.ones((2, 2), dtype=np.float32)

z = x @ y
print(z)
print(z.numpy())
print(z.spec)
```

## Run tests

```bash
python -m unittest -v
```

## Current scope

- CPU tensors backed by `numpy.ndarray`
- Shape, dtype, size, byte-count, and device metadata
- Broadcasting arithmetic
- Matrix multiplication
- Reshape, transpose, indexing, and reductions
- Safe NumPy export by copying by default

## Explicit limitations

This first backend does not implement automatic differentiation, CUDA/GPU
execution, distributed tensors, serialization, graph compilation, or a
production memory allocator. Those should be added behind the LMLM Tensor
interface rather than leaking backend-specific behavior into model code.
