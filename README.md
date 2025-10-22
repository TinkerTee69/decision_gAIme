Notfall-Response Simulator für Quick Response Teams
Ein KI-gestütztes Trainingsprogramm für Notfallsanitäter, Feuerwehr, THW, Polizei und andere Einsatzkräfte.

🎯 Konzept
Das Programm simuliert realistische Notfall-Szenarien mit zwei lokalen KI-Instanzen:

Assistenz-KI (Mistral 7B): Prüft deine Entscheidungen auf Durchführbarkeit, Sicherheit und Ressourcen
Simulator-KI (Llama 3.1 8B): Entwickelt das Szenario objektiv weiter (ohne Bewertung!)
Ablauf:

Szenario wird präsentiert
Du triffst Entscheidungen
Assistenz prüft - Ist es durchführbar? Sicher? Ressourcen vorhanden?
Du kannst überarbeiten
Simulator entwickelt weiter - Was passiert? (objektiv, keine Bewertung!)
Am Ende: Detaillierte Leistungsanalyse
⚙️ Features
✅ Zwei-KI-System - Assistenz prüft, Simulator entwickelt
✅ Lokale KIs - Kein Internet nötig, voller Datenschutz
✅ Realistische Szenarien - MANV, Brände, Razzien, THW-Einsätze
✅ Keine Zwischen-Bewertung - Simulator bleibt objektiv
✅ Finale Bewertung - Detaillierte Analyse nach Einsatzende
✅ Zeitbegrenzung - 2 Monate Testversion
✅ Detaillierte Logs - Komplette Einsatzdokumentation
📋 Systemanforderungen
OS: Windows 10/11, Linux, oder macOS
RAM: 16GB minimum, 32GB empfohlen ✅
GPU: NVIDIA RTX 4060 Ti (oder vergleichbar) - optional, läuft auch auf CPU
Speicher: ~10GB für beide KI-Modelle
Python: 3.9 oder höher
🚀 Schnellstart
1. Installation
bash
# Ollama installieren
# Windows: https://ollama.com/download

# Beide Modelle herunterladen
ollama pull mistral:7b       # Assistenz-KI (~4GB)
ollama pull llama3.1:8b      # Simulator-KI (~5GB)

# Python-Dependencies
pip install -r requirements.txt
2. Starten
bash
# Ollama-Server (falls nicht automatisch gestartet)
ollama serve

# In neuem Terminal:
python emergency_simulator.py
3. Szenario wählen
bash
# Standard (Notfallsanitäter)
python emergency_simulator.py

# Polizei-Razzia
python emergency_simulator.py --config scenario_police_raid.yaml

# Feuerwehr
python emergency_simulator.py --config scenario_fire.yaml
➡️ Ausführliche Anleitung: Siehe INSTALLATION.md

🎮 Nutzung
Spielablauf:
Szenario wird geladen - Ausgangslage wird präsentiert
Du triffst Entscheidungen - 6 strukturierte Felder pro Zug
Assistenz-KI prüft - Durchführbar? Sicher? Ressourcen OK?
Du kannst überarbeiten (optional)
Simulator entwickelt Lage - Objektive Beschreibung der Folgen (KEINE Bewertung!)
Nächster Zug - Neue Herausforderungen entstehen
Einsatz endet - Nach X Zügen oder auf deine Entscheidung
Finale Bewertung - Detaillierte Analyse aller Züge
Eingabe-Felder:
1. LAGEEINSCHÄTZUNG      - Wie bewertest du die Situation?
2. PRIORITÄTEN           - Was ist am wichtigsten?
3. SOFORTMASSNAHMEN      - Welche Maßnahmen JETZT?
4. RESSOURCENEINSATZ     - Wie verteilst du Personal/Material?
5. KOMMUNIKATION         - Mit wem kommunizierst du?
6. NÄCHSTE_SCHRITTE      - Was planst du für die nächsten Minuten?
Beispiel-Eingabe (Notfallsanitäter):
LAGEEINSCHÄTZUNG:
MANV mit mind. 8 Verletzten, 1 Person regungslos auf Fahrbahn, 
Benzingeruch. Polizei fehlt, Absicherung unzureichend.

