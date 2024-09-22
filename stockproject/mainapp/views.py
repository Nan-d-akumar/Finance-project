from django.shortcuts import render
from yahoo_fin.stock_info import *

# Create your views here.
from django.shortcuts import render
from yahoo_fin.stock_info import *
import yfinance as yf
from django.shortcuts import render, HttpResponse
import yfinance as yf
from yahoo_fin.stock_info import tickers_nifty50
from django.http import JsonResponse
import requests

# Create your views here.
def home(request):
    stock_picker = tickers_nifty50()  # Getting the list of Nifty 50 stocks
    return render(request, 'mainapp/index.html', {'stockpicker': stock_picker})  # Use 'stockpicker' as the key


def stocktracker(request):
    stockpicker = request.GET.getlist('stockpicker')
    available_stocks = tickers_nifty50()
    data = {}

    for stock in stockpicker:
        if stock in available_stocks:
            stock_info = yf.Ticker(stock)
            history_data = stock_info.history(period="1d")

            if not history_data.empty:
                price = history_data['Close'].iloc[-1]
                open_price = history_data['Open'].iloc[-1]
                change = price - open_price
                volume = history_data['Volume'].iloc[-1]
            else:
                price = open_price = change = volume = 'N/A'

            market_cap = stock_info.info.get('marketCap', 'N/A')

            data[stock] = {
                'price': price,
                'open': open_price,
                'change': change,
                'market_cap': market_cap,
                'volume': volume,
            }

    return render(request, 'mainapp/stocktracker.html', {'data': data})

# New view to serve stock data as JSON
def fetch_stock_data(request):
    stockpicker = request.GET.getlist('stockpicker')
    available_stocks = tickers_nifty50()
    data = {}
    news = {}

    finnhub_api_key = 'crkpqkhr01qhc7mj5m1gcrkpqkhr01qhc7mj5m20'  # Replace with your Finnhub API key

    for stock in stockpicker:
        if stock in available_stocks:
            stock_info = yf.Ticker(stock)
            history_data = stock_info.history(period="1d")

            if not history_data.empty:
                price = history_data['Close'].iloc[-1]
                open_price = history_data['Open'].iloc[-1]
                change = price - open_price
                volume = history_data['Volume'].iloc[-1]
            else:
                price = open_price = change = volume = 'N/A'

            market_cap = stock_info.info.get('marketCap', 'N/A')

            data[stock] = {
                'price': price,
                'open': open_price,
                'change': change,
                'market_cap': market_cap,
                'volume': volume,
            }

            # Fetch news articles using Finnhub
            news_url = f'https://finnhub.io/api/v1/news?category=general&token={finnhub_api_key}'
            news_response = requests.get(news_url)
            news_data = news_response.json()

            if news_data:
                news[stock] = news_data[:5]  # Get the first 5 news articles
            else:
                news[stock] = []

    return JsonResponse({'data': data, 'news': news})