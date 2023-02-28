from utils import *
import time

if __name__ == '__main__':
    while True:
        side = get_signal()
        print('side:',side)
        if side != 'PASS':
            send_to_telegram(message=side)
            #place_order(pair='BTCUSDT', side=side, quantity=10, stop_loss_percent=1, take_profit_percent=1)
        time.sleep(60)