PRIORITÄTEN:
1. Eigenschutz - Absicherung anfordern
2. Regungslose Person (potentiell rot)
3. Schnelle Sichtung aller Verletzten

SOFORTMASSNAHMEN:
- Kollege sichert mit Warndreieck ab
- Ich gehe zur regungslosen Person (ABCDE-Check)
- Per Funk: MANV mit >8 Verletzten, 3 weitere RTW, 1 NEF, LNA nachfordern

RESSOURCENEINSATZ:
- Notfallsanitäter: Sichtung + schwerste Fälle
- Rettungssanitäter: Dokumentation + gelbe Patienten
- Material: Sichtungskarten bereithalten

KOMMUNIKATION:
An Leitstelle: "MANV A7 km 245, >8 Verletzte, benötige 3 RTW, NEF, 
LNA, Polizei zur Absicherung dringend!"

NÄCHSTE_SCHRITTE:
Nach Erstversorgung regungsloser Patient: Systematische Sichtung 
aller Patienten, Sichtungskategorien vergeben, schwere Fälle priorisieren
Assistenz-KI prüft:

================================================================================
   🔍 ASSISTENZ-FEEDBACK
================================================================================

✅ DURCHFÜHRBARKEIT
Die Einsatzentscheidung ist grundsätzlich durchführbar und folgt 
gängigen Protokollen.

❌ KRITISCHE PROBLEME
Keine kritischen Probleme identifiziert.

⚠️ HINWEISE
- Absicherung mit Warndreieck ist nur Provisorium bei RTW-Ankunft. 
  Polizei wurde korrekt nachgefordert, aber bis dahin bleibt 
  Restrisiko für Einsatzkräfte.
  
- Benzingeruch wurde erkannt, aber keine explizite Maßnahme genannt 
  (z.B. Feuerwehr informieren, Zündquellen vermeiden).
  
- Dokumentation wurde dem Rettungssanitäter zugeteilt - sicherstellen 
  dass dieser während Sichtung Zeit dafür hat.

💡 ANMERKUNGEN
- Strukturiertes Vorgehen nach MANV-Protokoll erkennbar
- Kommunikation mit Leitstelle konkret und informativ
- Priorisierung (Eigenschutz → Schwerste → Systematik) ist sinnvoll

Optionen:
  [1] Entscheidung überarbeiten
  [2] Entscheidung ist final - weiter zur Simulation
Du wählst [2] - Simulator entwickelt:

================================================================================
   🎮 LAGE-ENTWICKLUNG
================================================================================

📊 ENTWICKLUNGEN
Während dein Kollege das Warndreieck aufstellt, näherst du dich der 
regungslosen Person. Es ist ein Mann, etwa 50 Jahre alt, bewusstlos. 
ABCDE-Check: Atemwege frei, flache Atmung, Puls schwach aber tastbar. 
Schwere Kopfverletzung sichtbar.

Die Leitstelle bestätigt: 3 RTW auf Anfahrt (ETA 8 Minuten), NEF 
(ETA 6 Minuten), LNA wird alarmiert, Polizei ETA 4 Minuten.

🆕 NEUE LAGE
Zeit: +2 Minuten seit Eintreffen

Aus dem gekippten Kleinbus ruft jemand um Hilfe. Eine Frau schreit, 
ihre Tochter sei eingeklemmt. Der Benzingeruch wird stärker - eine 
Pfütze bildet sich unter einem der PKW.

Zwei leichter verletzte Personen kommen auf dich zu und fragen was 
sie tun sollen. Eine ältere Frau sitzt am Straßenrand und weint.

Status regungsloser Patient: Stabil kritisch, müsste eigentlich 
kontinuierlich überwacht werden.

