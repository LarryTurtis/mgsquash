import logging

def read_int(s):
    n = int.from_bytes(s, 'little')
    logging.debug(n)
    return n

def write_int(s):
    return s.to_bytes(4, 'little')

def markers_to_positions(markers):
    removed = 0
    cues = []
    # 4 bytes per sample * 2 channels
    samples = [[int(start / 8), int(end / 8)] for [start, end] in markers]
    for [start, end] in samples:
        cues.append(start - removed)
        removed = removed + (end - start)
    logging.debug("Cues: %s", cues)
    return cues