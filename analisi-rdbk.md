# RDBK.app — Analisi di prodotto e mercato

Data: 29 settembre 2026
Autore: analisi condotta con l'utente (Maurizio Andreotti, co-maintainer)
Oggetto: `https://rdbk.app/`

---

## 0. Nota di provenienza

Questa analisi **non è due-diligence esterna**. Il repository GitHub di rdbk.app è
`alvarofranz/roadbook`, i maintainers dichiarati sono "Alvaro, Maurizio", e la issue #189
è stata aperta e chiusa da `maurizioandreotti`.

Il punto cambia la lettura: non si tratta di valutare un prodotto di terzi, ma di
valutare la posizione di mercato di un progetto di cui si è co-autore. Di conseguenza
l'obiettivo utile non è "il progetto è buono?" (lo è, tecnicamente è sopra la media del
settore) ma **"esiste un mercato abbastanza grande da giustificare questo prodotto,
e come si arriva a dimostrarlo?"**.

---

## 1. Cosa è RDBK.app

Suite gratuita e open source (MIT) per **roadbook digitali** — lo strumento di navigazione
dei rally fuoristrada (FIA rally-raid: Dakar, Baja, ecc.).

### 1.1 Il workflow

| Tool | Funzione |
|---|---|
| **Recorder** | Registra un GPX con waypoint, foto geotaggate e note vocali |
| **Editor** | Costruisce un roadbook da GPX o direttamente sulla mappa |
| **Reader** | Naviga con GPS live: odometro, CAP, mappa, barra di direzione — offline |
| **Tripmaster** | Odometro GPS puro, senza roadbook (distanza parziale e totale) |
| **Events** | Organizza eventi attorno a propri roadbook, invita team, pubblica risultati |
| **Classification** | Classifica finale per team: accuratezza, CAP, velocità, regolarità — da QR firmati |

Distribuzione: PWA installabile (Windows, macOS, iOS, Android) + app native via Capacitor.
Nessun app store obbligatorio.

### 1.2 Il formato `.rdbk` — la parte interessante

È lo sforzo più serio del progetto, e va valutato separatamente dall'app.

- **Contenitore**: ZIP con dentro `roadbook.json` (+ `media.json`, `photos/`), MIME
  `application/x-roadbook`.
- **Auto-contenuto**: le icone sono embedded come `data:` URI. Un file aperto tra dieci
  anni rende identico, senza dipendere da pacchetti di icone esterni. È la risposta
  diretta al problema degli standard basati su GPX, dove i simboli vivono fuori dal file.
- **Filosofia "derived values"**: nel file c'è **solo ciò che l'autore ha deciso**.
  Distanze, bearing, CAP, numeri di nota, lunghezza del tracciato sono *sempre ricalcolati*
  da chi legge (haversine su sfera di raggio 6.371.000 m, arrotondato a metri interi).
  Un file non può quindi contraddirsi. È una scelta architetturale forte e rara: quasi
  nessun formato open applica la single-source-of-truth in modo così restrittivo.
- **Simboli posizionati**: box di riferimento 230×162, origine al centro, +y in alto →
  rendering identico a ogni dimensione di display.
- **Tipi di strada 1–5** con tratti normalizzati secondo la FIA Road Book Lexicon
  (Cross Country 2026). Il tipo 5 "bike lane" è un'estensione proprietaria dichiarata
  onestamente nella spec ("the FIA knows no bicycles").
- **Blocco `compatibility`**: conserva ciò che OpenRally o GPX dicono e `.rdbk` non sa
  rappresentare. Il round-trip tra formati non perde dati. È la parte più matura del design.
- **Validator web** + specifica pubblica.

### 1.3 Valutazione tecnica

**Pro**
- Formato documentato, portatile, testabile, con licensing permissivo
- Scope molto focalizzato e coerente: un problema, fatto bene
- Separate concerns pulite: lo standard è documentato indipendentemente dall'app
- Uso corretto di "no official standard" come argomento, non come scorciatoia

**Contro / dubbi**
- `.rdbk` nasce da un singolo implementatore che si autoproclama standard nella stessa
  pagina della specifica. L'adozione reale **non è dimostrata**.
- Nessuno schema JSON ufficiale: la validazione dipende da un validator proprietario,
  quindi la "conformità" non è verificabile da terzi indipendenti.
