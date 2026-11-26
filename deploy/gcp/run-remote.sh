#!/usr/bin/env bash

sudo apt-get update -qq
sudo apt-get install -y -qq python3 unzip

mkdir -p "$HOME/ctdna-loci"
unzip -q -o "$HOME/ctdna-source.zip" -d "$HOME/ctdna-loci"
cd "$HOME/ctdna-loci"

bash scripts/run.sh
