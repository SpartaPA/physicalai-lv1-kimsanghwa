"""문제 1 — 벡터 연산 모듈. (학생 작성용 템플릿)

내적 · 사이각 · 정규화 · 정사영 · 반대칭행렬(외적) · 평면 법선과
가우스 소거 기반의 rank / 행렬식 / 역행렬을 **직접** 구현한다.

규칙
----
- `np.linalg` 는 노트북에서 **검산용으로만** 쓰고, 이 모듈 안에서는 쓰지 않는다.
  (`inverse_gauss_jordan` 이 던지는 `np.linalg.LinAlgError` 예외 타입만 예외)
- 각 함수의 docstring 에 적힌 계약(입력/출력/예외)을 그대로 지킨다.
  노트북의 검증 셀과 `tests/` 가 이 계약을 기준으로 채점된다.
- 구현을 마치면 `raise NotImplementedError(...)` 줄을 지운다.
"""

from __future__ import annotations

import numpy as np

__all__ = [
    "as_vector",
    "dot",
    "norm",
    "angle_between",
    "normalize",
    "project",
    "reject",
    "skew",
    "cross",
    "plane_normal",
    "row_echelon",
    "rank",
    "det",
    "gauss_eliminate",
    "inverse_gauss_jordan",
]


# ---------------------------------------------------------------- 기본 연산

def as_vector(v) -> np.ndarray:
    """입력(리스트/튜플/배열)을 1차원 float 배열로 변환한다.

    1차원이 아니면 ValueError 를 던진다.

    [구현 예시] 아래 세 줄이 이 파일에서 기대하는 코드 스타일이다.
    나머지 함수도 이런 식으로 채워 넣으면 된다.
    """
    arr = np.asarray(v, dtype=float)
    if arr.ndim != 1:
        raise ValueError(f"1차원 벡터가 필요합니다. 받은 shape={arr.shape}")
    return arr


def dot(a, b) -> float:
    """내적. sum(a_i * b_i) 를 직접 계산한다 (`np.dot` 사용 금지).

    두 벡터의 차원이 다르면 ValueError.
    """
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if a.shape != b.shape:
        raise ValueError(f"두 벡터의 차원이 서로 다릅니다: {a.shape} vs {b.shape}")
    return float(np.sum(a * b))


def norm(v) -> float:
    """유클리드 노름. sqrt(v·v) — 위에서 만든 dot 을 재사용한다."""
    v = np.asarray(v, dtype=float)
    return float(np.sqrt(dot(v, v)))


def angle_between(a, b, degrees: bool = True) -> float:
    """두 벡터 사이각. degrees=True 면 도(°), False 면 라디안.

    cos(theta) = (a·b) / (|a||b|)

    주의 1. 영벡터가 들어오면 사이각이 정의되지 않는다 -> ValueError.
    주의 2. 부동소수점 오차로 |cos| 가 1 을 아주 조금 넘으면 arccos 가 nan 을 낸다.
            [-1, 1] 로 clip 해야 무작위 입력에서도 안전하다.
    """
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    na = norm(a)
    nb = norm(b)
    if na < 1e-12 or nb < 1e-12:
        raise ValueError("영벡터의 사이각은 정의되지 않습니다.")
    c = dot(a, b) / (na * nb)
    c = np.clip(c, -1.0, 1.0)
    theta = float(np.arccos(c))
    return float(np.degrees(theta)) if degrees else theta


def normalize(v, eps: float = 1e-12) -> np.ndarray:
    """단위벡터로 정규화한다. v / |v|

    영벡터를 어떻게 처리할지는 **문제 1-2 에서 직접 정한다.**
    노트북 1-2 에서 (1) 아무 처리 없이 나눴을 때 무슨 일이 나는지 관찰하고,
    (2) 선택한 처리 방식과 근거를 마크다운에 적은 뒤, 그 방식대로 여기에 구현한다.
    선택에 따라 노트북/테스트의 검증 코드도 그 방식에 맞춰 작성한다.

    [선택한 정책] ZERO_POLICY = "raise" — 영벡터는 방향이 정의되지 않으므로
    조용히 0을 돌려주면 이후 계산에서 nan 이 소리 없이 전파된다. 그래서 명시적으로
    ValueError 를 던져 호출부가 즉시 문제를 알아채도록 한다.
    """
    v = np.asarray(v, dtype=float)
    n = norm(v)
    if n < eps:
        raise ValueError("영벡터는 정규화할 수 없습니다.")
    return v / n


