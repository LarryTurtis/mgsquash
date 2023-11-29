
f = open('mg1.wav', 'rb')
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
    data = f.read(data_size)
    w.write(chunk_marker)
    w.write(data_size.to_bytes(4, 'little'))
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


