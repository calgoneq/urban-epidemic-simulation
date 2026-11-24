# Strategie ograniczeń (K-01)

Opis trzech strategii porównywanych w M3/M6 oraz metryk potrzebnych do ich oceny.
Strategie 1 i 2 są zaimplementowane w `src/policies.py`, strategia 3 jest na razie tylko opisana.

## Konwencje

- `contact_multiplier` to **udział normalnych kontaktów, który pozostaje**:
  1.0 = brak ograniczeń, 0.3 = redukcja o 70%, 0.0 = brak kontaktów.
- Dni liczymy od 0. Polityka jest oceniana na początku każdej doby i obowiązuje 24 godziny.
- W pliku `metrics.csv` wiersz `hour=h` opisuje zakończoną godzinę, więc zasady dnia `d`
  widać w wierszach `hour = 24d+1 ... 24d+24`.

## Strategia 1: stała (`ConstantRestrictions`)

Ten sam mnożnik przez cały przebieg. Nazwa w wynikach: `constant_<mnożnik>`.
Rola: punkt odniesienia dla pozostałych strategii.

## Strategia 2: harmonogram (`ScheduledRestrictions`)

Lista okresów `(start_day, end_day, mnożnik)`, przedziały półotwarte `[start, end)`.
Okresy nie mogą się nakładać. Poza okresami obowiązuje 1.0 (`no_restrictions`).
Rola: lockdown z góry zaplanowany, niezależny od przebiegu epidemii.

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
| Skuteczność wykrywania | statusu wykrycia |

"Koszt społeczny" z tabeli pierwszej to tylko przybliżenie z mnożnika polityki. Nie uwzględnia
zachowań ani zmęczenia (R-01) i nie jest utraconą aktywnością.

## Ograniczenia

- Polityki nie są jeszcze wybierane z CLI ani z JSON, podpina się je w kodzie
  (`EpidemicModel(config, policy=...)`).
- Obecne miasto to jedno miejsce dla wszystkich, więc strategie różnią się tylko profilem czasowym.
- Wyniki pojedynczego przebiegu są losowe. Porównania wymagają wielu seedów (M6).
- Parametry demonstracyjne nie są kalibracją żadnej choroby.