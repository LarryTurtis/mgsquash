import sys
import pydub
from morphagently import Morphagently

Morphagently(path=sys.argv[1], silence_len=50, silence_threshold=-24)

# markers = example.hello('song.wav')
# [rate, data, bits, cue] = example.read('song.wav', readmarkers=True)
# example.write('song_cue.wav', rate=rate, data=data, bitrate=bits, markers=cue)
# segment = pydub.AudioSegment.from_wav(sys.argv[1])
# print(pydub.silence.detect_silence(segment, min_silence_len=50, silence_thresh=-24, seek_step=1))
