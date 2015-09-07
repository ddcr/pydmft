r"""
Single site review
==================

Searching for the coexistence region using the Hirsch-Fye impurity solver
for the single site DMFT problem

"""


from __future__ import division, print_function, absolute_import
from pytriqs.archive import HDFArchive
import dmft.common as gf
import matplotlib.pyplot as plt
import numpy as np
plt.matplotlib.rcParams.update({'figure.figsize': (8, 8), 'axes.labelsize': 22,
                                'axes.titlesize': 22})


def show_conv(beta, U, filestr='SB_PM_B{}.h5', nf=5, xlim=2):
    """Plot the evolution of the Green's function in DMFT iterations"""
    f, ax = plt.subplots(1, 2, figsize=(13, 8))
    freq_arr = []
    with HDFArchive(filestr.format(beta), 'r') as output_files:
        u_str = 'U{}'.format(U)
        w_n = gf.matsubara_freq(output_files[u_str]['it00']['setup']['BETA'],
                                output_files[u_str]['it00']['setup']['N_MATSUBARA'])
        for it in sorted(output_files[u_str].keys()):
            giw = output_files[u_str][it]['giw']
            ax[0].plot(w_n, giw.imag)
            freq_arr.append(giw.imag[:nf])

    freq_arr = np.asarray(freq_arr).T
    for num, freqs in enumerate(freq_arr):
        ax[1].plot(freqs, 'o-.', label=str(num))
    ax[0].set_xlim([0, 2])
    ax[1].legend(loc=0, ncol=nf)
    graf = r'$G(i\omega_n)$'
    ax[0].set_title(r'Change of {} @ $\beta={}$, U={}'.format(graf, beta, U))
    ax[0].set_ylabel(graf)
    ax[0].set_xlabel(r'$i\omega_n$')
    ax[1].set_title('Evolution of the first frequencies')
    ax[1].set_ylabel(graf+'$(l)$')
    ax[1].set_xlabel('iterations')

    plt.show()
    plt.close()
