#!/bin/sh
cd d2_generator
python3 generator.py --count 50 --seed 42 --output ../output/test_50.jsonl
python3 validate.py ../output/test_50.jsonl --count 50
