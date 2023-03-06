from utils import *
import time
import os
from datetime import datetime

if __name__ == '__main__':
    while True:# 持續執行
        side,period = get_rsi_signal()
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
        print('''
 /\_/\  
( o   o )
=(  =^=  )=
 (        )
  (      )
''')
        print(f'<比特幣自動交易程序> current_side:{side} current_time:{current_time}')
        
        if side != 'PASS':
            place_order(side,quantity=0.003)
            send_to_telegram(message=f"您好~剛剛機器人用幣安API下了一筆比特幣{side}單")
        # 下完單以後等待下一根k棒出來
        t = 0
        while t <= 60*15:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print('''
 /\_/\  
( o   o )
=(  =^=  )=
 (        )
  (      )
''')
            print(f'<比特幣自動交易程序>,上一根k棒方向為:{side},等待下一根k棒出來中,current_time:{current_time}')
            time.sleep(1)
            t += 1
            os.system("cls") # 清除屏幕
