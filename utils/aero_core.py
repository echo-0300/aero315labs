"""
Core aerodynamic calculations for the interactive airfoil concept tool.

Physics approach (documented so it's easy to defend in class / tune later):

- Geometry comes straight from the existing `Airfoil` class (NACA4 generator).
- Zero-lift angle of attack (alpha_L0) and the aerodynamic-center moment
  coefficient (Cm_ac) are computed from THIN AIRFOIL THEORY using the actual
  camber line of the current airfoil (numerically integrated Fourier
  coefficients A1, A2). This means symmetric airfoils correctly produce
  alpha_L0 = 0 and Cm_ac = 0 (and therefore CP stays glued to the AC), and
  cambered airfoils correctly produce nonzero pitching moment / a CP that
  migrates toward the AC as alpha increases -- all "for free", without
  hand-tuning per airfoil.
- Cl(alpha) is the standard thin-airfoil line 2*pi*(alpha - alpha_L0) below
  a stall angle, then rolled off smoothly above it. This stall behavior
  (and the post-stall Cd blow-up / CP jump) is intentionally simplified /
  illustrative -- it is NOT a panel-method or CFD result. That trade-off
  was a deliberate choice for a fundamentals lecture tool: fast, always
  well-behaved, and it reproduces the qualitative story (suction peak
  grows, then separation starts at the TE and marches forward, lift
  drops, drag spikes, CP shifts) without needing a boundary-layer solver.
"""

import numpy as np
if not hasattr(np, 'trapz'):
    np.trapz = getattr(np, 'trapezoid', None)

ALPHA_STALL_DEG = 16.0      # simplified fixed stall angle
CL_ALPHA = 2 * np.pi        # thin airfoil theory lift slope (per radian)


def thin_airfoil_coeffs(foil, n_theta=200):
    """
    Compute alpha_L0 (zero-lift AoA, radians) and Cm_ac from the camber line
    using the classic Glauert Fourier expansion:

        x = (1 - cos(theta)) / 2,   theta in [0, pi]
        dyc/dx = A0 + sum_n An cos(n*theta)

        alpha_L0 = -(1/pi) * Integral[0,pi] (dyc/dx)(cos(theta) - 1) dtheta
        A1 = (2/pi) * Integral[0,pi] (dyc/dx) cos(theta) dtheta
        A2 = (2/pi) * Integral[0,pi] (dyc/dx) cos(2*theta) dtheta
        Cm_ac = (pi/4) * (A2 - A1)
    """
    theta = np.linspace(1e-4, np.pi - 1e-4, n_theta)
    x = (1 - np.cos(theta)) / 2

    eps = 1e-4
    x_lo = np.clip(x - eps, 0, 1)
    x_hi = np.clip(x + eps, 0, 1)
    dydx = (foil.camber_line(x_hi) - foil.camber_line(x_lo)) / (x_hi - x_lo)

    alpha_L0 = -(1 / np.pi) * np.trapz(dydx * (np.cos(theta) - 1), theta)
    A1 = (2 / np.pi) * np.trapz(dydx * np.cos(theta), theta)
    A2 = (2 / np.pi) * np.trapz(dydx * np.cos(2 * theta), theta)
    Cm_ac = (np.pi / 4) * (A2 - A1)

    return float(alpha_L0), float(Cm_ac)


def lift_drag_coeffs(alpha_deg, alpha_L0_rad):
    """
    Returns (Cl, Cd, stalled: bool, stall_fraction: float in [0,1])
    stall_fraction = 0 fully attached, 1 = deep stall (used to drive the
    separation-point visualization).
    """
    alpha_rad = np.radians(alpha_deg)
    cl_lin = CL_ALPHA * (alpha_rad - alpha_L0_rad)

    overshoot = alpha_deg - ALPHA_STALL_DEG
    if overshoot <= 0:
        cl = cl_lin
        stall_fraction = max(0.0, 1 + overshoot / 6.0) if overshoot > -6 else 0.0
        stall_fraction = np.clip(stall_fraction, 0.0, 1.0) * 0.0  # no separation pre-stall
        stalled = False
    else:
        cl_at_stall = CL_ALPHA * (np.radians(ALPHA_STALL_DEG) - alpha_L0_rad)
        decay = max(0.35, 1 - 0.055 * overshoot)
        cl = cl_at_stall * decay
        stall_fraction = np.clip(overshoot / 10.0, 0.0, 1.0)
        stalled = True

    cd0, k = 0.008, 0.02
    cd = cd0 + k * cl_lin ** 2
    if overshoot > 0:
        cd += 0.9 * (overshoot / 10.0) ** 2

    return float(cl), float(cd), stalled, float(stall_fraction)


def cp_location(cl, cm_ac, stall_fraction, x_ac=0.25, cl_floor=0.08):
    """
    x_cp/c = x_ac - Cm_ac / Cl   (moment transfer AC -> CP)

    Near zero lift this blows up (physically correct -- CP is undefined at
    zero lift for a cambered section). We clip and flag it so the caller can
    fade the marker + show an explanatory note instead of drawing nonsense
    off-screen.

    Past stall we add a simplified aft "CP jump" driven by stall_fraction,
    representing the well-known destabilizing CP shift during separation.
    """
    cl_eff = cl if abs(cl) > cl_floor else np.sign(cl if cl != 0 else 1) * cl_floor
    valid = abs(cl) > cl_floor

    x_cp = x_ac - cm_ac / cl_eff
    x_cp += 0.18 * stall_fraction          # illustrative post-stall aft shift
    x_cp = float(np.clip(x_cp, -0.35, 1.3))

    return x_cp, valid


def separation_x(alpha_deg, stalled, stall_fraction):
    """Chordwise point (x/c) upstream of which flow is attached on the
    upper surface. 1.0 = fully attached to the TE."""
    if not stalled:
        return 1.0
    return float(np.clip(1.0 - 0.75 * stall_fraction, 0.12, 1.0))


def rotate_body_to_screen(x, y, alpha_deg, pivot):
    """
    Rotate body-frame points (x, y) about `pivot` (fixed screen location of
    the AC) by -alpha_deg (clockwise) so that increasing AoA pitches the
    leading edge UP relative to a fixed, horizontal relative-wind vector.
    """
    a = np.radians(-alpha_deg)
    c, s = np.cos(a), np.sin(a)
    dx = np.asarray(x) - pivot[0]
    dy = np.asarray(y) - pivot[1]
    x_new = pivot[0] + (dx * c - dy * s)
    y_new = pivot[1] + (dx * s + dy * c)
    return x_new, y_new
