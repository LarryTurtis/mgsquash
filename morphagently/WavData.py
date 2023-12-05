import math
import os, logging, struct
from .utils import read_int, write_int
from collections import deque

logging.basicConfig(level=logging.DEBUG)
class WavData:

    def __init__(self, path, data_pos, size) -> None:
        self.path = path
        self.data_pos = data_pos
        self.__size = size
        self.markers = []
        with open(path, 'rb') as wavfile:
            wavfile.seek(data_pos)
            self.data = wavfile.read(self.size)
            logging.debug(len(self.data))
            logging.debug(data_pos)
    
    @property
    def size(self):
        return self.__size
    
    def __calculate_rms(self, q, data, sum):
        if q.maxlen == len(q):
            remove = q.popleft()
            sum -= remove * remove
        val = struct.unpack('f', data)[0]
        q.append(val)
        sum += val * val
        if sum == 0:
            return [sum, -50]
        return [sum, math.sqrt(sum / q.maxlen)]
    
    def strip_sections(self, markers):
        size = 0
        for [start, end] in markers:
            size = size + (end - start)
            self.data = self.data[:start] + self.data[end:]
        logging.debug("Stripped %s bytes", size)
        logging.debug(len(self.data))
        self.__size = self.__size - size

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
            flip = False
            sum = 0
            total_bytes = int(len(self.data) / 4)
            # We start on the 3rd byte (2) because the first two are the header and size.
            # 1 sample = 4 bytes. 
            # We go through the bytestring using a frame of silence_len, shifting it by 1 sample each time.
            # We calculate the RMS of each frame and if it's below the threshold, we mark it as silence.
            for i in range(2, total_bytes):
                [sum, rms] = self.__calculate_rms(q, self.data[i*4:i*4+4], sum)

                # Don't calculate anything until we've filled up the first frame.
                if i > samples_per_frame:
                    if rms < silence_threshold and not flip:
                        flip = True
                        time = i / 48 / 2 - silence_len
                        logging.debug("Found silence at %s with rms %s", time, rms)
                        logging.debug("i: %s", i)
                        self.markers.append([i])
                    elif rms >= silence_threshold and flip:
                        time = i / 48 / 2
                        logging.debug("Found end of silence at %s with rms %s", time, rms)
                        self.markers[len(self.markers) - 1].append(i)
                        flip = False
                size += 4

            logging.debug("Wrote %s bytes", size)
            logging.debug("Markers: %s", self.markers)
            self.__size = size

            return self.markers