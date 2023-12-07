import os, time, logging
from .utils import read_int, read_int, markers_to_positions
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

    def read_fmt(self, f, size):
        chunk = f.read(size)
        wFormatTag = read_int(chunk[:2])
        logging.debug('wFormatTag: %s', str(wFormatTag))
        if wFormatTag != 3:
            raise Exception("Not a 32-bit float file")

        nChannels = read_int(chunk[2:4])
        logging.debug('nChannels: %s', str(nChannels))
        if nChannels != 2:
            raise Exception("Not a stereo file")
        
        nSamplesPerSec = read_int(chunk[4:8]) # nSamplesPerSec 
        logging.debug('nSamplesPerSec: %s', str(nSamplesPerSec))
        if nSamplesPerSec != 48000:
            raise Exception("Not a 48kHz file")
 
        nAvgBytesPerSec = read_int(chunk[8:12])
        logging.debug('nAvgBytesPerSec: %s', str(nAvgBytesPerSec))
        if nAvgBytesPerSec != 384000:
            raise Exception("Not a 32bit file")

        nBlockAlign = read_int(chunk[12:14]) # nBlockAlign 
        logging.debug('nBlockAlign: %s', nBlockAlign)
        if nBlockAlign != 8:
            raise Exception("Not a 32bit file")

        bitsPerSample = read_int(chunk[14:16])
        logging.debug('bitsPerSample: %s', str(bitsPerSample))
        if bitsPerSample != 32:
            raise Exception("Not a 32bit file")

        remainder = chunk[16:]
        if remainder != b'':
            logging.warning("Found extra data in header, this may cause issues.")
        

    def read_cue(self, f, size):
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

    def write_cue(self, w, positions):
        w.write(b'cue ')
        cue_len = 4 + 24 * len(positions)
        w.write(cue_len.to_bytes(4, 'little')) #cksize
        w.write((len(positions)).to_bytes(4, 'little')) #num points
        for i, pos in enumerate(positions):
            w.write(i.to_bytes(4, 'little')) #id
            w.write(pos.to_bytes(4, 'little')) #position
            w.write('data'.encode()) #data chunk id
            w.write((0).to_bytes(4, 'little')) # chunk start
            w.write((0).to_bytes(4, 'little')) # block start
            w.write(pos.to_bytes(4, 'little')) # sample start
        return cue_len + 8


    def __read_file_header(self):
        with open(self.path, 'rb') as f:
            f.seek(0)
            riff = f.read(4) # should be 'RIFF'
            if (riff != b'RIFF'):
                raise Exception("Not a RIFF file")
            size = f.read(4) # should be a 4-byte little-endian integer
            self.size = read_int(size)
            if self.size <= 0:
                raise Exception("Invalid file size")
            wave = f.read(4) # should be 'WAVE'
            if (wave != b'WAVE'):
                raise Exception("Not a WAVE file")
            self.header = riff + size + wave

    def __find_chunk_headers(self):
        with open(self.path, 'rb') as f:
            f.seek(12)
            self.chunks = {}
            while True:
                chunk_marker = f.read(4)
                chunk_size = read_int(f.read(4))
                chunk_start = f.tell()
                self.chunks[chunk_marker] = [chunk_start - 8, chunk_size]

                if chunk_marker == b'fmt ':
                    self.read_fmt(f, chunk_size)
                
                if chunk_marker == b'cue ':
                    logging.warning("Found existing cue chunk, removing")
                    self.chunks.pop(chunk_marker)
                
                if chunk_marker == b'plst' or chunk_marker == b'wavl':
                    raise Exception("Found plst or wavl chunk, not supported")

                f.seek(chunk_start + chunk_size)
                if not chunk_marker:
                    break
            logging.debug(self.chunks)

    def write_file(self):
        with open(self.path, 'rb') as f, open(str(time.time()) + self.path, 'wb') as w:
            updated_bytes = 0
            w.write(self.header)
            for chunk_marker in self.chunks:
                [pos, size] = self.chunks[chunk_marker]
                f.seek(pos)
                if (chunk_marker == b'data'):
                    wavData = WavData(self.path, pos, size)
                    markers = wavData.detect_silence(self.silence_len, self.silence_threshold)
                    removed_bytes = wavData.strip_sections(markers)
                    total_bytes = len(wavData.data)
                    last_sample = int(total_bytes / 8)
                    positions = markers_to_positions(markers)                    
                    positions.append(last_sample)

                    logging.debug("Writing positions %s", positions)
                    added_bytes = self.write_cue(w, positions)
                    updated_bytes = updated_bytes + added_bytes - removed_bytes
    
                    w.write(b'data')
                    logging.debug("Writing data of size %s", total_bytes)
                    w.write(total_bytes.to_bytes(4, 'little'))
                    w.write(wavData.data)
                else:
                    data = f.read(size + 8)
                    w.write(data)
            w.seek(4)
            w.write((self.size + updated_bytes).to_bytes(4, 'little'))   
            logging.debug("Wrote file with %s bytes added", added_bytes)
            logging.debug("Wrote file with %s bytes removed", removed_bytes)
            logging.debug("Wrote file with %s bytes updated", updated_bytes)

