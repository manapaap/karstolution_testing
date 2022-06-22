# -*- coding: utf-8 -*-
"""
Created on Wed Jun 22 10:16:16 2022

Getting Karstolution to work with data from babs

@author: Aakas
"""

from os import chdir, listdir
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict


chdir('C:/Users/Aakas/Documents/School/Oster_lab/karstolution/')


def load_data():
    """
    Loads climate output data and organizes each cave into a dictionary,
    with a nexted dictionary of eras
    """
    clim_runs = listdir('datafiles/Jessica')
    all_data = {}
    for file in clim_runs:
        # Uses the stripped filename as a dictionary key
        data = pd.read_csv('datafiles/Jessica/' + file,
                           names=['d18O', 'prp', 'tempp', 'sur_tem', 'evpt'],
                           na_values=['d18O', 'Precip', 'TS', 'T2M', 'Evap'],
                           sep=' ')
        data.dropna(how='all', inplace=True)
        data.reset_index(inplace=True, drop=True)
        all_data[file.replace('caves_', '')[:-4]] = data.apply(pd.to_numeric,
                                                               errors='ignore')
        # This needs to be converted in form I want a dictionary containing
        # the cave names as keys, with the value being a second dict. This
        # second dict will contain the mapping from years to the actual climate
        # data
    # To achieve this, we will iterate along the dataframe, taking slices
    # as we see fit to create a dataframe for the cave

    clim_data = defaultdict(dict)

    for key, value in all_data.items():
        # Reference colum that tells us the positions of the breaks
        test_ref = ~pd.to_numeric(all_data[key]['d18O'],
                                  errors='coerce').fillna(0).astype('bool')
        test_ref = test_ref.reset_index(level=0)
        test_ref.drop(test_ref[test_ref.d18O == False].index, inplace=True)

        for start, end in zip(test_ref['index'], test_ref['index'][1:]):
            name = value.d18O[start]
            era_dict = clim_data[name]
            era_dict[key] = value[start + 1:end]

    return clim_data


def clean_data(clim_data):
    """
    Takes the dictionary of values provided from load_data and cleans it
    so it is in a form usable by karstolution. Also removes weird extreme/
    error values
    """
    pass
