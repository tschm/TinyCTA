#    Copyright (c) 2023 Thomas Schmelzer
#
#    Permission is hereby granted, free of charge, to any person obtaining a copy
#    of this software and associated documentation files (the "Software"), to deal
#    in the Software without restriction, including without limitation the rights
#    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#    copies of the Software, and to permit persons to whom the Software is
#    furnished to do so, subject to the following conditions:
#
#    The above copyright notice and this permission notice shall be included in all
#    copies or substantial portions of the Software.
"""Linear algebra utilities that handle matrices with missing (NaN) values.

All operations extract the finite submatrix via the ``valid`` function before
performing computations, so partially-observed covariance matrices are handled
gracefully without raising errors.
"""

from __future__ import annotations

import numpy as np


def valid(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Extract the finite submatrix by checking diagonal elements.

    Args:
        matrix: A square NumPy array to be validated and processed.

    Returns:
        A tuple of (mask, submatrix) where mask is a boolean array of finite
        diagonal elements and submatrix contains only the rows and columns
        with finite diagonals.

    Raises:
        AssertionError: If the input matrix is not square.
    """
    if matrix.shape[0] != matrix.shape[1]:
        raise AssertionError

    v = np.isfinite(np.diag(matrix))
    return v, matrix[:, v][v]


def a_norm(vector: np.ndarray, matrix: np.ndarray | None = None) -> float:
    """Calculate the generalized norm of a vector with respect to a matrix.

    Computes the Euclidean norm when no matrix is provided, or the quadratic
    form ``sqrt(v^T A v)`` when a matrix is given.

    Args:
        vector: The input one-dimensional vector.
        matrix: Square matrix defining the quadratic form. Its size must match
            the vector length. If None, the standard Euclidean norm is returned.

    Returns:
        The computed norm, or NaN if no valid entries exist.

    Raises:
        AssertionError: If the matrix is not square or its dimensions do not
            match the vector.
    """
    if matrix is None:
        return float(np.linalg.norm(vector[np.isfinite(vector)], 2))

    if matrix.shape[0] != matrix.shape[1]:
        raise AssertionError

    if vector.size != matrix.shape[0]:
        raise AssertionError

    v, mat = valid(matrix)

    if v.any():
        return float(np.sqrt(np.dot(vector[v], np.dot(mat, vector[v]))))
    return float("nan")


def inv_a_norm(vector: np.ndarray, matrix: np.ndarray | None = None) -> float:
    """Calculate the inverse A-norm of a vector using an optional matrix.

    Computes ``sqrt(v^T A^{-1} v)`` when a matrix is provided, or the
    Euclidean norm of finite entries when no matrix is given.

    Args:
        vector: The input vector for which the norm is to be calculated.
        matrix: Square matrix used for computing the norm. If not provided,
            the Euclidean norm of finite entries is returned.

    Returns:
        The computed norm as a float. Returns ``np.nan`` if no valid entries exist.

    Raises:
        AssertionError: If the matrix is not square or the vector size is
            incompatible with the matrix dimensions.
    """
    if matrix is None:
        return float(np.linalg.norm(vector[np.isfinite(vector)], 2))

    if matrix.shape[0] != matrix.shape[1]:
        raise AssertionError

    if vector.size != matrix.shape[0]:
        raise AssertionError

    v, mat = valid(matrix)

    if v.any():
        return float(np.sqrt(np.dot(vector[v], np.linalg.solve(mat, vector[v]))))
    return float("nan")


def solve(matrix: np.ndarray, rhs: np.ndarray) -> np.ndarray:
    """Solve a linear system restricted to the valid (finite-diagonal) submatrix.

    Args:
        matrix: Square matrix representing the coefficients of the linear system.
        rhs: Right-hand side vector. Its length must match the number of rows
            in the matrix.

    Returns:
        Solution vector of the same length as ``rhs``. Entries corresponding
        to invalid rows/columns are set to NaN.

    Raises:
        AssertionError: If the matrix is not square or ``rhs`` length does not
            match the matrix dimensions.
    """
    if matrix.shape[0] != matrix.shape[1]:
        raise AssertionError

    if rhs.size != matrix.shape[0]:
        raise AssertionError

    x = np.nan * np.ones(rhs.size)
    v, mat = valid(matrix)

    if v.any():
        x[v] = np.linalg.solve(mat, rhs[v])

    return x
