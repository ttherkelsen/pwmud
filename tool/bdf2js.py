#!../python/bin/python3
#
# bdf2js.py -- convert BDF files into font definitions in JavaScript
#     to be used in the PWMud frontend.
#

import argparse, re, os.path

def run():
    cmdline = argparse.ArgumentParser(description="Convert BDF files into PWMud javascript font definitions.")
    cmdline.add_argument('-d', '--destdir', help='Which directory to write the files to, defaults to current dir.', default=".")
    cmdline.add_argument('bdffile', help='BDF file to convert')
    args = cmdline.parse_args()

    convert(args.bdffile, args.destdir)

def convert(bdf, destdir):
    RE = r'STARTCHAR (\S+).+?ENCODING (\S+).+?BBX (\d+) (\d+).+?BITMAP\s+(.*?)\s+ENDCHAR'
    TEMPLATE = 'Lowtek.data.font["%s"].glyph[%s] = %r;'
    fontname = os.path.basename(bdf).split(".")[0]
    glyphs = {}

    with open(bdf, 'r') as fd:
        for match in re.finditer(RE, fd.read(), re.DOTALL):
            name, encoding, width, height, bitmap = match.groups()
            encoding = int(encoding)
            width = int(width)
            height = int(height)
            shift = 8 - (width % 8)
            bitmap = [ int(t, 16) >> shift for t in bitmap.split("\n") ]

            if len(bitmap) != height:
                raise ValueError("%s bitmap has wrong size" % name)
          
            page = encoding >> 8
            if page not in glyphs:
                glyphs[page] = [ None ]*256
            
            glyphs[page][encoding % 256] = bitmap

    for page in sorted(glyphs.keys()):
        with open(os.path.join(destdir, '%s.js' % page), 'w') as fd:
            idx = -1
            for bitmap in glyphs[page]:
                idx += 1
                if bitmap is None:
                    continue
                print(TEMPLATE % (fontname, (page << 8) + idx, bitmap), file=fd)

if __name__ == '__main__':
    run()
