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
"""linear algebra."""

from __future__ import annotations

import numpy as np


def valid(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Validates and processes a square matrix.

    This function checks if the input matrix is square (i.e., has the same number
    of rows and columns). It also validates that the diagonal elements of the
    matrix are finite. If the matrix does not meet these criteria, an error is
    raised. If valid, it returns a boolean array indicating the validity of the
    diagonal elements and a sub-matrix with only the valid rows and columns.

    Parameters:
    matrix (np.ndarray): A NumPy array representing the input matrix to be
                         validated and processed.

    Returns:
    tuple[np.ndarray, np.ndarray]: A tuple where the first element is a boolean
                                    array indicating which diagonal elements are
                                    finite, and the second element is a sub-matrix
                                    containing only the rows and columns
                                    corresponding to finite diagonal elements.

    Raises:
    AssertionError: If the input matrix is not square.
    """
    # make sure matrix  is quadratic
    if matrix.shape[0] != matrix.shape[1]:
        raise AssertionError

    v = np.isfinite(np.diag(matrix))
    return v, matrix[:, v][v]


# that's somewhat not needed...
def a_norm(vector: np.ndarray, matrix: np.ndarray | None = None) -> float:
    """Calculate the generalized norm of a vector optionally using a matrix.

    The function computes the Euclidean norm of the vector if no matrix is
    provided. If a matrix is provided, it computes the generalized norm
    of the vector with respect to the quadratic form defined by the matrix.
    The function ensures both the matrix and vector meet certain validity
    conditions before proceeding with calculations.

    Parameters:
    vector: np.ndarray
        The input vector. Must be a one-dimensional numpy array.

    matrix: np.ndarray | None, optional
        An optional square matrix defining the quadratic form to calculate the
        generalized norm. If provided, its size must match the size of the
        input vector. If None, the function computes the standard Euclidean
        norm of the vector.

    Raises:
    AssertionError
        If the matrix is not square or if its dimensions do not align with
        the size of the input vector.

    Returns:
    float
        The norm of the vector calculated using the given quadratic form
        defined by the matrix, or the Euclidean norm if no matrix is supplied.
        If the computation is invalid, returns NaN.
    """
    if matrix is None:
        return float(np.linalg.norm(vector[np.isfinite(vector)], 2))

    # make sure matrix is quadratic
    if matrix.shape[0] != matrix.shape[1]:
        raise AssertionError

    # make sure the vector has the right number of entries
    if vector.size != matrix.shape[0]:
        raise AssertionError

    v, mat = valid(matrix)

    if v.any():
        return float(np.sqrt(np.dot(vector[v], np.dot(mat, vector[v]))))
    return np.nan


def inv_a_norm(vector: np.ndarray, matrix: np.ndarray | None = None) -> float:
    """Calculates the inverse A-norm of a given vector using an optional matrix.

    If the matrix is not provided, it defaults to calculating the Euclidean norm of the
    finite entries in the vector. If the matrix is provided, it checks that the
    matrix is square and that the dimensions are compatible with the vector before
    computing the norm.

    Parameters
    ----------
    vector : np.ndarray
        The input vector for which the norm is to be calculated.
    matrix : np.ndarray | None, optional
        An optional square matrix used for computing the norm. If not provided,
        the function computes the Euclidean norm.

    Returns:
    -------
    float
        The computed norm as a float value. If no valid entries exist for the
        calculation, it returns 'np.nan'.

    Raises:
    ------
    AssertionError
        If the matrix is not square or if the vector's size is incompatible with
        the matrix's dimensions.
    """
    if matrix is None:
        return float(np.linalg.norm(vector[np.isfinite(vector)], 2))

    # make sure matrix is quadratic
    if matrix.shape[0] != matrix.shape[1]:
        raise AssertionError

    # make sure the vector has the right number of entries
    if vector.size != matrix.shape[0]:
        raise AssertionError

    v, mat = valid(matrix)

    if v.any():
        return float(np.sqrt(np.dot(vector[v], np.linalg.solve(mat, vector[v]))))
    return np.nan


def solve(matrix: np.ndarray, rhs: np.ndarray) -> np.ndarray:
    """Solve a linear system of equations using parts of a given matrix marked as valid.

    This function solves a linear system Ax = b for the subset of the system where
    certain rows and columns of the square matrix A, and corresponding entries of
    the right-hand side vector b, are marked as valid. The solution is computed for
    the valid subset using NumPy's linear algebra solver. The input matrix must be
    a square matrix, and the size of the vector must match the number of rows (or
    columns) of the matrix.

    Parameters:
    matrix: np.ndarray
        A square matrix (2D array) representing the coefficients of the linear
        system.
    rhs: np.ndarray
        A 1D array representing the right-hand side vector of the equation. Its
        size must match the number of rows in the matrix.

    Returns:
    np.ndarray
        A 1D array containing the solution to the system for the valid subset. If
        no valid rows or columns exist, the array will contain only NaN values.
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
