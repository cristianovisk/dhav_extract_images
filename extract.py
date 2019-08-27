#!/usr/bin/env python3.7

import sys
import os
import binascii
import time
from datetime import datetime, time
import sqlite3
import hashlib

arq=sys.argv[1]
now = datetime.now()
beginning_of_day = datetime.combine(now.date(), time(0))
print("%s Inicio: " %arq)
print (now - beginning_of_day)

if os.path.isdir("%s_Extracted" %arq) == False: 
    os.system("mkdir %s_Extracted" %arq)
else:
    os.system("rm -rf %s_Extracted" %arq)
    os.system("mkdir %s_Extracted" %arq)


#Cria a estrutura do banco SQLite para relatório da analise
def createDB():
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
            filescanned TEXT NOT NULL,
            filehash TEXT NOT NULL
    );
    """)
    # desconectando...
    conn.commit()
    conn.close()

#Calcula hash SHA256 do arquivo de argumento
def sha256hash(filename):
    BUF_SIZE = 65536 #Lê o arquivo em blocos de 64 KB

    sha256 = hashlib.sha256()

    with open(filename, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            sha256.update(data)

    hashfile = sha256.hexdigest()
    return hashfile #Retorna a hash final

def deleteHash(archive, hasharq):
    conn = sqlite3.connect(archive)
    cursor = conn.cursor()
    cursor.execute("""DELETE FROM framesdhav WHERE filehash = '%s';
    """ %hasharq)
    rows = cursor.fetchall()
    # desconectando...
    conn.commit()
    conn.close()
    return rows

def checkFileAnalized(archive, hasharq):
    conn = sqlite3.connect(archive)
    cursor = conn.cursor()
    cursor.execute("""SELECT COUNT(filehash) FROM framesdhav WHERE filehash = '%s';
    """ %hasharq)
    rows = cursor.fetchall()
    # desconectando...
    conn.commit()
    conn.close()
    return rows

#Transforma Hex em Binario(string) depois processa o Timestamp
def timestamp_translate(timestamp):
    hexArg=timestamp
    hexLittleEndian=hexArg[6:8],hexArg[4:6],hexArg[2:4],hexArg[0:2]
    hexBigEndian=(''.join(hexLittleEndian))


    binario=bin(int('1'+hexBigEndian, 16))[3:]

    anobin=binario[0:6]
    if anobin.count('0') != 0:
        ano=int(anobin, 2)
    elif anobin.count('0') == 0:
        ano=int(1)

    mesbin=binario[7:10]
    if mesbin.count('0') != 0:
        mes=int(mesbin, 2)
    elif mesbin.count('0') == 0:
        mes=int(1)
    if mes > 12:
        mes = int(12)
    if mes < 1:
        mes = int(1)

    diabin=binario[10:15]
    if diabin.count('0') != 0:
        dia=int(diabin, 2)
    elif diabin.count('0') == 0:
        dia=int(1)
    if dia > 31:
        dia = int(31)
    if dia < 1:
        dia = int(1)

    horabin=binario[15:20]
    if horabin.count('0') != 0:
        hora=int(horabin, 2)
    elif horabin.count('0') == 0:
        hora=int(1)
    if hora > 23:
        hora = int(23)

    minutobin=binario[20:26]
    if minutobin.count('0') != 0:
        minuto=int(minutobin, 2)
    elif minutobin.count('0') == 0:
        minuto=int(1)
    if minuto > 59:
        minuto = int(59)

    segundobin=binario[26:32]
    if segundobin.count('0') != 0:
        segundo=int(segundobin, 2)
    elif segundobin.count('0') == 0:
        segundo=int(1)
    if segundo > 59:
        segundo = int(59)
    
    timedict = {
        "dia": dia,
        "mes": mes,
        "ano": ano,
        "hora": hora,
        "minuto": minuto,
        "segundo": segundo
    }
    return timedict

def main():
    mDHAV = b'\x44\x48\x41\x56'
    fDHAV = b'\x64\x68\x61\x76'
    filesize = os.path.getsize(arq)
    filehash = sha256hash(arq)
    option = "OPTION"
    createDB()
    ccheck = checkFileAnalized('relatorio.db', filehash)[0]

    if ccheck[0] > 0:
        print("\nArquivo %s de HASH %s ja foi analisado\nHash encontrada no relatorio.db\n" %(arq, filehash))
        print("Total de %i frames ja processados" %ccheck[0])
        option = input("Deseja deletar do relatorio.db as entradas deste arquivo? (S/N): ")
        if option == 'S' or option == 's':
            deleteHash('relatorio.db', filehash)
            print("Processando...")
            option = 'n'
            main()
        if option == 'N' or option == 'n':
            del option
            print("Terminado...")
            exit()

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
                        with open(framename, "wb") as wframe:
                            wframe.write(frameMatch)
                            cursor.execute("""
                            INSERT INTO framesdhav (seqframe, cam, typeframe, sizeframe, dateframe, filescanned, filehash)
                            VALUES (%i, %s, %i, %i, '%s', '%s', '%s')
                            """ %(seqFrame, camNumber, int(binascii.b2a_hex(typeframe), 16), sizeFrame, dt, arq, filehash))
                        del header
                        del footer
                else:
                    header=0
        conn.commit()
        conn.close()
        now = datetime.now()
        beginning_of_day = datetime.combine(now.date(), time(0))
        print("Termino: ")
        print (now - beginning_of_day)
        print("----------------------")
main()