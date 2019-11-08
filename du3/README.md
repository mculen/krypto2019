# DÚ 3

## Zadanie
Pre zníženie veľkosti verejného kľúča sme v LWE probléme každý druhý riadok matice vypočítali ako c_mult*a+c_add, kde 'a' je predchádzajúci riadok matice. Tým skrátime zápis matice na polovicu. Vyriešte LWE problém pre zadaný verejný kľúč, pričom počítame v GF(257) a chybová distribúcia je uniformná na množine {-3, ..., 3}. Parametre verejného kľúča sú v súbore hw3-data.zip), pričom pre zjednodušenie sú v matici ponechané aj odvodené riadky. Zdrojový kód pre generovanie zadania je hw3-gen-sage.txt. Riešenia pošlite e-mailom s predmetom správy "Kryptológia 1 - domáca úloha 3" obsahujúcim: (1) súkromný vektor 's' v tvare '(x, y, z, ...)', (2) zdrojový kód použitý pri riešení, (3) stručný popis riešenia.

## Dáta

pk08.txt:

    {'q': 257, 'A': [...], 'b': [...], 'c_add': 139, 'c_mult': 147}

## Riešenie

`python lwe.py`:

    s:  [252, 189, 127, 1, 253, 75, 57, 69, 206, 222, 122, 103, 150, 151, 177, 117, 28, 38, 148, 95, 214, 73, 92, 31, 183, 136, 145, 49, 206, 212, 78, 170, 179, 73, 55, 138, 98, 161, 256, 174]
    e:  [1, 0, 2, 2, 0, -2, -1, 1, -3, -2, -3, -1, 0, 2, -3, -2, -1, -3, -2, 0, 2, -1, -3, 2, -3, 2, 0, -1, -3, 1, 0, 1, 1, -3, 0, -1, -2, 2, -1, 1]
