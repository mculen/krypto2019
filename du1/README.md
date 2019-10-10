# DÚ 1

## Zadanie
Nájdite šifrovací kľúč v 1-kolovom AES-128, ktorý pozostáva z postupnosti operácií AddRoundKey, SubBytes, ShiftRows, MixColumns a opäť AddRoundKey. Pritom AddRoundKey pripočítava vždy 128-bitový kľúč bez nejakej modifikácie. Máte k dispozícii blok otvoreného textu pXX.bin a zodpovedajúci blok šifrového textu cXX.bin (dáta: hw1-data.zip). Zdrojový kód, ktorým boli vygenerované zadania je hw1.py. Riešenia pošlite e-mailom s predmetom správy "Kryptológia 1 - domáca úloha 1" obsahujúcim: (1) kľúč v hexadecimálnom formáte, (2) stručný popis riešenia a (3) zdrojový kód použitý pri riešení.

## Dáta

p08.bin:

    2bfe 61ac c2cd 546f f6cf b7e4 b0c1 094c

c08.bin:

    3df8 fe3d 6e3a 12ae 726f a45b b1c7 8dda

## Riešenie

kompilácia `recover`:

    g++ recover.cpp -o recover -O2 -fopenmp -march=native

`./recover hw1-data/p08.bin hw1-data/c08.bin`:

    plaintext       : 2bfe61acc2cd546ff6cfb7e4b0c1094c
    ciphertext      : 3df8fe3d6e3a12ae726fa45bb1c78dda

    recovered key   : ff76324e57a4527b32ef4958f103bb25
    ciphertext check: 3df8fe3d6e3a12ae726fa45bb1c78dda (OK)

kľúč:

    ff76 324e 57a4 527b 32ef 4958 f103 bb25
