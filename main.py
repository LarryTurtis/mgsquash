import time
import sys
import pydub
from morphagently import Morphagently

Morphagently(path=sys.argv[1], silence_len=200, silence_threshold=-24)

# markers = example.hello('song.wav')
# [rate, data, bits, cue] = example.read('song.wav', readmarkers=True)
# example.write('song_cue.wav', rate=rate, data=data, bitrate=bits, markers=cue)
segment = pydub.AudioSegment.from_wav(sys.argv[1])
segs = pydub.silence.split_on_silence(segment, min_silence_len=200, silence_thresh=-24, seek_step=1)
newseg = sum(segs)
newseg.export(str(time.time()) + sys.argv[1], format='wav')
# segment = pydub.AudioSegment.silent(duration=1000)
# print(pydub.silence.detect_silence(segment, min_silence_len=200, silence_thresh=-24, seek_step=1))
# print(pydub.utils.db_to_float(-24))
# print(segment.rms)
# print(segment.max_possible_amplitude)
