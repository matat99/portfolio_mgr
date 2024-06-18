#!/usr/bin/env bash

DIRNAME=`dirname $0`
cd "$DIRNAME/databases"

rm -f eurofxref*

wget 'https://www.ecb.europa.eu/stats/eurofxref/eurofxref.zip'
unzip 'eurofxref.zip' && rm 'eurofxref.zip'
