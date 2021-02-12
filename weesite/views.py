from django.shortcuts import render
import os 
from datetime import datetime, timedelta
import pandas_datareader.data as datareader
import pandas as pd
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.io import curdoc
from bokeh.resources import CDN
from django.views.decorators.csrf import csrf_exempt
from .forms import TickerForm

@csrf_exempt
def home(request):
    if request.method == 'POST':
        form = TickerForm(request.POST)
        if form.is_valid():
            ticker = form.cleaned_data['symbol']
            start = form.cleaned_data['start']
    else:
        form = TickerForm()
        ticker = 'GME'
        start = datetime.now() - timedelta(weeks=6)
    plot = plot_series(ticker, start)
    script, div = components(plot, CDN)
    return render(request, 'index.html', {'form' : form, 'script' : script, 'div' : div} )

def plot_series(ticker, start):    
    data = datareader.DataReader(ticker, "av-daily", start=start, end=datetime.now(), api_key=os.getenv('ALPHAVANTAGE_API_KEY'))
    data = data.dropna()
    data['timestamp'] = data.index
    data['timestamp'] = pd.to_datetime(data['timestamp'])
    data = data.reset_index(drop=True)
    plot = figure(plot_width=800, plot_height=250, x_axis_type="datetime")
    plot.line(x=data['timestamp'], y=data['close'], color='navy')
    plot.title.text = '%s price, since %s' % (ticker, start)
    return plot

# Not yet in use ...
def get_quote(ticker):
    data = datareader.get_quote_av(ticker)
    data = data.dropna()
    return data