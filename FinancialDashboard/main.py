import math
import datetime as dt
import yfinance as yf
import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.plotting import figure
from bokeh.models import TextInput, Button, DatePicker, MultiChoice, DataRange1d

def load_data(ticker1, ticker2, start, end):
    """Load data from Yahoo Finance API"""
    df1 = yf.download(ticker1, start=start, end=end)
    df2 = yf.download(ticker2, start=start, end=end)
    return df1, df2

def plot_data(data, indicators):
    df = data
    gain = df.Close > df.Open
    loss = df.Open > df.Close
    width = 12*60*60*1000 # half day in ms

    p = figure(x_axis_type='datetime', tools='pan,wheel_zoom,box_zoom,reset,save', width=1000, x_range=DataRange1d())
    p.xaxis.major_label_orientation = math.pi/4
    p.grid.grid_line_alpha = 0.25

    p.segment(df.index, df.High, df.index, df.Low, color='black')
    p.vbar(df.index[gain], width, df.Open[gain], df.Close[gain], fill_color='#00ff00', line_color='00ff00')
    p.vbar(df.index[loss], width, df.Open[loss], df.Close[loss], fill_color='#ff0000', line_color='ff0000')

    for indicator in indicators:
        if indicator == '30 Day SMA':
            df['SMA30'] = df['Close'].rolling(30).mean()
            p.line(df.index, df['SMA30'], color='purple', legend_label='30 Day SMA')
        elif indicator == '100 Day SMA':
            df['SMA100'] = df['Close'].rolling(100).mean()
            p.line(df.index, df['SMA100'], color='blue', legend_label='100 Day SMA')
        elif indicator == 'Linear Regression Line':
            par = np.polyfit(range(len(df.index.values)), df.Close.values, 1, full=True)
            slope = par[0][0]
            intercept = par[0][1]
            y_pred = [slope * i + intercept  for i in range(len(df.index.values))]
            p.segment(df.index[0], y_pred[0], df.index[-1], y_pred[-1], legend_label='Linear Regression Line', color='red')

    p.legend.location = 'top_left'
    p.legend.click_policy = 'hide'

    return p

def on_button_click():
    """Update plot with new data"""
    start_date = date_picker_start.value
    end_date = date_picker_end.value
    ticker1 = stock1.value
    ticker2 = stock2.value
    selected_indicators = indicator_choice.value
    df1, df2 = load_data(ticker1, ticker2, start_date, end_date)
    p1 = plot_data(df1, selected_indicators)
    p2 = plot_data(df2, selected_indicators)
    if not selected_indicators:  # No indicators selected
        layout.children = [stock1, stock2, date_picker_start, date_picker_end, indicator_choice, load_button]
    else:
        layout.children = [stock1, stock2, date_picker_start, date_picker_end, indicator_choice, load_button, row(p1, p2)]

stock1 = TextInput(title='Stock 1', value='AAPL')
stock2 = TextInput(title='Stock 2', value='MSFT')

date_picker_start = DatePicker(title='Start Date', value=dt.date(2020, 1, 1), min_date=dt.date(2000, 1, 1), max_date=dt.date.today())
date_picker_end = DatePicker(title='End Date', value=dt.datetime.now().strftime("%Y-%m-%d"), min_date="2020-01-01", max_date=dt.datetime.now().strftime("%Y-%m-%d"))

indicator_choice = MultiChoice(options=['100 Day SMA', '30 Day SMA', 'Linear Regression Line'])

load_button = Button(label='Load Data', button_type='success')
load_button.on_click(on_button_click)

layout = column(stock1, stock2, date_picker_start, date_picker_end, indicator_choice, load_button)

on_button_click()  # Load data initially

curdoc().add_root(layout)
