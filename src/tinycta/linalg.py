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
"""linear algebra"""

from __future__ import annotations

import numpy as np


def valid(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Construct the valid subset of a matrix
    :param matrix: n x n matrix

    :return: Tuple of matrix boolean vector indicating if row/column
    is valid and the valid subset of the matrix
    """
    # make sure matrix  is quadratic
    if matrix.shape[0] != matrix.shape[1]:
        raise AssertionError

    v = np.isfinite(np.diag(matrix))
    return v, matrix[:, v][v]


# that's somewhat not needed...
def a_norm(vector: np.ndarray, matrix: np.ndarray | None = None) -> float:
    """
    Compute the matrix-norm of matrix vector
    :param vector: the n x 1 vector
    :param matrix: n x n matrix
    :return: The matrix norm as a float
    """
    if matrix is None:
        return np.linalg.norm(vector[np.isfinite(vector)], 2)

    # make sure matrix is quadratic
    if matrix.shape[0] != matrix.shape[1]:
        raise AssertionError

    # make sure the vector has the right number of entries
    if vector.size != matrix.shape[0]:
        raise AssertionError

    v, mat = valid(matrix)

    if v.any():
        return np.sqrt(np.dot(vector[v], np.dot(mat, vector[v])))
    return np.nan


def inv_a_norm(vector: np.ndarray, matrix: np.ndarray | None = None) -> float:
    """
    Compute the matrix-norm of matrix vector
    :param vector: the n x 1 vector
    :param matrix: n x n matrix
    :return: The inverse matrix norm as a float
    """
    if matrix is None:
        return np.linalg.norm(vector[np.isfinite(vector)], 2)

    # make sure matrix is quadratic
    if matrix.shape[0] != matrix.shape[1]:
        raise AssertionError

    # make sure the vector has the right number of entries
    if vector.size != matrix.shape[0]:
        raise AssertionError

    v, mat = valid(matrix)

    if v.any():
        return np.sqrt(np.dot(vector[v], np.linalg.solve(mat, vector[v])))
    return np.nan


def solve(matrix: np.ndarray, rhs: np.ndarray) -> np.ndarray:
    """
    Solve the linear system matrix*x = b
    Note that only the same subset of the rows and columns of matrix might be "warm"

    :param matrix: n x n matrix
    :param rhs: n x 1 vector

    :return: The solution vector x (which may contain NaNs)
    """
    # make sure matrix is quadratic
    if matrix.shape[0] != matrix.shape[1]:
        raise AssertionError

    # make sure the vector rhs has the right number of entries
    if rhs.size != matrix.shape[0]:
        raise AssertionError

    x = np.nan * np.ones(rhs.size)
    v, mat = valid(matrix)

    if v.any():
        x[v] = np.linalg.solve(mat, rhs[v])

    return x
