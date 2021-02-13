import pyaudio
import audioop
import time


from roku import Roku
from datetime import datetime


# this is unironically a good sound value, usually its above this when the vent comes on
RMS_THRESHHOLD = 690

# IP of the roku device
IP_ADDDR = '192.168.1.11'

VOLUME_CLICKS = 5

# audio stuff
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000

# logging
SHOULD_LOG = True

# If we're in the loud level
IS_LOUD = False

roku = Roku(IP_ADDDR)


def roku_vol_up():
    for _ in range(0, VOLUME_CLICKS):
        roku.volume_up()


def roku_vol_down():
    for _ in range(0, VOLUME_CLICKS):
        roku.volume_down()


def average_list(lst):
    return sum(lst) / len(lst)


def logger(message):
    if SHOULD_LOG:
        print(message)


p = pyaudio.PyAudio()
print("IGNORE THESE ERRORS ITS ALL GOOD DWAG")

i = 0   # counter for loop

# this is so anomiloes don't constantly change the volume
# makes a list of the size i_limit
rms_average_size = 10
avg_rms = [RMS_THRESHHOLD-100] * rms_average_size

# main loop, one second seems to work best
while True:
    # do audio stuff
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                    input=True, output=True, frames_per_buffer=CHUNK)
    data = stream.read(CHUNK)

    # idk what unit of measure it is, but its consistent
    current_rms = audioop.rms(data, 2)

    avg_rms[i] = current_rms
    test_rms = average_list(avg_rms)

    if test_rms > RMS_THRESHHOLD:
        if not IS_LOUD:
            logger(datetime.now().strftime("%H:%M:%S") +
                   '-----------------volume up')
            roku_vol_up()

        IS_LOUD = True
    if test_rms < RMS_THRESHHOLD:
        if IS_LOUD:
            logger(datetime.now().strftime("%H:%M:%S") +
                   '-----------------volume down')
            roku_vol_down()
        IS_LOUD = False

    logger(test_rms)

    # clean up stream so it doesn't overflow
    stream.stop_stream()
    stream.close()

    # increment counter
    i += 1
    if i == rms_average_size:
        i = 0

    # wait
    time.sleep(1)
