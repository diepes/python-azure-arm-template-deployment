#!/bin/bash

for i in "$@"
do
case $i in
    --gen-keys=*)
    genkeys="${i#*=}"
    shift # past argument=value
    ;;
    --gen-keys-dir=*)
    genkeysdir="${i#*=}"
    shift # past argument=value
    ;;
    *)
          # unknown option
    ;;
esac
done

#Create fake files
echo "FakePUB" > $genkeysdir/$genkeys.pub 
echo "FakePVT" > $genkeysdir/$genkeys.pem
