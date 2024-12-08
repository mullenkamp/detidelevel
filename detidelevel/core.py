# -*- coding: utf-8 -*-
"""
Created on Sun Sep 30 12:33:58 2018

@author: michaelek
"""
import pandas as pd
import numpy as np
import statsmodels.api as sm
from detidelevel.util import tsreg

######################################
### Parameters

tide_freq = 745 # Number of minutes between tides

#####################################
### Functions


def detide(df, quantile, freq=None, interp='pchip'):
    """
    Function to remove the tidal influence on a flow time series. It simply removes the data associated with the tidal periods and interpolates between them. The function uses the seasonal_decompose function from statsmodels and the specified lower quantile to select the actual flow data periods.

    Parameters
    ----------
    df : DataFrame or Series
        Input DataFrame or Series with a time series index.
    quantile : float
        The quantile below which will contain the data. e.g. 0.3 for the lower 30% of the data.
    freq : str or None
        Pandas freq string of the time series. None will attemp to determine the freq.
    interp : str
        The Pandas interpolation code.

    Returns
    -------
    DataFrame or Series

    Notes
    -----
    Ideally, the time series frequency should be either 1 minute (1T) or 5 minutes (5T) as these are divisible by the tidal frequency of 745 minutes. Otherwise, the function will round to the nearest int and the results will be a bit off and the time periods used will need to be adjusted.
    """
    if isinstance(freq, str):
        df1 = tsreg(df.dropna(), freq, interp)
        freq_int = df1.index.freq.n
    else:
        df1 = tsreg(df.dropna(), interp=interp)
        freq_int = df1.index.freq.n
        freq = df1.index.freq.freqstr
    if 'T' not in freq:
        raise ValueError('freq must be a max of 30T and a min of 1T')

    sea1 = sm.tsa.seasonal_decompose(df1, period=int(np.round(tide_freq/freq_int)))

    tsdata2 = df1[sea1.seasonal < sea1.seasonal.quantile(quantile)].dropna().copy()

    tsdata3 = tsdata2.asfreq(freq).interpolate(interp)
    if isinstance(tsdata3, pd.DataFrame):
        tsdata3.columns = ['de-tided']
    elif isinstance(tsdata3, pd.Series):
        tsdata3.name = 'de-tided'

    return tsdata3

