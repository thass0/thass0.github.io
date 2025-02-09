#!/bin/bash
set -ex
python3 generate.py
python3 -m http.server --directory build/ 8000
