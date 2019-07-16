#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Classes for introducing random glitch effects into PNG files.

This script offers a class GlitchedPNGFile that enables the user
to partially decompress a PNG file and deliberately put errors into
it's bytestream.

Usage:

The constructor of GlitchedPNGFile takes a PNG file name and reads
in the chunks of the given file.
After that, you can call the glitch_file method to insert random
errors into the file. The glitch_file method iterates over the
resulting image files.
You can write these to disk via their write method.

You can also call the glitch effect methods (fill_noise, fill_zeros,
move, and switch) directly, but you have to wrap these calls between
calls to start_glitching and end_glitching.
The former decompresses the file, the latter compresses it again and
portions the data into equally-sized chunks again.

Methods preceded with an underscors can change the amount of pixels
in the image and, thus, render it completely unreadable. I advise
against using these.

"""

import zlib
import random


class Chunk(object):
    """Class representation of PNG chunks."""

    # --- Chunk constructors -------------------------------------------

    def __init__(self, name="IDAT", data=""):
        """Creates a chunk.

        Fill it with the data parameter or via the method from_file.

        """
        self.name = name
        self.pos = 0
        self.length = len(data)
        self.crc = None  # gets set through the data property
        self.raw_data = None
        self.data = data

    def from_file(self, pngfile, pos=None):
        """Reads a chunk from the current position in f.

        The pngfile argument is a PNG file opened in binary read mode.
        The pos argument is the position from which to read. It
        defaults to the current position.

        Please note that this method does not check if the chunk
        indeed starts at the given position.

        """

        def _read_long_from_file(file_):
            return self.get_long(bytearray(file_.read(4)))

        read_from_current = (pos is None)
        if not read_from_current:
            backup_pos = pngfile.tell()
            pngfile.seek(pos)
        # Read information.
        self.pos = pngfile.tell()
        self.length = _read_long_from_file(pngfile)
        self.name = pngfile.read(4).decode("ascii")
        self.raw_data = pngfile.read(self.length)
        self.crc = _read_long_from_file(pngfile)
        # Go back to old position if necessary.
        if not read_from_current:
            pngfile.seek(backup_pos)

    @classmethod
    def new_from_file(cls, pngfile, pos=None):
        """Like from_file, but returns a newly created Chunk."""
        chunk = cls()
        chunk.from_file(pngfile, pos)
        return chunk

    def copy(self):
        """Returns a copy of this chunk."""
        new_chunk = type(self)(self.name)
        new_chunk.pos = self.pos
        new_chunk.length = self.length
        new_chunk.raw_data = self.raw_data
        new_chunk.crc = self.crc
        return new_chunk

    # --- Handling bytearrays ------------------------------------------

    @staticmethod
    def set_long(num):
        """Stores a long int in a bytearray of length 4."""
        return bytearray((num >> (8 * (3 - i))) & 0xFF for i in range(4))

    @staticmethod
    def get_long(buf):
        """Extracts a long it from a bytearray of length 4."""
        return sum(byte << (8 * (3 - i)) for i, byte in enumerate(buf))

    # --- Conversion to Strings ----------------------------------------

    def get_raw(self):
        """Returns the whole chunk as a bytearray.

        Use this this method to write the chunk into a file.

        """
        return sum([
            self.set_long(self.length),
            self.name.encode("ascii"),
            self.raw_data,
            self.set_long(self.crc),
        ], bytearray())

    def __str__(self):
        return '{name} chunk of length {length}, CRC: {crc}'.format(
            name=self.name, length=self.length, crc=hex(self.crc))

    def __repr__(self):
        return '<{classname} object at {pos}>'.format(
            classname=type(self).__name__,
            pos=id(self),
        )

    # --- CRC Computation ----------------------------------------------

    def compute_crc(self):
        """Compute the cyclic redundancy check sum."""
        return zlib.crc32(self.name.encode("ascii") + self.raw_data)

    def update_crc(self):
        """Update the chunk's CRC."""
        self.crc = self.compute_crc()

    def update_length(self):
        """Update the chunk's length."""
        self.length = len(self.raw_data)

    def check_data(self):
        """Check whether the data's CRC matches the chunk's CRC
        attribute."""
        return self.crc == self.compute_crc()

    # --- Access to the Data Member Via Property -----------------------

    @property
    def data(self):
        """Access to the chunk data via property.

        The data property gives access to the raw chunk data while
        keeping the chunk length and check sum up-to-date.

        """
        return self.raw_data

    @data.setter
    def data(self, new_data):
        self.raw_data = new_data
        self.update_crc()
        self.length = len(new_data)

    # --- Various Built-ins --------------------------------------------

    def __len__(self):
        return self.length

    def __nonzero__(self):
        return bool(self.length)


