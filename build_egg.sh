#!/bin/bash
echo 'Cleaning up remaining files from previous build and tox runs'
rm -rfv dist
find . -name *pyc -delete

echo 'Building egg'
python setup.py bdist_egg

echo 'Removing build files'
rm -rfv build
rm -rfv *.egg-info/

echo 'Done. Built egg location:'
ls -1 `pwd`/dist/*egg
echo 'Install it with: easy_install <egg file>'
