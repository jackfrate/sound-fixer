import pyaudio
import audioop
import time


from roku import Roku
from datetime import datetime


# this is unironically a good sound value, usually its above this when the vent comes on
RMS_THRESHHOLD = 690
# RMS_THRESHHOLD = 100 # good for testing

# IP of the roku device
IP_ADDDR = '192.168.1.11'

# how many clicks to adjust the volume
VOLUME_CLICKS = 5

# audio stuff
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000

# logging
SHOULD_LOG = True

# If we're in the loud level
LOUD_NOW = False

roku = Roku(IP_ADDDR)


def logger(message):
    if SHOULD_LOG:
        print(message)


def make_timestamp(message: str = ''):
    return f'{datetime.now().strftime("%H:%M:%S")} -> {message}'


def roku_vol_up():
    msg = make_timestamp('volume up')
    logger(msg)
    try:
        for _ in range(0, VOLUME_CLICKS):
            roku.volume_up()
    except:
        logger('could not connect')


def roku_vol_down():
    msg = make_timestamp('volume down')
    logger(msg)
    try:
        for _ in range(0, VOLUME_CLICKS):
            roku.volume_down()
    except:
        logger('could not connect')


def average_list(lst):
    return sum(lst) / len(lst)


# this makes a bunch of errors that are a) ok and b) non-suppressable
p = pyaudio.PyAudio()
print("IGNORE THESE ERRORS ITS ALL GOOD DWAG")


# this is so anomiloes don't constantly change the volume
# makes a list of the size i_limit
rms_average_size = 10
avg_rms = [RMS_THRESHHOLD-100] * rms_average_size
i = 0   # counter for loop

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
        if not LOUD_NOW:
            roku_vol_up()
        LOUD_NOW = True

    if test_rms < RMS_THRESHHOLD:
        if LOUD_NOW:
            roku_vol_down()
        LOUD_NOW = False

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
