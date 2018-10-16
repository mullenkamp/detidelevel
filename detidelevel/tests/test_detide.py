# -*- coding: utf-8 -*-
"""
Created on Sun Sep 30 12:33:58 2018

@author: michaelek
"""
import pandas as pd
from pyhydrotel import get_mtypes, get_sites_mtypes, get_ts_data
import detidelevel as dtl

pd.options.display.max_columns = 10

######################################
### Parameters

server = 'sql2012prod05'
database = 'hydrotel'

site = '66401'
mtypes = ['water level', 'water level detided']

from_date = '2018-01-01'
to_date = '2018-03-01'

quantile = 0.3

output_path = r'E:\ecan\shared\projects\de-tide\de-tide_2018-10-16.html'

######################################
### Get data

mtypes1 = get_sites_mtypes(server, database, sites=site)

tsdata = get_ts_data(server, database, mtypes, site, from_date, to_date, None)

tsdata1 = dtl.util.tsreg(tsdata.unstack(1).reset_index().drop(['ExtSiteID'], axis=1).set_index('DateTime')).interpolate('time')

roll1 = tsdata1[['water level']].rolling(12, center=True).mean().dropna()
roll1.columns = ['smoothed original']

######################################
### Run detide

det1 = dtl.detide(roll1, quantile)

det2 = dtl.plot.plot_detide(roll1, quantile, output_path=output_path)



















