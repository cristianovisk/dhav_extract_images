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
	mkdir -m 777 $folder
	foremost -o $folder $fileDD
	sync
	chmod -R 777 $folder/dhav
	cd $folder/dhav
	total=$(ls | wc -l)
	clear
	echo "Extraido $total Frames em $folder - Tratando..."
	sleep 2
	clear
	echo "FILENAME;HEADER;IDSEQ;TYPEFRAME;NUMCAM;DIA;MES;ANO;HORA;MINUTO;SEGUNDO" > ../../report_images_$fileDD.csv
	num=0
	for file in `ls`;
	do
		header=$(cat $file | hexdump -ve '16/1 "%02x"' | cut -c1-44)
		idSeq=$(echo ${header^^} | cut -c17-24)
		typeFrame=$(echo ${header^^} | cut -c9-10)
		numCamFrame=$(echo `echo ${header^^} | cut -c13-14 | bc`+1 | bc)
		timestamp=$(echo ${header^^} | cut -c33-40)
		filename=$(echo `python -c "hexArg='$idSeq';hexLittleEndian=hexArg[6:8],hexArg[4:6],hexArg[2:4],hexArg[0:2];hexBigEndian=(''.join(hexLittleEndian));print(int(hexBigEndian, 16))"`-CAM$numCamFrame-`python ../../timestamp.py $timestamp 1`-$typeFrame.dat)
		echo "$folder/dhav/CAM$numCamFrame/$filename;$header;`python -c "hexArg='$idSeq';hexLittleEndian=hexArg[6:8],hexArg[4:6],hexArg[2:4],hexArg[0:2];hexBigEndian=(''.join(hexLittleEndian));print(int(hexBigEndian, 16))"`;$typeFrame;$numCamFrame;`python ../../timestamp.py $timestamp 2`" >> ../../report_images_$fileDD.csv
		num=$(echo $num+1 | bc)
		echo -ne "Categorizando imagens de $fileDD: $((${num}*100/${total})) %  -- $num - $total   \r"
		if [[ -d CAM$numCamFrame ]];
		then
			mv $file CAM$numCamFrame/$filename;
		else
			mkdir -m 777 CAM$numCamFrame
			mv $file CAM$numCamFrame/$filename;
		fi;
	done

	for cam in `ls`;
	do
		totalframe=$(ls $cam | wc -l)
		for frame in `ls $cam | sort -n`;
		do
			#echo $(pwd)
			#numn=$(echo $numn+1 | bc)
			echo -ne "Gerando video .h264 - Imbutindo frames $frame \r"
			cat $cam/$frame >> $cam.h264;
			#echo -ne "Gerando video .h264 - $((${numn}*100/${totalframe})) % \r";
		done;
	done
#	chmod -R 777 $folder
}

if [[ -f $fileDD ]];
then
	clear
	main;
else
	echo "Aponte um arquivo de dump como argumento... ( extract.sh filename.dd )"
	main;
fi
