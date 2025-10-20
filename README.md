# Taktischer Simulator für Offiziersausbildung

Ein KI-gestütztes Trainingsprogramm zur taktischen Entscheidungsfindung für Offiziersanwärter.

## 🎯 Konzept

Das Programm simuliert militärische Szenarien mit zwei lokalen KI-Instanzen:

1. **Assistenz-KI** (Mistral 7B): Berät dich und prüft deine Entscheidungen auf Realitätsnähe
2. **Simulator-KI** (Llama 3.1 8B): Wertet deine Aktionen aus und entwickelt das Szenario weiter

## ⚙️ Features

- ✅ **Lokale KI-Modelle** - Kein Internet nötig, voller Datenschutz
- ✅ **Strukturierte Eingabe** - 6 definierte Felder für taktische Planung
- ✅ **Verdeckte Aktionen** - Hidden Actions werden in Simulation verschleiert
- ✅ **Iterative Verbesserung** - Überarbeite Entscheidungen nach KI-Feedback
- ✅ **Detaillierte Logs** - Speichert alle Züge und Entscheidungen
- ✅ **Kein festes Spielende** - Realistische, fortlaufende Simulation

## 📋 Systemanforderungen

- **OS:** Windows 10/11, Linux, oder macOS
- **RAM:** 16GB minimum, **32GB empfohlen** ✅
- **GPU:** NVIDIA RTX 4060 Ti (oder vergleichbar) ✅
- **Speicher:** ~20GB für KI-Modelle
- **Python:** 3.9 oder höher

## 🚀 Schnellstart

### 1. Installation
```bash
# Ollama installieren
# Windows: https://ollama.com/download

# Modelle herunterladen
ollama pull mistral:7b
ollama pull llama3.1:8b

# Python-Dependencies
pip install -r requirements.txt
```

### 2. Starten
```bash
# Ollama-Server (falls nicht automatisch gestartet)
ollama serve

# In neuem Terminal:
python tactical_simulator.py
```

➡️ **Ausführliche Anleitung:** Siehe `INSTALLATION.md`

## 🎮 Nutzung

### Spielablauf:

1. **Szenario wird geladen** - Aus `scenario_config.yaml`
2. **Du gibst deine Entscheidung ein** - 6 strukturierte Felder
3. **Assistenz-KI prüft** - Gibt Feedback zu Realismus und Taktik
4. **Du überarbeitest** (optional) - Passe Entscheidungen an
5. **Simulator-KI wertet aus** - Entwickelt Szenario weiter
6. **Neue Lage** - Zurück zu Schritt 2

### Eingabe-Felder:

```
1. SITUATION_ASSESSMENT    - Deine Lageeinschätzung
2. INTENT                  - Deine Absicht/Ziele
3. OPEN_ACTIONS            - Sichtbare Aktionen
4. COVERT_ACTIONS          - Verdeckte Operationen
5. RESOURCE_ALLOCATION     - Ressourcen-Verteilung
6. INTELLIGENCE_REQUESTS   - Aufklärungswünsche
```

### Beispiel-Eingabe:

```
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
```

## 📊 Ausgaben

### Während des Spiels:
- **Assistenz-Feedback** - Strukturierte Bewertung deiner Entscheidungen
- **Simulations-Ergebnis** - Neue Lage nach deinen Aktionen

### Nach dem Spiel:
Zwei Textdateien werden erstellt:

1. **`spieler_log_TIMESTAMP.txt`**
   - Alle deine Eingaben
   - Feedback der Assistenz-KI
   - Deine Entscheidungsentwicklung

2. **`simulator_log_TIMESTAMP.txt`**
   - Szenario-Entwicklungen
   - Simulations-Ergebnisse
   - Fortlaufende Geschichte

## 🛠️ Szenario anpassen

Bearbeite `scenario_config.yaml`:

```yaml
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
```

**Tipp:** Behalte die Struktur bei, ändere nur die Inhalte!

## 🔧 Erweiterte Konfiguration

### Andere Modelle verwenden:

Im Code `tactical_simulator.py` ändern:

```python
# Zeile 14-15
self.assistant_model = "mistral:7b"    # Andere: "mistral:3b", "gemma:7b"
self.simulator_model = "llama3.1:8b"   # Andere: "llama3.1:13b"
```

Verfügbare Modelle: https://ollama.com/library

### KI-Parameter anpassen:

```python
# Zeile 38-41 in call_llm()
"options": {
    "temperature": 0.7,  # Höher = kreativer (0.1-1.0)
    "top_p": 0.9         # Nucleus Sampling (0.5-1.0)
}
```

## 📝 Tipps für bessere Ergebnisse

### Als Spieler:
- ✅ Sei konkret in deinen Aktionen
- ✅ Berücksichtige Logistik und Zeitfaktoren
- ✅ Denke an unerwartete Entwicklungen
- ✅ Nutze verdeckte Aktionen strategisch
- ❌ Vermeide unrealistische Super-Aktionen
- ❌ Ignoriere nicht die Einschränkungen

### Für die Simulation:
- Mehrere Durchgänge verbessern die KI-Qualität
- System-Prompts können in `tactical_simulator.py` angepasst werden
- Längere Antworten = detailliertere Simulation (aber langsamer)

## 🐛 Bekannte Limitierungen

- **KI-Qualität:** Lokale Modelle sind schwächer als GPT-4/Claude (aber datenschutzfreundlich!)
- **Antwortzeit:** 10-30 Sekunden pro KI-Antwort (abhängig von Hardware)
- **Kontext-Limit:** Nach ~10-15 Zügen kann KI frühere Aktionen vergessen
- **Keine echte Gegner-KI:** Simulator simuliert nur, spielt nicht aktiv gegen dich

## 🔮 Geplante Features (für spätere Versionen)

- [ ] Mehrere vorkonfigurierte Szenarien
- [ ] Multiplayer (2 Spieler über Netzwerk)
- [ ] Grafische Oberfläche (GUI)
- [ ] KI-Gegner (aktiv gegen dich spielend)
- [ ] Statistiken und Auswertungen
- [ ] Speichern/Laden von Spielständen
- [ ] Export als PDF statt TXT

## 📄 Lizenz & Nutzung

Für Ausbildungszwecke der Bundeswehr entwickelt.

## 🤝 Mitwirken

Verbesserungsvorschläge und Bug-Reports willkommen!

---

**Version:** 1.0 (Prototyp)  
**Letzte Änderung:** Oktober 2025