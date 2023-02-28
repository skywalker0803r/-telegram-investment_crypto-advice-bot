import numpy as np
import finlab_crypto
from finlab_crypto import Strategy
import datetime
import pandas as pd
from binance import Client

def get_signal(
      pair='BTCUSDT',
      freq='15m',
      n_bar = 10000,
      client = Client(api_key='IMe4eYde4ivFkH98FeDgAppDEqufxAVsqiciR3AQyucvpl01Obcm7uIlFhDDd19p',
                      api_secret='770u8vCFNlNzkn4TqIQDACed8J9uzyxBnuam1RHj8u9tB34lGU7roVI4Hi7gCjaG')
                      ):
  # 拿資料
  ohlcv = finlab_crypto.crawler.get_nbars_binance(pair,freq,n_bar,client)
  
  # 定義策略
  @Strategy(sma1=20, sma2=60)
  def sma_strategy(ohlcv):
    close = ohlcv.close
    # 雙均線製作
    sma1 = close.rolling(sma_strategy.sma1).mean()
    sma2 = close.rolling(sma_strategy.sma2).mean()
    # 金叉買死叉賣
    entries = (sma1 > sma2) & (sma1.shift() < sma2.shift())
    exits = (sma1 < sma2) & (sma1.shift() > sma2.shift())
    #figures = {'overlaps': {'sma1': sma1,'sma1': sma2}}
    return entries, exits#, figures
  
  # 搜索範圍
  variables = {
      'sma1': np.arange(5, 100, 5), 
      'sma2': np.arange(10, 200, 5),
      }
  
  # 用sma_strategy.backtest尋找最佳解之n1,n2
  portfolio = sma_strategy.backtest(ohlcv, variables=variables, freq=freq ,plot=False)
  # 找total_profit().max()
  temp = portfolio.total_profit()[portfolio.total_profit()==portfolio.total_profit().max()].to_frame().reset_index()
  # 最佳解之n1,n2
  n1,n2 = temp['sma1'].values[0],temp['sma2'].values[0]
  
  # 使用n1n2產生訊號
  table = pd.DataFrame()
  table['close'] = ohlcv.close
  table['n1'] = ohlcv.close.rolling(n1).mean()
  table['n2'] = ohlcv.close.rolling(n2).mean()
  table['buy'] = ((table['n1'] > table['n2']) & (table['n1'].shift() < table['n2'].shift())).astype(int)
  table['sell'] = ((table['n1'] < table['n2']) & (table['n1'].shift() > table['n2'].shift())).astype(int)
  # 只取買賣訊號table的最後一行
  table = table.replace(0,np.nan).tail(1)
  # 如果買賣訊號都是np.nan則無訊號
  if table[['buy','sell']].sum().sum() == 0:
     signal = '不動作'
  # 判斷buy是否為1
  if table[['buy']].values[0][0] == 1:
     signal = 'buy'
  # 判斷sell是否為1
  if table[['sell']].values[0][0] == 1:
     signal = 'sell'
  return signal

if __name__ == '__main__':
    while True:
        signal = get_signal()
        time.sleep(60)
