#!/bin/bash

git status

echo -e "\n"
read -p  "---> Do you want commit your changes (y/n)? " opt

if [ "${opt,,}" == "y" ] || [ "${opt,,}" == "yes" ]; then
	read -p "Type the commit message: `echo $'\n> '`" message
	git pull origin master
	git add .
	git commit -m "$message"
	git push origin $(git branch | grep \* | cut -d ' ' -f2)
else
	echo -e "\n--> Noting was commited!!"
fi