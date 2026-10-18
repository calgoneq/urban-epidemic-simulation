**Roadmapa — Urban Epidemic Simulation**

Kolejność poniżej oznacza zależności i odbiór rezultatów;
terminy kalendarzowe ustalamy wspólnie.

Pytanie projektowe: jak zmęczenie restrykcjami wpływa na skuteczność stałych
i adaptacyjnych strategii ograniczania kontaktów oraz kwarantanny?

| Etap | Rezultat i kryterium ukończenia | Odpowiedzialność | Stan |
| --- | --- | --- | --- |
| M0 | Zakres, konfiguracja i pierwsze kontrakty; każdy moduł ma wejście i wyjście | Wojciech | Gotowe dla fundamentu |
| M1 | Godzinowy SEIR, seed, CLI, CSV/JSON/PNG i testy mechaniki | Wojciech | Gotowe w 0.1 |
| M2 | Domy, praca, szkoła i miejsca spotkań; przypisania i ruch zgodny z harmonogramem | Łukasz | Do wykonania |
| M3 | Potrzeby opieki, wykrywanie przypadków, izolacja/kwarantanna oraz 3 strategie restrykcji | Karol; mechanika zdrowia i integracja: Wojciech | Do wykonania |
| M4 | Zróżnicowane przestrzeganie zasad, ryzyko, zmęczenie i maseczki wpływają na model | Raman | Do wykonania |
| M5 | Dashboard parametrów, uruchamianie/reset, wykresy i eksport | Misha | Do wykonania |
| M6 | Powtarzalne eksperymenty, przegląd parametrów strategii i analiza wrażliwości | Cały zespół; eksperymenty: Karol | Do wykonania |
| M7 | Sprawozdanie do 5 stron i działająca demonstracja projektu | Każdy opisuje swoją część; skład: Wojciech | Do wykonania |

M2–M5 mogą powstawać niezależnie na wspólnych kontraktach i przykładowych danych.
Rekomendowana kolejność integracji mechaniki: miasto → polityka/opieka → zachowania.
Dashboard można podłączyć do aktualnego CSV już po M1.

Docelowy podstawowy zakres: syntetyczne miasto, rytm dnia, SEIR, opieka o ograniczonej
pojemności, izolacja wykrytych przypadków i kwarantanna domowników, zmęczenie restrykcjami,
porównanie strategii oraz Streamlit. Import OpenStreetMap i dokładniejsza demografia
są rozszerzeniami po ukończeniu całości.

Eksperyment startowy: 3 strategie × 2 warianty zachowań × 10 seedów. Liczbę powtórzeń
zwiększamy, jeśli rozrzut wyników nie pozwala na stabilne wnioski. Rejestrujemy konfiguracje,
wersje kodu i bibliotek. Strategii nie oceniamy wyłącznie na jednym przebiegu.

Optymalizacja: mała siatka progu aktywacji i siły restrykcji, np. 3 × 3. Porównujemy
przeciążenie opieki i utracone godziny zaplanowanej aktywności. Wybór dotyczy badanych
konfiguracji w naszym modelu, nie globalnie najlepszej polityki dla prawdziwego miasta.
Finalistów sprawdzamy na dodatkowych seedach.

Sprawozdanie: maksymalnie 5 stron, porównanie planu z wykonaniem,
napotkane problemy i rozwiązania oraz rysunki i wykresy.
Szczegółowa dokumentacja i dane pozostają w repozytorium.