class PNGFile(object):
    """Nice class representation of our beloved PNG files.

    Contains methods for chunk access, loading, and writing.

    """

    # --- Constructor --------------------------------------------------

    def __init__(self, image_name=None):
        """Takes a file name and loads all chunks plus header."""
        self.chunks = []
        if image_name is None:
            self.header = b'\x89PNG\r\n\x1a\n'
            return
        with open(image_name, "rb") as png_file:
            self.header = png_file.read(8)
            eof = False
            while not eof:
                new_chunk = Chunk.new_from_file(png_file)
                if new_chunk:
                    self.chunks.append(new_chunk)
                else:
                    eof = True

    def copy(self):
        """Returns a deep copy of the PNG File."""
        new_image = type(self)()
        new_image.chunks = [chunk.copy() for chunk in self.chunks]
        return new_image

    # --- Chunk Iterators ----------------------------------------------

    def idat_chunks(self):
        """Returns an iterable over all IDAT chunks."""
        return (chunk for chunk in self.chunks if chunk.name == "IDAT")

    def various_chunks(self):
        """Returns an iterable over all chunks except IDAT and IEND."""
        return (chunk for chunk in self.chunks
                if chunk.name not in {"IDAT", "IEND"})

    # --- Compression & Decompression ----------------------------------

    def decompress(self):
        """Get the decompressed image data.

        This does not undo the filter applied to the image.

        """
        buf = ''.join(chunk.data for chunk in self.idat_chunks())
        return bytearray(zlib.decompress(buf))

    @staticmethod
    def buffer_to_chunks(buf, chunk_size):
        """Splits an uncompressed buffer into a list of IDAT chunks."""
        buf = zlib.compress(buffer(buf))
        chunk_count = (
            len(buf) / chunk_size + (1 if len(buf) % chunk_size else 0))
        new_chunks = []
        for i in xrange(chunk_count):
            data = buf[i * chunk_size:(i + 1) * chunk_size]
            new_chunks.append(Chunk("IDAT", data))
        return new_chunks

    def overload(self, buf):
        """Forget the old image data and replace it with buf.

        This compresses buf via Deflate and portions it into nice
        chunks.
        Do not delete the old image data before calling this method.
        This method will do that for you.

        """
        chunk_size = len(next(self.idat_chunks()))
        new_chunks = list(self.various_chunks())
        new_chunks.extend(self.buffer_to_chunks(buf, chunk_size))
        new_chunks.append(Chunk("IEND"))
        self.chunks = new_chunks

    # --- Writing to Disk ----------------------------------------------

    def write(self, name):
        """Write the object into the file called name."""
        with open(name, "wb") as pngfile:
            pngfile.write(self.header)
            for chunk in self.chunks:
                pngfile.write(chunk.get_raw())


