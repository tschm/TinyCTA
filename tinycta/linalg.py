#    Copyright 2023 Thomas Schmelzer
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
"""linear algebra"""

from __future__ import annotations

import numpy as np


def valid(matrix):
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
def a_norm(vector, matrix=None):
    """
    Compute the matrix-norm of matrix vector
    :param vector: the n x 1 vector
    :param matrix: n x n matrix
    :return:
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


def inv_a_norm(vector, matrix=None):
    """
    Compute the matrix-norm of matrix vector
    :param vector: the n x 1 vector
    :param matrix: n x n matrix
    :return:
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


def solve(matrix, rhs):
    """
    Solve the linear system matrix*x = b
    Note that only the same subset of the rows and columns of matrix might be "warm"

    :param matrix: n x n matrix
    :param rhs: n x 1 vector

    :return: The solution vector x (which may contain NaNs
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
