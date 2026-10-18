**Kontrakty modułów — wersja 0.1**

Wspólne definicje są w `src/contracts.py`, konfiguracja w `src/config.py`.
Są to zwykłe klasy danych i protokoły Pythona; nie ma potrzeby osobnego serwera ani API HTTP.
Zmiany wspólnych pól uzgadniamy z Wojciechem. Poniżej opis aktualnego kodu.

| Moduł | Metoda | Wynik |
| --- | --- | --- |
| Polityka | `decide(metrics, day)` | `PolicyRules(name, contact_multiplier)` |
| Zachowania | `decide(agent, rules, public_risk, rng)` | `BehaviorDecision(contact_multiplier, transmission_multiplier)` |
| Miasto | `locate(agents, rules, decisions, hour, rng)` | Mapowanie `{agent_id: location_id}` dla wszystkich osób |

`AgentView` jest niemodyfikowalnym widokiem: `unique_id`, `state`, `location_id`.
Moduły nie dostają całego modelu i nie zmieniają samodzielnie stanów choroby.
`location_id` w widoku oznacza poprzednią lokalizację; `locate` wyznacza lokalizację
na bieżącą godzinę. Miasto może przechowywać własne przypisania domów i aktywności
w słownikach indeksowanych `unique_id`, bez rozszerzania agenta w pierwszym zadaniu.

`decisions` to słownik decyzji zachowania indeksowany identyfikatorem osoby.
`rng` jest generatorem `random.Random` należącym do modelu. `hour` oznacza liczbę
pełnych godzin od początku; godzina dnia to `hour % 24`. Każdy agent musi mieć dokładnie
jedno niepuste tekstowe ID miejsca. Osoby w różnych miejscach nie przekazują sobie infekcji.

Polityka jest oceniana na początku dnia 0, potem co 24 godziny. `metrics` to ostatni
snapshot, nie cały dzienny raport. Zachowania i miasto są wywoływane co godzinę.
Obiekty modułów mogą przechowywać własny stan, np. przypisania miejsc albo zmęczenie
poszczególnych agentów; do nowego niezależnego przebiegu twórz nowe obiekty modułów.

**Podłączenie własnej implementacji**

```python
from src.config import SimulationConfig
from src.model import EpidemicModel

model = EpidemicModel(
    SimulationConfig(population=100, days=10),
    city=MyCity(),
    policy=MyPolicy(),
    behavior=MyBehavior(),
)
history = model.run()
```

`MyCity`, `MyPolicy` i `MyBehavior` to przykładowe nazwy własnych klas, nie klasy istniejące
w repo. Można podać tylko jeden moduł, pozostałe mają implementacje domyślne.
Przykłady działających podmian są w `tests/test_modules.py`.

**Format wyników dla dashboardu**

`model.run()` zwraca `pandas.DataFrame` z kolumnami:

| Kolumny | Interpretacja |
| --- | --- |
| `hour`, `day` | Czas; `day = hour / 24` |
| `S`, `E`, `I`, `R` | Liczebności stanów na granicy godziny |
| `new_infections` | Nowe S → E z zakończonej godziny; 0 w wierszu początkowym |
| `cumulative_infections` | Wszystkie dotychczas zakażone osoby, w tym początkowe E/I |
| `policy_name`, `policy_contact_multiplier` | Zastosowana polityka i mnożnik kontaktów |
| `mean_behavior_contact_multiplier` | Średni mnożnik kontaktów wynikający z zachowania |

Na dziennym wykresie S/E/I/R wybieramy stan na końcu dnia. Nowe zakażenia sumujemy
po godzinach należących do dnia. Wiersz `hour=24` zawiera nowe zakażenia z ostatniej
godziny pierwszej doby; wiersz 0 nie opisuje przedziału czasu. Nie sumujemy liczebności S/E/I/R.

Dashboard odczytuje dane lub uruchamia `EpidemicModel`; nie implementuje drugiej wersji
mechaniki epidemii. Zmiana kontrolki Streamlit nie powinna przypadkowo ponownie wykonywać
symulacji. Wynik przebiegu należy przechowywać w stanie sesji.

**Planowane rozszerzenie kontraktów**

Przed M3 uzgadniamy status wykrycia, izolację i kwarantannę, pojemność i zapotrzebowanie
opieki, zamknięcia typów miejsc oraz mierzenie utraty aktywności. Te pola nie są jeszcze
obsługiwane. Nie zastępujemy ich pozornymi zerowymi wynikami w wykresach.
