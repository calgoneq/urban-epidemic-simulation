# Wieloagentowy system symulacji rozprzestrzeniania się epidemii w aglomeracji miejskiej z adaptacją zachowań społecznych i optymalizacją strategii kwarantanny

Projekt zespołowy na przedmiot **Studio projektowe 1**, AGH.
Prowadzący: **prof. Andrzej Bielecki**. Temat został zaakceptowany.

Celem jest porównanie strategii kwarantanny i ograniczania kontaktów przy zmieniającym
się przestrzeganiu zasad przez mieszkańców. Docelowy model połączy epidemię SEIR,
mobilność w mieście, zachowania społeczne i obciążenie opieki zdrowotnej.

**Aktualna wersja: 0.1 — fundament silnika.** Działa godzinowa symulacja SEIR
w Mesie, konfiguracja JSON, powtarzalne losowanie, zapis CSV/JSON i wykres PNG.
Miasto, zachowania i polityka mają proste implementacje zastępcze oraz wspólne interfejsy.
Nie są jeszcze zaimplementowane hospitalizacje, kwarantanna, zmęczenie restrykcjami,
optymalizacja ani dashboard. Parametry przykładowe nie są kalibracją konkretnej choroby.

**Uruchomienie**

Python **3.11–3.13**, zalecany **3.12**, oraz Git. Polecenia wykonuj z katalogu projektu.
Wersje głównych bibliotek są zapisane w `requirements.txt`.

Windows / PowerShell — osobne środowisko bez konieczności aktywacji skryptu:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe main.py
```

Jeżeli korzystasz już z odpowiedniego środowiska, używaj jego polecenia `python`:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python main.py
```

Linux / macOS:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
.venv/bin/python main.py
```

Do samego uruchomienia wystarczy `requirements.txt`. Wersja `requirements-dev.txt`
instaluje dodatkowo narzędzie do testów. Nie ma potrzeby instalowania projektu jako paczki.

**Przykłady**

```bash
python main.py --days 30 --population 200 --seed 7
python main.py --config configs/no_transmission.json
python main.py --days 10 --no-plot
python main.py --help
```

Każdy przebieg tworzy osobny katalog `data/runs/<identyfikator>/`:

| Plik | Zawartość |
| --- | --- |
| `metrics.csv` | Godzinowa historia stanów, zakażeń i aktywnych mnożników |
| `config.json` | Parametry po zastosowaniu argumentów z terminala |
| `summary.json` | Szczyt zakaźnych, łączne zakażenia i stany końcowe |
| `metadata.json` | Seed znajduje się w konfiguracji; tutaj wersje bibliotek, kodu, nazwy modułów i czas obliczeń |
| `seir.png` | Wykres S/E/I/R; pomijany przy `--no-plot` |

Wyniki nie nadpisują wcześniejszych przebiegów i są ignorowane przez Git.
`--output` zmienia katalog nadrzędny dla nowych przebiegów.

**Zespół i moduły**

| Osoba | Odpowiedzialność | Główne pliki |
| --- | --- | --- |
| Wojciech Caldzudis | Architektura, silnik Mesa, SEIR, transmisja i integracja | `src/agent.py`, `src/model.py`, `src/config.py`, `src/contracts.py` |
| Łukasz Borysiuk | Miasto, miejsca aktywności i mobilność | `src/city.py`, przyszły `src/mobility.py` |
| Raman Chmirou | Ryzyko, zmęczenie i przestrzeganie zasad | `src/behavior.py` |
| Karol Baran | Strategie ograniczeń, kwarantanna i eksperymenty | `src/policies.py`, przyszły `src/experiments.py` |
| Misha Daniov | Dashboard, wizualizacja i prezentacja wyników | przyszłe `app.py`, `src/charts.py`; uzgodnione zmiany w `src/results.py` |

Stack: Python, Mesa, NumPy, SciPy, pandas, Matplotlib i docelowo Streamlit.

**Dokumentacja**

- [Roadmapa](docs/ROADMAP.md) — etapy i kryteria zakończenia.
- [Model](docs/MODEL.md) — jednostki, mechanika zakażeń i ograniczenia.
- [Interfejsy](docs/INTERFACES.md) — jak podłączyć własny moduł.
- [Pierwsze zadania](docs/TASKS.md) — zakres prac dla zespołu.
- [Zasady współpracy](CONTRIBUTING.md) — gałęzie, testy i pull requesty.
- [Stan projektu](docs/STATUS.md) — ukończone elementy i następny krok.

Kod znajduje się w `src/`, konfiguracje w `configs/`, a testy w `tests/`.
Automatyczne sprawdzanie zmian jest dostępne w zakładce [Actions](https://github.com/calgoneq/urban-epidemic-simulation/actions).
W pull requestach zbiorczy status `CI` obejmuje testy na Linux i Windows.
