**Stan projektu — fundament 0.1**

Temat zaakceptowany. Gotowe: konfiguracja JSON, Mesa SEIR, godzinowy czas, synchroniczne
ekspozycje, seed, CSV/JSON/PNG, testy oraz kontrakty dla miasta, zachowań i polityki.
Domyślne moduły są wersjami zastępczymi, nie ukończonymi częściami zespołu.

Sprawdzenie lokalne: czysta instalacja na Pythonie 3.12; 38 testów oraz `python main.py`.
Wojciech potwierdził również 38 testów i ten sam wynik domyślnego przebiegu na Windows.
Nie potwierdzono jeszcze uruchomienia na komputerach pozostałych członków zespołu.

Kontrolny wynik domyślnego przebiegu dla zapisanych zależności i seed=42:
S=66, E=0, I=0, R=434; 429 nowych zakażeń poza 5 początkowymi I.
To wynik testowy modelu demonstracyjnego, nie obserwacja medyczna.

Następny krok: każdy uruchamia wersję bazową i realizuje własne pierwsze zadanie
z [TASKS.md](TASKS.md). Przed adaptacyjną polityką należy uzgodnić model opieki,
wykrywania i kwarantanny. Dashboard można zacząć od aktualnych plików wynikowych.

Workflow `Tests` sprawdza PR-y i zmiany na main: Python 3.11/3.12/3.13 na Linux oraz
Python 3.12 na Windows. Obejmuje instalację zależności, testy i krótki przebieg z wykresem.
Zbiorczy status `CI` przechodzi tylko wtedy, gdy wszystkie środowiska zakończą się sukcesem.
Wynik każdego wykonania jest widoczny w zakładce Actions; definicja workflow nie oznacza
jeszcze, że dany przebieg został wykonany i zakończył się sukcesem.

Do organizacji repo pozostaje dodanie członków zespołu i skonfigurowanie ochrony main.
W regule ochrony jako wymagany status należy wybrać `CI` po pierwszym poprawnym przebiegu.
Liczbę wymaganych akceptacji ustawiamy na 1 po dołączeniu drugiego recenzenta.
