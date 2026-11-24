#!/bin/bash

set -e

python3 -m src.assembler examples/stage3.asm stage3.bin
python3 -m src.main stage3.bin memory.csv --start 0 --end 85