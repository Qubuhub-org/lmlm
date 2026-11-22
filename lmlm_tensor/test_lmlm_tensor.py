import unittest
import numpy as np
from lmlm_tensor import Tensor, ShapeError, tensor


class TensorTests(unittest.TestCase):
    def test_metadata(self):
        x = tensor([[1, 2], [3, 4]], dtype=np.float32)
        self.assertEqual(x.shape, (2, 2))
        self.assertEqual(x.ndim, 2)
        self.assertEqual(x.spec.device, "cpu")
        self.assertEqual(x.dtype, np.dtype("float32"))

    def test_broadcast_arithmetic(self):
        x = tensor([[1], [2], [3]], dtype=np.float32)
        y = tensor([10, 20], dtype=np.float32)
        np.testing.assert_array_equal((x + y).numpy(), [[11, 21], [12, 22], [13, 23]])

    def test_matmul(self):
        a = tensor([[1, 2], [3, 4]], dtype=np.float32)
        b = tensor([[2], [1]], dtype=np.float32)
        np.testing.assert_array_equal((a @ b).numpy(), [[4], [10]])

    def test_shape_error(self):
        with self.assertRaises(ShapeError):
            tensor([1, 2, 3]) @ tensor([1, 2])

    def test_reshape_and_transpose(self):
        x = Tensor.arange(6).reshape(2, 3)
        self.assertEqual(x.T.shape, (3, 2))
        self.assertEqual(x.reshape(3, 2).shape, (3, 2))

    def test_numpy_copy_is_safe_by_default(self):
        x = tensor([1, 2, 3])
        exported = x.numpy()
        exported[0] = 99
        self.assertEqual(x.numpy()[0], 1)


if __name__ == "__main__":
    unittest.main()