- Nessun secondo implementatore noto. Finché esiste un solo writer, è un'API interna,
  non uno standard.

---

## 2. Chi è la community potenziale

Il roadbook è consumato da **tre ruoli con esigenze che non si sovrappongono**. Confonderli
è l'errore più probabile.

| Segmento | Chi | Cosa acquista davvero | Dimensione |
|---|---|---|---|
| **Organizzatori** | Club, promoter, comitati | Affidabilità, scoring, timing, zero interventi telefonici | Piccola, ma paga e detta il formato |
| **Navigatori / equipaggi** | Scendenti in rally raid, endurance, navigazione | Robustezza offline, lettura a colpo d'occhio, CAP affidabile | Il cuore |
| **Dilettanti** | Amici, club, gite, "voglio fare il rallyraid nel weekend" | Zero frizione: apro GPX, ho il roadbook | Il volume |

### 2.1 Il professionista è un mercato minuscolo e federale

- **FIA-FIM World Rally-Raid Championship 2027**: 5 round confermati — Dakar (1–15 gennaio,
  49ª edizione), Abu Dhabi Desert Challenge, South African Safari Rally (14–19 giugno),
  bp Ultimate Rally-Raid Portugal (21–26 settembre), Rallye du Maroc (24–29 ottobre).
- **FIM Hard Enduro World Championship 2026**: 9 round (Francia, Portogallo, Indonesia,
  Svezia, Italia/Abetone, Lesotho, Türkiye, Spagna).

Cinque eventi l'anno non sono un TAM. Il TAM reale è il livello amatoriale: FIM Hard
Enduro, i club nazionali, e soprattutto l'ecosistema overland.

### 2.2 Segnali quantitativi della community esistente

| Segnale | Dimensione | Pertinenza |
|---|---|---|
| Budapest-Bamako News & Community (Facebook) | 64.1K membri | Alta — è il cuore del rally raid amatoriale |
| Roadbook Adventure Challenge (Facebook, Romania) | ~2.700 like, gruppo dedicato a rally raid **in moto** | Alta — nicchia in crescita |
| Pirate4x4 (forum) | 379K membri, 19M messaggi | **Bassa** — cultura build & crawl, non navigazione |
| RallyForums.com | 15K membri | **Nulla** — è rally su asfalto, altro sport |
| Tutorial YouTube "how to read a roadbook" | Diffusi | Consumano contenuto, non strumenti |

**Il pattern è chiaro**: la community esiste ed è grande, ma è quasi tutta su Facebook,
frammentata per evento e per club, e non ha un luogo tecnico.

### 2.3 Il vuoto strutturale

**Non esiste una community tecnica di navigazione rally.** Nessun forum, nessun Discord,
nessun archivio. Non c'è un posto dove si discuta di CAP, tulip, raggio di validazione,
regole FIA 2026, tolleranze GPS.

Questo è il buco vero. Ed è anche la ragione per cui un formato open *potrebbe*
diventare standard: non c'è un altro luogo dove standardizzarsi.

---

## 3. Panorama competitivo

| Prodotto | Posizionamento | Debolezza che RDBK può colpire | Rischio per RDBK |
|---|---|---|---|
| **Rally Navigator** (rallynavigator.com) | Desktop, PDF, storico, maturo | Proprietario, PDF-first, non open, niente mobile nativo | Bassa —Dominio per ausilio, non per prodotto |
| **RoadbookRally.com** | Eventi + timing, importa OpenRally | Beta, anglocentrico, gestore eventi prima che navigatore | Media — overlap sul lato organizzativo |
| **The Roadbook Project** (UK Ltd) | Coaching, sessioni scored, leaderboard | Non è uno strumento di costruzione | Bassa — complementare |
| **RallyRoadbooks** (iOS) | Lettore economico | Rating 2.4/5, pochi download, POC fragile | Bassa |
| **OpenRally** | Lo standard *de facto* preesistente | GPX dilatato, non auto-contenuto (icone esterne) | **Alta** — è il formato di default del settore |
| **TerraPirata** | Roadbook app | Poco visibile | Bassa |
| **Road & Rally** (US) | Community di driving/cruise, 187K driver | Tutt'altro sport | Nulla |

### 3.1 Il posto libco — e quanto è stretto

RDBK ha davvero uno spazio libero: **formato auto-contenuto + costruttore + organizzatore
+ gara, in un unico prodotto open source**. Nessun competitor fa i quattro insieme.

