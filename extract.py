#!/usr/bin/env python3.7

import sys
import os
import binascii
import time 

arq=sys.argv[1]
if os.path.isdir("%s_Extracted" %arq) == False: 
    os.system("mkdir %s_Extracted" %arq)
else:
    os.system("rm -rf %s_Extracted" %arq)
    os.system("mkdir %s_Extracted" %arq)

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total: 
        print()

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
    if segundobin.count('0') != 0:
        segundo=int(segundobin, 2)
    elif segundobin.count('0') == 0:
        segundo=int(0)
    #10176421
    
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
fDHAV = b'\x64\x68\x61\x76'
filesize = os.path.getsize(arq)
with open(arq, "rb") as bytes:
    #bytes.seek(13,0)
    #print(binascii.b2a_hex(bytes.read(1)))
    #printProgressBar(0, filesize, prefix = 'Progress:', suffix = 'Complete', length = 50)
    for byte in range(filesize):
        #printProgressBar(byte, filesize, prefix = 'Progress:', suffix = 'Complete', length = 50)
        bytes.seek(byte, 0)
        offset = bytes.read(4)
        if mDHAV == offset:
            header=byte
            #print("Match DHAV Frame")
            #print(byte)
            #Tipo de Frame Primário ou Dependente FD/FC/F1 respectivamente
            bytes.seek(byte+4,0)
            typeframe = bytes.read(1)
            #print("Tipo de Frame: %s" %typeframe)
            #Numero do Canal/Camera do Frame
            bytes.seek(byte+6,0)
            camNumber = int(binascii.b2a_hex(bytes.read(1)), 16)+1
            #print("Camera: %s" %camNumber)
            folderCam=os.path.isdir("%s_Extracted/CAM%s" %(arq, camNumber))
            if folderCam == False:
                os.system("mkdir %s_Extracted/CAM%s" %(arq, camNumber))
            #Numero Sequencial do Frame
            bytes.seek(byte+8,0)
            seqFrame = int.from_bytes(bytes.read(4), byteorder='little')
            #print("Numero Frame: %i" %seqFrame)
            #Tamanho em Bytes do Frame
            bytes.seek(byte+12,0)
            sizeFrame = int.from_bytes(bytes.read(4), byteorder='little')
            #print("Tamanho Frame: %i Bytes" %sizeFrame)
            #Timestamp do Frame
            bytes.seek(byte+16,0)
            timestamp = int.from_bytes(bytes.read(4), byteorder='big')

            timestamp = timestamp_translate(str(hex(timestamp)).replace('0x', ''))
            '''#Footer do Arquivo
            bytes.seek(byte+sizeFrame-8,0)
            footerFrame = bytes.read(4)
            if footerFrame != fDHAV:
                print("Footer: %s" %footerFrame)
                '''
        if fDHAV == offset:
            footer=byte
            try:
                header
            except NameError:
                header = None
            if header != None:
                if header != 0:
                    bytes.seek(header,0)
                    frameMatch=bytes.read(footer-header)
                    with open("%s_Extracted/CAM%s/%i-CAM%s-%i-%i-%i-%i-%i-%i-TF%i" %(arq, camNumber, seqFrame, camNumber, timestamp['dia'], timestamp['mes'], timestamp['ano'],timestamp['hora'],timestamp['minuto'],timestamp['segundo'],int(binascii.b2a_hex(typeframe), 16)), "wb") as wframe:
                        wframe.write(frameMatch)
                    del header
                    del footer
            else:
                header=0
