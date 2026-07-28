import pytest

np = pytest.importorskip("numpy", reason="numpy not installed - install requirements-embeddings.txt to run these tests")

from app.services.semantic_matcher import cosine_similarity


def test_cosine_similarity_identical_vectors():
    v = np.array([1.0, 2.0, 3.0])
    assert abs(cosine_similarity(v, v) - 1.0) < 1e-9


def test_cosine_similarity_orthogonal_vectors():
    a = np.array([1.0, 0.0])
    b = np.array([0.0, 1.0])
    assert abs(cosine_similarity(a, b) - 0.0) < 1e-9


def test_cosine_similarity_opposite_vectors():
    a = np.array([1.0, 0.0])
    b = np.array([-1.0, 0.0])
    assert abs(cosine_similarity(a, b) - (-1.0)) < 1e-9


def test_cosine_similarity_handles_zero_vector_without_error():
    zero = np.array([0.0, 0.0])
    other = np.array([1.0, 1.0])
    assert cosine_similarity(zero, other) == 0.0
