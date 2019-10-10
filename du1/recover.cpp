#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#include <immintrin.h>

/*
 * Stručný popis riešenia:
 * Predstavme si, že zašifrujme plaintext kľúčom,
 * ktorý má nastavené bajty iba na diagonále:
 *     (|p00|p04|p08|p12|    |k00| 0 | 0 | 0 |)
 *     (|p01|p05|p09|p13|    | 0 |p05| 0 | 0 |)
 *  AES(|p02|p06|p10|p14|,   | 0 | 0 |p10| 0 |)
 *     (|p03|p07|p11|p15|    | 0 | 0 | 0 |p15|)
 * Po operáciách AddRoundKey, SubBytes a ShiftRows dostaneme:
 * |S(p00 ^ k00)|S(p04 ^  0 )|S(p08 ^  0 )|S(p12 ^  0 )|
 * |S(p05 ^ k05)|S(p09 ^  0 )|S(p13 ^  0 )|S(p01 ^  0 )|
 * |S(p10 ^ k10)|S(p14 ^  0 )|S(p02 ^  0 )|S(p06 ^  0 )|
 * |S(p15 ^ k15)|S(p03 ^  0 )|S(p07 ^  0 )|S(p11 ^  0 )|
 * Ako vidíme, hodnota prvého stĺpca vôbec nezávisí od nediagonálnych
 * bajtov kľúča. To sa teda zjavne nezmení ani po prebehnutí operácie
 * MixColumns, ktorá nám bajty v prvom stĺpci nahradí bajtmi M0, M1, M2, M3:
 * |M0|     |
 * |M1|     |
 * |M2| ... |
 * |M3|     |
 * Až do tejto chvíle platí, že ak sme správne uhádli diag. bajty
 * kľúča, stav prvého stĺpca bude rovnaký, ako pri šifrovaní s celým
 * kľúčom. Po posledenj operácií AddRoundKey sa to zmení:
 *           |M0 ^ k00|     |     vs.     |M0 ^ k00|     |
 *           |M1 ^  0 |     |     vs.     |M1 ^ k01|     |
 *           |M2 ^  0 | ... |     vs.     |M2 ^ k02| ... |
 *           |M3 ^  0 |     |     vs.     |M3 ^ k03|     |
 *         (naša situácia - c')     (pri šif. s cel. kľúčom - c)
 * Tu vidíme dve veci: Prvý bajt sa pre správne diag. bajty vždy zašifruje
 * rovnako - môžeme teda možné hodnoty diag. bajtov kľúča zúžiť z 2^32 na
 * 2^24. Zároveň pre každú z týchto možností vieme dopočítať aj bajty
 * k01, k02 a k03 kľúča - zjavne napr. k01 = M1 ^ (M1 ^ k01) = c'[1] ^ c[1].
 * Takto dostaneme 2^24 možných hodnôt 7 bajtov (= 56 bitov) kľúča.
 * V čase 2^32 sme teda získali 32 bitov informácie o kľúči.
 * Máme ale 4 diagonály, z ktorej z každej vieme získať 32 bitov,
 * a 32 * 4 = 128.
 * Alternatívne sa na to vieme pozerať tak, že pre každú diagonálu
 * dostaneme množniu 2^96 možností kľúča (2^24 možností pre 7 bajtov
 * krát 2^72 možností pre zvyšných 9 bajtov) - a kľúč je jednoducho prienik
 * všetkých štyroch množín.
 *
 * Toľko k myšlienke, teraz to už iba úspešne implementovať. :-)
 */

#define likely(x) __builtin_expect((x), true)
#define unlikely(x) __builtin_expect((x), false)

// jednokolová verzia AES-u
// ak nemáme AES-NI, mohli by sme nahradiť
// oveľa pomalšou sw-implementáciou
static inline __m128i aes_enc(__m128i block, __m128i key)
{
    block = _mm_xor_si128(block, key);
    return _mm_aesenc_si128(block, key);
}

// cyklický posun o n stĺpcov doprava
template<int n>
static inline __m128i shift_columns(__m128i x)
{
    return _mm_alignr_epi8(x, x, 16 - n * 4);
}

// umožňuje prehľadnejší zápis konštánt nižšie
static inline __m128i set_bytes(uint8_t b00, uint8_t b04, uint8_t b08, uint8_t b12,
                                uint8_t b01, uint8_t b05, uint8_t b09, uint8_t b13,
                                uint8_t b02, uint8_t b06, uint8_t b10, uint8_t b14,
                                uint8_t b03, uint8_t b07, uint8_t b11, uint8_t b15)
{
    return _mm_setr_epi8(b00, b01, b02, b03,
                         b04, b05, b06, b07,
                         b08, b09, b10, b11,
                         b12, b13, b14, b15);
}

