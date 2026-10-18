# Wieloagentowy system symulacji rozprzestrzeniania się epidemii w aglomeracji miejskiej z adaptacją zachowań społecznych i optymalizacją strategii kwarantanny

Projekt zaawansowanej symulacji wieloagentowej (Agent-Based Model – ABM) analizujący dynamikę rozprzestrzeniania się patogenów w środowisku zurbanizowanym z uwzględnieniem sprzężenia zwrotnego między decyzjami administracyjnymi a psychologią tłumu.

---

## Cele projektu

- Modelowanie dynamiki transmisji wirusa w oparciu o stany **SEIR** (*Susceptible*, *Exposed*, *Infected*, *Recovered*).
- Badanie wpływu ograniczeń mobilności i izolacji na wskaźnik reprodukcji wirusa (R<sub>t</sub>).
- Analiza zjawiska zmęczenia restrykcjami (*pandemic fatigue*) oraz zmiennego poziomu dyscypliny społecznej (*compliance rate*).
- Wyznaczanie optymalnego balansu między wydolnością ochrony zdrowia a minimalizacją paraliżu miejskiego.

---

## Stack technologiczny

- **Python 3.10+** – główny język programowania
- **Mesa** – framework do modelowania wieloagentowego (ABM)
- **NumPy** – obliczenia macierzowe i stochastyczne
- **Matplotlib** – generowanie wykresów i analiz statystycznych
- **Streamlit** – interaktywny interfejs telemetryczny i dashboard analityczny czasu rzeczywistego

---

## Struktura zespołu i podział odpowiedzialności

1. **Tech Lead / Core Engine Developer** – [Wojciech Caldzudis]  
   *Architektura systemu, silnik agentowy Mesa, implementacja stanów SEIR i mechaniki transmisji.*
2. **Środowisko i Mobilność (Spatial/GIS Developer)** – [Łukasz Borysiuk]  
   *Topologia miasta, punkty POI (domy, miejsca pracy, szkoły, transport), cykl dobowy agentów.*
3. **Inżynier Zachowań Społecznych (Behavioral Modeler)** – [Raman Chmirou]  
   *Model psychologiczny percepcji ryzyka, zmęczenie obostrzeniami, skłonność do łamania kwarantanny.*
4. **Inżynier Polityki Sanitarnej (Policy/Rule Engine)** – [Karol Baran]  
   *Silnik regułowy obostrzeń, scenariusze lockdownu, progowanie obciążenia szpitali.*
5. **Frontend & Data Visualization (Streamlit / Analytics)** – [Misha Daniov]  
   *Interaktywny dashboard, telemetria na żywo, wizualizacja krzywych epidemiologicznych.*

---

## Struktura katalogów

```text
├── src/          # Kod źródłowy symulacji oraz aplikacji
├── docs/         # Dokumentacja projektowa, specyfikacja i raporty
├── data/         # Zbiory danych wejściowych oraz wyniki symulacji
├── requirements.txt # Zależności środowiska Python
└── README.md     # Opis projektu
