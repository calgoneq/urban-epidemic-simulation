**Stan projektu — fundament 0.1**

Gotowe: konfiguracja JSON, Mesa SEIR, godzinowy czas, synchroniczne
ekspozycje, seed, CSV/JSON/PNG, testy oraz kontrakty dla miasta, zachowań i polityki.
Domyślne moduły są wersjami zastępczymi, nie ukończonymi częściami zespołu.

Weryfikacja na Linux i Windows: 38 testów oraz zgodne wyniki domyślnego przebiegu
uruchamianego przez `python main.py`.

Kontrolny wynik domyślnego przebiegu dla zapisanych zależności i seed=42:
S=66, E=0, I=0, R=434; 429 nowych zakażeń poza 5 początkowymi I.
To wynik testowy modelu demonstracyjnego, nie obserwacja medyczna.

Następny krok: każdy uruchamia wersję bazową i realizuje własne pierwsze zadanie
z [TASKS.md](TASKS.md). Przed adaptacyjną polityką należy uzgodnić model opieki,
wykrywania i kwarantanny. Dashboard można zacząć od aktualnych plików wynikowych.

Workflow `Tests` sprawdza PR-y i zmiany na main: Python 3.11/3.12/3.13 na Linux oraz
Python 3.12 na Windows. Obejmuje instalację zależności, testy i krótki przebieg z wykresem.
Zbiorczy status `CI` przechodzi tylko wtedy, gdy wszystkie środowiska zakończą się sukcesem.
Wyniki sprawdzeń są dostępne w zakładce
[Actions](https://github.com/calgoneq/urban-epidemic-simulation/actions).
