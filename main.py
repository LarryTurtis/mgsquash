# from morphagently import main
from morphagently import Morphagently

Morphagently(path='test.wav', silence_len=100, silence_threshold=0.03)

# markers = example.hello('song.wav')
# [rate, data, bits, cue] = example.read('song.wav', readmarkers=True)
# example.write('song_cue.wav', rate=rate, data=data, bitrate=bits, markers=cue)