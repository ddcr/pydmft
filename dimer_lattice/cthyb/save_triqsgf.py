# -*- coding: utf-8 -*-
r"""
Saving high temp gf
===================

Using a spectral function create the higher temperature versions
"""
# Created Mon Jan 30 19:17:19 2017
# Author: Óscar Nájera

from __future__ import division, absolute_import, print_function
import numpy as np
import matplotlib.pyplot as plt

from pytriqs.gf.local import GfImFreq, BlockGf
from pytriqs.archive import HDFArchive

import dmft.common as gf
import py3qs.dimer_lattice as dlat
from pymaxent.tools import hilbert_trans, differential_weight

tp = 0.3
u_int = 1.8
# u_int = 2.01
# u_int = 2.15

data = np.load('AwmetB25tp0.3U{}G_sym.npz'.format(u_int))
Aw = data['Aw']
w = data['w']

plt.plot(w, Aw)
plt.show()

###############################################################################
# High temperature seeds
# ----------------------

hot_beta = np.round(1 / np.arange(1 / 25, .2, 1.44e-3), 3)
gfsiw = []
wnli = []
for beta in hot_beta:
    freq = 2 * int(beta * 3)
    wnh = gf.matsubara_freq(beta, freq, 1 - freq)
    wnli.append(wnh)
    print(beta)
    gfsiw.append(hilbert_trans(1j * wnh, w, differential_weight(w), Aw, 0))
    plt.plot(wnh, gfsiw[-1].imag, 'o:')
    plt.plot(wnh, gfsiw[-1].real, 'o:')

    # triqs blocks
    gfarr = GfImFreq(indices=[0], beta=beta, n_points=int(beta * 3))
    G_iw = BlockGf(name_list=['asym_dw', 'asym_up', 'sym_dw', 'sym_up'],
                   block_list=(gfarr, gfarr, gfarr, gfarr), make_copies=True)
    dlat.gf_sym_2_triqs_blockgf(gfsiw[-1], G_iw, u_int, tp)

    with HDFArchive('DIMER_PM_met_B{}_tp0.3.h5'.format(beta), 'a') as dest:
        dest['/U{}/it000/G_iw'.format(u_int)] = G_iw

# block_names = ['sym_up', 'sym_dw', 'asym_up', 'asym_dw']
# gref = np.squeeze([G_iw[name].data for name in block_names])
# plt.plot(wnh, gref.T.real)
# plt.plot(wnh, gref.T.imag)
