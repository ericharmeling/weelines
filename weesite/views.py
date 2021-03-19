from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.forms.models import model_to_dict
from weesite.forms import TickerForm, PositionForm, LoginForm
from weesite.models import Position
import os 
from math import pi
from datetime import datetime, timedelta
import pandas_datareader.data as datareader
import pandas as pd
from bokeh.palettes import Category20c
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.resources import CDN
from bokeh.transform import cumsum
import requests

# Home page 

@csrf_exempt
def home_page(request):
    if request.method == 'POST':
        form = TickerForm(request.POST)
        if form.is_valid():
            ticker = form.cleaned_data['symbol']
            start = datetime.now() - timedelta(days=form.cleaned_data['delta'])
    else:
        form = TickerForm()
        ticker = 'GME'
        start = datetime.now() - timedelta(days=45)
    plot = plot_series(ticker, start)
    script, div = components(plot, CDN)
    return render(request, 'index.html', {'ticker_form' : form, 'script' : script, 'div' : div} )


# Home page 

@csrf_exempt
def portfolio_page(request):
    if request.method == 'POST':
        form = PositionForm(request.POST)
        if form.is_valid():
            account = str(form.cleaned_data['account'])
            symbol = str(form.cleaned_data['symbol'])
            quantity = int(form.cleaned_data['quantity'])
            last_price = get_quote(symbol)
            last_total = quantity*last_price
            p = Position(account=account, symbol=symbol, quantity=quantity, last_price=last_price, last_total=last_total)
            p.save()
    else:
        form = PositionForm()
    positions = Position.objects.all().values()
    if positions is None:
        script, div = None, None
    else:
        portfolio = get_portfolio(positions)
        plot = plot_pie(portfolio)
        script, div = components(plot, CDN)
    return render(request, 'portfolio.html', {'position_form' : form, 'script' : script, 'div' : div} )

# Login

@csrf_exempt
def login_page(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate()
    return render(request, 'login.html', {'form' : form, 'script' : script, 'div' : div} )

# Utility functions

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

def plot_pie(portfolio):
    data = pd.Series(portfolio)
    data.columns = ['ticker', 'position']
    data.reset_index(name='position')
    print(pd.Series(portfolio))
    data['angle'] = data['position']/data['position'].sum() * 2*pi
    data['color'] = Category20c[len(portfolio)]

    plot = figure(plot_height=350, title="portfolio", toolbar_location=None,
            tools="hover", tooltips="@ticker: @position", x_range=(-0.5, 1.0))

    plot.wedge(x=0, y=1, radius=0.4,
            start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
            line_color="white", fill_color='color', legend_field='ticker', source=data)
    return plot

# Not yet in use ...
def get_quote(ticker):
    resp = requests.get('https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={0}&apikey={1}'.format(ticker, os.getenv('ALPHAVANTAGE_API_KEY')))
    price = float(resp.json()["Global Quote"]["05. price"])
    return price

def get_portfolio(positions):
    portfolio = dict()
    print(positions)
    for position in positions:
        symbol = str(position['symbol'])
        print(symbol)
        quantity = int(position['quantity'])
        try:
            price = get_quote(symbol)
            portfolio[symbol] = quantity*price
        except KeyError as e:
            print(e)
            print('You probably ran into the API request limit. Using stored price values.')
            portfolio[symbol] = position['last_total']
    return portfolio