#! /bin/sh

NAME=IncrementalSearch
VERSION=0.1.0

mkdir build
mkdir build/files
FILES=build/files

cp -f -r descriptions ${FILES}/descriptions
cp -f -r META-INF ${FILES}/META-INF
cp -f -r pythonpath ${FILES}/pythonpath
cp -f *.xcu ${FILES}
cp -f *.xcs ${FILES}
cp -f descriptions.xml ${FILES}
cp -f LICENSE ${FILES}
cp -f README ${FILES}
cp -f registration.py ${FILES}
cp -f -r pymigemo ${FILES}/pythonpath

cd ${FILES}
zip -9 -r -n pyc -o ../${NAME}-${VERSION}.oxt \
 META-INF/* *.xcu *.xcs *.py description.xml \
 descriptions/* dialogs/* \
 pythonpath/incsearch/*.py \
 pythonpath/pymigemo/*.py \
 pythonpath/pymigemo/**/*.* \
 LICENSE README  

cd ../..
