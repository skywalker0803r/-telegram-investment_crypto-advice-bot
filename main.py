from utils import *
import time
import winsound

if __name__ == '__main__':
    while True:
        side,n1,n2 = get_signal()
        print(f'side:{side} n1:{n1} n2:{n2}')
        # 判斷是否出現方向
        if side != 'PASS':
            send_to_telegram(message=side)
            # 持續逼逼叫
            while True:
                winsound.Beep(2222,111)
                winsound.MessageBeep()
                time.sleep(1)
            # 串接binance api 下單
            #place_order(pair='BTCUSDT', side=side, quantity=10, stop_loss_percent=1, take_profit_percent=1)
        time.sleep(60)
