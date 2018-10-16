# -*- coding: utf-8 -*-
"""
Created on Tue Oct 16 10:24:05 2018

@author: michaelek
"""
import detidelevel as dtl
import pandas as pd
try:
    import plotly.offline as py
    import plotly.graph_objs as go
except:
    print('install plotly for plot functions to work')


def plot_detide(df, quantile, freq=None, interp='pchip', output_path='detide.html', title='De-tiding example', yaxis_label='water level (m)'):
    """
    Function to run and plot the detide results.

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
    output_path : str
        Path to save the html file.

    Returns
    -------
    DataFrame or Series
    """

    orig_name = 'original'
    det_name = 'de-tided'

    det = dtl.detide(df, quantile, freq, interp)

    df1 = df.copy()

    if isinstance(df1, pd.DataFrame):
        df1.columns = [orig_name]
    elif isinstance(df1, pd.Series):
        df1.name = orig_name
        df1 = df1.to_frame()

    colors1 = ['rgb(102,194,165)', 'rgb(252,141,98)', 'rgb(141,160,203)']

    orig = go.Scattergl(
        x=df1.index,
        y=df1[orig_name],
        name = orig_name,
        line = dict(color = colors1[0]),
        opacity = 0.8)

    detide = go.Scattergl(
        x=det.index,
        y=det[det_name],
        name = det_name,
        line = dict(color = colors1[1]),
        opacity = 0.8)

    data = [orig, detide]

    layout = dict(
        title=title,
        yaxis={'title': yaxis_label},
        dragmode='pan')

    config = {"displaylogo": False, 'scrollZoom': True, 'showLink': False}

    fig = dict(data=data, layout=layout)
    py.plot(fig, filename = output_path, config=config)

    return det
