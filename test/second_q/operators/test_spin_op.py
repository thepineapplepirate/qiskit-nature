# This code is part of Qiskit.
#
# (C) Copyright IBM 2021, 2023.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""Test for SpinOp"""

import unittest
from test import QiskitNatureTestCase

import numpy as np
from ddt import data, ddt

from qiskit_nature.second_q.operators import SpinOp


@ddt
class TestSpinOp(QiskitNatureTestCase):
    """SpinOp tests."""

    op1 = SpinOp({"X_0 Y_0": 1}, num_spins=1)
    op2 = SpinOp({"X_0^2 Z_0": 2}, num_spins=1)
    op3 = SpinOp({"X_0 Y_0": 1, "X_0^2 Z_0": 2}, num_spins=1)
    op4 = SpinOp({"": 1}, num_spins=2)

    spin_1_matrix = {
        "X_0": np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]]) / np.sqrt(2),
        "Y_0": np.array([[0, -1j, 0], [1j, 0, -1j], [0, 1j, 0]]) / np.sqrt(2),
        "Z_0": np.array([[1, 0, 0], [0, 0, 0], [0, 0, -1]]),
    }

    def test_neg(self):
        """Test __neg__"""
        spin_op = -self.op1
        targ = SpinOp({"X_0 Y_0": -1}, num_spins=1)
        self.assertEqual(spin_op, targ)

    def test_mul(self):
        """Test __mul__, and __rmul__"""
        with self.subTest("rightmul"):
            spin_op = self.op1 * 2
            targ = SpinOp({"X_0 Y_0": 2}, num_spins=1)
            self.assertEqual(spin_op, targ)

        with self.subTest("left mul"):
            spin_op = (2 + 1j) * self.op3
            targ = SpinOp({"X_0 Y_0": (2 + 1j), "X_0^2 Z_0": (4 + 2j)}, num_spins=1)
            self.assertEqual(spin_op, targ)

    def test_div(self):
        """Test __truediv__"""
        spin_op = self.op1 / 2
        targ = SpinOp({"X_0 Y_0": 0.5}, num_spins=1)
        self.assertEqual(spin_op, targ)

    def test_add(self):
        """Test __add__"""
        spin_op = self.op1 + self.op2
        targ = self.op3
        self.assertEqual(spin_op, targ)

        with self.subTest("sum"):
            spin_op = sum(SpinOp({label: 1}, num_spins=3) for label in ["X_0", "Z_1", "X_2 Z_2"])
            targ = SpinOp({"X_0": 1, "Z_1": 1, "X_2 Z_2": 1})
            self.assertEqual(spin_op, targ)

    def test_sub(self):
        """Test __sub__"""
        spin_op = self.op3 - self.op2
        targ = SpinOp({"X_0 Y_0": 1, "X_0^2 Z_0": 0}, num_spins=1)
        self.assertEqual(spin_op, targ)

    def test_simplify(self):
        """Test simplify"""
        with self.subTest("do not simplify"):
            spin_op = SpinOp({"X_0 Y_0": 1, "X_0 X_0 X_0 Y_0": 1}, num_spins=1)
            simplified_op = spin_op.simplify()
            targ = SpinOp({"X_0 Y_0": 1, "X_0 X_0 X_0 Y_0": 1}, num_spins=1)
            self.assertEqual(simplified_op, targ)

        with self.subTest("do not simplify to identity"):
            spin_op = SpinOp({"X_0 X_0": 1}, num_spins=1)
            simplified_op = spin_op.simplify()
            targ = SpinOp({"X_0 X_0": 1}, num_spins=1)
            self.assertEqual(simplified_op, targ)

        with self.subTest("expand label"):
            spin_op = SpinOp({"X_0^3": 1}, num_spins=1)
            simplified_op = spin_op.simplify()
            targ = SpinOp({"X_0 X_0 X_0": 1}, num_spins=1)
            self.assertEqual(simplified_op, targ)

        with self.subTest("simplify empty"):
            spin_op = SpinOp({"": 5}, num_spins=3)
            simplified_op = spin_op.simplify()
            targ = SpinOp({"": 5}, num_spins=3)
            self.assertEqual(simplified_op, targ)

        with self.subTest("simplify identity"):
            spin_op = self.op4
            simplified_op = spin_op.simplify()
            targ = SpinOp({"": 1}, num_spins=3)
            self.assertEqual(simplified_op, targ)

        with self.subTest("simplify zero"):
            spin_op = self.op1 - self.op1
            simplified_op = spin_op.simplify()
            targ = SpinOp.zero()
            self.assertEqual(simplified_op, targ)

        with self.subTest("simplify 0 exponent"):
            spin_op = SpinOp({"X_0^0": 1}, num_spins=1)
            simplified_op = spin_op.simplify()
            targ = SpinOp.one()
            self.assertEqual(simplified_op, targ)

    def test_conjugate(self):
        """Test conjugate method"""
        spin_op = SpinOp(
            {"": 1j, "X_0 Y_1 X_1": 3, "X_0 Y_0 X_1": 1j, "Y_0 Y_1": 2 + 4j}, num_spins=3
        ).conjugate()
        targ = SpinOp(
            {"": -1j, "X_0 Y_1 X_1": -3, "X_0 Y_0 X_1": 1j, "Y_0 Y_1": 2 - 4j}, num_spins=3
        )
        self.assertEqual(spin_op, targ)

    def test_transpose(self):
        """Test transpose method"""
        spin_op = SpinOp(
            {"": 1j, "X_0 Y_1 X_1": 3, "X_0 Y_0 X_1": 1j, "Y_0 Y_1": 2 + 4j}, num_spins=3
        ).transpose()
        targ = SpinOp(
            {"": 1j, "X_1 Y_1 X_0": -3, "X_1 Y_0 X_0": -1j, "Y_1 Y_0": 2 + 4j}, num_spins=3
        )
        self.assertEqual(spin_op, targ)

    def test_adjoint(self):
        """Test adjoint method"""
        spin_op = SpinOp(
            {"": 1j, "X_0 Y_1 X_1": 3, "X_0 Y_0 X_1": 1j, "Y_0 Y_1": 2 + 4j}, num_spins=3
        ).adjoint()
        targ = SpinOp(
            {"": -1j, "X_1 Y_1 X_0": 3, "X_1 Y_0 X_0": -1j, "Y_1 Y_0": 2 - 4j}, num_spins=3
        )
        self.assertEqual(spin_op, targ)

    def test_tensor(self):
        """Test tensor multiplication"""
        spin_op = self.op1.tensor(self.op2)
        targ = SpinOp({"X_0 Y_0 X_1 X_1 Z_1": 2}, num_spins=2)
        self.assertEqual(spin_op, targ)

    def test_expand(self):
        """Test reversed tensor multiplication"""
        spin_op = self.op1.expand(self.op2)
        targ = SpinOp({"X_0 X_0 Z_0 X_1 Y_1": 2}, num_spins=2)
        self.assertEqual(spin_op, targ)

    def test_compose(self):
        """Test operator composition"""
        with self.subTest("single compose"):
            spin_op = SpinOp({"X_0 X_1": 1}, num_spins=2) @ SpinOp({"Y_0": 2}, num_spins=2)
            targ = SpinOp({"X_0 X_1 Y_0": 2}, num_spins=2)
            self.assertEqual(spin_op, targ)

        with self.subTest("multi compose"):
            spin_op = SpinOp({"X_0 X_1 Y_1": 1, "X_0 Y_0 Y_1": -1}, num_spins=2) @ SpinOp(
                {"Y_0": 1, "X_0 Y_1": -1}, num_spins=2
            )
            targ = SpinOp(
                {
                    "X_0 X_1 Y_1 Y_0": 1,
                    "X_0 X_1 Y_1 X_0 Y_1": -1,
                    "X_0 Y_0 Y_1 Y_0": -1,
                    "X_0 Y_0 Y_1 X_0 Y_1": 1,
                },
                num_spins=2,
            )
            self.assertEqual(spin_op, targ)

    @data("X_0", "Y_0", "Z_0")
    def test_to_matrix(self, label):
        """Test to_matrix for single qutrit op"""
        actual = SpinOp({label: 1}, 1)
        actual = actual.to_matrix()
        np.testing.assert_array_almost_equal(actual, self.spin_1_matrix[label])

    def test_to_matrix_multi_site(self):
        """Test the to_matrix method when multiple sites are involved.

        This is a regression test against https://github.com/Qiskit/qiskit-nature/issues/1187.
        """
        with self.subTest("spin 1/2; 2 sites"):
            op = SpinOp({"X_0 X_1": 1, "Y_0 Y_1": 1, "Z_0 Z_1": 1})
            actual = op.to_matrix()
            expected = 0.25 * np.diag([1, -1, -1, 1])
            expected[1, 2] = 0.5
            expected[2, 1] = 0.5
            np.testing.assert_array_almost_equal(actual, expected)

        with self.subTest("spin 1; 2 sites"):
            op = SpinOp({"X_0 X_1": 1, "Y_0 Y_1": 1, "Z_0 Z_1": 1}, spin=1)
            actual = op.to_matrix()
            expected = np.zeros((9, 9))
            for i, j, v in zip(
                [0, 1, 2, 2, 3, 4, 4, 5, 6, 6, 7, 8],
                [0, 3, 2, 4, 1, 2, 6, 7, 4, 6, 5, 8],
                [1, 1, -1, 1, 1, 1, 1, 1, 1, -1, 1, 1],
            ):
                expected[i, j] = v
            np.testing.assert_array_almost_equal(actual, expected)

        with self.subTest("spin 1/2; 3 sites"):
            op = SpinOp({"X_0 X_1 X_2": 1, "Y_0 Y_2": 1, "Z_1": 1})
            actual = op.to_matrix()
            expected = np.zeros((8, 8))
            for i, j, v in zip(
                [0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 5, 6, 6, 6, 7, 7, 7],
                [0, 5, 7, 1, 4, 6, 2, 5, 7, 3, 4, 6, 1, 3, 4, 0, 2, 5, 1, 3, 6, 0, 2, 7],
                # fmt: off
                [
                    0.5, -0.25, 0.125, 0.5, 0.25, 0.125, -0.5, 0.125, -0.25, -0.5, 0.125, 0.25,
                     0.25, 0.125, 0.5, -0.25, 0.125, 0.5, 0.125, 0.25, -0.5, 0.125, -0.25, -0.5,
                ],
                # fmt: on
            ):
                expected[i, j] = v
            np.testing.assert_array_almost_equal(actual, expected)

    def test_index_order(self):
        """Test index_order method"""
        with self.subTest("Test for single operators"):
            orig = SpinOp({"Y_0": 1})
            spin_op = orig.index_order()
            self.assertEqual(spin_op, orig)

        with self.subTest("Test for multiple operators 1"):
            orig = SpinOp({"X_1 X_0": 1})
            spin_op = orig.index_order()
            targ = SpinOp({"X_0 X_1": 1})
            self.assertEqual(spin_op, targ)

        with self.subTest("Test for multiple operators 2"):
            orig = SpinOp({"X_2 Y_0 Z_1 X_0": 1, "Z_0 X_1": 2})
            spin_op = orig.index_order()
            targ = SpinOp({"Y_0 X_0 Z_1 X_2": 1, "Z_0 X_1": 2})
            self.assertEqual(spin_op, targ)

        with self.subTest("Test index ordering simplifies"):
            orig = SpinOp({"X_0 Y_1": 1, "Y_1 X_0": 1, "": 0.0})
            spin_op = orig.index_order()
            targ = SpinOp({"X_0 Y_1": 2})
            self.assertEqual(spin_op, targ)

        with self.subTest("index order + simplify"):
            orig = SpinOp({"X_0 Y_0 X_1 Y_0": 1, "X_0 X_1": 2})
            spin_op = orig.index_order().simplify()
            targ = SpinOp({"X_0 Y_0 Y_0 X_1": 1, "X_0 X_1": 2})
            self.assertEqual(spin_op, targ)

    def test_terms(self):
        """Test terms generator."""
        op = SpinOp(
            {
                "X_0": 1,
                "X_0 Z_1": 2,
                "Z_1 Y_1 X_2": 2,
            }
        )

        terms = [([("X", 0)], 1), ([("X", 0), ("Z", 1)], 2), ([("Z", 1), ("Y", 1), ("X", 2)], 2)]

        with self.subTest("terms"):
            self.assertEqual(list(op.terms()), terms)

        with self.subTest("from_terms"):
            self.assertEqual(SpinOp.from_terms(terms), op)

    def test_permute_indices(self):
        """Test index permutation method."""
        op = SpinOp(
            {
                "X_0 Y_1": 1,
                "Z_1 X_2": 2,
            },
            num_spins=4,
        )

        with self.subTest("wrong permutation length"):
            with self.assertRaises(ValueError):
                _ = op.permute_indices([1, 0])

        with self.subTest("actual permutation"):
            permuted_op = op.permute_indices([2, 1, 3, 0])

            self.assertEqual(permuted_op, SpinOp({"X_2 Y_1": 1, "Z_1 X_3": 2}, num_spins=4))


if __name__ == "__main__":
    unittest.main()
