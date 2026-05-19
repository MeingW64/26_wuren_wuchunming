#!/bin/bash
mkdir linux_practice

cd linux_practice
mkdir docs
mkdir backup

cd docs
touch readme.txt notes.log temp.tmp
rm temp.tmp
mv notes.log daily_report.txt

echo "Project Status: Active" > daily_report.txt
date >> daily_report.txt

cd ..
cp -r docs/. backup/

chmod -444 backup/daily_report.txt
chmod -444 backup/readme.txt

echo "Archive Complete. File [daily_report.txt] is now read-only"
echo "Archive Complete. File [readme.txt] is now read-only"