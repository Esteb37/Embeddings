import numpy as np


def orthogonal_projection(u, v):
    """
        Project vector u on vector v
    """
    return projection_score(u, v) * v


def projection_score(u, v):
    """
        Get a scalar magnitude of u on v
    """
    return np.dot(u, v)/np.dot(v, v)
