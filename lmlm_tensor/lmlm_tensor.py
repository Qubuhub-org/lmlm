"""LMLM tensor abstraction with a NumPy CPU backend.

This is a small, dependency-light foundation. It deliberately does not implement
autograd, GPU execution, distributed execution, or implicit device transfers.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Optional, Sequence, Tuple, Union
import numpy as np

ArrayLike = Any
Shape = Tuple[int, ...]


class TensorError(Exception):
    """Base exception for LMLM tensor errors."""


class ShapeError(TensorError):
    """Raised when an operation receives incompatible shapes."""


class DTypeError(TensorError):
    """Raised when a requested dtype cannot be used."""


@dataclass(frozen=True)
class TensorSpec:
    shape: Shape
    dtype: str
    device: str = "cpu"


class NumpyBackend:
    """CPU backend. Backend methods are the only layer that directly uses NumPy."""

    name = "numpy"
    device = "cpu"

    def asarray(self, value: ArrayLike, dtype=None, copy: bool = False) -> np.ndarray:
        try:
            arr = np.array(value, dtype=dtype, copy=True) if copy else np.asarray(value, dtype=dtype)
        except (TypeError, ValueError) as exc:
            raise DTypeError(str(exc)) from exc
        if arr.dtype.kind in {"O", "U", "S", "V"}:
            raise DTypeError(f"Unsupported tensor dtype: {arr.dtype}")
        return arr

    def matmul(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        try:
            return np.matmul(a, b)
        except ValueError as exc:
            raise ShapeError(f"matmul shape mismatch: {a.shape} and {b.shape}") from exc


_DEFAULT_BACKEND = NumpyBackend()


class Tensor:
    """LMLM-owned tensor interface backed by a NumPy ndarray."""

    __slots__ = ("_array", "_backend")

    def __init__(
        self,
        data: ArrayLike,
        dtype=None,
        *,
        copy: bool = False,
        backend: Optional[NumpyBackend] = None,
    ):
        self._backend = backend or _DEFAULT_BACKEND
        self._array = self._backend.asarray(data, dtype=dtype, copy=copy)

    @classmethod
    def zeros(cls, shape: Sequence[int], dtype=np.float32) -> "Tensor":
        return cls(np.zeros(tuple(shape), dtype=dtype))

    @classmethod
    def ones(cls, shape: Sequence[int], dtype=np.float32) -> "Tensor":
        return cls(np.ones(tuple(shape), dtype=dtype))

    @classmethod
    def full(cls, shape: Sequence[int], fill_value: Any, dtype=None) -> "Tensor":
        return cls(np.full(tuple(shape), fill_value, dtype=dtype))

    @classmethod
    def arange(cls, *args, dtype=None) -> "Tensor":
        return cls(np.arange(*args, dtype=dtype))

    @property
    def shape(self) -> Shape:
        return self._array.shape

    @property
    def ndim(self) -> int:
        return self._array.ndim

    @property
    def size(self) -> int:
        return self._array.size

    @property
    def dtype(self):
        return self._array.dtype

    @property
    def nbytes(self) -> int:
        return self._array.nbytes

    @property
    def spec(self) -> TensorSpec:
        return TensorSpec(self.shape, str(self.dtype), self._backend.device)

    @property
    def device(self) -> str:
        return self._backend.device

    def numpy(self, *, copy: bool = True) -> np.ndarray:
        """Return a NumPy array; copy by default to protect tensor ownership."""
        return self._array.copy() if copy else self._array

    def astype(self, dtype, *, copy: bool = True) -> "Tensor":
        return Tensor(self._array.astype(dtype, copy=copy), backend=self._backend)

    def reshape(self, *shape: int) -> "Tensor":
        if len(shape) == 1 and isinstance(shape[0], (tuple, list)):
            shape = tuple(shape[0])
        try:
            return Tensor(self._array.reshape(*shape), backend=self._backend)
        except ValueError as exc:
            raise ShapeError(f"cannot reshape {self.shape} to {shape}") from exc

    def transpose(self, *axes: int) -> "Tensor":
        try:
            arr = self._array.transpose(*axes) if axes else self._array.transpose()
            return Tensor(arr, backend=self._backend)
        except ValueError as exc:
            raise ShapeError(f"invalid transpose axes {axes} for {self.shape}") from exc

    @property
    def T(self) -> "Tensor":
        return self.transpose()

    def sum(self, axis=None, keepdims: bool = False) -> "Tensor":
        return Tensor(self._array.sum(axis=axis, keepdims=keepdims), backend=self._backend)

    def mean(self, axis=None, keepdims: bool = False) -> "Tensor":
        return Tensor(self._array.mean(axis=axis, keepdims=keepdims), backend=self._backend)

    def max(self, axis=None, keepdims: bool = False) -> "Tensor":
        return Tensor(self._array.max(axis=axis, keepdims=keepdims), backend=self._backend)

    def matmul(self, other: "Tensor") -> "Tensor":
        other = self._coerce(other)
        return Tensor(self._backend.matmul(self._array, other._array), backend=self._backend)

    def _coerce(self, other) -> "Tensor":
        if isinstance(other, Tensor):
            if other.device != self.device:
                raise TensorError(f"device mismatch: {self.device} vs {other.device}")
            return other
        return Tensor(other, backend=self._backend)

    def _binary(self, other, op) -> "Tensor":
        rhs = self._coerce(other)
        try:
            return Tensor(op(self._array, rhs._array), backend=self._backend)
        except ValueError as exc:
            raise ShapeError(
                f"operation cannot broadcast shapes {self.shape} and {rhs.shape}"
            ) from exc

    def __add__(self, other): return self._binary(other, np.add)
    def __radd__(self, other): return self.__add__(other)
    def __sub__(self, other): return self._binary(other, np.subtract)
    def __rsub__(self, other): return self._coerce(other)._binary(self, np.subtract)
    def __mul__(self, other): return self._binary(other, np.multiply)
    def __rmul__(self, other): return self.__mul__(other)
    def __truediv__(self, other): return self._binary(other, np.divide)
    def __rtruediv__(self, other): return self._coerce(other)._binary(self, np.divide)
    def __matmul__(self, other): return self.matmul(other)
    def __neg__(self): return Tensor(-self._array, backend=self._backend)

    def __getitem__(self, key) -> "Tensor":
        return Tensor(self._array[key], backend=self._backend)

    def __len__(self):
        return len(self._array)

    def __repr__(self) -> str:
        return f"Tensor(shape={self.shape}, dtype={self.dtype}, device='{self.device}')"


def tensor(data: ArrayLike, dtype=None, *, copy: bool = False) -> Tensor:
    """Convenience factory for constructing an LMLM Tensor."""
    return Tensor(data, dtype=dtype, copy=copy)
