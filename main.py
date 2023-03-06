from utils import *
import time
import os
from datetime import datetime

if __name__ == '__main__':
    while True:# 持續執行
        try:
            side,period = get_rsi_signal()
        except Exception as e:
            print(e)
            send_to_telegram(message=f"您好~剛剛機器人發生錯誤{e}")
        
        print('''
 /\_/\  
( o   o )
=(  =^=  )=
 (        )
  (      )
''')
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
        print(f'<比特幣自動交易程序> current_side:{side} current_time:{current_time}')
        
        # 判斷是否下單
        if side != 'PASS':
            place_order(side,quantity=0.003)
            send_to_telegram(message=f"您好~剛剛機器人用幣安API下了一筆比特幣{side}單")
        # 下完單以後等待下一根k棒出來
        t = 60*15
        while t > 0:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print('''
 /\_/\  
( o   o )
=(  =^=  )=
 (        )
  (      )
''')
            print(f'<比特幣自動交易程序>,上一根k棒方向為:{side},等待下一根k棒出來中,倒數:{t}秒鐘')
            time.sleep(1)
            t -= 1
            os.system("cls") # 清除屏幕