class GlitchedPNGFile(PNGFile):
    """Subclass of PNGFile that adds methods to add glitch effects."""

    # --- Actually Important Methods -----------------------------------

    def __init__(self, image_name=None):
        """See PNGFile.__init__ for help."""
        PNGFile.__init__(self, image_name)
        self._decompressed = None

    def begin_glitching(self):
        """Prepares the file for applying glitches."""
        self._decompressed = self.decompress()

    def end_glitching(self):
        """Stops glitching and pack the file into chunks again."""
        self.overload(self._decompressed)
        self._decompressed = None

    def random_glitches(self, glitch_amount, glitch_size, glitch_dev):
        """Applies random glitches to the image data.

        glich_amount: number of bytes to be affected
        glitch_size: mean size of one glitch in bytes
        glich_dev: standard deviation of glitch_size

        """
        method_list = (4 * [self.fill_noise] + 3 * [self.fill_zeros] +
                       [self.move, self.switch])
        to_be_glitched = glitch_amount
        while to_be_glitched > 0:
            amount = int(random.gauss(glitch_size, glitch_dev))
            amount = min(max(amount, 2), to_be_glitched)
            to_be_glitched -= amount
            random.choice(method_list)(amount)

    def glitch_file(self, glitch_amount, glitch_size, glitch_dev, copies=1):
        """Applies random glitches to a PNG file.

        This is an iterator that calls the random_glitches method,
        wrapped in begin_glitching and end_glitching, and yields
        the resulting PNG files.
        The copies argument specifies how many results to yield.
        For help on the mandatory arguments, refer to the
        random_glitches method.

        """
        self.begin_glitching()
        backup = self._decompressed[:]
        for _ in range(copies):
            self._decompressed = backup[:]
            self.random_glitches(glitch_amount, glitch_size, glitch_dev)
            self.end_glitching()
            yield self.copy()

    # --- Internal Stuff (Better Not Call Directly) --------------------

    @staticmethod
    def random_bytes(length):
        """Returns a random bytearray of specified length."""
        return bytearray(random.randint(0, 255) for i in range(length))

    def _insert(self, pos, ins):
        """Inserts bytearray ins at position pos into the image data."""
        self._decompressed[pos:pos] = ins
        return len(ins)

    def _remove(self, pos, length):
        """Removes length bytes at position pos from the image data."""
        rem = self._decompressed[pos:pos + length]
        del self._decompressed[pos:pos + length]
        return rem

    def replace(self, pos, rep):
        """Replace image data at position pos with bytearray rep."""
        length = len(self._decompressed)
        self._decompressed[pos:pos + len(rep)] = rep
        del self._decompressed[length:]

    def fill_noise(self, length, pos=None):
        """Replace image data with random bytes.

        The pos argument is random if not specified otherwise.

        """
        if pos is None:
            pos = random.randint(0, len(self._decompressed) - length)
        self.replace(pos, self.random_bytes(length))

    def fill_zeros(self, length, pos=None):
        """Replace image data with zero bytes.

        The pos argument is random if not specified otherwise.

        """
        if pos is None:
            pos = random.randint(0, len(self._decompressed) - length)
        self.replace(pos, length * '\x00')

    def move(self, length, from_=None, to_=None):
        """Move a block of image data from one place to another.

        The position arguments are random if not specified otherwise.

        """
        if from_ is None:
            from_ = random.randint(0, len(self._decompressed) - length)
        if to_ is None:
            to_ = random.randint(0, len(self._decompressed) - length)
        self._insert(to_, self._remove(from_, length))

    def switch(self, len_one, pos_one=None, len_two=None, pos_two=None):
        """Move a block of image data from one place to another.

        The position arguments are random if not specified otherwise.
        If len_two is not specifies, len_one will be split into two
        random parts.

        """
        if len_two is None:
            len_two = random.randint(1, len_one)
            len_one -= len_two
        if pos_one is None:
            pos_one = random.randint(
                0,
                len(self._decompressed) - len_one - len_two,
            )
        if pos_two is None:
            pos_two = random.randint(
                pos_one + len_one,
                len(self._decompressed) - len_two,
            )
        if pos_one > pos_two:
            pos_one, pos_two = pos_two, pos_one
            len_one, len_two = len_two, len_one
        assert pos_one + len_one <= pos_two
        self.move(len_two, pos_two, pos_one + len_one)
        self.move(len_one, pos_one, pos_two)