// extrahuje 24 bitové číslo z 3 bytov kľúča špecifikovaných
// parametrami index_{0, 1, 2}, ktoré budeme používať
// na indexovanie do poľa
static inline uint32_t extract_index24(__m128i key,
                                       uint8_t index_0,
                                       uint8_t index_1,
                                       uint8_t index_2)
{
    uint32_t index0123 = (index_0) | (index_1 << 8) | (index_2 << 16) | 0xff000000;
    return _mm_cvtsi128_si32(_mm_shuffle_epi8(key,
                                              _mm_setr_epi32(index0123,
                                                             -1, -1, -1)));
}

// vyskúša všetkých 2^32 možných bajtov na
// n-tej diagonále kľúča ({0, 5, 10, 15}, {4, 9, 14, 3}, ...),
// vylúči kľúče, kde sa prvý bajt nezašifruje správne,
// dopočíta zvyšné 3 bajty kľúča a na zvyšných 2^24
// možnostiach siedmich bajtov kľúča zavolá funkciu f
template<int n, typename Func>
void bruteforce_diagonal(__m128i plaintext, __m128i ciphertext, Func f)
{
    uint8_t c_n = _mm_extract_epi8(ciphertext, n * 4);

    __m128i shuffle_mask = shift_columns<n>(set_bytes(
        0x00, 0xff, 0xff, 0xff,
        0xff, 0x01, 0xff, 0xff,
        0xff, 0xff, 0x02, 0xff,
        0xff, 0xff, 0xff, 0x03));

    __m128i column_mask  = shift_columns<n>(set_bytes(
        0xff, 0x00, 0x00, 0x00,
        0xff, 0x00, 0x00, 0x00,
        0xff, 0x00, 0x00, 0x00,
        0xff, 0x00, 0x00, 0x00));

    for (uint64_t i = 0; i < 1L << 32; i++) {
        __m128i key = _mm_shuffle_epi8(_mm_cvtsi32_si128(i), shuffle_mask);
        __m128i ciphertext_2 = aes_enc(plaintext, key);
        uint8_t c_n_2 = _mm_extract_epi8(ciphertext_2, n * 4);
        if (likely(c_n != c_n_2))
            continue;
        ciphertext_2 = _mm_xor_si128(ciphertext_2, ciphertext);
        ciphertext_2 = _mm_and_si128(ciphertext_2, column_mask);
        key = _mm_or_si128(key, ciphertext_2);
        f(key);
    }
}

static void print_block(__m128i block)
{
    uint8_t* b = (uint8_t*)&block;
    for (int i = 0; i < 16; i++) {
        printf("%02x", b[i]);
    }
}

