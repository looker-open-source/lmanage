import time
from progress.bar import ChargingBar

mylist = [1, 2, 3, 4, 5, 6, 7, 8]
bar = ChargingBar('Countdown', max=len(mylist))
for item in mylist:
    print("    "+str(item))
    bar.next()
    time.sleep(1)
bar.finish()
