# -*- coding: utf-8 -*-
"""
Created on Wed Jul  6 16:00:35 2022

@author: Aakas
"""


from os import chdir
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yaml
from Karstolution import karstolution
from collections import defaultdict
from PyAstronomy.pyasl import decimalYearGregorianDate as decimal_to_date


chdir('C:/Users/Aakas/Documents/School/Oster_lab/karstolution/')


@np.vectorize
def decimal_to_date_vec(decimal_year):
    """
    Vectorize the function to convert decimal years to datetime objects
    having its own function definition because wrapper functions are fun
    and I wanted to use them
    """
    return decimal_to_date(decimal_year)


def load_data():
    """
    Loads all the data and places it into a dictionary organized by location
    """
    data = defaultdict(dict)
    names = ['WA', 'PR', 'MG']

    for place in names:
        info = data[place]
        info['evpt'] = pd.read_csv('datafiles/Isiah/' + place +
                                   '_ET_Output.csv', skiprows=2,
                                   names=['date', 'tempp',
                                          'evpt_TH', 'evpt_BC'],
                                   usecols=[0, 2, 17, 20])
        # Coerce to more usefil datetime object now
        info['evpt']['date'] = info['evpt']['date'].apply(pd.to_datetime)
        # Keep dates precise th month to make joins easier
        info['evpt']['date'] = info['evpt']['date'].values.astype('<M8[M]')

        info['prp'] = pd.read_csv('datafiles/Isiah/' + place +
                                  '_precip.mon.mean.txt', skiprows=1,
                                  names=['date', 'prp'],
                                  usecols=[1, 2],
                                  sep='\t')
        # Also coercing into datetime
        info['prp']['date'] = info['prp']['date'].apply(decimal_to_date_vec)
        info['prp']['date'] = info['prp']['date'].values.astype('<M8[M]')

        info['d18o'] = pd.read_excel('datafiles/Isiah/d18O_data.xlsx',
                                     sheet_name=place, skiprows=4,
                                     names=['month', 'd18o'])
        info['d18o']['mm'] = info['d18o'].index + 1
    return data


def clean_data(raw_data, evpt_calc='TH'):
    """
    Organizes the data in the format as provided by loading from separate
    files into one organized file, in form ready for karstolution
    """
    clean_data = {}
    for key, value in raw_data.items():
        # Need to add a column for the dates to allow for a merge to happen
        final_df = compare_dates(value['prp'], value['evpt'])
        final_df = final_df.merge(value['prp'], on='date', how='left')
        final_df = final_df.merge(value['evpt'], on='date', how='left')

        # Relabelling the evpt
        final_df['evpt'] = final_df['evpt_' + evpt_calc]
        final_df.drop(['evpt_BC', 'evpt_TH'], axis=1, inplace=True)

        # Adding tt for karstolution and to allow d18o merge
        final_df['mm'] = final_df['date'].dt.month
        final_df = final_df.merge(value['d18o'], on='mm', how='left')

        final_df['tt'] = final_df.index
        clean_data[key] = final_df

    return clean_data


def compare_dates(rain, evpt):
    """
    Compares the "date" column of the two arrays to find the ideal start
    and end times that allow for overlap between eras

    Parameters are two dataframes and not the dictionary they are nested in

    Returns a dataframe with monthly intervals of time from overlapped
    start to end
    """
    start_year_rain = rain['date'].iloc[0]
    end_year_rain = rain['date'].iloc[-1]

    start_year_evpt = evpt['date'].iloc[0]
    end_year_evpt = evpt['date'].iloc[-1]

    start_year = np.max([start_year_rain, start_year_evpt])
    end_year = np.min([end_year_rain, end_year_evpt])

    final_df = pd.DataFrame(pd.date_range(start_year, end_year, freq='m'),
                            columns=['date'])
    final_df['date'] = final_df['date'].values.astype('<M8[M]')
    if end_year not in final_df['date']:
        # Prevent loss of end month as we are creating this sequence by month
        final_df = pd.concat([final_df,
                              pd.DataFrame([end_year], columns=['date'])],
                             ignore_index=True)
    return final_df


def run_karstolution(karst_data, config):
    """
    Runs karstolution using the provided inputs,
    looping over each site in question
    """
    karst_outputs = {}
    for key, value in karst_data.items():
        karst_outputs[key] = karstolution(config, value, calculate_drip=True)

    return karst_outputs


def csv_out(karst_data, name):
    """
    Prints the dictionary of values into three separate CSVs so I can send to
    Isiah. For both the raw data and the processed form
    """
    for key, value in karst_data.items():
        value.to_csv('datafiles/outputs/' + name + '_' + key + '.csv',
                     index=False)


if __name__ == '__main__':
    raw_data = load_data()
    karst_data = clean_data(raw_data)

    config = yaml.safe_load(open('config.yaml', 'rt').read())

    karst_output = run_karstolution(karst_data, config)

    csv_out(karst_data, 'input')
    csv_out(karst_output, 'output')

