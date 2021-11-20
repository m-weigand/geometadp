import datetime
import numpy as np
import pandas as pd

import plotly.graph_objects as go
from ipywidgets import widgets


"""
db tab
"""

df = pd.read_csv(
    'https://raw.githubusercontent.com/agrogeophy/catalog/master/db.csv')
#df = df.drop(df.columns[[0]], axis=1)

container = widgets.HBox(children=[use_date, month])

textbox = widgets.Dropdown(
    description='instrument:   ',
    value='',
    options=df['instrument'].unique().tolist()
)

display(textbox)
