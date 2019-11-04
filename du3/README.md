# DÚ 3

## Zadanie
Pre zníženie veľkosti verejného kľúča sme v LWE probléme každý druhý riadok matice vypočítali ako c_mult*a+c_add, kde 'a' je predchádzajúci riadok matice. Tým skrátime zápis matice na polovicu. Vyriešte LWE problém pre zadaný verejný kľúč, pričom počítame v GF(257) a chybová distribúcia je uniformná na množine {-3, ..., 3}. Parametre verejného kľúča sú v súbore hw3-data.zip), pričom pre zjednodušenie sú v matici ponechané aj odvodené riadky. Zdrojový kód pre generovanie zadania je hw3-gen-sage.txt. Riešenia pošlite e-mailom s predmetom správy "Kryptológia 1 - domáca úloha 3" obsahujúcim: (1) súkromný vektor 's' v tvare '(x, y, z, ...)', (2) zdrojový kód použitý pri riešení, (3) stručný popis riešenia.

## Dáta

pk08.txt:

    {'q': 257, 'A': [...], 'b': [...], 'c_add': 139, 'c_mult': 147}
