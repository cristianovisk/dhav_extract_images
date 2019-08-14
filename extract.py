# In development don't use.

#!/usr/bin/env python3.7

import sys
import os
import binascii

''' // Write binary data in file with hexadecimal
with open("bytes.txt", "wb") as byte_file:
    byte_file.write(b'\xFF\xD8\xFF')
    '''
def timestamp_translate(timestamp):
    hexArg=timestamp
    hexLittleEndian=hexArg[6:8],hexArg[4:6],hexArg[2:4],hexArg[0:2]
    hexBigEndian=(''.join(hexLittleEndian))


    binario=bin(int('1'+hexBigEndian, 16))[3:]

    anobin=binario[0:6]
    ano=int(anobin, 2)
    mesbin=binario[7:10]
    mes=int(mesbin, 2)
    diabin=binario[10:15]
    dia=int(diabin, 2)
    horabin=binario[15:20]
    hora=int(horabin, 2)
    minutobin=binario[20:26]
    minuto=int(minutobin, 2)
    segundobin=binario[26:32]
    boole=segundobin is None:
        print("None")
    segundo=int(segundobin, 2)
    timedict = {
        "dia": dia,
        "mes": mes,
        "ano": ano,
        "hora": hora,
        "minuto": minuto,
        "segundo": segundo
    }
    return timedict
    #print ("d%s-m%s-a%s_h%s-m%s-s%s" %(dia,mes,ano,hora,minuto,segundo))

mDHAV = b'\x44\x48\x41\x56'
filesize = os.path.getsize(sys.argv[1])
with open(sys.argv[1], "rb") as bytes:
    #bytes.seek(13,0)
    #print(binascii.b2a_hex(bytes.read(1)))
    for byte in range(filesize):
        bytes.seek(byte, 0)
        offset = bytes.read(4)
        if mDHAV == offset:
            print("Match DHAV Frame")
            print(byte)
            #Tipo de Frame Primário ou Dependente FD/FC/F1 respectivamente
            bytes.seek(byte+4,0)
            typeframe = bytes.read(1)
            print("Tipo de Frame: %s" %typeframe)
            #Numero do Canal/Camera do Frame
            bytes.seek(byte+6,0)
            camNumber = int(binascii.b2a_hex(bytes.read(1)), 16)+1
            print("Camera: %s" %camNumber)
            #Numero Sequencial do Frame
            bytes.seek(byte+8,0)
            seqFrame = int.from_bytes(bytes.read(4), byteorder='little')
            print("Numero Frame: %i" %seqFrame)
            #Tamanho em Bytes do Frame
            bytes.seek(byte+12,0)
            sizeFrame = int.from_bytes(bytes.read(4), byteorder='little')
            print("Tamanho Frame: %i Bytes" %sizeFrame)
            #Timestamp do Frame
            bytes.seek(byte+16,0)
            timestamp = int.from_bytes(bytes.read(4), byteorder='big')

            print(timestamp_translate(str(hex(timestamp)).replace('0x', '')))
            #Footer do Arquivo
            bytes.seek(byte+sizeFrame-8,0)
            footerFrame = bytes.read(4)
            print(footerFrame)
