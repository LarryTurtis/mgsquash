import math
import os, logging, struct
from .utils import read_int, write_int
from collections import deque

logging.basicConfig(level=logging.DEBUG)
class WavData:

    def __init__(self, path, data_pos, size) -> None:
        self.path = path
        self.data_pos = data_pos
        self.__markers = []
        with open(path, 'rb') as wavfile:
            wavfile.seek(data_pos)
            self.data = wavfile.read(size)
            logging.debug(len(self.data))
            logging.debug(data_pos)

    @property
    def size(self):
        return len(self.data) - 8
    
    @property
    def markers(self):
        return self.__markers
    
    def __calculate_rms(self, q, data, sum):
        if q.maxlen == len(q):
            remove = q.popleft()
            sum -= remove * remove
        val = struct.unpack('f', data)[0]
        q.append(val)
        sum += val * val
        try:
            result = [sum, math.sqrt(sum / q.maxlen)]
        except:
            result = [sum, 0]
        return result
    
    def strip_sections(self, markers):
        offset = 0
        for [start, end] in markers:
            size = end - start
            self.data = self.data[:start - offset] + self.data[(start - offset) + size:]
            offset += size
        logging.debug("Stripped %s bytes", offset)
        return offset
    
    def detect_silence(self, silence_len, silence_threshold):
        with open(self.path, 'rb') as wavfile:
            size = 0
            # Convert to float for easier comparison
            silence_threshold = 10 ** (silence_threshold / 20)
            logging.debug("Removing silence for length %s and threshold %s", silence_len, silence_threshold)
            # We write the old header for the size, we'll update it after

            # 48 samples per channel per ms * silence_len in ms
            samples_per_frame = silence_len * 2 * 48

            logging.debug("Reading %s samples per frame", samples_per_frame)
            
            q = deque(maxlen=samples_per_frame)
            sum = 0
            total_bytes = int(len(self.data) / 4)
            # We start on the 3rd byte (2) because the first two are the header and size.
            # 1 sample = 4 bytes. 
            # We go through the bytestring using a frame of silence_len, shifting it by 1 sample each time.
            # We calculate the RMS of each frame and if it's below the threshold, we mark it as silence.
            starts = []
            for i in range(2, total_bytes):
                [sum, rms] = self.__calculate_rms(q, self.data[i*4:i*4+4], sum)

                # Don't calculate anything until we've filled up the first frame.
                start = i*4 - samples_per_frame*4
                if i > samples_per_frame and rms < silence_threshold:
                    time = i / 48 / 2 - silence_len
                    # logging.debug("Found silence at %s with rms %s", time, rms)
                    starts.append(start)

            markers = []
            # combine adjacent starts
            prev = starts.pop(0)
            current_range_start = prev
            for s in starts:
                continuous = (s == prev + 1)
                has_gap = s > prev + samples_per_frame*4

                if not continuous and has_gap:
                    markers.append([current_range_start,
                                  prev + samples_per_frame*4])
                    current_range_start = s
                prev = s
            markers.append([current_range_start, prev + samples_per_frame*4])
            logging.debug("Wrote %s bytes", size)
            self.__markers = markers
            logging.debug("Markers: %s", self.__markers)

            return self.__markers