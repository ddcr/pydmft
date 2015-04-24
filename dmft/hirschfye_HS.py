# -*- coding: utf-8 -*-
"""
================================
QMC Hirsch - Fye Impurity solver
================================

To treat the Anderson impurity model and solve it using the Hirsch - Fye
Quantum Monte Carlo algorithm
"""
from __future__ import division, absolute_import, print_function
import numpy as np
from scipy.linalg.blas import dger

import dmft.hirschfye as hf


def ising_v(dtau, U, L=32):
    """Initialize the vector of the Hubbard-Stratonovich fields

    .. math:: V = -\\Delta \\tau M_l

    where the vector entries :math:`M_l` are normaly distributed according to

    .. math:: P(M_l) \\alpha \\exp(-  \\frac{\\Delta \\tau}{2U} M_l^2)

    Parameters
    ----------
    dtau : float
        time spacing :math:`\\Delta \\tau`
    U : float
        local Coulomb repulsion
    L : integer
        length of the array

    Returns
    -------
    out : single dimension ndarray
    """
    return -dtau * np.random.normal(0, np.sqrt(U/dtau), L)


def imp_solver(g0up, g0dw, v, parms, therm=1000):
    r"""Impurity solver call. Calcutaltes the interacting Green function
    as given by the contribution of the auxiliary discretized spin field.
    """

    gxu = hf.ret_weiss(g0up)
    gxd = hf.ret_weiss(g0dw)
    kroneker = np.eye(v.size)
    gup = hf.gnewclean(gxu, v, 1., kroneker)
    gdw = hf.gnewclean(gxd, v, -1., kroneker)

    gstup, gstdw = np.zeros_like(gup), np.zeros_like(gdw)
    for mcs in range(parms['sweeps']+therm):
        update(gup, gdw, v, parms['U'], parms['dtau_mc'])

        if mcs % therm == 0:
            gup = hf.gnewclean(gxu, v, 1., kroneker)
            gdw = hf.gnewclean(gxd, v, -1., kroneker)

        if mcs > therm:

            gstup += gup
            gstdw += gdw

    gstup = gstup/parms['sweeps']
    gstdw = gstdw/parms['sweeps']

    return hf.avg_g(gstup), hf.avg_g(gstdw)


def update(gup, gdw, v, U, dtau):
    for j in range(v.size):
        Vjp = - dtau * np.random.normal(0, np.sqrt(U/dtau), 1)
        dv = Vjp - v[j]
        ratup = 1. + (1. - gup[j, j])*(np.exp( dv)-1.)
        ratdw = 1. + (1. - gdw[j, j])*(np.exp(-dv)-1.)
        rat = ratup * ratdw
        gauss_weight = np.exp((Vjp**2-v[j]**2)/(2*U*dtau))
        rat = rat/(gauss_weight+rat)
        if rat > np.random.rand():
            v[j] = Vjp
            gnew(gup, dv, j)
            gnew(gdw,-dv, j)


def gnew(g, dv, k):
    """Quick update of the interacting Green function matrix after a single
    spin flip of the auxiliary field. It calculates

    .. math:: \\alpha = \\frac{\\exp(v'_j - v_j) - 1}
                        {1 + (1 - G_{jj})(\\exp(v'_j v_j) - 1)}
    .. math:: G'_{ij} = G_{ij} + \\alpha (G_{ik} - \\delta_{ik})G_{kj}

    no sumation in the indexes"""
    ee = np.exp(dv)-1.
    a = ee/(1. + (1.-g[k, k])*ee)
    x = g[:, k].copy()
    x[k] -= 1
    y = g[k, :].copy()
    g = dger(a, x, y, 1, 1, g, 1, 1, 1)