ℹ️ ZUSÄTZLICHE INFORMATIONEN
Verkehr staut sich, einige Gaffer steigen aus ihren Fahrzeugen. 
Dein Kollege kehrt vom Warndreieck zurück.

Was ist deine nächste Entscheidung?
WICHTIG: Die Simulation bewertet NICHT ob deine Entscheidung "gut" war - sie zeigt nur objektiv die Folgen!

📊 Bewertungssystem
Am Ende des Einsatzes erhältst du eine detaillierte Bewertung:

Bewertungskriterien:
✅ Prioritätensetzung - Wichtiges zuerst?
✅ Ressourcennutzung - Effektiv eingesetzt?
✅ Kommunikation - Strukturiert koordiniert?
✅ Zeitmanagement - Schnell genug?
✅ Problemlösung - Kreative Lösungen?
✅ Sicherheit - Eigenschutz beachtet?
Ausgabe-Format:
📊 GESAMTBEWERTUNG
[Zusammenfassende Einschätzung]

✅ STÄRKEN
- [Was lief gut]

⚠️ VERBESSERUNGSPOTENZIAL
- [Was hätte besser sein können]

💡 VERBESSERUNGSVORSCHLÄGE
- [Konkrete Tipps]

⭐ BEWERTUNG: 7/10 Punkte
🔒 Lizenz-System
Testversion: 2 Monate ab Installation

Automatische Lizenz-Erstellung beim ersten Start
Warnung 7 Tage vor Ablauf
Nach Ablauf: Programm nicht mehr nutzbar
Die Lizenz ist versteckt in: %APPDATA%\Local\.qrt_sys_cfg

Für Vollversion: Kontakt aufnehmen

📝 Verfügbare Szenarien
1. Notfallsanitäter (scenario_paramedic.yaml)
MANV - Verkehrsunfall Autobahn
8-10 Verletzte, Sichtung, Triage
Ressourcenmangel, Zeitdruck
2. Polizei Razzia (scenario_police_raid.yaml)
Durchsuchung Drogenlabor
SEK-Einsatz, Festnahmen
Unbeteiligte schützen, Beweissicherung
3. Feuerwehr (scenario_fire.yaml)
Wohnungsbrand mit Menschenrettung
Vermisste Personen, Einsturzgefahr
Atemschutz, Brandbekämpfung
🛠️ Eigene Szenarien erstellen
Kopiere eine bestehende .yaml Datei und passe an:

yaml
scenario_name: "Dein Szenario"
scenario_type: "typ"
max_turns: 10  # Anzahl Züge

team:
  role: "Deine Rolle"
  objective: "Dein Ziel"
  resources:
    personal: "Verfügbares Personal"
    # ... weitere Ressourcen

situation_details:
  - "Detail 1"
  - "Detail 2"

initial_situation:
  - "Ausgangslage Punkt 1"
  - "Ausgangslage Punkt 2"
🔧 Erweiterte Konfiguration
CPU vs. GPU Modus:
CPU-Modus (langsamer, funktioniert immer):

bash
set OLLAMA_NO_GPU=1
python emergency_simulator.py
GPU-Modus (schneller, braucht NVIDIA-Treiber):

bash
# Automatisch wenn CUDA installiert
python emergency_simulator.py
Andere Modelle verwenden:
python
# In emergency_simulator.py, Zeile 115
self.simulator_model = "llama3.1:8b"  # Andere: "mistral:7b", "llama3.1:13b"
📄 Ausgaben
Nach jedem Einsatz wird eine Datei erstellt:

einsatz_log_TIMESTAMP.txt