def project(a, b) -> np.ndarray:
    """a 를 b 방향으로 정사영한 성분.

        proj_b(a) = (a·b / b·b) * b

    분모가 |b|^2 이므로 b 를 미리 정규화할 필요는 없다.
    b 가 영벡터면 ValueError.
    """
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    denom = dot(b, b)
    if denom < 1e-15:
        raise ValueError("영벡터 방향으로는 정사영을 정의할 수 없습니다.")
    return (dot(a, b) / denom) * b


def reject(a, b) -> np.ndarray:
    """a 에서 b 방향 성분을 뺀 나머지(수직 성분). a = project + reject 가 성립해야 한다."""
    a = np.asarray(a, dtype=float)
    return a - project(a, b)


def skew(a) -> np.ndarray:
    """3차원 벡터 a 에 대응하는 반대칭행렬 [a]_x 를 만든다.

        [a]_x = [[  0, -a3,  a2],
                 [ a3,   0, -a1],
                 [-a2,  a1,   0]]

    만족해야 하는 성질: [a]_x @ b == a x b,  [a]_x.T == -[a]_x
    3차원이 아니면 ValueError.
    """
    a = np.asarray(a, dtype=float)
    if a.shape != (3,):
        raise ValueError(f"벡터의 차원이 3이 아닙니다. 받은 shape={a.shape}")
    return np.array([[0.0, -a[2], a[1]],
                      [a[2], 0.0, -a[0]],
                      [-a[1], a[0], 0.0]])


def cross(a, b) -> np.ndarray:
    """외적을 **반대칭행렬 곱으로** 계산한다 (`np.cross` 사용 금지)."""
    b = np.asarray(b, dtype=float)
    if b.shape != (3,):
        raise ValueError(f"벡터의 차원이 3이 아닙니다. 받은 shape={b.shape}")
    return skew(a) @ b


def plane_normal(P1, P2, P3) -> np.ndarray:
    """세 점이 이루는 평면의 **단위** 법선 벡터.

    두 모서리 벡터(P2-P1, P3-P1)의 외적이 평면에 수직이다.
    세 점이 일직선이면 외적이 영벡터가 되어 평면이 하나로 정해지지 않는다 -> ValueError.
    """
    P1 = np.asarray(P1, dtype=float)
    P2 = np.asarray(P2, dtype=float)
    P3 = np.asarray(P3, dtype=float)
    if not (P1.shape == P2.shape == P3.shape == (3,)):
        raise ValueError("세 점은 모두 3차원이어야 합니다.")

    u = P2 - P1
    v = P3 - P1
    n = cross(u, v)

    if norm(n) < 1e-12:
        raise ValueError("세 점이 일직선상에 있어 평면을 정의할 수 없습니다.")

    return normalize(n)


# ------------------------------------------------- 가우스 소거 기반 선형대수

def row_echelon(A, pivoting: bool = True):
    """행 사다리꼴(row echelon form) 로 만든다.

    Parameters
    ----------
    pivoting : True 면 부분 피벗팅(각 열에서 절댓값이 가장 큰 행을 피벗으로 올림)

    Returns
    -------
    U : (m, n) 상삼각 형태 행렬
    pivot_cols : 피벗이 선 열 인덱스 리스트
    n_swaps : 행 교환 횟수 (행렬식 부호 계산에 필요)

    힌트: 0 인지 판정할 때는 `== 0` 대신 허용오차(tol)를 쓴다.
          예) tol = max(m, n) * np.finfo(float).eps * max(1.0, np.max(np.abs(U)))
    """
    A = np.asarray(A, dtype=float)
    if A.ndim != 2:
        raise ValueError("2차원 행렬이 아닙니다.")
    m, n = A.shape
    U = A.copy()
    tol = max(m, n) * np.finfo(float).eps * max(1.0, np.max(np.abs(U))) if U.size else 0.0

    pivot_cols: list[int] = []
    n_swaps = 0
    pivot_row = 0

    for col in range(n):
        if pivot_row >= m:
            break

        if pivoting:
            max_row = pivot_row + int(np.argmax(np.abs(U[pivot_row:, col])))
        else:
            max_row = pivot_row

        if abs(U[max_row, col]) < tol:
            continue

        if max_row != pivot_row:
            U[[pivot_row, max_row], :] = U[[max_row, pivot_row], :]
            n_swaps += 1

        for i in range(pivot_row + 1, m):
            factor = U[i, col] / U[pivot_row, col]
            U[i, col:] -= factor * U[pivot_row, col:]

        pivot_cols.append(col)
        pivot_row += 1

    return U, pivot_cols, n_swaps


