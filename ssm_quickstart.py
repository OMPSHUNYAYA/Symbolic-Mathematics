# ssm_quickstart.py
# Minimal Shunyaya Symbolic Mathematics (SSM) demo
# - Numbers are pairs (m, a) with a in (-1, +1)
# - Core ops: add (oplus), sub (ominus), mul (otimes, M2), div (odiv, M2)
# - ASCII only; no external deps

import math

EPS_A = 1e-6   # clamp for alignment before atanh
EPS_W = 1e-12  # tiny guard for zero total weight in addition
GAMMA = 1.0    # weight exponent: w(m) = |m|**GAMMA (default replicates the paper's examples)

def clamp_alignment(a, eps=EPS_A):
    # Ensure a stays in (-1, +1) before atanh
    return max(min(a, 1.0 - eps), -1.0 + eps)

def ssm_add(x, y, gamma=GAMMA):
    """(m1, a1) oplus (m2, a2) = (m1+m2, tanh((w1*u1 + w2*u2)/(w1+w2))) with u=atanh(a), w=|m|**gamma"""
    (m1, a1), (m2, a2) = x, y
    u1 = math.atanh(clamp_alignment(a1))
    u2 = math.atanh(clamp_alignment(a2))
    w1 = abs(m1) ** gamma
    w2 = abs(m2) ** gamma
    W = w1 + w2
    if W <= EPS_W:
        # zero total weight: fall back to neutral alignment
        a = 0.0
    else:
        a = math.tanh((w1 * u1 + w2 * u2) / W)
    return (m1 + m2, a)

def ssm_neg(x):
    """Negation flips only magnitude; alignment preserved."""
    m, a = x
    return (-m, a)

def ssm_sub(x, y, gamma=GAMMA):
    """x ominus y = x oplus ( -y )"""
    return ssm_add(x, ssm_neg(y), gamma=gamma)

def ssm_mul(x, y):
    """M2 (rapidity-additive) multiplication:
       (m1, a1) otimes (m2, a2) = (m1*m2, tanh(atanh(a1) + atanh(a2)))"""
    (m1, a1), (m2, a2) = x, y
    u1 = math.atanh(clamp_alignment(a1))
    u2 = math.atanh(clamp_alignment(a2))
    m = m1 * m2
    a = math.tanh(u1 + u2)
    return (m, a)

def ssm_div(x, y):
    """M2 division:
       (m1, a1) odiv (m2, a2) = (m1/m2, tanh(atanh(a1) - atanh(a2))) ; requires m2 != 0"""
    (m1, a1), (m2, a2) = x, y
    if m2 == 0:
        raise ZeroDivisionError("ssm_div: divisor magnitude m2 must be nonzero")
    u1 = math.atanh(clamp_alignment(a1))
    u2 = math.atanh(clamp_alignment(a2))
    m = m1 / m2
    a = math.tanh(u1 - u2)
    return (m, a)

def almost_eq(x, y, atol=1e-3):
    return abs(x - y) <= atol

if __name__ == "__main__":
    # Worked example (Addition)
    x = (10.0, 0.8)
    y = (5.0, -0.6)
    add_res = ssm_add(x, y)  # expected ~ (15, 0.463)
    print("Addition (10, 0.8) oplus (5, -0.6) ->", (round(add_res[0], 6), round(add_res[1], 3)))

    # Worked example (Subtraction via addition with negation)
    x2 = (12.0, 0.7)
    y2 = (5.0, 0.9)
    sub_res = ssm_sub(x2, y2)  # expected ~ (7, 0.780)
    print("Subtraction (12, 0.7) ominus (5, 0.9) ->", (round(sub_res[0], 6), round(sub_res[1], 3)))

    # Worked example (Multiplication, M2)
    x3 = (4.0, 0.6)
    y3 = (3.0, -0.5)
    mul_res = ssm_mul(x3, y3)  # expected ~ (12, 0.143)
    print("Multiplication (4, 0.6) otimes (3, -0.5) ->", (round(mul_res[0], 6), round(mul_res[1], 3)))

    # Worked example (Division, M2)
    x4 = (9.0, 0.9)
    y4 = (3.0, 0.5)
    div_res = ssm_div(x4, y4)  # expected ~ (3, 0.728)
    print("Division (9, 0.9) odiv (3, 0.5) ->", (round(div_res[0], 6), round(div_res[1], 3)))

    # Identity checks
    add_id = ssm_add((7.0, 0.25), (0.0, 1.0))
    mul_id = ssm_mul((7.0, 0.25), (1.0, 0.0))
    print("Add identity (m,a) oplus (0, +1) ->", add_id)
    print("Mul identity (m,a) otimes (1, 0) ->", mul_id)

    # Inverse checks
    add_inv = ssm_add((3.0, -0.4), ssm_neg((3.0, -0.4)))
    mul_inv = ssm_mul((2.0, 0.3), (1.0 / 2.0, -0.3))
    print("Add inverse (3,-0.4) oplus (−3,-0.4) ->", add_inv, "(zero-class canonical in display)")
    print("Mul inverse (2,0.3) otimes (0.5,-0.3) ->", mul_inv)

    # Quick self-checks (tolerances)
    assert add_res[0] == 15.0 and almost_eq(add_res[1], 0.463, 1e-3)
    assert sub_res[0] == 7.0 and almost_eq(sub_res[1], 0.780, 1e-3)
    assert mul_res[0] == 12.0 and almost_eq(mul_res[1], 0.143, 1e-3)
    assert div_res[0] == 3.0 and almost_eq(div_res[1], 0.728, 1e-3)
    assert mul_id[0] == 7.0 and almost_eq(mul_id[1], 0.25, 1e-12)
    print("\n[ok] basic checks passed.")
