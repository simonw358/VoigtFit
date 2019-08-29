# -*- coding: UTF-8 -*-

from numpy import loadtxt, log10
import VoigtFit as vfit

# Input from synpars_simple.dat
# R = 10000 # Resolution
#
# # Input Parameters:
# SiII: 13.95
# SII: 13.69
# FeII: 13.59
# ZnII: 11.54,
# CrII: 12.10
#
# z1 = 2.3532
# z2 = 2.3539
#
# b1 = 15.
# b2 = 11.


def test_column_densities():

    input_data = dict()
    dat_in = loadtxt('test_2comp.input', dtype=str)
    for line in dat_in:
        ion = line[0]
        input_data[ion] = float(line[3])

    ### Load the test data and check output
    z_sys = 2.3538
    test_fname = 'test_2comp.dat'
    ds = vfit.DataSet(z_sys)
    ds.verbose = False
    ds.cheb_order = -1
    ds.velspan = 200.
    res = 299792. / 10000.
    ds.add_spectrum(test_fname, res, normalized=True)
    ds.add_lines(['SiII_1808', 'FeII_1611', 'FeII_2249', 'FeII_2260', 'FeII_2374'])
    ds.add_lines(['SII_1253', 'SII_1250'])
    ds.add_component('SiII', 2.3532, 10., 15.4)
    ds.add_component('SiII', 2.3539, 10., 15.8)
    ds.copy_components(from_ion='SiII', to_ion='SII')
    ds.copy_components(from_ion='SiII', to_ion='FeII')
    ds.prepare_dataset(mask=False, f_lower=10.)

    popt, chi2 = ds.fit(verbose=False)

    logN_criteria = list()
    for ion in list(ds.components.keys()):
        logN1 = popt.params['logN0_%s' % ion].value
        logN2 = popt.params['logN1_%s' % ion].value
        logN_tot = log10(10**logN1 + 10**logN2)
        delta = logN_tot - input_data[ion]
        logN_criteria.append(delta <= 0.01)

    assert all(logN_criteria), "Not all column densities were recovered correctly."


def test_dataset():
    z_sys = 2.3538
    test_fname = 'test_2comp.dat'
    res = 299792. / 10000.
    ds = vfit.DataSet(z_sys)
    ds.add_spectrum(test_fname, res, normalized=True)
    ds.verbose = False
    ds.cheb_order = 2
    ds.velspan = 200.

    ds.add_lines(['FeII_1608', 'FeII_1611', 'SiII_1526', 'SiII_1808'])
    ds.deactivate_line('SiII_1526')
    ds.add_component_velocity('FeII', -50., 10, 15.1)
    ds.add_component_velocity('FeII', +10., 10, 15.4)
    ds.add_component_velocity('SiII', -50., 10, 15.4)
    ds.add_component_velocity('SiII', +10., 10, 15.8)
    ds.prepare_dataset(mask=False, f_lower=10.)

    N_regions = len(ds.regions)
    N_active_regions = len([reg for reg in ds.regions if reg.has_active_lines()])
    N_pars = len(ds.pars.keys())

    assert N_regions == 4, "Incorrect number of fit regions!"
    assert N_active_regions == 3, "Incorrect number of active fit regions!"
    assert N_pars == 21

    ds.delete_component('SiII', 0)
    ds.add_line('FeII_2374')
    ds.add_fine_lines('CI_1656')
    ds.deactivate_fine_lines('CI_1656')
    ds.activate_line('SiII_1526')
    ds.prepare_dataset(mask=False, f_lower=10.)

    assert len(ds.regions) == 6
    N_active_regions = len([reg for reg in ds.regions if reg.has_active_lines()])
    assert N_active_regions == 5
    assert len(ds.pars.keys()) == 24
    N_lines = len(ds.all_lines)
    assert N_lines == 11, "Incorrect number of lines"
