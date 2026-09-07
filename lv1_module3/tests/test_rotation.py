"""문제 3 — 회전 행렬의 수학적 성질 검증 (pytest). [학생 작성용 템플릿]

지시문이 요구하는 4가지를 각각 테스트 함수로 작성한다.

  1. 회전행렬의 열이 서로 직교하는 단위벡터인가   -> test_columns_are_orthonormal
  2. 행렬식이 1인가                               -> test_determinant_is_one
  3. 역행렬이 전치와 같은가                       -> test_inverse_equals_transpose
  4. 재직교화 결과가 직교행렬인가                 -> test_gram_schmidt_restores_orthogonality

작성 요령
--------
- `@pytest.mark.parametrize` 로 여러 축 x 여러 각도를 한 함수에서 검사하면
  테스트 하나가 여러 케이스를 담당한다 (아래 ANGLES / MAKERS 참고).
- 비교는 반드시 `np.isclose` / `np.allclose` 로 한다 (부동소수점).
- `np.linalg` 는 검산용으로만 쓰고, 쓸 때는 주석으로 검산임을 밝힌다.
- assert 에 실패 메시지를 붙이면 어디가 깨졌는지 바로 보인다.
- 4개는 **최소 개수**다. 반사 행렬 반례, 로드리게스 일치, 축·각 왕복 같은
  테스트를 더 붙이면 좋다.

실행: 프로젝트 루트에서  pytest -v
"""

import numpy as np
import pytest

from src.rotation import (
    axis_angle_from_matrix,
    gram_schmidt,
    is_rotation,
    orthogonality_error,
    rodrigues,
    rot_x,
    rot_y,
    rot_z,
)
from src.vectors import det, dot, norm

ANGLES = [0.0, np.deg2rad(22.5), np.pi / 6, np.pi / 4, np.pi / 2, 2.0, np.pi, -1.234]
MAKERS = [rot_x, rot_y, rot_z]


@pytest.fixture
def rng():
    """난수는 반드시 시드를 고정한다."""
    return np.random.default_rng(42)


# --- 1. 열이 서로 직교하는 단위벡터인가 -------------------------------------

@pytest.mark.parametrize("maker", MAKERS)
@pytest.mark.parametrize("theta", ANGLES)
def test_columns_are_orthonormal(maker, theta):
    R = maker(theta)
    for i in range(3):
        assert np.isclose(norm(R[:, i]), 1.0), \
            f"{maker.__name__}({theta}): {i}번째 열의 길이가 1이 아님 -> {norm(R[:, i])}"
    for i in range(3):
        for j in range(i + 1, 3):
            d = dot(R[:, i], R[:, j])
            assert abs(d) < 1e-8, \
                f"{maker.__name__}({theta}): {i},{j}번 열이 직교하지 않음 (내적={d:.3e})"


# --- 2. 행렬식이 1인가 --------------------------------------------------------

@pytest.mark.parametrize("maker", MAKERS)
@pytest.mark.parametrize("theta", ANGLES)
def test_determinant_is_one(maker, theta):
    R = maker(theta)
    d = det(R)
    assert abs(d - 1.0) < 1e-8, f"{maker.__name__}({theta}): 행렬식이 1이 아님 -> {d}"


# --- 3. 역행렬 == 전치 --------------------------------------------------------

@pytest.mark.parametrize("maker", MAKERS)
@pytest.mark.parametrize("theta", ANGLES)
def test_inverse_equals_transpose(maker, theta):
    R = maker(theta)
    assert np.allclose(R.T @ R, np.eye(3), atol=1e-8), \
        f"{maker.__name__}({theta}): R.T @ R 이 단위행렬이 아님"
    R_inv = np.linalg.inv(R)   # 검산용
    assert np.allclose(R_inv, R.T, atol=1e-8), \
        f"{maker.__name__}({theta}): 역행렬이 전치와 다름"


# --- 4. 재직교화 결과가 직교행렬인가 -----------------------------------------

def test_gram_schmidt_restores_orthogonality(rng):
    R0 = rot_z(0.9) @ rot_y(-0.35) @ rot_x(1.3)
    noisy = R0 + 1e-3 * rng.standard_normal((3, 3))

    err_before = orthogonality_error(noisy)
    assert err_before > 0.0, "노이즈를 섞었는데 직교성 오차가 0 입니다"

    fixed = gram_schmidt(noisy)
    err_after = orthogonality_error(fixed)

    assert err_after < err_before, "재직교화 후 오차가 더 커졌습니다"
    assert err_after < 1e-10, f"재직교화 후에도 직교성 오차가 큽니다: {err_after}"
    assert np.isclose(det(fixed), 1.0), f"복구 행렬의 행렬식이 1이 아닙니다: {det(fixed)}"
    assert is_rotation(fixed), "복구 행렬이 회전행렬 판정(직교 + det=1)을 통과하지 못했습니다"
    assert np.max(np.abs(fixed - noisy)) < 1e-2, "재직교화로 자세 자체가 크게 바뀌면 안 됩니다"


# --- 여기부터는 추가 테스트 (권장) -------------------------------------------

@pytest.mark.parametrize("reflect_axis", [0, 1, 2])
def test_reflection_is_not_a_rotation(reflect_axis):
    """det = -1 인 반사 행렬은 직교여도 회전이 아니다."""
    signs = [1.0, 1.0, 1.0]
    signs[reflect_axis] = -1.0
    reflect = np.diag(signs)

    assert np.allclose(reflect.T @ reflect, np.eye(3)), "반사 행렬 자체는 직교여야 함"
    d = det(reflect)
    assert abs(d - (-1.0)) < 1e-8, f"반사 행렬의 행렬식은 -1이어야 함 -> {d}"
    assert not is_rotation(reflect), "반사 행렬은 회전행렬로 판정되면 안 됨"


@pytest.mark.parametrize("theta", ANGLES)
def test_rodrigues_matches_rot_z(theta):
    R_axis = rodrigues([0.0, 0.0, 1.0], theta)
    R_direct = rot_z(theta)
    assert np.allclose(R_axis, R_direct, atol=1e-8), \
        f"rodrigues([0,0,1], {theta}) != rot_z({theta})\n{R_axis}\n{R_direct}"


@pytest.mark.parametrize("maker", MAKERS)
@pytest.mark.parametrize("theta", [t for t in ANGLES if abs(t) > 1e-8])
def test_axis_angle_roundtrip(maker, theta):
    """axis_angle_from_matrix 로 복원한 축·각으로 다시 rodrigues 를 돌리면 원래 행렬이 나온다."""
    R = maker(theta)
    axis, angle = axis_angle_from_matrix(R)
    R_back = rodrigues(axis, angle)
    assert np.isclose(angle, abs(theta), atol=1e-6), \
        f"복원한 각도가 다릅니다: angle={angle}, |theta|={abs(theta)}"
    assert np.allclose(R_back, R, atol=1e-6), \
        f"축·각으로 재구성한 행렬이 원본과 다릅니다\n{R_back}\n{R}"