def rank(A) -> int:
    """행 사다리꼴의 피벗 개수 = rank."""
    _, pivot_cols, _ = row_echelon(A)
    return len(pivot_cols)


def det(A) -> float:
    """행렬식 = 행 사다리꼴 대각성분의 곱 x (-1)^(행 교환 횟수).

    피벗이 n 개보다 적으면(특이행렬) 0.0 을 돌려준다.
    정사각 행렬이 아니면 ValueError.
    """
    A = np.asarray(A, dtype=float)
    if A.ndim != 2 or A.shape[0] != A.shape[1]:
        raise ValueError("행렬이 정방행렬이 아닙니다.")
    n = A.shape[0]
    U, pivot_cols, n_swaps = row_echelon(A)
    if len(pivot_cols) < n:
        return 0.0
    return float(((-1.0) ** n_swaps) * np.prod(np.diag(U)))


def gauss_eliminate(A, b, pivoting: bool = True, verbose: bool = False):
    """가우스 소거법 + 후진대입으로 Ax = b 를 푼다.

    Parameters
    ----------
    pivoting : True 면 부분 피벗팅을 적용한다. False 면 피벗을 그대로 쓴다
               (문제 4-4 에서 두 경우의 오차를 비교하므로 **둘 다 동작해야 한다**).
    verbose  : True 면 각 소거 단계의 첨가행렬 [A|b] 를 출력한다
               (문제 4-1 이 요구하는 '단계별 출력').

    Returns
    -------
    x : 해 벡터
    steps : 단계별 첨가행렬 [A|b] 스냅샷 리스트 (초기 상태 포함)

    피벗이 0 이면 해가 유일하지 않다 -> ZeroDivisionError.
    """
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    n = len(b)

    steps = [np.hstack([A, b.reshape(-1, 1)])]
    if verbose:
        print("[초기] 첨가행렬 [A|b]")
        print(steps[-1])

    for k in range(n - 1):
        if pivoting:
            max_row = k + int(np.argmax(np.abs(A[k:, k])))
            if max_row != k:
                A[[k, max_row]] = A[[max_row, k]]
                b[[k, max_row]] = b[[max_row, k]]
                steps.append(np.hstack([A, b.reshape(-1, 1)]))
                if verbose:
                    print(f"\n[{k + 1}단계-a] 행 {k} <-> 행 {max_row} 교환")
                    print(steps[-1])

        if A[k, k] == 0.0:
            raise ZeroDivisionError(f"{k}번 피벗이 0 입니다. 해가 유일하지 않습니다.")

        for i in range(k + 1, n):
            factor = A[i, k] / A[k, k]
            A[i, k:] -= factor * A[k, k:]
            b[i] -= factor * b[k]

        steps.append(np.hstack([A, b.reshape(-1, 1)]))
        if verbose:
            print(f"\n[{k + 1}단계-b] {k}열 아래를 0으로 소거")
            print(steps[-1])

    x = np.zeros(n)
    for i in range(n - 1, -1, -1):
        x[i] = (b[i] - np.sum(A[i, i + 1:] * x[i + 1:])) / A[i, i]
    if verbose:
        print("\n[후진대입] x =", x)

    return x, steps


def inverse_gauss_jordan(A) -> np.ndarray:
    """가우스-조던 소거로 역행렬을 구한다. [A|I] -> [I|A^-1].

    정사각이 아니면 ValueError, 특이행렬이면 np.linalg.LinAlgError.
    (`np.linalg.inv` 를 부르지 말고 소거로 직접 구한다)
    """
    A = np.array(A, dtype=float)
    if A.ndim != 2 or A.shape[0] != A.shape[1]:
        raise ValueError("행렬이 정방행렬이 아닙니다.")
    n = A.shape[0]
    M = np.hstack([A, np.eye(n)])

    for k in range(n):
        max_row = k + int(np.argmax(np.abs(M[k:, k])))
        if abs(M[max_row, k]) < 1e-10:
            raise np.linalg.LinAlgError("행렬이 특이(singular)행렬이라 역행렬이 존재하지 않습니다.")
        if max_row != k:
            M[[k, max_row]] = M[[max_row, k]]
        M[k, :] /= M[k, k]
        for i in range(n):
            if i != k:
                M[i, :] -= M[i, k] * M[k, :]

    return M[:, n:]
