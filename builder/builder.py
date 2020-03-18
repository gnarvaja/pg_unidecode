# -*- coding: utf-8 -*-
"""
Generates source data
"""
import imp
import os
import io
import re
import sys
from unidecode import unidecode


if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")


BUILD_DIR = 'src/data'


def c_escape(char):
    if not char:
        return ""
    char = char.replace('\\', '\\\\')
    char = ''.join([
        u'\\x%02x' % ord(c) if ord(c) < 0x20 else c
        for c in char
    ])
    char = char.replace('"', '\\"')
    char = char.replace('%', '\\%')
    char = char.replace('?', '\\?')
    return char


def create_data(data_file, pos_file):
    """
    create_data
    """
    pos = 0
    positions = []
    data = ""

    for chr_index in range(0xffffffff):
        try:
            char = chr(chr_index)
        except (ValueError, OverflowError):
            break
        decoded = unidecode(char)
        c_escaped = c_escape(decoded)
        positions.append(pos)
        data += c_escaped
        pos += len(decoded)

    # shrink all empty positions at the end
    last_non_empty_index = max((i + 1) for i, p in enumerate(positions[1:]) if positions[i] != positions[i + 1])
    positions = positions[:last_non_empty_index + 1]

    # Write files
    data_file.write(u'char chars[] = "\\\n')
    pos_file.write(u'int pos[] = {\n')

    for page in range(0xffffff):
        is_last = (page + 1) * 256 > len(positions)
        pos_line = ", ".join(map(str, positions[page * 256: (page + 1) * 256]))
        if not is_last:
            pos_line += ","

        pos_first_char = positions[page * 256]
        pos_last_char = len(data) if is_last else positions[(page + 1) * 256]
        data_line = data[pos_first_char:pos_last_char]

        pos_file.write(pos_line + "\n")
        data_file.write(data_line + "\\\n")
        if is_last:
            break

    data_file.write('";\n')
    pos_file.write('};\n')


def build():
    """
    build
    """
    if not os.path.exists(BUILD_DIR):
        os.makedirs(BUILD_DIR)

    chars_path = os.path.join(BUILD_DIR, 'chars.h')
    pos_path = os.path.join(BUILD_DIR, 'pos.h')

    with io.open(chars_path, mode='w') as data_file:
        with io.open(pos_path, mode='w') as pos_file:
            create_data(data_file, pos_file)

if __name__ == "__main__":
    build()
