@echo off
cd d2_generator
python generator.py --count 50 --seed 42 --output ../output/test_50.jsonl
python validate.py ../output/test_50.jsonl --count 50
pause
