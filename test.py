import os
from datetime import datetime
import time

while True:
    print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    time.sleep(1)
    os.system("cls")