int main(int argc, char* argv[])
{
    if (argc < 3) {
        printf("usage: ./recover <plaintext> <ciphertext>\n");
        return 0;
    }
    FILE* f_c = fopen(argv[2], "rb");
    FILE* f_p = fopen(argv[1], "rb");
    if (!f_p || !f_c) {
        perror("error");
        return 1;
    }
    __m128i p, c;
    fread(&p, 16, 1, f_p);
    fread(&c, 16, 1, f_c);

    printf("plaintext       : "); print_block(p); printf("\n");
    printf("ciphertext      : "); print_block(c); printf("\n");

    printf("\n");

    // množiny 2^24 možností sedmíc bajtov kľúča
    // získaných z diagonál 0, 1, 2 budeme označovať
    // A, B, C:
    // |A| | | |     | |B| | |     | | |C| |
    // |A|A| | |     | |B|B| |     | | |C|C|
    // |A| |A| |     | |B| |B|     |C| |C| |
    // |A| | |A|     |B|B| | |     | |C|C| |

    __m128i* set_a = (__m128i*)aligned_alloc(16, (1 << 24) * 16);
    __m128i* set_b = (__m128i*)aligned_alloc(16, (1 << 24) * 16);
    __m128i* set_c = (__m128i*)aligned_alloc(16, (1 << 24) * 4 * 16);
    uint8_t* set_c_sizes = new uint8_t[1 << 24];

    __m128i* keys_abc = (__m128i*)aligned_alloc(16, (1 << 25) * 16);
    uint32_t keys_abc_size = 0;

    //memset(set_a, 0xff, (1 << 24) * 16);
    //memset(set_b, 0xff, (1 << 24) * 16);

    #pragma omp parallel sections
    {
        // množiny A a B budeme ukladať do tabuľky
        // 2^16 riadkov * 2^8 stĺpcov, kde číslo riadku
        // bude určené bajtmi 3 a 5, ktoré majú A a B
        // spoločné, a číslo stĺpca je určené bajtom
        // 0, resp. 4, ktorý nadobúda všetky hodnoty
        // pre každý riadok (experimentálne zistené)

        // A
        #pragma omp section
        bruteforce_diagonal<0>(p, c, [=](__m128i key) {
            uint32_t index = extract_index24(key, 0, 3, 5);
            //if (!_mm_test_all_ones(_mm_load_si128(set_a + index))) {
            //    printf("error (A): %06x\n", index);
            //}
            _mm_store_si128(set_a + index, key);
        });

        // B
        #pragma omp section
        bruteforce_diagonal<1>(p, c, [=](__m128i key) {
            uint32_t index = extract_index24(key, 4, 3, 5);
            //if (!_mm_test_all_ones(_mm_load_si128(set_b + index))) {
            //    printf("error (B): %06x\n", index);
            //}
            _mm_store_si128(set_b + index, key);
        });

        // ideálne, množinu C by sme ukladali do tabuľky
        // indexovanej všetkými štyrmi bajtmi, ktorými
        // sa prekrýva s A alebo B - t.j. 2, 7, 9 a 10,
        // to by ale vyžadovalo priveľa pamäťe,
        // takže sa musíme uspokojiť s indexom z bajtov
        // 7, 9, 10, a neskôr prehľadať max. štyri
        // rôzne kombinácie, ktoré sa nám môžu uložiť
        // na jeden index (opäť experimentálne určené)

        // C
        #pragma omp section
        bruteforce_diagonal<2>(p, c, [=](__m128i key) {
            uint32_t index = extract_index24(key, 10, 9, 7);
            uint8_t index2 = set_c_sizes[index]++;
            //if (index2 >= 4) {
            //    printf("error(C): %06x\n", index);
            //}
            _mm_store_si128(set_c + index * 4 + index2, key);
        });
    }

    // teraz skombinujeme A, B a C a dostaneme ~2^24 možností
    // pre 15 bajtov kľúča (všetky okrem bajtu 12)
    #pragma omp parallel for
    for (int row = 0; row < 1 << 16; row++) {
        for (int i = 0; i < 256; i++) {
            __m128i key_a = set_a[row * 256 + i];
            for (int j = 0; j < 256; j++) {
                __m128i key_b = set_b[row * 256 + j];
                __m128i key_ab = _mm_or_si128(key_a, key_b);
                int index = extract_index24(key_ab, 10, 9, 7);
                uint8_t size = set_c_sizes[index];
                for (int k = 0; k < size; k++) {
                    __m128i key_c = _mm_load_si128(set_c + index * 4 + k);
                    const uint16_t compare_mask = 0b0000'0110'1000'0100;
                    if (unlikely((_mm_movemask_epi8(_mm_cmpeq_epi8(key_c, key_ab)) & compare_mask) == compare_mask)) {
                        __m128i key_abc = _mm_or_si128(key_ab, key_c);
                        uint32_t store_index;
                        #pragma omp atomic capture
                        store_index = keys_abc_size++;
                        _mm_store_si128(keys_abc + store_index, key_abc);
                    }
                }
            }
        }
    }

    // pre každú možnú 15-ticu bajtov kľúča už iba jednoducho
    // vyskúšame každú z 2^8 možných hodnôt posledného bajtu
    // a vypíšeme nájdené kľúče
    #pragma omp parallel for
    for (uint32_t i = 0; i < keys_abc_size; i++) {
        __m128i key_abc = _mm_load_si128(keys_abc + i);
        for (int j = 0; j < 256; j++) {
            __m128i key = _mm_insert_epi8(key_abc, j, 12);
            if (unlikely(_mm_movemask_epi8(_mm_cmpeq_epi8(aes_enc(p, key), c)) == 0xffff)) {
                #pragma omp critical
                {
                    printf("recovered key   : "); print_block(key); printf("\n");
                    __m128i c2 = aes_enc(p, key);
                    printf("ciphertext check: "); print_block(c2);
                    printf(" (%s)\n", (memcmp(&c, &c2, 16) == 0) ? "OK" : "FAIL");
                    printf("\n");
                }
            }
        }
    }
}
