# -*- coding: utf-8 -*-
"""
Created on Wed Jul  6 16:00:35 2022

@author: Aakas
"""


from os import chdir, listdir
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from copy import deepcopy
import yaml
from Karstolution import karstolution
from collections import defaultdict


chdir('C:/Users/Aakas/Documents/School/Oster_lab/karstolution/')


def load_data():
    """
    Loads all the data and places it into a dictionary organized by location
    """
    data = defaultdict(dict)
    names = ['WA', 'PR', 'MG']

    for place in names:
        info = data[place]
        info['evap'] = pd.read_csv('datafiles/Isiah/' + place +
                                   '_ET_Output.csv', skiprows=2,
                                   names=['date', 'T_mean',
                                          'evpt_TH', 'evpt_BC'],
                                   usecols=[0, 2, 17, 20])
        info['rain'] = pd.read_csv('datafiles/Isiah/' + place + 
                                   '_precip.mon.mean.txt', skiprows=1,
                                    names=['date', 'rain'],
                                    usecols=[1, 2],
                                    sep = '\t')
        info['d18o'] = pd.read_excel('datafiles/Isiah/d18O_data.xlsx',
                                     sheet_name=place, skiprows=4,
                                     names=['month', 'd18o'])
    return data


def clean_data(raw_data):
    """
    Organizes the data in the format as provided by loading from separate
    files into one organized file, in form ready for karstolution
    """
    pass

