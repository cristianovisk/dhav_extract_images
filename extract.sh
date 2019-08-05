#!/bin/bash

#--- Created by Cristianovisk Forensics ---
#---  https://github.com/cristianovisk  ---


fileDD=$1
dhavMagicNumber="dhav	y	20000000	\x44\x48\x41\x56	\x64\x68\x61\x76"
folder="DHAV_Extracted_$RANDOM"

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
	cd $folder/dhav
	clear
	echo "Extraido `ls | wc -l` Frames em $folder - Tratando..."
	sleep 1
	for file in `ls`;
	do
		header=$(cat $file | hexdump -ve '16/1 "%02x"' | cut -c1-44)
		echo $header
		typeFrame=$(echo ${header^^} | cut -c9-10)
		numCamFrame=$(echo `echo ${header^^} | cut -c13-14 | bc`+1 | bc);
		
		#$(echo 'ibase=16;obase=2;``' | bc)
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