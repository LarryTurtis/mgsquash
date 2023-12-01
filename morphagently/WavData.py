import os, logging, struct
from .utils import read_int, write_int

logging.basicConfig(level=logging.DEBUG)
class WavData:
    tmp = 'tmp'

    def __init__(self, path, data_pos, size) -> None:
        self.path = path
        self.data_pos = data_pos
        self.size = size
        data = b''
        os.remove(self.tmp)
        with open(path, 'rb') as wavfile, open(self.tmp, 'wb') as tmpfile:
            wavfile.seek(data_pos)
            data = wavfile.read(self.size)
            tmpfile.write(data)

    def remove_silence(self, silence_len=4000, threshold=0.03):
        os.remove(self.tmp)
        with open(self.path, 'rb') as wavfile, open(self.tmp, 'wb') as tmpfile:
            size = 0
            silenceCount = silence_len

            # We write the old header for the size, we'll update it after
            wavfile.seek(self.data_pos)
            headers = wavfile.read(8)
            tmpfile.write(headers)
            for i in range(int(self.size / 4)):
                sample = wavfile.read(4)
                val = struct.unpack('f', sample)[0]
                if val > threshold or val < -threshold:
                    silenceCount = 0
                else:
                    silenceCount += 1
                if silenceCount < silence_len:
                    tmpfile.write(sample)
                    size += 4 
            logging.debug(size)

            # Now update the size
            tmpfile.seek(4)
            tmpfile.write(write_int(size))
            self.size = size
            return self.get()

    def get(self):
        return open(self.tmp, 'rb').read(self.size)