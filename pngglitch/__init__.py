#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Classes for introducing random glitch effects into PNG files.

This script offers a class `GlitchedPNGFile` that enables the user to partially
decompress a PNG file and deliberately put errors into its bytestream.

The constructor of `GlitchedPNGFile` takes a PNG file name and reads it chunk
by chunk.  After that, you have two options:

1. Call `~GlitchedPNGFile.glitch_file()` to get an iterator that produces one
   or multiple glitched image files from the original. You can then write each
   one to disk.
2. Call `~GlitchedPNGFile.begin_glitching()` and then manually apply various
   glitch effects to the file. You can also call
   `~GlitchedPNGFile.random_glitches()` to have glitch effects randomly picked.
   Afterwards, call `~GlitchedPNGFile.end_glitching()` to recompress the file
   and write it to disk.

Methods preceded with an underscore can change the amount of pixels in the
image and, thus, may render it unreadable. They should not be used.

"""

import zlib
import random

# TODO: Split into several modules. Turn glitch effects into functions or an
# unrelated class that *operates* on PNG files instead of *being* a PNG file.
# Allow streaming operation if possible.


class Chunk(object):
    """Class representation of PNG chunks.

    This class encapsulates the encoding and decoding of chunks as well as
    computation of their CRCs.

    The constructor is best used to create new chunks from scratch. To read an
    existing chunk from a PNG file, use `new_from_file()` instead.

    Args:
        name (str): The 4-letter, case-sensitive chunk type.
        data (str): The payload bytes of the chunk.

    Attributes:
        name (str): The chunk type, consisting of 4 ASCII alphabetic
            characters. The case of the characters determines various
            properties:

            1. If uppercase, the chunk is *critical*, otherwise *ancillary*.
            2. If uppercase, the chunk type is a *standard* type, otherwise
               it's a *private* type.
            3. Must always be uppercase.
            4. If uppercase, the chunk is not safe to copy and must be
               discarded if the picture is modified; otherwise, it is safe to
               copy even if the chunk type is unknown.

        pos (int): The position of the chunk in its PNG file. 0 for newly
            created chunks.
        length (int): The length of the chunk payload in bytes. This does not
            count length nor type nor CRC. Do not modify this attribute. It
            gets updated whenever `data` is set.
        crc (int): The cyclic redundancy checksum of this chunk's payload. Do
            not modify this attribute. It gets updated whenever `data` is set.
        raw_data (str): The payload of this chunk as raw bytes. Do not modify
            this attribute. The `data` property should be used instead, it
            automatically updates CRC and length.
    """

    # --- Chunk constructors -------------------------------------------

    def __init__(self, name="IDAT", data=""):
        # TODO: Verify the chunk type better.
        if len(name) != 4:
            raise TypeError('invalid chunk type: {}'.format(name))
        self.name = name
        self.pos = 0
        self.length = len(data)
        # TODO: Make `crc` a readonly property.
        self.crc = None  # This gets set through the `data` property.
        self.raw_data = None  # TODO: Deprecate public usage.
        self.data = data

    # TODO: Deprecate this function.
    def from_file(self, pngfile, pos=None):
        """Read a chunk from a file.

        This replaces this chunks data with data read from a PNG file.
        Depending on whether `pos` is passed, this function operates in one of
        two ways:

        `pos` is not passed:
            This reads from the current position and updates the file cursor
            normally.
        `pos` is passed:
            This seeks to `pos` and reads the chunk. After *successful*
            reading, this seeks back to the position before the call.

        Note:
            This reads blindly from the given file. No check is performed that
            a PNG chunk actually starts at the given position.

        Args:
            pngfile (file): A readable PNG file opened in binary mode.
            pos (*int*, optional): If passed, chunk data is read from this
                position inside `pngfile`. Otherwise, this reads from the
                current position.

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
        if len(self.name) != 4:
            raise TypeError('invalid chunk type: {}'.format(self.name))

    @classmethod
    def new_from_file(cls, pngfile, pos=None):
        """Create a new chunk and fill it via `from_file()`."""
        chunk = cls()
        chunk.from_file(pngfile, pos)
        return chunk

    def copy(self):
        """Copy this chunk.

        Returns:
            Chunk: A new chunk with the same type, payload and CRC.

        """
        new_chunk = type(self)(self.name)
        new_chunk.pos = self.pos
        new_chunk.length = self.length
        new_chunk.raw_data = self.raw_data
        new_chunk.crc = self.crc
        return new_chunk

    # --- Handling bytearrays ------------------------------------------

    @staticmethod
    def set_long(num):
        """Convert a 32-bit integer to a big-endian bytearray.

        Args:
            num (int): The integer to convert. Gets truncated to 32 bits.

        Returns:
            bytearray: An array of 4 bytes in big-endian order, i.e. the
            first byte contains the most significant digits.

        """
        return bytearray((num >> (8 * (3 - i))) & 0xFF for i in range(4))

    @staticmethod
    def get_long(buf):
        """Extract a 32-bit integer from a big-endian bytearray.

        Args:
            buf (bytearray): The buffer to convert. Must be of length 4. The
                buffer is interpreted in big-endian order, i.e. first byte
                contains the most significant digits.

        Returns:
            int: A 32-bit integer.

        """
        return sum(byte << (8 * (3 - i)) for i, byte in enumerate(buf))

    # --- Conversion to Strings ----------------------------------------

    def get_raw(self):
        """Return the chunk in a form writable to file.

        Returns:
            bytearray: The serialized chunk including the length field, the
            chunk type and the CRC.

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
        """Compute the cyclic redundancy checksum of this chunk's payload.

        Returns:
            int: The checksum.
        """
        # TODO: The signature of crc32 changed in Python 3. See the docs.
        return zlib.crc32(self.name.encode("ascii") + self.raw_data)

    def update_crc(self):
        """Update this chunk's CRC."""
        self.crc = self.compute_crc()

    def update_length(self):
        """Update this chunk's length."""
        self.length = len(self.raw_data)

    def check_data(self):
        """Check whether this chunk's CRC is consistent with its payload.

        Returns:
            bool: True if the CRC matches the payload, False otherwise.
        """
        return self.crc == self.compute_crc()

    # --- Access to the Data Member Via Property -----------------------

    @property
    def data(self):
        """The payload of this chunk.

        Only access the data through this property. This ensures that the CRC
        and length attributes stay consistent.

        """
        return self.raw_data

    @data.setter
    def data(self, new_data):
        self.raw_data = new_data
        self.update_crc()
        self.length = len(new_data)

    # --- Various Built-ins --------------------------------------------

    def __len__(self):
        """The length of the chunk payload in bytes."""
        return self.length

    def __nonzero__(self):
        """True if the chunk contains any data, False otherwise."""
        return bool(self.length)


