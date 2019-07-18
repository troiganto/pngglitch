Pngglitch Command-Line Documentation
====================================

.. highlight:: bash

Synopsis
--------

**pngglitch** [*options*] *infile.png*

**pngglitch** **-o** *outfile.%d.png* [*options*] *infile.png*

**pngglitch** **-R** [*options*] *infile.png*

Description
-----------

This program allows the user to partially decompress a PNG file and
deliberately put errors into its bytestream. The decompression concerns all
levels that are verified via checksums, but none further. This gives the
errors a characteristic "glitchy" look.

After error insertion, the program recompresses the bytestream and recalculates
all checksums. This ensures that the result is still a valid PNG file.

Options
-------

-h, --help            Show a help message and exit.
--outfile outfile, -o outfile
                      Naming pattern for the output files. Defaults to
                      *<infile>.%d.png* if **--num** *N* is specified and to
                      *<infile>.corrupt.png* otherwise.
--num N, -N N         Number of output files to generate. If not specified,
                      defaults to one.
-R                    Generate a random name for the output file. Ignored
                      if --num is specified.
--amount size, -a size
                      Describes how many bytes should be affected in total.
                      Defaults to 100.
--mean size, -m size  Average glitch size in bytes. Defaults to 20.
--deviation deviation, -d deviation
                      Standard deviation of glitch size in bytes. Defaults
                      to 5.

Examples
--------

Introduce glitches into the file *input.png* and save the result as
*input.corrupted.png*::

    pngglitch input.png

Introduce glitches into the file *input.png* and save the result as *output.png*::

   pngglitch -o output.png input.png

Make 10 different attempts at glitching the file *input.png*. Save the output
as files *input.0.png* through *input.9.png*::

   pngglitch -N 10 input.png

Make 10 different attempts at glitching the file *input.png*. Save the output
as files *corrupt file 0.png* through *corrupt file 9.png*::

   pngglitch -N 10 -o "corrupt file %d.png" input.png

Chunk Ordering
--------------

PNG files are structured as "chunks", where each chunk has a type that
identifies its contents. The most important ones are:

IHDR
   The image header, contains the picture dimensions, bit depth and various
   other crucial information. Always the first chunk.
PLTE
   Contains the color palette, if any. Must come before the first IDAT chunk.
IDAT
   Contains the actual image data. The data may be split into several IDAT
   chunks. In this case, all IDAT chunks must appear consecutively, without any
   chunk in-between.
IEND
   An empty chunk that marks the end of the file. Always the last chunk.

Of these chunks, this program only modifies the IDAT chunk(s). Conceptually, it
does so by filtering them out of the chunk stream and applying its effects,
then reinserting them into the stream directly before the IEND chunk.

Because of this procedure, chunks that appear after the last IDAT chunk in the
original file will appear before the first IDAT chunk in the glitched file.
This is no problem for the standardized chunk types (most of which are required
to appear before the first IDAT chunk anyway), but may affect private chunk
types.

Known Bugs
----------

Bugs should be reported at https://github.com/troiganto/pngglitch/issues/.

In the PNG filter method 0 (the only standardized method at this date), each
non-empty scanline of the picture is prefixed with a byte that indicates which
filter type has been used in this line. Only values between 0 and 4 inclusive
are allowed.

This program is ignorant of these filter-type bytes. As such, it may randomly
replace such a byte with an invalid value, rendering the picture invalid.

See Also
--------

:manpage:`png(5)`, :manpage:`libpng(3)`, :manpage:`zlib(3)`.

Credits
-------

This tool would have not been possible without the extensive and well
comprehensible "PNG (Portable Network Graphics) Specification, Version 1.2",
available at http://www.libpng.org/pub/png/.