Alle deine Entscheidungen
Alle Lage-Entwicklungen
Finale Bewertung mit Punktzahl
Stärken und Verbesserungspotenzial
🐛 Bekannte Limitierungen
KI-Qualität: Lokale Modelle schwächer als GPT-4 (aber datenschutzfreundlich!)
Antwortzeit: 10-30 Sekunden pro Zug
Testversion: 2 Monate, danach Vollversion nötig
Realismus: Simulation kann nicht alle Realitäts-Aspekte abbilden
💡 Tipps für bessere Ergebnisse
Als Einsatzkraft:
✅ Strukturiert denken (ABC, ABCDE, 4A-1C-4E)
✅ Eigenschutz nicht vergessen
✅ Kommunikation explizit benennen
✅ Ressourcen realistisch einschätzen
✅ Prioritäten klar setzen
❌ Nicht "übermenschlich" agieren
❌ Dokumentation nicht vergessen
🔮 Geplante Features
 Multiplayer (Team-Einsätze)
 Sprachsteuerung (Funksprüche)
 VR-Integration
 Mehr Szenarien (SEG, Terrorlage, etc.)
 Statistiken über mehrere Einsätze
 Trainer-Modus (Ausbilder kann bewerten)
📄 Lizenz & Nutzung
Für Ausbildungszwecke von Behörden und Organisationen mit Sicherheitsaufgaben (BOS).

Testversion: 2 Monate kostenlos
Vollversion: Auf Anfrage

Version: 2.0 (QRT Edition)
Letzte Änderung: Oktober 2025

⚙️ Features
✅ Lokale KI-Modelle - Kein Internet nötig, voller Datenschutz
✅ Strukturierte Eingabe - 6 definierte Felder für taktische Planung
✅ Verdeckte Aktionen - Hidden Actions werden in Simulation verschleiert
✅ Iterative Verbesserung - Überarbeite Entscheidungen nach KI-Feedback
✅ Detaillierte Logs - Speichert alle Züge und Entscheidungen
✅ Kein festes Spielende - Realistische, fortlaufende Simulation
📋 Systemanforderungen
OS: Windows 10/11, Linux, oder macOS
RAM: 16GB minimum, 32GB empfohlen ✅
GPU: NVIDIA RTX 4060 Ti (oder vergleichbar) ✅
Speicher: ~20GB für KI-Modelle
Python: 3.9 oder höher
🚀 Schnellstart
1. Installation
bash
# Ollama installieren
# Windows: https://ollama.com/download

# Modelle herunterladen
ollama pull mistral:7b
ollama pull llama3.1:8b

# Python-Dependencies
pip install -r requirements.txt
2. Starten
bash
# Ollama-Server (falls nicht automatisch gestartet)
ollama serve

# In neuem Terminal:
python tactical_simulator.py
➡️ Ausführliche Anleitung: Siehe INSTALLATION.md

🎮 Nutzung
Spielablauf:
Szenario wird geladen - Aus scenario_config.yaml
Du gibst deine Entscheidung ein - 6 strukturierte Felder
Assistenz-KI prüft - Gibt Feedback zu Realismus und Taktik
Du überarbeitest (optional) - Passe Entscheidungen an
Simulator-KI wertet aus - Entwickelt Szenario weiter
Neue Lage - Zurück zu Schritt 2
Eingabe-Felder:
1. SITUATION_ASSESSMENT    - Deine Lageeinschätzung
2. INTENT                  - Deine Absicht/Ziele
3. OPEN_ACTIONS            - Sichtbare Aktionen
4. COVERT_ACTIONS          - Verdeckte Operationen
5. RESOURCE_ALLOCATION     - Ressourcen-Verteilung
6. INTELLIGENCE_REQUESTS   - Aufklärungswünsche
Beispiel-Eingabe:
SITUATION_ASSESSMENT:
Gegner nähert sich mit überlegenen Kräften. Meine Verteidigungsposition 
am Nordpass gibt mir Geländevorteil. Höhe 517 ist noch unbesetzt.

INTENT:
Verzögere den Gegner, gewinne Zeit für Verstärkungen. Halte Nordpass 
mindestens 48h.

OPEN_ACTIONS:
- 1 Zug Infanterie besetzt Höhe 517
- Panzer in Verteidigungsstellungen am Nordpass
- Mörserzug in Feuerstellung hinter Bergheim

