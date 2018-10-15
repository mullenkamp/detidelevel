# -*- coding: utf-8 -*-
"""
Created on Sun Sep 30 12:33:58 2018

@author: michaelek
"""

import plotly.offline as py
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from pyhydrotel import get_mtypes, get_sites_mtypes, get_ts_data
import statsmodels.api as sm
from hydrointerp.util import tsreg

pd.options.display.max_columns = 10

######################################
### Parameters

server = 'sql2012prod05'
database = 'hydrotel'

site = '66401'
mtypes = ['water level', 'water level detided']

from_date = '2018-01-01'
to_date = '2018-03-01'

tide_freq = 745 # Number of minutes between tides

output_path = r'E:\ecan\shared\projects\de-tide\de-tide_2018-10-15.html'

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

    sea1 = sm.tsa.seasonal_decompose(df1, freq=int(np.round(tide_freq/freq_int)))

    tsdata2 = df1[sea1.seasonal < sea1.seasonal.quantile(quantile)].dropna().copy()

    tsdata3 = tsdata2.asfreq(freq).interpolate(interp)
    if isinstance(tsdata3, pd.DataFrame):
        tsdata3.columns = ['de-tided']
    elif isinstance(tsdata3, pd.Series):
        tsdata3.name = 'de-tided'

    return tsdata3





######################################
### Get data

mtypes1 = get_sites_mtypes(server, database, sites=site)

tsdata = get_ts_data(server, database, mtypes, site, from_date, to_date, None)

tsdata1 = tsreg(tsdata.unstack(1).reset_index().drop(['ExtSiteID'], axis=1).set_index('DateTime')).interpolate('time')

roll1 = tsdata1[['water level']].rolling(12, center=True).mean().dropna()
roll1.columns = ['smoothed original']

s1 = sm.tsa.seasonal_decompose(roll1, freq=freq_int)

s2 = s1.seasonal.copy()

tsdata2 = roll1[s2 < s2.quantile(0.3)].dropna().copy()

tsdata3 = tsdata2.asfreq('5T').interpolate('pchip')
tsdata3.columns = ['de-tided']

combo1 = pd.concat([roll1, tsdata3, tsdata1['water level detided']], axis=1).dropna()

########################################
###

colors1 = ['rgb(102,194,165)', 'rgb(252,141,98)', 'rgb(141,160,203)']

orig = go.Scattergl(
    x=combo1.index,
    y=combo1['smoothed original'],
    name = 'smoothed original',
    line = dict(color = colors1[0]),
    opacity = 0.8)

new_detide = go.Scattergl(
    x=combo1.index,
    y=combo1['de-tided'],
    name = 'de-tided',
    line = dict(color = colors1[1]),
    opacity = 0.8)

old_detide = go.Scattergl(
    x=combo1.index,
    y=combo1['water level detided'],
    name = 'old de-tided',
    line = dict(color = colors1[2]),
    opacity = 0.8)

data = [orig, new_detide, old_detide]

layout = dict(
    title='De-tiding example',
    yaxis={'title':'water level (m)'},
    dragmode='pan')

config = {"displaylogo": False, 'scrollZoom': True, 'showLink': False}

fig = dict(data=data, layout=layout)
py.plot(fig, filename = output_path, config=config)














