#!/usr/bin/env python
#01000101101000010101110110110100
#010001011010001101110010000101001
import sys

#hex = [sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]]
#reverseHex = hex[::-1]
#bin(int("%s" %reverseHex[0]), 16)[2::]
#binario = bin(int("%s%s%s%s" %(reverseHex[0],reverseHex[1],reverseHex[2],reverseHex[3]), 16))[2:]
hexArg=sys.argv[1]
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
segundo=int(segundobin, 2)
#print ("-----\nBINARIO: %s\n" %binario)
#print ("ANO: %i - BIN ANO: %s \nMES: %i - BIN MES: %s\nDIA: %i - BIN DIA: %s\nHORA: %i - BIN HORA: %s\nMINUTO: %i - BIN MINUTO: %s\nSEGUNDO: %i - BIN SEGUNDO: %s" %(ano,anobin,mes,mesbin,dia,diabin,hora,horabin,minuto,minutobin,segundo,segundobin))
#print ("TIME FINAL: %s/%s/%s as %s:%s:%s" %(dia,mes,ano,hora,minuto,segundo))
print ("d%s-m%s-a%s_h%s-m%s-s%s" %(dia,mes,ano,hora,minuto,segundo))


#bin(int("45a15d84", 16))[2:]
