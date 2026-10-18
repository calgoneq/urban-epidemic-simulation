**Zasady współpracy**

Pierwszy fundament został przygotowany bezpośrednio dla `main`. Po dołączeniu
zespołu każda kolejna zmiana, także lidera, przechodzi przez gałąź zadania i pull request.
`main` powinien zawierać wersję, którą można uruchomić zgodnie z README.

1. Pobierz aktualny `main`: `git switch main`, następnie `git pull --ff-only`.
2. Utwórz gałąź jednego zadania, np. `git switch -c feat/city-v1`.
3. Zaimplementuj mały, kompletny fragment we własnym module.
4. Uruchom `python -m pytest -q` oraz odpowiedni przykład użycia.
5. Zapisz i wypchnij swoją gałąź, otwórz PR do `main` i opisz wynik sprawdzenia.
6. Wojciech przegląda integrację. Jego zmiany przegląda jedna z pozostałych osób.
7. Po scaleniu kolejna gałąź powstaje z aktualnego `main`.

Nie utrzymujemy jednej osobistej gałęzi przez cały semestr. Nie zmieniamy cudzych
modułów ani wspólnych kontraktów bez uzgodnienia. Konflikty przed scaleniem rozwiązuje
autor zmiany z pomocą właściciela kolidującego pliku. Nie używamy wymuszonego push na main.

Właścicielem wspólnych typów, konfiguracji i pętli symulacji jest Wojciech.
Potrzebę nowego pola albo zmiany jednostki zgłoś przed rozwijaniem modułu.
Nie nadpisuj pól zarządzanych przez Mesę, np. `model.agents` i `agent.unique_id`.

Każdy PR zawiera: co działa, jak uruchomić, jak sprawdzono i co jeszcze jest ograniczeniem.
Do istotnej mechaniki dodaj test jej zachowania. Wyniki z `data/runs`, środowisko `.venv`,
hasła i tokeny nie trafiają do repo. Nie zmieniamy wersji zależności bez wspólnego sprawdzenia.

GitHub Actions uruchamia instalację, testy i przykład CLI na kilku wersjach Pythona
oraz na Linux i Windows. Przed scaleniem zbiorczy status `CI` musi być zielony.
Nie wyłączaj testu ani sprawdzenia tylko po to, żeby uzyskać zielony wynik.

Konwencje: kod i identyfikatory po angielsku, dokumentacja zespołowa po polsku,
cztery spacje, nazwy modułów `snake_case`, klasy `PascalCase`. Losowania wykorzystują
generator otrzymany od modelu; nie dodawaj globalnych wywołań `random`/`numpy.random`.
