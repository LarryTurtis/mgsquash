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
    for [start, end] in markers:
        cues.append(start - removed)
        removed = removed + (end - start)
    return cues