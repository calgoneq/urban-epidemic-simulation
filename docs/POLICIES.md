# Strategie ograniczeń (K-01)

Opis trzech strategii porównywanych w M3/M6 oraz metryk potrzebnych do ich oceny.
Strategie 1 i 2 są zaimplementowane w `src/policies.py`, strategia 3 jest na razie tylko opisana.

## Konwencje

- `contact_multiplier` to **udział normalnych kontaktów, który pozostaje**:
  1.0 = brak ograniczeń, 0.3 = redukcja o 70%, 0.0 = brak kontaktów.
- Dni liczymy od 0. Polityka jest oceniana na początku każdej doby i obowiązuje 24 godziny.
- W pliku `metrics.csv` wiersz `hour=h` opisuje zakończoną godzinę, więc zasady dnia `d`
  widać w wierszach `hour = 24d+1 ... 24d+24`.
- Mnożniki podawaj jako liczby ułamkowe (`0.0`, `0.5`, `1.0`), żeby kolumna
  `policy_contact_multiplier` miała zawsze ten sam typ.

## Przykład uruchomienia

Polityki podpina się w kodzie, przez argument `policy` modelu (wybór z CLI/JSON nie jest jeszcze dostępny):

```python
from src.config import SimulationConfig
from src.model import EpidemicModel
from src.policies import ConstantRestrictions, ScheduledRestrictions

config = SimulationConfig(population=200, days=60, seed=7)

# stała redukcja kontaktów o 50%
history = EpidemicModel(config, policy=ConstantRestrictions(0.5)).run()

# lockdown w dniach 10-19, lżejsze ograniczenia w dniach 30-39
policy = ScheduledRestrictions([(10, 20, 0.3), (30, 40, 0.5)])
history = EpidemicModel(config, policy=policy).run()

print(history[["hour", "I", "cumulative_infections"]].tail())
```

Do nowego, niezależnego przebiegu twórz nowy obiekt polityki i nowy model.
Testy: `python -m pytest -q`.

## Strategia 1: stała (`ConstantRestrictions`)

Ten sam mnożnik przez cały przebieg. Nazwa w wynikach: `constant_<mnożnik>`.
Rola: punkt odniesienia dla pozostałych strategii.

| Parametr | Znaczenie |
| --- | --- |
| `contact_multiplier` | Udział normalnych kontaktów, liczba z przedziału [0, 1] |

Niepoprawna wartość (poza [0, 1], NaN, `bool`) powoduje `ValueError` już przy tworzeniu polityki.

## Strategia 2: harmonogram (`ScheduledRestrictions`)

Lista okresów `(start_day, end_day, mnożnik)`, przedziały półotwarte `[start, end)`,
jak w `range(start, end)`: dzień końcowy **nie** należy do okresu, więc `(10, 20, ...)`
obejmuje dni 10-19, a okresy `(10, 20, ...)` i `(20, 30, ...)` mogą się stykać.
Poza okresami obowiązuje 1.0 (`no_restrictions`). Nazwa w okresie: `scheduled_<mnożnik>`.
Rola: lockdown zaplanowany z góry, niezależny od przebiegu epidemii.

| Element okresu | Znaczenie |
| --- | --- |
| `start_day` | Pierwszy dzień obowiązywania, liczba całkowita >= 0 |
| `end_day` | Pierwszy dzień bez ograniczenia, liczba całkowita > `start_day` |
| `mnożnik` | Udział normalnych kontaktów, liczba z przedziału [0, 1] |

Okresy nie mogą się nakładać, kolejność na liście nie ma znaczenia.
Błędne dane (nakładanie, `end <= start`, ujemny start, zły mnożnik) powodują `ValueError`
przy tworzeniu polityki. Pusta lista oznacza brak ograniczeń.

## Strategia 3: adaptacyjna (opis, bez implementacji)

Restrykcje włączają się, gdy epidemia rośnie, i wyłączają, gdy opada.

### Sygnał wejściowy

Polityka dostaje tylko ostatni `MetricsSnapshot`. Dostępne dziś pola:
`I`, `E`, `new_infections`, `cumulative_infections`.

- `new_infections` w snapshocie dotyczy tylko **ostatniej godziny**, więc jest zbyt szumiące.
  Dobowe nowe zakażenia liczymy jako różnicę `cumulative_infections` między kolejnymi
  wywołaniami (polityka zapamiętuje poprzednią wartość).
- Wygładzanie: średnia z ostatnich `window_days` dni, żeby jeden losowy dzień nie przełączał zasad.
- Alternatywnie udział zakaźnych `I / N` (N = S+E+I+R).

To jest **prawdziwa** liczba zakażonych, a nie wykryte przypadki. Wykrywania jeszcze nie ma
(patrz W-04), więc strategia jest przybliżeniem i tak ją nazywamy w wynikach.

### Parametry

| Parametr | Znaczenie |
| --- | --- |
| `activation_threshold` | Poziom sygnału, od którego włączamy restrykcje |
| `deactivation_threshold` | Niższy poziom, poniżej którego je wyłączamy (histereza) |
| `restriction_multiplier` | Mnożnik kontaktów w czasie restrykcji ("siła") |
| `min_duration_days` | Minimalny czas trwania restrykcji, żeby nie "migały" |
| `window_days` | Długość okna wygładzania sygnału |

Wymóg: `deactivation_threshold < activation_threshold`.

### Logika dnia (pseudokod)

```text
signal = średnia dobowych nowych zakażeń z ostatnich window_days
if restrykcje wyłączone and signal >= activation_threshold:
    włącz; zapamiętaj dzień startu
elif restrykcje włączone and signal <= deactivation_threshold
        and (day - dzień startu) >= min_duration_days:
    wyłącz
zwróć PolicyRules(restriction_multiplier) jeśli włączone, inaczej PolicyRules()
```

### Co zostaje do M3

Docelowy sygnał to obciążenie opieki zdrowotnej (zajęte łóżka / pojemność) albo liczba
wykrytych przypadków. Wymaga to rozszerzenia kontraktów (W-04): status wykrycia, potrzeby
i pojemność opieki. Do tego czasu nie zastępujemy brakujących danych zerami w wykresach.

### Optymalizacja (M6)

Mała siatka 3 × 3: `activation_threshold` × `restriction_multiplier`, pozostałe parametry stałe.
Wynik dotyczy badanych konfiguracji w naszym modelu, nie jest "najlepszą polityką" dla prawdziwego miasta.

## Metryki do porównywania strategii

Dostępne już teraz (z `metrics.csv`):

| Metryka | Jak liczona |
| --- | --- |
| Szczyt zakaźnych | `max(I)` |
| Dzień szczytu | `day` dla `max(I)` |
| Łączne zakażenia | ostatnia wartość `cumulative_infections` |
| Dni z restrykcjami | liczba dni, w których `policy_contact_multiplier < 1` |
| Przybliżony koszt społeczny | suma po dniach z `1 - policy_contact_multiplier` |

Wymagają rozszerzenia modelu (po W-04):

| Metryka | Wymaga |
| --- | --- |
| Przeciążenie opieki | pojemności i zapotrzebowania opieki |
| Utracone godziny aktywności | mierzenia zaplanowanej vs. wykonanej aktywności |
| Skuteczność wykrywania | statusu