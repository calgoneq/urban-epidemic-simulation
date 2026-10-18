**Model bazowy 0.1**

Jeden krok oznacza godzinę, dzień ma 24 kroki. Populacja jest zamknięta: brak narodzin,
zgonów i importu infekcji. Każda osoba ma jeden rozłączny stan S/E/I/R.

| Stan | Znaczenie | Przejście |
| --- | --- | --- |
| S | Podatny na zakażenie | Do E po ekspozycji zakończonej zakażeniem |
| E | Zakażony, jeszcze niezakaźny | Do I po `latent_hours` |
| I | Zakaźny | Do R po `infectious_hours` |
| R | Ozdrowiały, odporny w badanym okresie | Brak dalszego przejścia |

W E modelujemy latencję do zakaźności, niekoniecznie czas do objawów. W początkowej
populacji E i I mają zerowy czas w stanie. Czasy są na razie stałe dla wszystkich.
Początkowe stany są przypisywane losowo; identyfikator osoby nie determinuje zakażenia.

**Kolejność godziny**

1. Na początku dnia aktualizuj reguły polityki na podstawie ostatniego snapshotu.
2. Wylicz decyzje zachowania i lokalizacje na przedział `[t, t+1)`.
3. Oblicz wszystkie ekspozycje z tych samych stanów zdrowia z czasu `t`.
4. Na granicy `t+1` wykonaj należne E → I i I → R dla dotychczasowych chorych.
5. Zastosuj razem nowe S → E z początkiem stanu w `t+1`.
6. Zapisz stan na granicy `t+1` i liczbę nowych zakażeń z zakończonej godziny.

Przykład: osoba zakażona na koniec godziny 1 przy latencji 48 godzin staje się I
na granicy godziny 49 i może zakażać w przedziale `[49,50)`. Nowe E nie zakażają
w godzinie, w której nastąpiła ekspozycja. Początkowe I z czasem zakaźności 120 godzin
zakaża w `[0,120)` i jest R w wierszu `hour=120`.

**Transmisja we wspólnym miejscu**

Kontakty są modelowane jako proces Poissona, bez zapisywania indywidualnych par kontaktów.
Miejsca są rozłączne w danej godzinie. Dla podatnej osoby `i` w grupie `n > 1`:

```text
lambda_i = (contacts_per_day / 24) * policy_contact_multiplier
           * transmission_probability * a_i * m_i
           * sum(a_j * m_j for infectious j in the same place) / (n - 1)
P(S -> E during this hour) = 1 - exp(-lambda_i)
```

`a` to mnożnik kontaktów danej osoby, `m` to mnożnik transmisji. Każdy należy do [0,1].
Ochrona i ograniczenie kontaktów mogą działać po obu stronach: podatnego i źródła.
Wspólny mnożnik polityki stosujemy jeden raz. Samotny agent nie może zakazić się sam.
W pełnej populacji podstawowej `a=m=policy_contact_multiplier=1`.

`transmission_probability` jest prawdopodobieństwem na kontakt, a `contacts_per_day`
średnią liczbą potencjalnych kontaktów na osobę na dobę. Godzinowe prawdopodobieństwo
jest wyprowadzone z intensywności, nie otrzymywane przez powtarzanie dziennej szansy 24 razy.
Agregowanie źródeł w miejscu pozwala uniknąć porównywania każdej pary agentów w całym mieście.

**Parametry demonstracyjne**

| Parametr | Domyślnie | Jednostka / status |
| --- | --- | --- |
| population | 500 | osoby |
| initial_infected | 5 | początkowe osoby I |
| initial_exposed | 0 | początkowe osoby E |
| days | 120 | doby |
| latent_hours | 48 | godziny; założenie demonstracyjne |
| infectious_hours | 120 | godziny; założenie demonstracyjne |
| contacts_per_day | 12 | kontakty/osobę/dobę; założenie demonstracyjne |
| transmission_probability | 0.04 | prawdopodobieństwo na kontakt; założenie demonstracyjne |
| seed | 42 | nieujemne całkowite ziarno generatora |

Te wartości służą sprawdzaniu działania silnika. Nie są dopasowane do wybranego wirusa
ani prawdziwego miasta. Przed eksperymentem interpretowanym epidemiologicznie należy
wybrać patogen i udokumentować źródła lub kalibrację parametrów.

**Metryki i odtwarzalność**

CSV zawiera wiersz początkowy `hour=0`, następnie jeden wiersz na godzinę.
S/E/I/R to stan na końcu przedziału, `new_infections` to liczba nowych S → E
w zakończonej godzinie, a `cumulative_infections` uwzględnia także początkowe E i I.
Mnożniki i nazwa polityki opisują zasady zastosowane w zakończonej godzinie.
W wierszu początkowym dotyczą ustawień początkowych.

Zawsze S + E + I + R = N. Bez początkowych E/I nie ma epidemii. Przy zerowej transmisji
lub kontaktach nie ma nowych zakażeń; obecni chorzy nadal przechodzą do R.
Powtarzalność dotyczy tego samego kodu, konfiguracji, implementacji modułów i środowiska.
Każdy moduł losuje wyłącznie przez przekazany generator.

**Ograniczenia i dalsze decyzje**

- `BaselineCity` umieszcza wszystkich w jednym miejscu; nie ma jeszcze planu dnia ani demografii.
- `NeutralBehavior` nie modeluje ryzyka ani zmęczenia. Argument `public_risk` jest obecnie
  jawnym przybliżeniem z rzeczywistego I/N, ignorowanym przez tę implementację.
  Przed badaniem reakcji na publiczne dane ustalimy mechanizm wykrywania i sygnał obserwowany.
- `NoRestrictions` nie podejmuje interwencji. Podstawowe kontrakty nie zawierają jeszcze
  hospitalizacji, wykrywania, zamknięć ani kwarantanny. Dodajemy je wspólnie w M3.
- Nie szacujemy R_t. Iloraz liczby chorych z kolejnych dni nie zastępuje takiej estymacji.
- Testy weryfikują zgodność kodu z przyjętymi regułami. Walidacja wobec danych rzeczywistych
  i analiza wrażliwości należą do kolejnych etapów.
