import math
import os, logging, struct
from .utils import read_int, write_int

logging.basicConfig(level=logging.DEBUG)
TMP = 'tmp.wav'
class WavData:

    def __init__(self, path, data_pos, size) -> None:
        self.path = path
        self.data_pos = data_pos
        self.size = size
        self.markers = []
        data = b''
        self.__remove_temp_file() 
        with open(path, 'rb') as wavfile, open(TMP, 'wb') as tmpfile:
            wavfile.seek(data_pos)
            data = wavfile.read(self.size)
            tmpfile.write(data)
    
    def __remove_temp_file(self):
        try:
            os.remove(TMP)
            logging.debug('Removed temp file')
        except:
            logging.debug('No temp file to remove')

    def __read_n_ms(self, ms, wavfile):
        # 1 ms should have 2 channels * 48 samples. 
        # Each sample is 4 bytes.
        samples = int(ms * 2 * 48)
        bytes = samples * 4
        logging.debug("Reading %s bytes", bytes)
        return wavfile.read(bytes)

    def __calculate_rms(self, data, sample_count):
        sum = 0
        for i in range(sample_count):
            val = struct.unpack('f', data[i*4:i*4+4])[0]
            sum += val * val
        rms = 20 * math.log10(math.sqrt(sum / sample_count))
        logging.debug("RMS: %s", rms)
        return rms
        

    def remove_silence(self, silence_len, silence_threshold):
        self.__remove_temp_file() 
        with open(self.path, 'rb') as wavfile, open(TMP, 'wb') as tmpfile:
            size = 0
            silenceCount = silence_len
            logging.debug("Removing silence for length %s and threshold %s", silence_len, silence_threshold)
            # We write the old header for the size, we'll update it after
            wavfile.seek(self.data_pos)
            headers = wavfile.read(8)
            tmpfile.write(headers)
            # samples = silence_len * 2 * 48
            # logging.debug("Reading %s samples", samples)
            # for i in range(int(self.size / samples / 4)):
            #     sec = self.__read_n_ms(silence_len, wavfile)
            #     rms = self.__calculate_rms(sec, samples)
            #     logging.debug("RMS: %s", rms)
            #     if rms > silence_threshold:
            #         tmpfile.write(sec)
            #         size += samples * 4
            for i in range(int(self.size / 4)):
                sample = wavfile.read(4)
                val = struct.unpack('f', sample)[0]

                # we detected noise over the threshold, reset the count.
                if (val >= silence_threshold or val <= -silence_threshold) and (silenceCount > 0):
                    logging.debug("Detected noise, resetting silence count from %s", silenceCount)
                    silenceCount = 0
                else:
                    silenceCount += 1
                if silenceCount <= silence_len:
                    tmpfile.write(sample)
                    size += 4 
            logging.debug("Wrote %s bytes", size)
            logging.debug("Markers: %s", self.markers)

            # Now update the size
            tmpfile.seek(4)
            tmpfile.write(write_int(size))
            self.size = size
            return self.get()

    def get(self):
        return open(TMP, 'rb').read(self.size)