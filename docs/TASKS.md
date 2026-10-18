**Pierwsze zadania po dołączeniu do repo**

Przed rozpoczęciem: uruchom instalację, testy i przykład z README. Utwórz gałąź z aktualnego
main. Każdy PR zawiera instrukcję uruchomienia, wynik testów i krótki opis ograniczeń.

Zadania na GitHubie: [L-01](https://github.com/calgoneq/urban-epidemic-simulation/issues/1),
[K-01](https://github.com/calgoneq/urban-epidemic-simulation/issues/2),
[R-01](https://github.com/calgoneq/urban-epidemic-simulation/issues/3),
[M-01](https://github.com/calgoneq/urban-epidemic-simulation/issues/4),
[W-04](https://github.com/calgoneq/urban-epidemic-simulation/issues/5).
Aktualizację postępu zapisujemy w odpowiadającym zadaniu.

| ID / właściciel | Zadanie | Odbiór |
| --- | --- | --- |
| L-01 / Łukasz | Generator syntetycznych gospodarstw domowych, miejsc pracy i szkół; przypisania agentów oraz prosty harmonogram dzień/noc w nowej implementacji miasta | Każdy agent ma dom i jedno miejsce w danej godzinie; rano/wieczorem lokalizacje są zgodne z planem; działają testy i model z podmienionym miastem |
| K-01 / Karol | Zaimplementuj stałe ograniczenie kontaktów i ograniczenie według harmonogramu dni; opisz trzecią strategię adaptacyjną i potrzebne metryki | Dwa warianty zwracają poprawne `PolicyRules`; testy granic dni i braku ograniczeń poza harmonogramem; próg szpitalny zostaje do M3 |
| R-01 / Raman | Zróżnicowany mnożnik kontaktów i prosty model zmęczenia w słowniku per agent; opisz wzór, jednostki i sygnał ryzyka | Wyniki mieszczą się w 0–1, generator jest wspólny, brak zmęczenia daje przypadek kontrolny; zachowania wpływają na symulację |
| M-01 / Misha | Dashboard Streamlit czytający aktualny `metrics.csv`: krzywe S/E/I/R, nowe zakażenia, metryki i eksport | Poprawna interpretacja godzin/dni i reset; UI działa na danych z głównej gałęzi; brak wykresów jeszcze nieistniejących danych |
| W-04 / Wojciech | Po uzgodnieniu potrzeb modułów rozszerz kontrakty i silnik o wykrywanie, potrzeby opieki, izolację/kwarantannę oraz mierzenie aktywności | Jawne reguły, jednostki i testy; dane wymagane przez adaptacyjną politykę i dashboard |

Kolejność: L-01, K-01, R-01 i M-01 można wykonywać niezależnie. W-04 uzgadniamy z autorami
modułów przed implementacją M3. Każdy zaczyna od małego działającego fragmentu.

Zalecane pierwsze gałęzie: `feat/city-v1`, `feat/policies-v1`, `feat/behavior-v1`,
`feat/dashboard-v1`. Nie tworzymy ich wcześniej bez rozpoczęcia konkretnego zadania.
