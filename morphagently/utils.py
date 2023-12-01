import logging

def read_int(s):
    n = int.from_bytes(s, 'little')
    logging.debug(n)
    return n

def write_int(s):
    return s.to_bytes(4, 'little')
