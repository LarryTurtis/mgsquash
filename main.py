import time
import sys
import pydub
from morphagently import Morphagently

Morphagently(path=sys.argv[1], silence_len=int(sys.argv[2]), silence_threshold=int(sys.argv[3]))

# markers = example.hello('song.wav')
# [rate, data, bits, cue] = example.read('song.wav', readmarkers=True)
# example.write('song_cue.wav', rate=rate, data=data, bitrate=bits, markers=cue)
# segment = pydub.AudioSegment.from_wav(sys.argv[1])
# print(pydub.silence.detect_silence(segment, min_silence_len=200, silence_thresh=-34, seek_step=1))
# segs = pydub.silence.split_on_silence(segment, min_silence_len=200, silence_thresh=-34, seek_step=1)
# newseg = sum(segs)
# newseg.export(str(time.time()) + sys.argv[1], format='wav')

