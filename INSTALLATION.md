# Notfall-Response Simulator - Installationsanleitung

## Voraussetzungen

- **Windows 10/11** (oder Linux/Mac)
- **Python 3.9+** installiert
- **32GB RAM** (vorhanden ✅)
- **NVIDIA RTX 4060 Ti** (vorhanden ✅) - optional, läuft auch auf CPU
- **~10GB freier Festplattenspeicher** für beide KI-Modelle

---

## Schritt 1: Ollama installieren

Ollama ist die einfachste Methode, lokale LLMs zu betreiben.

### Windows:
1. Download von: https://ollama.com/download
2. Installer ausführen (`OllamaSetup.exe`)
3. Installation abschließen

### Überprüfung:
```bash
ollama --version
```

---

## Schritt 2: Beide KI-Modelle herunterladen

Öffne ein Terminal (CMD oder PowerShell) und führe aus:

```bash
# Assistenz-KI (Mistral 7B) - ~4GB Download
ollama pull mistral:7b

# Simulator-KI (Llama 3.1 8B) - ~5GB Download
ollama pull llama3.1:8b
```

**⏱️ Dauer:** Je nach Internet ~20-40 Minuten für beide

### Modelle testen:
```bash
ollama run mistral:7b "Test Assistenz-KI"
ollama run llama3.1:8b "Test Simulator-KI"
```

---

## Schritt 3: Ollama-Server starten

Ollama muss als Service laufen:

```bash
ollama serve
```

**Wichtig:** Dieses Terminal-Fenster muss während der Nutzung offen bleiben!

**Alternative:** Ollama startet oft automatisch als Hintergrund-Service nach Installation.

---

## Schritt 4: Python-Umgebung einrichten

### Python-Dependencies installieren:

```bash
# In deinem Projekt-Ordner
pip install -r requirements.txt
```

**Oder manuell:**
```bash
pip install requests PyYAML
```

---

## Schritt 5: Projektstruktur erstellen

Erstelle einen Ordner mit folgender Struktur:

```
emergency_simulator/
├── emergency_simulator.py      # Hauptprogramm
├── scenario_paramedic.yaml     # Notfallsanitäter-Szenario
├── scenario_police_raid.yaml   # Polizei-Szenario
├── scenario_fire.yaml          # Feuerwehr-Szenario
├── requirements.txt            # Python-Dependencies
└── INSTALLATION.md             # Diese Anleitung
```

Kopiere alle bereitgestellten Dateien in diesen Ordner.

---

## Schritt 6: Programm starten

### Im Terminal:
```bash
cd emergency_simulator
python emergency_simulator.py
```

### Wenn alles klappt, siehst du:
```
⚙️  Prüfe Ollama-Verbindung...
  → Teste Assistenz-KI (Mistral 7B)...
  → Teste Simulator-KI (Llama 3.1 8B)...
✅ Beide KI-Modelle bereit!

⚠️  Testversion läuft noch XX Tage!

================================================================================
   MANV - Verkehrsunfall auf der Autobahn
================================================================================
...
```

---

## Troubleshooting

### Problem: "Ollama läuft nicht!"

**Lösung:**
```bash
# Starte Ollama manuell
ollama serve
```

**Oder:** Überprüfe, ob Ollama läuft:
```bash
# Windows Task-Manager: Suche nach "ollama"
# Oder im Terminal:
curl http://localhost:11434
```

---

### Problem: "Model not found"

**Lösung:** Beide Modelle nochmal herunterladen:
```bash
ollama pull mistral:7b
ollama pull llama3.1:8b

# Liste aller installierten Modelle:
ollama list
```

**Sollte zeigen:**
```
NAME           ID              SIZE      MODIFIED
mistral:7b     xxx...          4.4 GB    X minutes ago
llama3.1:8b    yyy...          4.9 GB    X minutes ago
```

---

### Problem: LLM-Antworten sehr langsam

**Ursache:** Modell läuft auf CPU statt GPU.

**Lösung für NVIDIA GPU:**
1. Installiere CUDA Toolkit: https://developer.nvidia.com/cuda-downloads
2. Ollama erkennt GPU automatisch nach Neustart

**Überprüfung:**
```bash
nvidia-smi  # Sollte GPU-Auslastung zeigen während LLM läuft
```

---

### Problem: "Out of Memory"

**Lösung:** Verwende kleinere Modelle:
```bash
# Statt mistral:7b
ollama pull mistral:3b

# Statt llama3.1:8b (sollte aber passen mit 32GB RAM)
```

---

## Performance-Tipps

### GPU-Nutzung optimieren:
Mit deiner RTX 4060 Ti (16GB VRAM) können BEIDE Modelle gut laufen:
- Mistral 7B: ~4-5 GB VRAM
- Llama 3.1 8B: ~5-6 GB VRAM
- **Gesamt: ~10GB VRAM** - passt auf deine GPU!

### Erwartete Antwortzeiten:

**GPU-Modus (mit NVIDIA-Treibern):**
- **Assistenz-KI (Mistral 7B):** ~5-10 Sekunden
- **Simulator-KI (Llama 3.1 8B):** ~10-15 Sekunden

**CPU-Modus (Fallback):**
- **Assistenz-KI:** ~20-40 Sekunden
- **Simulator-KI:** ~30-60 Sekunden

Wenn deutlich langsamer → GPU-Support prüfen!

---

## Später: EXE-Datei erstellen

Wenn alles funktioniert und du eine `.exe` erstellen willst:

### Mit PyInstaller:
```bash
pip install pyinstaller

pyinstaller --onefile --name TacticalSimulator tactical_simulator.py
```

**Achtung:** Die `.exe` braucht trotzdem Ollama + Modelle auf dem Zielrechner!

---

## Nächste Schritte

1. ✅ Ollama installieren
2. ✅ Modelle downloaden
3. ✅ Ollama starten (`ollama serve`)
4. ✅ Python-Programm starten
5. 🎮 Spielen!

**Bei Problemen:** Überprüfe die Ollama-Logs:
```bash
# Windows
%LOCALAPPDATA%\Ollama\logs\

# Linux/Mac
~/.ollama/logs/
```

---

## Support

- **Ollama Doku:** https://ollama.com/docs
- **Mistral Modell:** https://ollama.com/library/mistral
- **Llama 3.1 Modell:** https://ollama.com/library/llama3.1

Viel Erfolg! 🎯