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
		sudo su
	else
		#spinner&
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
		echo $dhavMagicNumber >> /etc/foremost.conf
		extractDHAV;
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
	for file in `ls`;
	do
		header=$(cat $file | hexdump -ve '16/1 "%02x"' | cut -c1-44)
		typeFrame=$(echo $header | cut -c9-10)
		numCamFrame=$(echo $header | cut -c13-14 | bc);
		$(echo 'ibase=16;obase=2;``' | bc)

	done
}


if [[ -f $fileDD ]];
then
	clear
	main;
else
	echo "Aponte um arquivo de dump como argumento... ( extract.sh filename.dd )";
fi
