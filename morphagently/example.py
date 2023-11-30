import struct
# For morphagene, we need 32-bit float, 48kHz, stereo, little-endian.
# Since the samples are 32 bit, each sample gets 4 bytes.
# This is in stereo, it will be
# byte 1 | byte 2 | byte 3 | byte 4 | byte 5 | byte 6 | byte 7 | byte 8
# left channel                      | right channel
# Each second of audion contains 48000 samples for each channel.
# So each second of audio is 48000 * 8 bytes = 384000 bytes.
# We can measure the length of the file by dividing the data chunk size by 384000.

f = open('song.wav', 'rb')
w = open('cued_mg1.wav', 'wb')

def byteStringToInt(s):
    return int.from_bytes(s, 'little')

def read_int(n):
    r = byteStringToInt(f.read(n))
    # print(r)
    return r

# read the FMT
def read_fmt(f):
    cksize = read_int(4) # cksize 
    chunk = f.read(cksize)
    wFormatTag = chunk[:2]
    nChannels = chunk[2:4]
    nSamplesPerSec = chunk[4:8] # nSamplesPerSec 
    nAvgBytesPerSec = chunk[8:12] # nSamplesPerSec 
    nBlockAlign = chunk[12:14] # nBlockAlign 
    bitsPerSample = chunk[14:16]
    remainder = chunk[16:]
    print('wFormatTag: ' + str(byteStringToInt(wFormatTag)))
    print('nChannels: ' + str(byteStringToInt(nChannels)))
    print('nSamplesPerSec: ' + str(byteStringToInt(nSamplesPerSec)))
    print('nAvgBytesPerSec: ' + str(byteStringToInt(nAvgBytesPerSec)))
    print('nBlockAlign: ' + str(byteStringToInt(nBlockAlign)))
    print('bitsPerSample: ' + str(byteStringToInt(bitsPerSample)))
    w.write(b'fmt ')
    w.write(cksize.to_bytes(4, 'little'))
    w.write(chunk)
    
# At this point, there may be additional format data up to cksize.

# But for us it's probably the next chunk

def read_data(f, chunk_marker):
    data_size = read_int(4)
    print(f.tell())
    print(data_size)
    w.write(chunk_marker)
    if chunk_marker == b'data':
        temp = open('tmp', 'wb')
        size = 0
        silenceCount = 24000
        for i in range(int(data_size / 4)):
            sample = f.read(4)
            val = struct.unpack('f', sample)[0]
            if val > 0.03 or val < -0.03:
                silenceCount = 0
            else:
                silenceCount += 1
            if silenceCount < 24000:
                # print(val)
                temp.write(sample)
                size += 4
        print(size)
        w.write(size.to_bytes(4, 'little'))
        data = open('tmp', 'rb').read(size)
        w.write(data)
    else:
        w.write(data_size.to_bytes(4, 'little'))
        data = f.read(data_size)
        w.write(data)

def read_cue(f, size):
    print('---------------')
    cksize = read_int(4)
    num_points = read_int(4)
    for i in range(num_points):
        read_int(4) # id
        read_int(4) # position
        f.read(4) # data chunk id
        read_int(4) # chunk start
        read_int(4) # block start
        read_int(4) # sample start
    print('---------------')
    # Write a cue point at the 50 percent mark

def write_cue():
    w.write(b'cue ')
    w.write((28).to_bytes(4, 'little')) #cksize
    w.write((1).to_bytes(4, 'little')) #num points
    w.write((0).to_bytes(4, 'little')) #id
    w.write(int(byteStringToInt(size) / 20).to_bytes(4, 'little')) #position
    w.write('data'.encode()) #data chunk id
    w.write((0).to_bytes(4, 'little')) # chunk start
    w.write((0).to_bytes(4, 'little')) # block start
    w.write(int(byteStringToInt(size) / 20).to_bytes(4, 'little')) # sample start

def read_chunk_header(f, size):
    chunk_marker = f.read(4)
    if not chunk_marker:
        return False
    print(chunk_marker)
    if chunk_marker == b'cue ':
        read_cue(f, size)
    elif chunk_marker == b'fmt ':
        read_fmt(f)
    else:
        read_data(f, chunk_marker)
    return True

riff = f.read(4) # should be 'RIFF'
size = f.read(4) # should be a 4-byte little-endian integer
wave = f.read(4) # should be 'WAVE'
newSize = (byteStringToInt(size) - 220 + 28).to_bytes(4, 'little')
w.write(riff + newSize + wave)

while True:
    cont = read_chunk_header(f, int.from_bytes(size, 'little'))
    if not cont:
        break
write_cue()


