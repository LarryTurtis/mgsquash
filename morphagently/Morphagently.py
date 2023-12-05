import logging
from .utils import read_int, read_int
from .WavData import WavData
# For morphagene, we need 32-bit float, 48kHz, stereo, little-endian.
# Since the samples are 32 bit, each sample gets 4 bytes.
# This is in stereo, it will be
# byte 1 | byte 2 | byte 3 | byte 4 | byte 5 | byte 6 | byte 7 | byte 8
# left channel                      | right channel
# Each second of audion contains 48000 samples for each channel.
# So each second of audio is 48000 * 8 bytes = 384000 bytes.
# We can measure the length of the file by dividing the data chunk size by 384000.

# read the FMT

class Morphagently:
    def __init__(self, path,silence_len=0,silence_threshold=0) -> None:
        self.path = path
        self.silence_len = silence_len
        self.silence_threshold = silence_threshold
        self.__read_file_header()
        self.__find_chunk_headers()
        self.write_file()

    def read_fmt(f):
        cksize = read_int(f.read(4)) # cksize 
        chunk = f.read(cksize)
        wFormatTag = chunk[:2]
        nChannels = chunk[2:4]
        nSamplesPerSec = chunk[4:8] # nSamplesPerSec 
        nAvgBytesPerSec = chunk[8:12] # nSamplesPerSec 
        nBlockAlign = chunk[12:14] # nBlockAlign 
        bitsPerSample = chunk[14:16]
        remainder = chunk[16:]
        logging.debug('wFormatTag: %s', str(read_int(wFormatTag)))
        logging.debug('nChannels: %s', str(read_int(nChannels)))
        logging.debug('nSamplesPerSec: %s', str(read_int(nSamplesPerSec)))
        logging.debug('nAvgBytesPerSec: %s', str(read_int(nAvgBytesPerSec)))
        logging.debug('nBlockAlign: %s', str(read_int(nBlockAlign)))
        logging.debug('bitsPerSample: %s', str(read_int(bitsPerSample)))
        w.write(b'fmt ')
        w.write(cksize.to_bytes(4, 'little'))
        w.write(chunk)
        

    def read_cue(f, size):
        print('---------------')
        cksize = read_int(f.read(4))
        num_points = read_int(f.read(4))
        for i in range(num_points):
            read_int(f.read(4)) # id
            read_int(f.read(4)) # position
            f.read(4) # data chunk id
            read_int(f.read(4)) # chunk start
            read_int(f.read(4)) # block start
            read_int(f.read(4)) # sample start
        print('---------------')
        # Write a cue point at the 50 percent mark

    def write_cue():
        w.write(b'cue ')
        w.write((28).to_bytes(4, 'little')) #cksize
        w.write((1).to_bytes(4, 'little')) #num points
        w.write((0).to_bytes(4, 'little')) #id
        w.write(int(read_int(size) / 20).to_bytes(4, 'little')) #position
        w.write('data'.encode()) #data chunk id
        w.write((0).to_bytes(4, 'little')) # chunk start
        w.write((0).to_bytes(4, 'little')) # block start
        w.write(int(read_int(size) / 20).to_bytes(4, 'little')) # sample start


    def __read_file_header(self):
        with open(self.path, 'rb') as f:
            f.seek(0)
            riff = f.read(4) # should be 'RIFF'
            size = f.read(4) # should be a 4-byte little-endian integer
            wave = f.read(4) # should be 'WAVE'
            self.header = riff + size + wave

    def __find_chunk_headers(self):
        with open(self.path, 'rb') as f:
            f.seek(12)
            self.chunks = {}
            while True:
                chunk_marker = f.read(4)
                chunk_size = read_int(f.read(4))
                self.chunks[chunk_marker] = [f.tell() - 8, chunk_size]
                f.seek(f.tell() + chunk_size)
                if not chunk_marker:
                    break
            logging.debug(self.chunks)

    def write_file(self):
        with open(self.path, 'rb') as f, open('cue_' + self.path, 'wb') as w:
            w.write(self.header)
            for chunk_marker in self.chunks:
                [pos, size] = self.chunks[chunk_marker]
                f.seek(pos)
                if (chunk_marker == b'data'):
                    wavData = WavData(self.path, pos, size).detect_silence(self.silence_len, self.silence_threshold)
                    # w.write(wavData)
                else:
                    data = f.read(size + 8)
                    w.write(data)