Ma è uno spazio stretto, per due motivi:
1. Il valore per l'utente finale (leggere un roadbook offline) è già risolto da soluzioni
   gratuite e abbastanza buone. Non c'è dolore forte.
2. Il valore vero — scoring, eventi, classifiche — è il lato B2B, dove i concorrenti
   esistono già e hanno budget.

---

## 4. Il problema reale: i numeri

I segnali di trazione sono **quasi nulli**.

| Metrica | Valore | Lettura |
|---|---|---|
| GitHub stars | **0** | Nessuna scoperta organica |
| GitHub forks | **0** | Nessuna adozione da terzi |
| GitHub watchers | **0** | Nessuna osservazione |
| Commit | 769 | Sviluppo intenso |
| PR chiuse | 116 | Processo disciplinato |
| Issue aperte | 11 | Manutenzione attiva |
| Canali social citati sul sito | 0 | Nessuna distribuzione |
| Forum / Discord | 0 | Nessuna community |

**Dato non verificato**: la pagina "Public roadbooks" carica dinamicamente e non sono
riuscito a contare quanti roadbook pubblici esistano. Se quel numero è basso, la community
non esiste ancora e va misurata per prima.

### 4.1 La traduzione

Il progetto è tecnicamente superiore alla media del settore, in un mercato dove non
esiste un product-market fit dimostrato.

**Il rischio non è il competitor. È che non esista un mercato abbastanza grande da
giustificare la standardizzazione.** E un formato open che nessuno adotta è un file di
nicchia, non uno standard.

---

## 5. Le tre mosse

### 5.1 Prima i numeri
Contare: roadbook pubblici, utenti registrati, download nativi, roadbook per utente.
Se sono <100 utenti, il problema non è la community, è l'evangelizzazione.
Nessuna decisione di mercato senza questo dato. **È il blocco su tutto il resto.**

### 5.2 Ancorarsi a un organizzatore, non a un rider
Un singolo club che adotta `.rdbk` per i propri eventi vale più di mille roadbook
condivisi: crea utenti, crea contenuto, crea pressione a farlo standard.

Il README dice giustamente *"with no official standard in the field"*. La strada per
diventarlo è **dimostrare adozione**, non dichiararla. Un organizzatore con 200
partecipanti e ranking pubblico è una prova; la pagina della spec non lo è.

### 5.3 Chiudere l'argomento "standard" per ora
Finché non c'è un secondo implementatore, `.rdbk` è un'API interna.

Il vantaggio competitivo vero è il **lato organizzativo** (scoring, QR firmati, gestione
eventi): è lì che il progetto fa qualcosa che nessun altro fa bene, ed è lì che esiste
potenziale reale di monetizzazione. Il formato è il *consulente*; il prodotto a pagamento
è l'evento.

---

## 6. Domande aperte

- Quanti roadbook pubblici e quanti utenti registrati? (dato mancante, bloccante)
- Esiste un secondo implementatore `.rdbk` in sviluppo? Se no, il piano standard è da
  abbandonare o da rivedere?
- Quanto costa mantenere tre piattaforme (web, iOS, Android) + standard + validator?
  È sostenibile con zero entrate?
- Esiste una fonte di entrata prevista? Il MIT + gratuità è una scelta di posizionamento
  o un vincolo?
- Le issue #147 (offline-first) e #496 (ui-contracts) suggeriscono un progetto con
  standard di qualità alti. Quanto di quello standard di qualità è reinvestito in community?

---

## 7. Appendice — fonti consultate

- `rdbk.app` — home, `/standard/`, `/wiki/what-is-a-roadbook/`, `/roadbooks/`
- `rdbk.app/assets/js/config.js` — configurazione client (verificata accessibile)
- GitHub `alvarofranz/roadbook` — README, issue #189, pull request list
- FIM — comunicati World Rally-Raid 2027, Hard Enduro 2026
- FIA / Performance Racing Industry — calendario W2RC 2027
- Rally Navigator, RoadbookRally.com, The Roadbook Project, Road & Rally, TerraPirata
- Gruppi Facebook: Budapest-Bamoko, Roadbook Adventure Challenge
- Forum: Pirate4x4, RallyForums
- Google Play / App Store — Rally Roadbook Reader, RallyRoadbooks
