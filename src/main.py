import pyaudio
import audioop
import time


from roku import Roku
from datetime import datetime


RMS_THRESHHOLD = 420

IP_ADDDR = '192.168.1.11'
VOLUME_CLICKS = 6

chunk = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
# RATE = 44100
RATE = 48000
IS_LOUD = False

roku = Roku(IP_ADDDR)

# TODO: make it turn up 4 clicks every ~200 units of sound
# 100-399 tranquil
# 399-


def roku_vol_up():
    for _ in range(0, VOLUME_CLICKS):
        roku.volume_up()
        time.sleep(0.05)


def roku_vol_down():
    for _ in range(0, VOLUME_CLICKS):
        roku.volume_down()
        time.sleep(0.05)


def average_list(lst):
    return sum(lst) / len(lst)


p = pyaudio.PyAudio()
print("IGNORE THESE ERRORS ITS ALL GOOD DWAG")
prev_rms = RMS_THRESHHOLD-1
i = 0
i_limit = 10
# makes a list of the size i_limit
avg_list = [RMS_THRESHHOLD-100] * i_limit
while True:
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                    input=True, output=True, frames_per_buffer=chunk)
    data = stream.read(chunk)
    current_rms = audioop.rms(data, 2)

    avg_list[i] = current_rms
    # this is so anomiloes don't fuck up our threshhold
    test_rms = average_list(avg_list)

    # test_rms = current_rms

    # set is loud
    if test_rms > RMS_THRESHHOLD:
        if not IS_LOUD:
            print(datetime.now().strftime("%H:%M:%S") +
                  '-----------------volume up')
            roku_vol_up()

        IS_LOUD = True
    if test_rms < RMS_THRESHHOLD:
        if IS_LOUD:
            print(datetime.now().strftime("%H:%M:%S") +
                  '-----------------volume down')
            roku_vol_down()
        IS_LOUD = False

    print(test_rms)
    prev_rms = current_rms

    # clean up stream so it doesn't overflow
    stream.stop_stream()
    stream.close()
    # wait
    time.sleep(1)
    i += 1
    if i == i_limit:
        i = 0
# p.terminate()