class PNGFile(object):
    """Nice class representation of our beloved PNG files.

    Contains methods for chunk access, loading, and writing.

    Args:
        image_name (*str*, optional): Path of a PNG file to load. If None or
            not passed, an empty PNG file is created. This empty file contains
            consists of a valid header and no chunks. (not even the mandatory
            ``IEND`` chunk!)

    Raises:
        TypeError: If the file given by `image_name` does not have a PNG
            header.

    Attributes:
        header (str): The magic PNG header.
        chunks (list(Chunk)): The chunks of this PNG file.

    """

    # --- Constructor --------------------------------------------------

    def __init__(self, image_name=None):
        magic_header = b'\x89PNG\r\n\x1a\n'
        self.chunks = []
        if image_name is None:
            self.header = magic_header
            return
        with open(image_name, "rb") as png_file:
            self.header = png_file.read(8)
            if self.header != magic_header:
                raise TypeError('not a PNG file: {}'.format(image_name))
            eof = False
            while not eof:
                # TODO: Check for IEND, not just for an empty chunk.
                new_chunk = Chunk.new_from_file(png_file)
                if new_chunk:
                    self.chunks.append(new_chunk)
                else:
                    eof = True

    def copy(self):
        """Perform a deep copy of this file."""
        new_image = type(self)()
        new_image.chunks = [chunk.copy() for chunk in self.chunks]
        return new_image

    # --- Chunk Iterators ----------------------------------------------

    def idat_chunks(self):
        """Iterate over all chunks that contain pixel data.

        Yields:
            Chunk: `Chunks <Chunk>` of type ``IDAT``.

        """
        return (chunk for chunk in self.chunks if chunk.name == "IDAT")

    def various_chunks(self):
        """Iterate over all non-data chunks.

        Yields:
            Chunk: `Chunks <Chunk>` of all types except ``IDAT`` and ``IEND``.

        """
        return (chunk for chunk in self.chunks
                if chunk.name not in {"IDAT", "IEND"})

    # --- Compression & Decompression ----------------------------------

    def decompress(self):
        """Get the decompressed image data.

        This concatenates the data of all ``IDAT`` chunks and decompresses it,
        but it does not unapply the PNG adaptive filter.

        """
        buf = ''.join(chunk.data for chunk in self.idat_chunks())
        return bytearray(zlib.decompress(buf))

    @staticmethod
    def buffer_to_chunks(buf, chunk_size):
        """Compresses a buffer and packs it into equally-sized ``IDAT`` chunks.

        Args:
            buf (str): The uncompressed string of bytes to pack into chunks.
            chunk_size (int): How many bytes (after compression) to pack into a
                single chunk. The final chunk may have a different size.

        Returns:
            list(Chunk): The ``IDAT`` chunks created from the data. Because
            each of them is made out of thin air, the `pos` attribute of each
            is 0.
        """
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

        This removes all ``IDAT`` and ``IEND`` chunks, but retains the rest. It
        then turns `buf` into ``IDAT`` chunks and appends them. Finally, it
        appends a single ``IEND`` chunk to the list.

        Args:
            buf (str): The image data that replaces this file's current data.

        """
        chunk_size = len(next(self.idat_chunks()))
        new_chunks = list(self.various_chunks())
        new_chunks.extend(self.buffer_to_chunks(buf, chunk_size))
        new_chunks.append(Chunk("IEND"))
        self.chunks = new_chunks

    # --- Writing to Disk ----------------------------------------------

    def write(self, name):
        """Write this PNG file to disk.

        Args:
            name (str): The path to the file to write. If the file already
                exists, it is overwritten.
        """
        with open(name, "wb") as pngfile:
            pngfile.write(self.header)
            for chunk in self.chunks:
                pngfile.write(chunk.get_raw())


class GlitchedPNGFile(PNGFile):
    """Subclass of `PNGFile` that adds methods to add glitch effects.

    Note:
        TODO: usage example

    Args:
        image_name (str): Path to the PNG file to load. If None or not passed,
            this creates an empty PNG file. This file has a valid header, but
            no chunks. (not even the mandatory ``IEND``!)
    """

    # --- Actually Important Methods -----------------------------------

    def __init__(self, image_name=None):
        PNGFile.__init__(self, image_name)
        self._decompressed = None

    def begin_glitching(self):
        """Prepare the file for applying glitches.

        This must be called before any other glitching method.

        """
        self._decompressed = self.decompress()

    def end_glitching(self):
        """Stop applying glitches and pack the file into chunks again.

        This must be called after glitching the file. Only then the glitches
        will actually persist.

        """
        self.overload(self._decompressed)
        self._decompressed = None

    def random_glitches(self, glitch_amount, glitch_size, glitch_dev):
        """Apply a random choice of glitch effects to the image data.

        The exact details of the algorithm are intentionally left unspecified.
        The gist is: Take a random amount of bytes, apply a random effect on
        them, repeat until `glitch_amount` bytes have been processed.

        Args:
            glitch_amount (int): Number of bytes to be affected in total. This
                will always be fulfilled exactly. However, a byte may be
                glitched multiple times, so the number of glitched bytes
                generally will be lower than this.
            glitch_size (float): Average glitch size in bytes. Higher values
                concentrate the glitch effect into larger contiguous sections.
            glich_dev (float): Glitch size standard deviation in bytes. Higher
                values will make the glitch size fluctuate more wildly.

        """
        method_list = (4 * [self.fill_noise] + 3 * [self.fill_zeros] +
                       [self.move, self.switch])
        while glitch_amount > 0:
            amount = int(random.gauss(glitch_size, glitch_dev))
            amount = min(max(amount, 2), glitch_amount)
            glitch_amount -= amount
            random.choice(method_list)(amount)

    def glitch_file(self, glitch_amount, glitch_size, glitch_dev, copies=1):
        """Produce glitched PNG files from this one.

        This returns an iterator over glitched PNG files. Each file is produced
        by calling `random_glitches()` on the unmodified version of this file.

        Args:
            glitch_amount (int): Passed to `random_glitches()`.
            glitch_size (float): Passed to `random_glitches()`.
            glitch_dev (float): Passed to `random_glitches()`.
            copies (int): The number of glitched PNG files to produce.

        Yields:
            GlitchedPNGFile: A copy of this file with glitches applied. This
            file itself is left unmodified.

        """
        for _ in range(copies):
            copy = self.copy()
            copy.begin_glitching()
            copy.random_glitches(glitch_amount, glitch_size, glitch_dev)
            copy.end_glitching()
            yield copy

    # --- Internal Stuff (Better Not Call Directly) --------------------

    @staticmethod
    def random_bytes(length):
        """Produce an array of random bytes.

        Args:
            length (int): The number of bytes to produce.

        Returns:
            bytearray: Random bytes.

        """
        return bytearray(random.randint(0, 255) for i in range(length))

    def _insert(self, pos, ins):
        """Insert bytes into the image data.

        Args:
            pos (int): The position at which to insert the bytes.
            ins (str): The bytes to insert.

        Returns:
            int: The number of bytes inserted.

        """
        self._decompressed[pos:pos] = ins
        return len(ins)

    def _remove(self, pos, length):
        """Remove bytes from the image data.

        Args:
            pos (int): The position at which to remove bytes.
            length (int): The number of bytes to remove.

        Returns:
            str: The bytes that have been removed.

        """
        rem = self._decompressed[pos:pos + length]
        del self._decompressed[pos:pos + length]
        return rem

    def replace(self, pos, rep):
        """Replace image data with other data.

        Note:
            This leaves the number of bytes constant, unless ``pos+len(rep)``
            lies outside of the buffer.

        Args:
            pos (int): The position at which to start overwriting bytes.
            rep (str): The bytes to write over the image data.

        """
        length = len(self._decompressed)
        self._decompressed[pos:pos + len(rep)] = rep
        del self._decompressed[length:]

    def fill_noise(self, length, pos=None):
        """Replace image data with random bytes.

        Note:
            The same note regarding out-of-bounds writing applies as for
            `replace()`.

        Args:
            length (int): The number of bytes to overwrite.
            pos (*int*, optional): If passed, the position at which to start
                overwriting data. If not passed, a random position is chosen.
                The random position will ensure that writing stays in-bounds.

        """
        if pos is None:
            pos = random.randint(0, len(self._decompressed) - length)
        self.replace(pos, self.random_bytes(length))

    def fill_zeros(self, length, pos=None):
        """Like `fill_noise()` but overwrite bytes with zeros."""
        if pos is None:
            pos = random.randint(0, len(self._decompressed) - length)
        self.replace(pos, length * '\x00')

    def move(self, length, from_=None, to_=None):
        """Move a block of image data from one place to another.

        Args:
            length (int): The number of bytes to move.
            from_ (*int*, optional): The position at which to cut out bytes.
            to_ (*int*, optional): The position at which to reinsert the bytes.

        """
        if from_ is None:
            from_ = random.randint(0, len(self._decompressed) - length)
        if to_ is None:
            to_ = random.randint(0, len(self._decompressed) - length)
        self._insert(to_, self._remove(from_, length))

    def switch(self, len_one, pos_one=None, len_two=None, pos_two=None):
        """Switch two blocks of image data with each other.

        Args:
            len_one (int): If `len_two` is passed, the length of the first
                block of bytes. Otherwise, the total number of bytes affected.
            pos_one (*int*, optional): The position of the first block of
                bytes. If not passed, a random position is chosen.
            len_two (*int*, optional): If passed, the length of the second
                block of bytes. Otherwise, `len_one` is randomly split into two
                parts, one used for `len_one` and one for `len_two`.
            pos_two (*int*, optional): The position of the second block of
                bytes. If not passed, a random position is chosen.

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
