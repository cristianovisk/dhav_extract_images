#!/usr/bin/env python3.7


import sys
import os
import binascii
import time
from datetime import datetime, time
import sqlite3

now = datetime.now()
beginning_of_day = datetime.combine(now.date(), time(0))
print (now - beginning_of_day)

arq=sys.argv[1]

if os.path.isdir("%s_Extracted" %arq) == False: 
    os.system("mkdir %s_Extracted" %arq)
else:
    os.system("rm -rf %s_Extracted" %arq)
    os.system("mkdir %s_Extracted" %arq)

def createDB():
    #os.system('rm %s.db' %arq)
    conn = sqlite3.connect('relatorio.db')
    
    # definindo um cursor
    cursor = conn.cursor()

    # criando a tabela (schema)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS framesdhav (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            seqframe INTEGER NOT NULL,
            cam INTEGER NOT NULL,
            typeframe INTERGER NOT NULL,
            sizeframe INTEGER NOT NULL,
            dateframe DATE NOT NULL,
            filescanned TEXT NOT NULL
    );
    """)
    # desconectando...
    conn.commit()
    conn.close()

#Transforma Hex em Binario(string) depois processa o Timestamp
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
    if minutobin.count('0') != 0:
        minuto=int(minutobin, 2)
    elif minutobin.count('0') == 0:
        minuto=int(0)
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

mDHAV = b'\x44\x48\x41\x56'
fDHAV = b'\x64\x68\x61\x76'
filesize = os.path.getsize(arq)
createDB()
with open(arq, "rb") as bytes:
    conn = sqlite3.connect('relatorio.db')
    
    # definindo um cursor
    cursor = conn.cursor()
    for byte in range(filesize):
        bytes.seek(byte, 0)
        offset = bytes.read(4)
        if mDHAV == offset:
            header=byte
            #Tipo de Frame Primário ou Dependente FD/FC/F1 respectivamente
            bytes.seek(byte+4,0)
            typeframe = bytes.read(1)
            #Numero do Canal/Camera do Frame
            bytes.seek(byte+6,0)
            camNumber = int(binascii.b2a_hex(bytes.read(1)), 16)+1
            folderCam=os.path.isdir("%s_Extracted/CAM%s" %(arq, camNumber))
            if folderCam == False:
                os.system("mkdir %s_Extracted/CAM%s" %(arq, camNumber))
            #Numero Sequencial do Frame
            bytes.seek(byte+8,0)
            seqFrame = int.from_bytes(bytes.read(4), byteorder='little')
            #Tamanho em Bytes do Frame
            bytes.seek(byte+12,0)
            sizeFrame = int.from_bytes(bytes.read(4), byteorder='little')
            #Timestamp do Frame
            bytes.seek(byte+16,0)
            timestamp = int.from_bytes(bytes.read(4), byteorder='big')
            timestamp = timestamp_translate(str(hex(timestamp)).replace('0x', ''))

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
                    framename="%s_Extracted/CAM%s/%i-CAM%s-%i-%i-%i-%i-%i-%i-TF%i.dat" %(arq, camNumber, seqFrame, camNumber, timestamp['dia'], timestamp['mes'], timestamp['ano'],timestamp['hora'],timestamp['minuto'],timestamp['segundo'],int(binascii.b2a_hex(typeframe), 16))
                    dt = datetime(timestamp['ano']+2000, timestamp['mes'], timestamp['dia'], timestamp['hora'], timestamp['minuto'], timestamp['segundo'])
                    #print(dateforma)
                    with open(framename, "wb") as wframe:
                        wframe.write(frameMatch)
                        cursor.execute("""
                        INSERT INTO framesdhav (seqframe, cam, typeframe, sizeframe, dateframe, filescanned)
                        VALUES (%i, %s, %i, %i, '%s', '%s')
                        """ %(seqFrame, camNumber, int(binascii.b2a_hex(typeframe), 16), sizeFrame, dt, arq))
                    del header
                    del footer
            else:
                header=0
    conn.commit()
    conn.close()
    now = datetime.now()
    beginning_of_day = datetime.combine(now.date(), time(0))
    print (now - beginning_of_day)
