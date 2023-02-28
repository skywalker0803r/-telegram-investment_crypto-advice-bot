from utils import place_order,send_to_telegram,get_signal
import time

if __name__ == '__main__':
    while True:# 持續執行
        side,n1,n2 = get_signal() # 取得交易訊號
        print(f'side:{side} n1:{n1} n2:{n2}')
        if side != 'PASS': # 判斷是否出現方向
            send_to_telegram(message=side)# 發送電報
            place_order(side) # 根據訊號方向下單
        time.sleep(60) # 等一分鐘
