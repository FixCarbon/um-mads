import pandas as pd
import numpy as np

'''Based on the hardines zones function in the xclim library: https://xclim.readthedocs.io/en/stable/indices.html#xclim.indices.hardiness_zones
    Built for USDA Hardiness Zones in Farenheit.
'''

def temp_min(df,freq='YS'):
    ''' Takes DataFrame with temperature data and finds minimum temperature in the frequency given'''
    if df.index.name=='time':
        return df.groupby([pd.Grouper(level='time',freq=freq),'lat','lon']).min()
    else:
        return df.groupby([pd.Grouper(key='time',freq=freq),'lat','lon']).min()

def output_hardiness(df,window=30,temp_col='fahrenheit'):
    '''Get USDA Hardiness Zones with rolling window
    Args:
        df: DataFrame with DateTimeIndex and data of minimum temperature
        window: window of rolling period
        temp_col: name of column with minimum temperature
    Output:
        Series with Hardiness Zones mapped to the same index provided 
    '''
    window_df = df.rolling(window,min_periods=1).mean()
    binned = pd.cut(window_df[temp_col],bins=range(-60,70,5),labels=np.linspace(1,13,25))
    return binned

def get_hardiness(df,freq='YS',window=30,temp_col='fahrenheit'):
    '''Get USDA Hardiness Zones from DataFrame containing temperature'''
    min_df = temp_min(df,freq)
    zones = output_hardiness(min_df,window,temp_col)
    return zones.astype(float)