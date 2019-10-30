# DÚ 2

## Zadanie
Demonštrujte Bleichenbacherov útok na upravený PKCS#1 v1.5, pričom tentokrát nie je úvod výplne 00 02 ale 00 07. Máte k dispozícii parametre RSA schémy (hodnoty n, e, d) a šifrový text c. Vytvorte simuláciu útoku, kde orákulum budete simulovať vďaka znalosti súkromného exponentu d. Parametre sú v súbore hw2-data.zip). Riešenia pošlite e-mailom s predmetom správy "Kryptológia 1 - domáca úloha 2" obsahujúcim: (1) otvorený text, (2) zdrojový kód simulácie, (3) súbor slistXX.txt obsahujúci postupnosť hodnôt s_i (ako čísla v desiatkovej sústave, každé s_i na samostatnom riadku), (4) stručný popis odlišností od útoku na pôvodný PKCS#1 v1.5.

## Dáta

rsa08.txt:

    n = 11162468308532210160332899883951230336154890001470416271632043577384506025541656533028400896244330204504255200862241093658306770417020963947456518834241113
    e = 65537
    d = 9838546460381991664273153011223566369190702443580528945703241912263890719126234021723126164491759556645569326358625795657638818990999368153127757020427089
    c = 7154961360195750808070188040790941039659697721396314808057272022086352501635908707071146602080497866635109201252792290644407540423808956204460056076248586

## Riešenie

`python bleichenbacher.py`:

    [...]
    message: 000775b6088a8dea8f6dc299d9f0d5c9ed477929c66361522b51dd53c3d3c5742cb4a2cb6a21daf1cc6085d800446f6d61636120756c6f68612032202f203038
    plaintext: b'Domaca uloha 2 / 08'
    oracle queries: 29575

Úlohy:

1. `Domaca uloha 2 / 08`
2. `bleichenbacher.py`
3. `slist08.txt`
4. `m` hľadáme v intervale (7B, 8B) namiesto (2B, 3B) - v zásade teda len vymeníme konštanty 2B a 3B za 7B a 8B
