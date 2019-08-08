#!/bin/bash

#--- Created by Cristianovisk Forensics ---
#---  https://github.com/cristianovisk  ---


fileDD=$1
dhavMagicNumber="dhav	y	20000000	\x44\x48\x41\x56	\x64\x68\x61\x76"
folder="DHAV_Extracted_$fileDD"

function main {
	if [ `whoami` != "root" ];
	then
		echo "Execute novamente como ROOT...";
		exit
	else
		printf "Configurando...";
	fi

	if [[ -f `which foremost` ]];
	then
		configForemost;
	else
		apt-get update
		apt-get install foremost -y
		main;
	fi
}

function configForemost {
	if  [[ -f  "/etc/foremost.conf" ]];
	then
		if [ $(cat /etc/foremost.conf | grep dhav | wc -l) -eq 1 ];
		then
			extractDHAV;
		else
			echo $dhavMagicNumber >> /etc/foremost.conf
			extractDHAV;
		fi;
	else
		echo "" >> /etc/foremost.conf
		main;
	fi
}

function extractDHAV {
	clear
	printf "Extraindo..."
	foremost -o $folder $fileDD
	sync
	cd $folder/dhav
	clear
	echo "Extraido `ls | wc -l` Frames em $folder - Tratando..."
	sleep 1
	echo "FILENAME;HEADER;IDSEQ;TYPEFRAME;NUMCAM;DIA;MES;ANO;HORA;MINUTO;SEGUNDO" > ../../report_images_$fileDD.csv
	for file in `ls`;
	do
		header=$(cat $file | hexdump -ve '16/1 "%02x"' | cut -c1-44)
		idSeq=$(echo ${header^^} | cut -c17-24)
		typeFrame=$(echo ${header^^} | cut -c9-10)
		numCamFrame=$(echo `echo ${header^^} | cut -c13-14 | bc`+1 | bc)
		timestamp=$(echo ${header^^} | cut -c33-40)
		filename=$(echo CAM$numCamFrame-`python -c "hexArg='$idSeq';hexLittleEndian=hexArg[6:8],hexArg[4:6],hexArg[2:4],hexArg[0:2];hexBigEndian=(''.join(hexLittleEndian));print(int(hexBigEndian, 16))"`-`python ../../timestamp.py $timestamp 1`-$typeFrame.dat)
		echo "$filename;$header;`python -c "hexArg='$idSeq';hexLittleEndian=hexArg[6:8],hexArg[4:6],hexArg[2:4],hexArg[0:2];hexBigEndian=(''.join(hexLittleEndian));print(int(hexBigEndian, 16))"`;$typeFrame;$numCamFrame;`python ../../timestamp.py $timestamp 2`" >> ../../report_images_$fileDD.csv
		echo $filename
		if [[ -d CAM$numCamFrame ]];
		then
			mv $file CAM$numCamFrame/$filename;
		else
			mkdir CAM$numCamFrame
			mv $file CAM$numCamFrame/$filename;
		fi;
	done
}


if [[ -f $fileDD ]];
then
	clear
	main;
else
	echo "Aponte um arquivo de dump como argumento... ( extract.sh filename.dd )"
	main;
fi
