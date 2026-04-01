@echo off
title Matching Engine - Testes
color 0B

echo Executando a suite de testes...
echo ========================================

cd Source

python -m unittest Tests/test_main.py

echo ========================================
pause