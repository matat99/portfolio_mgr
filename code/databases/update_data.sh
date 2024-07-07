#!/usr/bin/env bash

# Absolute path to the script's directory
SCRIPT_DIR="/Users/matat99/Projects/portfolio_mgr/code/databases"

# Change to the script's directory
cd "$SCRIPT_DIR" || exit

# Remove old files
rm -f eurofxref*

# Download the new file
wget 'https://www.ecb.europa.eu/stats/eurofxref/eurofxref.zip'

# Unzip and clean up
unzip 'eurofxref.zip' && rm 'eurofxref.zip'
