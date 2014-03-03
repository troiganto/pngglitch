pngglitch
=========

Python script that puts glitch effects into PNG files

Usage on the command-line:
--------------------------

* **pngglitch input.png** <br />
Introduces glitches into the file input.png and saves the result
as input.corrupted.png.

* **pngglitch -o output.png input.png** <br />
Introduces glitches into the file input.png and saves the result
as output.png.

* **pngglitch -N 10 input.png** <br />
Makes 10 different attempts at glitching the file input.png.
The resulting files are saves as input.0.png through input.9.png

* **pngglitch -N 10 -o "corrupt file %d.png" input.png** <br />
Makes 10 different attempts at glitching the file input.png.
The resulting files are saves as "corrupt file 0.png" through
"corrupt file 9.png".

The parameters **-a**, **-m**, and **-d** change the amount, size and
size variation of glitches. Just play around with them and see what has
the best results.

Usage in Python:
----------------

This script offers a class *GlitchedPNGFile* that enables the user
to partially decompress a PNG file and deliberately put errors into
it's bytestream.

The constructor of *GlitchedPNGFile* takes a PNG file name and reads
in the chunks of the given file.
After that, you can call the *glitch_file* method to insert random
errors into the file. The *glitch_file* method iterates over the
resulting image files.
You can write these to disk via their write method.

You can also call the glitch effect methods (*random_glitches*,
*fill_noise*, *fill_zeros*, *move*, and *switch*) directly, but you have
to wrap these calls between calls to *start_glitching* and
*end_glitching*.
The former decompresses the file, the latter compresses it again and
portions the data into equally-sized chunks again.

Methods preceded with an underscors can change the amount of pixels
in the image and, thus, render it completely unreadable. I advise
against using these.
