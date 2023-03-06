from binance.client import Client
import numpy as np
from binance.enums import *
import finlab_crypto
from finlab_crypto import Strategy
import pandas as pd
from binance import Client
import requests
from tokens import api_key,api_secret,apiToken,chatID

# 建立客戶端
client = Client(api_key=api_key,api_secret=api_secret)

# 定義下單函數
def place_order(side,quantity,client=client):
    usdt_balance = float(client.get_asset_balance(asset='USDT')['free'])
    btc_balance = float(client.get_asset_balance(asset='BTC')['free'])
    btc_price = float(client.get_symbol_ticker(symbol='BTCUSDT')['price'])
    if (side == 'BUY') and ((usdt_balance / btc_price) > quantity) :
      try:
         order = client.create_order(symbol='BTCUSDT',side=SIDE_BUY,type=ORDER_TYPE_MARKET,quantity=quantity)
         print(f'buy quantity:{quantity} BTC success',quantity)
      except Exception as e:
         print(f'while do {side} BTC action occur error:{e}')
    if (side == 'SELL') and (btc_balance > quantity):
      try:
         order = client.create_order(symbol='BTCUSDT',side=SIDE_SELL,type=ORDER_TYPE_MARKET,quantity=quantity)
         print(f'sell quantity:{quantity} BTC success')
      except Exception as e:
         print(f'while do {side} BTC action occur error:{e}')
    return order

# 定義發送電報函數
def send_to_telegram(message):
    apiURL = f'https://api.telegram.org/bot{apiToken}/sendMessage'
    try:
        response = requests.post(apiURL, json={'chat_id': chatID, 'text': message})
        print(response.text)
    except Exception as e:
        print(e)

# 定義漲跌訊號函數
def get_signal(
      pair='BTCUSDT',
      freq='15m',
      n_bar = 10000,
      client = client
      ):
  # get the pair ohlcv data
  ohlcv = finlab_crypto.crawler.get_nbars_binance(pair,freq,n_bar,client)
  
  # def base sma_Strategy
  @Strategy(sma1=20, sma2=60)
  def sma_strategy(ohlcv):
    close = ohlcv.close
    # crete sma1 and sma2
    sma1 = close.rolling(sma_strategy.sma1).mean()
    sma2 = close.rolling(sma_strategy.sma2).mean()
    # def entries and exits
    entries = (sma1 > sma2) & (sma1.shift() < sma2.shift())
    exits = (sma1 < sma2) & (sma1.shift() > sma2.shift())
    return entries, exits
  
  # search range
  variables = {
      'sma1': np.arange(5, 100, 5), 
      'sma2': np.arange(10, 200, 5),
      }
  
  # sma_strategy.backtest
  portfolio = sma_strategy.backtest(ohlcv, variables=variables, freq=freq ,plot=False)
  # find portfolio.total_profit().max()
  temp = portfolio.total_profit()[portfolio.total_profit()==portfolio.total_profit().max()].to_frame().reset_index()
  # find portfolio.total_profit().max() use n1 and n2
  n1,n2 = temp['sma1'].values[0],temp['sma2'].values[0]
  
  # create signal table
  table = pd.DataFrame()
  table['close'] = ohlcv.close
  table['n1'] = ohlcv.close.rolling(n1).mean()
  table['n2'] = ohlcv.close.rolling(n2).mean()
  table['buy'] = ((table['n1'] > table['n2']) & (table['n1'].shift() < table['n2'].shift())).astype(int)
  table['sell'] = ((table['n1'] < table['n2']) & (table['n1'].shift() > table['n2'].shift())).astype(int)
  # get last row of the table
  table = table.replace(0,np.nan).tail(1)
  # if buy and sell eqal np.nan pass
  if table[['buy','sell']].sum().sum() == 0:
     signal = 'PASS'
  # if buy == 1
  if table[['buy']].values[0][0] == 1:
     signal = 'BUY'
  # if sell == 1
  if table[['sell']].values[0][0] == 1:
     signal = 'SELL'
  return signal,n1,n2

def get_signal_fast(
      pair='BTCUSDT',
      freq='15m',
      n_bar = 10000,
      client = client,
      n1 = 65,
      n2 = 95,
      ):
  
  # get data
  ohlcv = finlab_crypto.crawler.get_nbars_binance(pair,freq,n_bar,client)
  
  # get signal table
  table = pd.DataFrame()
  table['close'] = ohlcv.close
  table['n1'] = ohlcv.close.rolling(n1).mean()
  table['n2'] = ohlcv.close.rolling(n2).mean()
  table['buy'] = ((table['n1'] > table['n2']) & (table['n1'].shift() < table['n2'].shift())).astype(int)
  table['sell'] = ((table['n1'] < table['n2']) & (table['n1'].shift() > table['n2'].shift())).astype(int)
  table = table.replace(0,np.nan).tail(1)
  
  # if buy and sell eqal np.nan pass
  if table[['buy','sell']].sum().sum() == 0:
     signal = 'PASS'
  # if buy == 1
  if table[['buy']].values[0][0] == 1:
     signal = 'BUY'
  # if sell == 1
  if table[['sell']].values[0][0] == 1:
     signal = 'SELL'
  
  return signal,n1,n2

# RSI策略 2023/03/06研發 報酬率15% 最大回撤-0.08%
def get_rsi_signal(
      pair='BTCUSDT',
      freq='15m',
      n_bar = 10000,
      period = 14,
      client = client):
    
    # get data
    ohlcv = finlab_crypto.crawler.get_nbars_binance(pair,freq,n_bar,client)
  
    # create signal table
    table = pd.DataFrame()
    table['rsi'] = TA.RSI(ohlcv,period=period)
    table['buy'] = table['rsi'] <= 20 
    table['sell'] = table['rsi'] >= 80 
    table = table.replace(0,np.nan).tail(1)
    if table[['buy','sell']].sum().sum() == 0:
        signal = 'PASS'
    if table[['buy']].values[0][0] == 1:
        signal = 'BUY'
    if table[['sell']].values[0][0] == 1:
        signal = 'SELL'
  return signal,period
