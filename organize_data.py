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
from copy import deepcopy
import yaml
from Karstolution  import karstolution


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
                           names=['d18o', 'prp', 'tempp', 'T2M', 'evpt'],
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
        test_ref = ~pd.to_numeric(all_data[key]['d18o'],
                                  errors='coerce').fillna(0).astype('bool')
        test_ref = test_ref.reset_index(level=0)
        test_ref.drop(test_ref[test_ref.d18o == False].index, inplace=True)

        for start, end in zip(test_ref['index'], test_ref['index'][1:]):
            name = value.d18o[start]
            era_dict = clim_data[name]
            era_dict[key] = (value[start + 1:end]).apply(pd.to_numeric)

    return clim_data


def looped_len(finite_list, max_len):
    """
    Returns a list of a looped sequence to the maximum length
    """
    return np.concatenate(finite_list * max_len, axis=None)


def clean_data(clim_data):
    """
    Takes the dictionary of values provided from load_data and cleans it
    so it is in a form usable by karstolution. Also removes weird extreme/
    error values
    """
    karst_clim_data = deepcopy(clim_data)
    for cave, eras in karst_clim_data.items():
        for time, data in eras.items():
            # standardize indices
            data.reset_index(inplace=True, drop=True)
            # Remove near surface temperature
            data.drop('T2M', axis=1, inplace=True)
            # Convert to centigrade
            data.tempp = data.tempp - 273.15
            # Remove weird extreme values from climate model errors
            # Also interpolate the values to prevent data loss
            data.replace(0.0, np.nan, inplace=True)
            if data.isnull().any().any():
                old_index = deepcopy(data.index)
                data.dropna(inplace=True)
                # For some reason need to refer directly to the dict to make
                # Change; will amke things slower but whatever
                # Included if statement so interpolation only happens on
                # Required vals
                eras[time] = data.reindex(old_index)
                eras[time].interpolate(method='polynomial',
                                       order=2, inplace=True)
                eras[time].reset_index(inplace=True, drop=True)
            # Now time to inject the tt axis signifying month
            length = int(np.ceil(eras[time].index.size / 12))
            month_index = looped_len(list(range(1, 13)), length)
            # Slice sequence to length as one entry is shorter
            eras[time]['mm'] = month_index[:eras[time].index.size]
            # add the ID column required
            eras[time]['tt'] = eras[time].index

    return karst_clim_data


def run_karstolution(karst_clim_data):
    """
    Runs karstolution using the processed inputs
    """
    config = yaml.safe_load(open('config.yaml', 'rt').read())
    karst_outputs = deepcopy(karst_clim_data)

    for cave, eras in karst_outputs.items():
        for time, data in eras.items():
            eras[time] = karstolution(config, data, calculate_drip=True)

    return karst_outputs


def main():
    pass