COVERT_ACTIONS:
- Aufklärungstrupp infiltriert südlich, sammelt Aufklärung über 
  Gegner-Hauptstoßrichtung
- Vorbereitung von Sprengladungen an Südbrücke (nicht gezündet)

RESOURCE_ALLOCATION:
- 40% der Kräfte auf Höhe 517
- 40% am Nordpass
- 20% Reserve in Bergheim

INTELLIGENCE_REQUESTS:
- Wo ist der Angriffsschwerpunkt des Gegners?
- Welche Route nehmen ihre Panzer?
📊 Ausgaben
Während des Spiels:
Assistenz-Feedback - Strukturierte Bewertung deiner Entscheidungen
Simulations-Ergebnis - Neue Lage nach deinen Aktionen
Nach dem Spiel:
Zwei Textdateien werden erstellt:

spieler_log_TIMESTAMP.txt
Alle deine Eingaben
Feedback der Assistenz-KI
Deine Entscheidungsentwicklung
simulator_log_TIMESTAMP.txt
Szenario-Entwicklungen
Simulations-Ergebnisse
Fortlaufende Geschichte
🛠️ Szenario anpassen
Bearbeite scenario_config.yaml:

yaml
scenario_name: "Dein Szenario-Name"
description: "Beschreibung"

player_blue:
  role: "Deine Rolle"
  objective: "Dein Auftrag"
  forces:
    infantry: "Verfügbare Truppen"
    # ...weitere Kräfte
  constraints:
    - "Einschränkung 1"
    - "Einschränkung 2"
Tipp: Behalte die Struktur bei, ändere nur die Inhalte!

🔧 Erweiterte Konfiguration
Andere Modelle verwenden:
Im Code tactical_simulator.py ändern:

python
# Zeile 14-15
self.assistant_model = "mistral:7b"    # Andere: "mistral:3b", "gemma:7b"
self.simulator_model = "llama3.1:8b"   # Andere: "llama3.1:13b"
Verfügbare Modelle: https://ollama.com/library

KI-Parameter anpassen:
python
# Zeile 38-41 in call_llm()
"options": {
    "temperature": 0.7,  # Höher = kreativer (0.1-1.0)
    "top_p": 0.9         # Nucleus Sampling (0.5-1.0)
}
📝 Tipps für bessere Ergebnisse
Als Spieler:
✅ Sei konkret in deinen Aktionen
✅ Berücksichtige Logistik und Zeitfaktoren
✅ Denke an unerwartete Entwicklungen
✅ Nutze verdeckte Aktionen strategisch
❌ Vermeide unrealistische Super-Aktionen
❌ Ignoriere nicht die Einschränkungen
Für die Simulation:
Mehrere Durchgänge verbessern die KI-Qualität
System-Prompts können in tactical_simulator.py angepasst werden
Längere Antworten = detailliertere Simulation (aber langsamer)
🐛 Bekannte Limitierungen
KI-Qualität: Lokale Modelle sind schwächer als GPT-4/Claude (aber datenschutzfreundlich!)
Antwortzeit: 10-30 Sekunden pro KI-Antwort (abhängig von Hardware)
Kontext-Limit: Nach ~10-15 Zügen kann KI frühere Aktionen vergessen
Keine echte Gegner-KI: Simulator simuliert nur, spielt nicht aktiv gegen dich
🔮 Geplante Features (für spätere Versionen)
 Mehrere vorkonfigurierte Szenarien
 Multiplayer (2 Spieler über Netzwerk)
 Grafische Oberfläche (GUI)
 KI-Gegner (aktiv gegen dich spielend)
 Statistiken und Auswertungen
 Speichern/Laden von Spielständen
 Export als PDF statt TXT
📄 Lizenz & Nutzung
Für Ausbildungszwecke der Bundeswehr entwickelt.

🤝 Mitwirken
Verbesserungsvorschläge und Bug-Reports willkommen!

Version: 1.0 (Prototyp)
Letzte Änderung: Oktober 2025

