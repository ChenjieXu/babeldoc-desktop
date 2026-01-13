#!/usr/bin/env python3
import struct
import zlib
import os

os.chdir('/Users/chenjiexu/Projects/OpenSource/babeldoc-desktop/src-tauri/icons')

def create_png(filename, size=32):
    png_sig = b'\x89PNG\r\n\x1a\n'
    # Type 6 = RGBA (8 bits per channel)
    ihdr_data = struct.pack('>IIBBBBB', size, size, 8, 6, 0, 0, 0)
    ihdr_crc = zlib.crc32(b'IHDR' + ihdr_data) & 0xffffffff
    ihdr = struct.pack('>I', 13) + b'IHDR' + ihdr_data + struct.pack('>I', ihdr_crc)
    
    image_data = b''
    for _ in range(size):
        # Filter byte (0) + RGBA bytes (white with full alpha)
        image_data += b'\x00' + (b'\xFF\xFF\xFF\xFF' * size)
    
    compressed = zlib.compress(image_data, 9)
    idat_crc = zlib.crc32(b'IDAT' + compressed) & 0xffffffff
    idat = struct.pack('>I', len(compressed)) + b'IDAT' + compressed + struct.pack('>I', idat_crc)
    
    iend_crc = 0xae426082
    iend = struct.pack('>I', 0) + b'IEND' + struct.pack('>I', iend_crc)
    
    with open(filename, 'wb') as f:
        f.write(png_sig + ihdr + idat + iend)

create_png('32x32.png', 32)
create_png('128x128.png', 128)
create_png('128x128@2x.png', 128)

# ico file
with open('icon.ico', 'wb') as f:
    f.write(b'\x00\x00\x01\x00\x01\x00\x10\x10\x00\x00\x01\x00\x18\x00\x30\x00\x00\x00\x16\x00\x00\x00\x28\x00\x00\x00\x10\x00\x00\x00\x20\x00\x00\x00\x01\x00\x18\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    f.write(b'\xFF' * 100)

# icns file  
with open('icon.icns', 'wb') as f:
    f.write(b'icns\x00\x00\x00\x20\x00\x00\x00\x10icon')
    f.write(b'\xFF' * 100)

print('Icons created successfully')
