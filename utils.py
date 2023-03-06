from binance.client import Client
import numpy as np
from binance.enums import *
import finlab_crypto
from finlab_crypto import Strategy
import pandas as pd
from binance import Client
import requests
from tokens import api_key,api_secret,apiToken,chatID
from finta import TA

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
        
def get_sma_signal(
      pair='BTCUSDT',
      freq='15m',
      n_bar = 10000,
      client = client,
      n1 = 65,
      n2 = 95,
      ):
  ohlcv = finlab_crypto.crawler.get_nbars_binance(pair,freq,n_bar,client)
  table = pd.DataFrame()
  table['close'] = ohlcv.close
  table['n1'] = ohlcv.close.rolling(n1).mean()
  table['n2'] = ohlcv.close.rolling(n2).mean()
  table['buy'] = ((table['n1'] > table['n2']) & (table['n1'].shift() < table['n2'].shift())).astype(int)
  table['sell'] = ((table['n1'] < table['n2']) & (table['n1'].shift() > table['n2'].shift())).astype(int)
  table = table.replace(0,np.nan).tail(1)
  if table[['buy','sell']].sum().sum() == 0:
     signal = 'PASS'
  if table[['buy']].values[0][0] == 1:
     signal = 'BUY'
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
    ohlcv = finlab_crypto.crawler.get_nbars_binance(pair,freq,n_bar,client)
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
