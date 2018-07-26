import sys
import logging
from struct import pack, unpack
from xclib.utf8 import unutf8

# Message formats described in `../doc/Protocol.md`

class saslauthd_io:
    @classmethod
    def read_request(cls, infd, outfd):
        try:
            infd = infd.buffer
        except AttributeError:
            pass
        field_no = 0
        fields = [None, None, None, None]
        length_field = infd.read(2)
        while len(length_field) == 2:
            (size,) = unpack('>H', length_field)
            val = infd.read(size)
            if len(val) != size:
               logging.warn('premature EOF while reading field %d: %d != %d' % (field_no, len(val), size))
               return
            fields[field_no] = val
            field_no = (field_no + 1) % 4
            if field_no == 0:
                logging.debug('from_saslauthd got %r, %r, %r, %r' % tuple(fields))
                yield ('auth', unutf8(fields[0], 'illegal'), unutf8(fields[3], 'illegal'), unutf8(fields[1], 'illegal'))
            length_field = infd.read(2)

    @classmethod
    def write_response(cls, flag, outfd):
        try:
            outfd = outfd.buffer
        except AttributeError:
            pass
        answer = b'NO xcauth authentication failure'
        if flag:
            answer = b'OK success'
        token = pack('>H', len(answer)) + answer
        outfd.write(token)
        outfd.flush()
