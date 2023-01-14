import numpy as np


def valid(matrix):
    """
    Construct the valid subset of matrix (correlation) matrix matrix
    :param matrix: n x n matrix

    :return: Tuple of matrix boolean vector indicating if row/column is valid and the valid subset of the matrix
    """
    # make sure matrix  is quadratic
    assert matrix.shape[0] == matrix.shape[1]
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
    assert matrix.shape[0] == matrix.shape[1]
    # make sure the vector has the right number of entries
    assert vector.size == matrix.shape[0]

    v, mat = valid(matrix)

    if v.any():
        return np.sqrt(np.dot(vector[v], np.dot(mat, vector[v])))
    else:
        return np.nan


def inv_a_norm(vector, a=None):
    """
    Compute the matrix-norm of matrix vector
    :param vector: the n x 1 vector
    :param a: n x n matrix
    :return:
    """
    if a is None:
        return np.linalg.norm(vector[np.isfinite(vector)], 2)

    # make sure matrix is quadratic
    assert a.shape[0] == a.shape[1]
    # make sure the vector has the right number of entries
    assert vector.size == a.shape[0]

    v, mat = valid(a)

    if v.any():
        return np.sqrt(np.dot(vector[v], np.linalg.solve(mat, vector[v])))
    else:
        return np.nan


def solve(a, b):
    """
    Solve the linear system matrix*x = b
    Note that only the same subset of the rows and columns of matrix might be "warm"

    :param a: n x n matrix
    :param b: n x 1 vector

    :return: The solution vector x (which may contain NaNs
    """
    # make sure matrix is quadratic
    assert a.shape[0] == a.shape[1]
    # make sure the vector b has the right number of entries
    assert b.size == a.shape[0]

    x = np.nan * np.ones(b.size)
    v, mat = valid(a)

    if v.any():
        x[v] = np.linalg.solve(mat, b[v])

    return x
