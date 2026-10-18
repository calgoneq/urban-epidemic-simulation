**Stan projektu — fundament 0.1**

Temat zaakceptowany. Gotowe: konfiguracja JSON, Mesa SEIR, godzinowy czas, synchroniczne
ekspozycje, seed, CSV/JSON/PNG, testy oraz kontrakty dla miasta, zachowań i polityki.
Domyślne moduły są wersjami zastępczymi, nie ukończonymi częściami zespołu.

Sprawdzenie lokalne: Python 3.12; `python -m pytest -q` oraz `python main.py`.
Nie potwierdzono jeszcze uruchomienia na komputerach wszystkich członków zespołu.

Kontrolny wynik domyślnego przebiegu dla zapisanych zależności i seed=42:
S=66, E=0, I=0, R=434; 429 nowych zakażeń poza 5 początkowymi I.
To wynik testowy modelu demonstracyjnego, nie obserwacja medyczna.

Następny krok: każdy uruchamia wersję bazową i realizuje własne pierwsze zadanie
z [TASKS.md](TASKS.md). Przed adaptacyjną polityką należy uzgodnić model opieki,
wykrywania i kwarantanny. Dashboard można zacząć od aktualnych plików wynikowych.

Do organizacji repo pozostaje: dodanie członków zespołu, skonfigurowanie ochrony main
i ewentualnego automatycznego uruchamiania testów. Nie są one częścią kodu 0.1.
