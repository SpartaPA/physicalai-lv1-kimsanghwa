"""문제 5 — 동차변환 inv_T 검증 (pytest). [학생 작성용 템플릿]

지시문이 요구하는 것은 `inv_T` 검증이지만,
점/방향 구분과 벡터화, 최소자승까지 함께 검증해 두면 이후 문제에서 안전하다.

실행: 프로젝트 루트에서  pytest -v
"""

import numpy as np
import pytest

from src.rotation import rot_x, rot_y, rot_z
from src.transform import (
    inv_T,
    least_squares_normal_equation,
    make_T,
    transform_direction,
    transform_point,
    transform_points,
)


@pytest.fixture
def T():
    """테스트에 쓸 대표 동차변환 하나."""
    R = rot_z(0.9) @ rot_y(-0.35) @ rot_x(1.3)
    return make_T(R, [0.35, -0.15, 0.55])


def test_inv_T_gives_identity(T):
    T_inv = inv_T(T)
    assert np.allclose(T_inv @ T, np.eye(4), atol=1e-10), "inv_T(T) @ T 가 단위행렬이 아닙니다"
    assert np.allclose(T @ T_inv, np.eye(4), atol=1e-10), "T @ inv_T(T) 가 단위행렬이 아닙니다"


def test_inv_T_matches_generic_inverse(T):
    T_inv = inv_T(T)
    T_inv_generic = np.linalg.inv(T)   # 검산용
    assert np.allclose(T_inv, T_inv_generic, atol=1e-8), "inv_T 결과가 np.linalg.inv 와 다릅니다"


def test_point_and_direction_differ(T):
    v = np.array([1.0, 2.0, 3.0])
    p_out = transform_point(T, v)
    d_out = transform_direction(T, v)

    assert not np.allclose(p_out, d_out), "점과 방향 변환 결과가 같으면 안 됩니다"
    assert np.allclose(p_out - d_out, T[:3, 3], atol=1e-10), \
        "점과 방향 결과의 차이가 병진 벡터와 일치해야 합니다"
    assert np.isclose(np.linalg.norm(d_out), np.linalg.norm(v)), "방향 변환은 길이를 보존해야 합니다"


def test_transform_points_is_vectorized(T):
    rng = np.random.default_rng(42)
    P = rng.standard_normal((30, 3))

    out_vectorized = transform_points(T, P)
    out_loop = np.array([transform_point(T, p) for p in P])

    assert np.allclose(out_vectorized, out_loop, atol=1e-10), \
        "벡터화된 transform_points 결과가 반복문 결과와 다릅니다"


def test_roundtrip_through_inverse(T):
    rng = np.random.default_rng(42)
    P = rng.standard_normal((20, 3))

    P_transformed = transform_points(T, P)
    P_back = transform_points(inv_T(T), P_transformed)

    assert np.allclose(P_back, P, atol=1e-8), "T -> inv_T(T) 왕복 후 원래 점군이 복원되지 않습니다"


def test_least_squares_matches_lstsq():
    rng = np.random.default_rng(42)
    A = rng.standard_normal((50, 4))          # 과결정 (측정 50개, 미지수 4개)
    x_true = np.array([2.0, -1.0, 0.5, 3.0])
    b = A @ x_true + 0.01 * rng.standard_normal(50)   # 노이즈 섞기

    x, residual = least_squares_normal_equation(A, b)
    x_lstsq, *_ = np.linalg.lstsq(A, b, rcond=None)   # 검산용

    assert np.allclose(x, x_lstsq, atol=1e-6), "정규방정식 해가 np.linalg.lstsq 와 다릅니다"
    assert np.allclose(A.T @ residual, 0.0, atol=1e-6), \
        "잔차가 A 의 열공간에 수직(A^T r = 0)이어야 합니다"
