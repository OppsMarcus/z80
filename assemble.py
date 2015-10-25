#!/usr/bin/python

"""
This script calls the z80 assembler z80asm (which is part of the Ubuntu
repos and translates the binary code in C code to generate an array
that can be read by Arduino or in a file that can be written to a PROM.)
"""

import sys
import getopt
from subprocess import check_output, CalledProcessError
import binascii

# use file name as imported in z80.ino
OUTPUTFILE_NAME = 'z80_code.h'
# use string as required by MiniPro programmer
ROM_MODEL = 'X28C64'
# size of the ROM (gets filled with ffh)
ROM_SIZE = 8192
# the c code that forms the array
TEMPLATE = (
    '// this file has been created by compiling\n'
    '// %s\n\n'
    '#include <Arduino.h>\n'
    '#ifndef codebase\n'
    '#define codebase\n\n'
    'codebase byte code[] {\n'
    '%s'
    '\n};\n\n'
    '#endif'
)


def get_command_line_options():
    """Reads command line options provided."""
    argv=sys.argv[1:]
    ret = {}
    try:
       opts, args = getopt.getopt(argv,"hi:",["ifile="])
    except getopt.GetoptError:
       print 'assemble.py -i <inputfile>'
       sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'assemble.py -i <inputfile>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            ret['inputfile'] = arg
    return ret


def compile(inputfile_name, binfile_name=None):
    """Compiles the code using z80asm."""
    # TODO: improve error handling?
    binfile_name = (
        binfile_name or '{}.bin'.format(inputfile_name.split('.')[0]))
    try:
        check_output(["z80asm", inputfile_name, "-o", binfile_name])
    except CalledProcessError:
        print '\nThere have been errors compiling your z80 code.\n'
    print 'Binary file:', binfile_name
    return binfile_name


def create_arduino_code(binfile_name, outfile_name=OUTPUTFILE_NAME,
                        template=TEMPLATE):
    """Creates Arduino code, C array"""
    with open(binfile_name, 'rb') as f:
        content = f.read()
    coded_code = bin_to_c_array(content)
    with open(outfile_name, 'w') as f:
        f.write(template % (binfile_name, coded_code))
    print 'Arduino C array: {}\n\nBuild successfully\n'.format(
        outfile_name)
    return outfile_name


def bin_to_c_array(bin):
    """
    Converts the binary generated by z80asm into
    a C array syntax.
    """
    hexstring = binascii.hexlify(bin)
    ret = ''
    for i in range(0, len(hexstring), 2):
        ret += '0x{},\n'.format(hexstring[i:i+2])
    return ret[0:-2]


def create_rom_file(bin_filename, rom_size=ROM_SIZE):
    """
    Creates the file that can be written to ROM.
    """
    rom_filename = bin_filename.replace('.bin', '_rom.bin')
    with open(bin_filename, 'rb') as f:
        content = binascii.hexlify(f.read())
    while len(content) < rom_size *2:
        content += 'ff';
    content = binascii.unhexlify(content)
    with open(rom_filename, 'wb') as f:
        f.write(content)


def main():
    args = get_command_line_options()
    if args:
        inputfile = args['inputfile']
        print '\nInput file: %s' % inputfile
        binfile_name = compile(inputfile)
        create_arduino_code(binfile_name)
        create_rom_file(binfile_name)
    else:
        print '\nNo input file provided.\n'

if __name__ == "__main__":
    main()
