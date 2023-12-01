import sys
from morphagently import Morphagently

Morphagently(path=sys.argv[1], silence_len=200, silence_threshold=0.03)

# markers = example.hello('song.wav')
# [rate, data, bits, cue] = example.read('song.wav', readmarkers=True)
# example.write('song_cue.wav', rate=rate, data=data, bitrate=bits, markers=cue)