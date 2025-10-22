import os
import json
import yaml
import requests
import hashlib
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


class FirstRunSetup:
    """Automatisches Setup beim ersten Start"""

    def __init__(self):
        self.setup_file = Path.home() / "AppData" / "Local" / ".qrt_setup_done"
        self.ollama_download_url = "https://ollama.com/download/OllamaSetup.exe"

    def is_first_run(self) -> bool:
        return not self.setup_file.exists()

    def check_ollama(self) -> bool:
        """Prüft ob Ollama installiert ist"""
        try:
            result = subprocess.run(
                ["ollama", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False

    def check_ollama_running(self) -> bool:
        """Prüft ob Ollama Service läuft"""
        try:
            response = requests.get("http://localhost:11434", timeout=2)
            return response.status_code == 200
        except:
            return False

    def check_models(self, models: List[str]) -> Dict[str, bool]:
        """Prüft welche Modelle installiert sind"""
        result = {}
        try:
            output = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            installed = output.stdout

            for model in models:
                result[model] = model in installed
        except:
            for model in models:
                result[model] = False

        return result

    def download_model(self, model: str) -> bool:
        """Lädt ein Modell herunter"""
        print(f"\n📥 Lade Modell herunter: {model}")
        print("⏳ Dies kann 10-30 Minuten dauern (je nach Internet)...")
        print("☕ Perfekte Zeit für einen Kaffee!\n")

        try:
            process = subprocess.Popen(
                ["ollama", "pull", model],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            for line in process.stdout:
                # Zeige Download-Fortschritt
                if "pulling" in line.lower() or "%" in line:
                    print(f"  {line.strip()}")

            process.wait()
            return process.returncode == 0

        except Exception as e:
            print(f"❌ Fehler beim Download: {e}")
            return False

    def start_ollama_service(self) -> bool:
        """Startet Ollama Service"""
        print("\n⚙️  Starte Ollama Service...")
        try:
            # Versuche Ollama im Hintergrund zu starten
            if sys.platform == "win32":
                subprocess.Popen(
                    ["ollama", "serve"],
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                subprocess.Popen(
                    ["ollama", "serve"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

            # Warte bis Service läuft
            for i in range(10):
                if self.check_ollama_running():
                    print("✅ Ollama Service läuft!\n")
                    return True
                print(f"  Warte... ({i + 1}/10)")
                import time
                time.sleep(1)

            return False

        except Exception as e:
            print(f"❌ Fehler beim Starten: {e}")
            return False

    def run_first_time_setup(self, required_models: List[str]):
        """Führt Setup beim ersten Start durch"""

        print("\n" + "=" * 80)
        print("   🎉 WILLKOMMEN ZUM NOTFALL-RESPONSE SIMULATOR!")
        print("=" * 80)
        print("\n📋 Erster Start erkannt - automatische Einrichtung startet...\n")

        # 1. Prüfe Ollama Installation
        print("🔍 Schritt 1/3: Prüfe Ollama Installation...")
        if not self.check_ollama():
            print("\n⚠️  Ollama ist nicht installiert!\n")
            print("📥 Bitte installiere Ollama:")
            print(f"   1. Download von: {self.ollama_download_url}")
            print("   2. Installer ausführen")
            print("   3. Dieses Programm neu starten\n")
            input("Drücke ENTER um zu beenden...")
            sys.exit(1)

        print("✅ Ollama gefunden!\n")

        # 2. Starte Ollama Service
        print("🔍 Schritt 2/3: Starte Ollama Service...")
        if not self.check_ollama_running():
            if not self.start_ollama_service():
                print("\n⚠️  Ollama Service konnte nicht gestartet werden!\n")
                print("Bitte starte Ollama manuell:")
                print("   1. Öffne Terminal/CMD")
                print("   2. Führe aus: ollama serve")
                print("   3. Lasse das Terminal offen")
                print("   4. Starte dieses Programm neu\n")
                input("Drücke ENTER um zu beenden...")
                sys.exit(1)
        else:
            print("✅ Ollama Service läuft bereits!\n")

        # 3. Prüfe und lade Modelle
        print("🔍 Schritt 3/3: Prüfe KI-Modelle...")
        models_status = self.check_models(required_models)

        missing_models = [m for m, installed in models_status.items() if not installed]

        if missing_models:
            print(f"\n📥 {len(missing_models)} Modell(e) müssen heruntergeladen werden:")
            for model in missing_models:
                print(f"   • {model}")

            total_size = len(missing_models) * 8  # ~8GB pro Modell
            print(f"\n💾 Geschätzte Download-Größe: ~{total_size}GB")
            print("⏱️  Geschätzte Dauer: 20-60 Minuten (je nach Internet)\n")

            response = input("Jetzt herunterladen? (j/n): ").strip().lower()

            if response == 'j':
                for model in missing_models:
                    success = self.download_model(model)
                    if not success:
                        print(f"\n❌ Download von {model} fehlgeschlagen!")
                        print("Bitte versuche es manuell:")
                        print(f"   ollama pull {model}\n")
                        input("Drücke ENTER um zu beenden...")
                        sys.exit(1)

                print("\n🎉 Alle Modelle erfolgreich heruntergeladen!")
            else:
                print("\n⚠️  Ohne Modelle kann der Simulator nicht starten.")
                print("Bitte lade sie manuell herunter:")
                for model in missing_models:
                    print(f"   ollama pull {model}")
                print()
                input("Drücke ENTER um zu beenden...")
                sys.exit(1)
        else:
            print("✅ Alle Modelle bereits installiert!\n")

        # Setup abgeschlossen
        self.setup_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.setup_file, 'w') as f:
            json.dump({
                'setup_date': datetime.now().isoformat(),
                'models': required_models
            }, f)

        print("\n" + "=" * 80)
        print("   ✅ SETUP ABGESCHLOSSEN!")
        print("=" * 80)
        print("\n🎮 Der Simulator startet jetzt...\n")
        input("Drücke ENTER um fortzufahren...")


class LicenseManager:
    """Lizenz-Verwaltung mit verstecktem Zeitstempel (2 Monate Test)"""

    def __init__(self):
        self.license_file = Path.home() / "AppData" / "Local" / ".qrt_sys_cfg"
        self.secret_salt = "QRT_EMERGENCY_SIMULATOR_2025_v1"

    def initialize_license(self):
        """Erstellt Lizenz-Datei beim ersten Start"""
        if not self.license_file.exists():
            install_date = datetime.now()
            expiry_date = install_date + timedelta(days=60)  # 2 Monate

            license_data = {
                'install_timestamp': install_date.timestamp(),
                'expiry_timestamp': expiry_date.timestamp(),
                'checksum': self._generate_checksum(install_date),
                'version': '1.0'
            }

            self.license_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.license_file, 'w') as f:
                json.dump(license_data, f)

    def _generate_checksum(self, date):
        data = f"{date.timestamp()}_{self.secret_salt}"
        return hashlib.sha256(data.encode()).hexdigest()

    def check_license(self) -> bool:
        if not self.license_file.exists():
            self.initialize_license()

        try:
            with open(self.license_file, 'r') as f:
                license_data = json.load(f)

            install_date = datetime.fromtimestamp(license_data['install_timestamp'])
            expiry_date = datetime.fromtimestamp(license_data['expiry_timestamp'])

            expected_checksum = self._generate_checksum(install_date)
            if license_data['checksum'] != expected_checksum:
                self._show_tamper_error()
                return False

            now = datetime.now()

            if now < install_date:
                self._show_tamper_error()
                return False

            if now > expiry_date:
                self._show_expiry_message(expiry_date)
                return False

            days_left = (expiry_date - now).days
            if days_left <= 7:
                print(f"\n⚠️  Testversion läuft in {days_left} Tagen ab!\n")

            return True

        except Exception:
            self._show_tamper_error()
            return False

    def _show_expiry_message(self, expiry_date):
        print("\n" + "=" * 80)
        print("   ⚠️  TESTVERSION ABGELAUFEN")
        print("=" * 80)
        print(f"\nDie 2-monatige Testphase endete am: {expiry_date.strftime('%d.%m.%Y')}")
        print("\nFür die Vollversion kontaktieren Sie:")
        print("   📧 kontakt@qrt-simulator.de")
        print("   📞 +49 XXX XXXXXXX\n")

    def _show_tamper_error(self):
        print("\n" + "=" * 80)
        print("   ⚠️  LIZENZ-FEHLER")
        print("=" * 80)
        print("\nDie Lizenzdatei wurde manipuliert oder ist beschädigt.")
        print("Bitte kontaktieren Sie den Support.\n")


class EmergencySimulator:
    def __init__(self):
        self.config_path = None
        self.scenario = None
        self.turn_number = 1
        self.game_log = []

        # Ollama endpoints
        self.ollama_url = "http://localhost:11434/api/generate"
        self.assistant_model = "deepseek-r1:14b"
        self.simulator_model = "qwen2.5:14b"

        # Manager
        self.license_mgr = LicenseManager()
        self.setup_mgr = FirstRunSetup()

    def find_scenarios(self) -> List[Dict[str, str]]:
        """Findet alle Szenario-Dateien im scenarios-Ordner"""
        scenarios = []
        scenario_dir = Path("./scenarios")

        if not scenario_dir.exists():
            print(f"\n⚠️  Ordner './scenarios' nicht gefunden!")
            print("Erstelle Ordner...")
            scenario_dir.mkdir(parents=True, exist_ok=True)
            print("⚠️  Bitte lege Szenario-Dateien (.yaml) in './scenarios' ab.\n")
            return []

        yaml_files = list(scenario_dir.glob("*.yaml")) + list(scenario_dir.glob("*.yml"))

        if not yaml_files:
            print(f"\n⚠️  Keine Szenario-Dateien in './scenarios' gefunden!\n")
            return []

        for yaml_file in sorted(yaml_files):
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    scenarios.append({
                        'path': str(yaml_file),
                        'filename': yaml_file.name,
                        'name': data.get('scenario_name', yaml_file.stem),
                        'type': data.get('scenario_type', 'unbekannt'),
                        'description': data.get('description', 'Keine Beschreibung')
                    })
            except Exception as e:
                print(f"⚠️  Fehler beim Laden von {yaml_file.name}: {e}")

        return scenarios

    def select_scenario(self) -> str:
        """Interaktives Szenario-Auswahl-Menü"""
        print("\n" + "=" * 80)
        print("   📋 SZENARIO-AUSWAHL")
        print("=" * 80 + "\n")

        scenarios = self.find_scenarios()

        if not scenarios:
            print("❌ Keine Szenarien verfügbar!")
            print("\nLege Szenario-Dateien (.yaml) im Ordner './scenarios' ab.\n")
            exit(1)

        for i, scenario in enumerate(scenarios, 1):
            print(f"[{i}] {scenario['name']}")
            print(f"    Typ: {scenario['type']}")
            desc = scenario['description']
            if len(desc) > 70:
                desc = desc[:70] + "..."
            print(f"    {desc}")
            print()

        print(f"[q] Abbrechen\n")

        while True:
            choice = input("Wähle ein Szenario (Nummer): ").strip().lower()

            if choice == 'q':
                print("\n⚠️  Abgebrochen.\n")
                exit(0)

            try:
                idx = int(choice) - 1
                if 0 <= idx < len(scenarios):
                    selected = scenarios[idx]
                    print(f"\n✅ Gewählt: {selected['name']}\n")
                    return selected['path']
                else:
                    print("❌ Ungültige Nummer!")
            except ValueError:
                print("❌ Bitte eine Nummer eingeben!")

    def load_scenario(self) -> Dict:
        """Lädt das Szenario aus der Config-Datei"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"❌ Datei '{self.config_path}' nicht gefunden!")
            exit(1)
        except Exception as e:
            print(f"❌ Fehler beim Laden: {e}")
            exit(1)

    def call_llm(self, model: str, prompt: str, system_prompt: str = "", strict_mode: bool = False) -> str:
        """Ruft lokales LLM via Ollama auf"""
        try:
            temperature = 0.3 if strict_mode else 0.7

            payload = {
                "model": model,
                "prompt": prompt,
                "system": system_prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "top_p": 0.9 if not strict_mode else 0.5
                }
            }

            response = requests.post(self.ollama_url, json=payload, timeout=120)
            response.raise_for_status()
            return response.json()['response']

        except requests.exceptions.ConnectionError:
            print("\n❌ FEHLER: Ollama läuft nicht!")
            print("Starte Ollama mit: 'ollama serve'")
            exit(1)
        except Exception as e:
            print(f"\n❌ Fehler beim LLM-Aufruf: {e}")
            return ""

    def display_scenario(self):
        """Zeigt das initiale Szenario"""
        print("\n" + "=" * 80)
        print(f"   {self.scenario['scenario_name']}")
        print("=" * 80 + "\n")
        print(f"📋 {self.scenario['description']}\n")

        print(f"🎯 DEINE ROLLE: {self.scenario['team']['role']}")
        print(f"🎯 EINSATZZIEL: {self.scenario['team']['objective']}\n")

        print("⚔️  VERFÜGBARE RESSOURCEN:")
        for key, value in self.scenario['team']['resources'].items():
            print(f"   • {key.capitalize()}: {value}")

        if 'constraints' in self.scenario['team']:
            print("\n⚠️  EINSCHRÄNKUNGEN:")
            for constraint in self.scenario['team']['constraints']:
                print(f"   • {constraint}")

        if 'situation_details' in self.scenario:
            print("\n🗺️  LAGE:")
            for detail in self.scenario['situation_details']:
                print(f"   • {detail}")

        print("\n" + "=" * 80 + "\n")

    def format_player_input(self, player_input: Dict[str, str]) -> str:
        """Formatiert Spieler-Input für LLMs"""
        formatted = ""
        for field, value in player_input.items():
            formatted += f"**{field}**\n{value}\n\n"
        return formatted

    def get_player_input(self) -> Dict[str, str]:
        """Sammelt strukturierte Entscheidungen"""
        print("\n" + "=" * 80)
        print(f"   EINSATZ-ZUG #{self.turn_number}")
        print("=" * 80 + "\n")

        fields = {
            'LAGEEINSCHÄTZUNG': 'Wie bewertest du die aktuelle Situation?',
            'PRIORITÄTEN': 'Was ist am wichtigsten / dringendsten?',
            'SOFORTMASSNAHMEN': 'Welche Maßnahmen ergreifst du SOFORT?',
            'RESSOURCENEINSATZ': 'Wie verteilst du Personal und Material?',
            'KOMMUNIKATION': 'Mit wem kommunizierst du? Was teilst du mit?',
            'NÄCHSTE_SCHRITTE': 'Was planst du für die nächsten Minuten?'
        }

        player_input = {}

        for field_name, prompt_text in fields.items():
            print(f"\n📝 {field_name}")
            print(f"   ({prompt_text})")
            value = input("   >>> ").strip()

            if not value:
                print("⚠️  Eingabe erforderlich!")
                value = input("   >>> ").strip()

            player_input[field_name] = value

        return player_input

    def check_feasibility(self, player_input: Dict[str, str]) -> str:
        """Prüft nur die Durchführbarkeit - KEINE BEWERTUNG!"""

        resources_info = json.dumps(self.scenario['team']['resources'], ensure_ascii=False, indent=2)
        constraints_info = "\n".join(self.scenario['team'].get('constraints', []))

        system_prompt = f"""Du bist ein OBJEKTIVER DURCHFÜHRBARKEITS-CHECKER für Notfall-Response-Teams.

WICHTIG: DEINE EINZIGE AUFGABE IST ES ZU PRÜFEN, OB DIE GEPLANTEN MASSNAHMEN MIT DEN VORHANDENEN RESSOURCEN PHYSISCH UMSETZBAR SIND!

DU DARFST NICHT:
❌ Die Qualität der Entscheidungen bewerten (kein "gut", "schlecht", "korrekt", "effizient")
❌ Taktische Ratschläge geben
❌ Sagen ob Prioritäten richtig oder falsch sind
❌ Die Entscheidung als "klug" oder "unklug" beurteilen

DU DARFST NUR:
✅ Prüfen ob genug Personal vorhanden ist
✅ Prüfen ob genug Material vorhanden ist
✅ Prüfen ob zeitlich/physikalisch möglich
✅ Auf fehlende Ressourcen hinweisen
✅ Auf objektive Widersprüche hinweisen (z.B. "4 Trupps geplant, aber nur 2 verfügbar")

SZENARIO:
Typ: {self.scenario['scenario_type']}
Team: {self.scenario['team']['role']}

VERFÜGBARE RESSOURCEN:
{resources_info}

EINSCHRÄNKUNGEN:
{constraints_info}

AUSGABE-FORMAT (NEUTRAL UND OBJEKTIV):

✅ DURCHFÜHRBARKEIT: [UMSETZBAR / TEILWEISE UMSETZBAR / NICHT UMSETZBAR]

RESSOURCEN-CHECK:
[Checkliste im Format:]
✓ Personal: X Personen verfügbar → [Alle Rollen besetzbar / Engpass bei...]
✓ Material: [Liste] → [Ausreichend / Fehlt...]
✓ Fahrzeuge: [Liste] → [Verfügbar / Nicht verfügbar...]
✓ Zeitablauf: [Parallel/Sequenziell möglich / Zeitkonflikt...]

ENGPÄSSE/WIDERSPRÜCHE (wenn vorhanden):
⚠️ [Neutrale Beschreibung des Problems]
⚠️ [z.B. "Plan sieht 4 PA-Geräte vor, nur 2 vorhanden"]

GESETZLICHE/VERFAHRENSPFLICHTEN (wenn relevant):
⚠️ [z.B. "Atemschutzüberwachung gesetzlich vorgeschrieben - nicht im Plan erwähnt"]
⚠️ [z.B. "Durchsuchungsbefehl muss vorgezeigt werden - nicht erwähnt"]

KRITISCHE REGEL:
Wenn du Wörter wie "gut", "schlecht", "korrekt", "falsch", "effizient", "klug", "richtig" verwendest → DU MACHST EINEN FEHLER!

Antworte auf Deutsch, rein objektiv, nur Fakten."""

        formatted_input = self.format_player_input(player_input)
        user_prompt = f"Prüfe AUSSCHLIESSLICH die Durchführbarkeit (KEINE Bewertung!):\n\n{formatted_input}"

        print("\n🔍 Assistenz-KI prüft Durchführbarkeit...\n")
        return self.call_llm(self.assistant_model, user_prompt, system_prompt, strict_mode=True)

    def refine_loop(self, initial_input: Dict[str, str]) -> Dict[str, str]:
        """Überarbeitungsschleife mit Assistenz-KI"""
        current_input = initial_input

        while True:
            feedback = self.check_feasibility(current_input)

            print("\n" + "=" * 80)
            print("   🔍 DURCHFÜHRBARKEITS-CHECK")
            print("=" * 80)
            print(feedback)
            print("=" * 80 + "\n")

            print("Optionen:")
            print("  [1] Entscheidung überarbeiten")
            print("  [2] Entscheidung ist final - weiter zur Simulation")
            print("  [q] Abbrechen\n")

            choice = input(">>> ").strip()

            if choice == '2':
                return current_input
            elif choice == 'q':
                print("\n⚠️  Abgebrochen.\n")
                exit(0)
            elif choice == '1':
                print("\n🔄 Welches Feld überarbeiten?")
                fields = list(current_input.keys())
                for i, field in enumerate(fields, 1):
                    print(f"   [{i}] {field}")
                print("   [a] Alle Felder neu\n")

                field_choice = input(">>> ").strip().lower()

                if field_choice == 'a':
                    current_input = self.get_player_input()
                else:
                    try:
                        idx = int(field_choice) - 1
                        if 0 <= idx < len(fields):
                            field_name = fields[idx]
                            print(f"\n📝 Neuer Wert für {field_name}:")
                            new_value = input("   >>> ").strip()
                            current_input[field_name] = new_value
                    except ValueError:
                        print("❌ Ungültige Eingabe!")
            else:
                print("❌ Ungültige Option!")

    def simulate_turn(self, player_input: Dict[str, str]) -> str:
        """Simuliert die Folgen der Entscheidungen - OBJEKTIV, KEINE BEWERTUNG!"""

        initial_situation = "\n".join(self.scenario.get('initial_situation', []))
        known_risks = "\n".join(self.scenario.get('known_risks', []))

        system_prompt = f"""Du bist ein OBJEKTIVER EINSATZ-SIMULATOR für Notfall-Response-Training.

DEINE AUFGABE:
1. Nimm die Spieler-Entscheidungen 1:1 und setze sie um
2. Simuliere die REALISTISCHEN Folgen
3. Sei NEUTRAL - keine Bewertung, keine Dramatik
4. Zeige Fakten und Konsequenzen

INITIALE LAGE:
{initial_situation}

BEKANNTE RISIKEN:
{known_risks}

KRITISCHE REGELN:

1. SPIELER-INPUT IST GESETZ:
   - Wenn Spieler sagt "Trupp A macht X" → Dann macht Trupp A genau X
   - Wenn Spieler sagt "Atemschutzüberwachung SOFORT" → Dann beginnt sie SOFORT (nicht nach 10 Min!)
   - Wenn Spieler etwas nicht erwähnt → Es passiert nicht automatisch

2. KEINE ERFINDUNGEN:
   - Wenn Spieler Leitstelle nicht kontaktiert → Dann kommt KEINE Verstärkung
   - Wenn Spieler keine DLK anfordert → Dann kommt KEINE DLK
   - Bleib bei dem was der Spieler entschieden hat

3. REALISTISCHE ZEITANGABEN:
   - PA-Flaschen: 20-30 Minuten unter Volllast
   - Wasserversorgung aufbauen: 2-5 Minuten
   - Brandbekämpfung: Je nach Größe 10-60 Minuten
   - Rettung über DLK: 2-5 Minuten pro Person

4. KEINE DRAMATIK:
   ❌ "verzweifelt", "panisch", "dramatisch"
   ✅ "orientierungslos", "Rauchexposition seit X Min", "keine Sichtung"

5. KEINE WIDERSPRÜCHE:
   - Rauchvergiftung = Verletzung (nicht "keine Verletzten" + "Rauchvergiftung")
   - Personen entweder gerettet ODER nicht - nicht beides

6. STRUKTURIERTE AUSGABE:
   - Klare Zeitlinie
   - Konkrete Fakten
   - Keine Wiederholungen

AUSGABE-FORMAT:

ZEITLINIE (X Minuten nach Eintreffen):

MIN 0-2:
✓ [Was wurde erfolgreich umgesetzt]
✗ [Was wurde nicht umgesetzt / vergessen]
⚠️ [Probleme die auftraten]

MIN 2-5:
[Fortsetzung...]

MIN 5-10:
[Fortsetzung...]

AKTUELLE LAGE (MIN X):
🔥 Hauptgefahr: [Status]
👤 Personen: [Status aller betroffenen Personen]
🚨 Einsatzkräfte: [Status, PA-Luft, etc.]
⚠️ Weitere Gefahren: [Liste]
✅ Verstärkung: [Wenn angefordert]

KRITISCHE INFORMATIONEN:
• PA-Luft Trupp 1: [X Minuten verbleibend]
• PA-Luft Trupp 2: [X Minuten verbleibend]
• Wasserversorgung: [Status]
• [Weitere relevante Infos]

NEUE ERKENNTNISSE:
• [Was wurde entdeckt/gefunden]
• [Neue Gefahren]

Antworte auf Deutsch, rein faktisch, keine Dramatik, keine Bewertung."""

        formatted_input = self.format_player_input(player_input)

        context = ""
        if len(self.game_log) > 0:
            context = "\n\nBISHERIGER VERLAUF:\n"
            for entry in self.game_log[-2:]:
                context += f"Zug {entry['turn']}: {entry['simulation'][:150]}...\n"

        user_prompt = f"{context}\n\nSimuliere die EXAKTEN Folgen dieser Entscheidungen (1:1 umsetzen, keine Erfindungen!):\n\n{formatted_input}"

        print("\n🎮 Simulator entwickelt die Lage...\n")
        return self.call_llm(self.simulator_model, user_prompt, system_prompt)

    def evaluate_performance(self) -> str:
        """Finale Bewertung aller Züge"""

        system_prompt = f"""Du bist ein erfahrener Ausbilder für Notfall-Response-Teams.

Bewerte die GESAMTE Einsatzleistung konstruktiv und detailliert:

BEWERTUNGSKRITERIEN:
1. Prioritätensetzung (Leben > Sachwerte?)
2. Ressourcennutzung (Effizient eingesetzt?)
3. Kommunikation (Leitstelle, Team informiert?)
4. Zeitmanagement (Schnell genug reagiert?)
5. Sicherheit (Eigenschutz, Atemschutzüberwachung?)
6. Vollständigkeit (Alles bedacht? Dachboden, Glutnester, etc.?)

FORMAT:
📊 GESAMTBEWERTUNG
[Kurze Zusammenfassung der Leistung]

✅ STÄRKEN
[Liste der positiven Aspekte]

⚠️ VERBESSERUNGSPOTENZIAL
[Liste der Schwächen]

💡 KONKRETE VERBESSERUNGSVORSCHLÄGE
[Spezifische Tipps für die Zukunft]

📈 LERNPUNKTE
[Was sollte mitgenommen werden?]

⭐ GESAMTBEWERTUNG: X/10 Punkte
[Begründung der Punktzahl]

Antworte auf Deutsch, konstruktiv und lehrreich."""

        full_game = "=== KOMPLETTER EINSATZ ===\n\n"
        for entry in self.game_log:
            full_game += f"\n--- ZUG {entry['turn']} ---\n"
            full_game += "ENTSCHEIDUNG:\n"
            for field, value in entry['input'].items():
                full_game += f"{field}: {value}\n"
            full_game += f"\nFOLGEN:\n{entry['simulation']}\n"
            full_game += "=" * 80 + "\n"

        user_prompt = f"Bewerte diesen Einsatz konstruktiv:\n\n{full_game}"

        print("\n📊 Finale Bewertung wird erstellt...\n")
        return self.call_llm(self.simulator_model, user_prompt, system_prompt)

    def save_logs(self, final_evaluation: str = ""):
        """Speichert Spielverlauf"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"einsatz_log_{timestamp}.txt"

        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"NOTFALL-RESPONSE SIMULATOR\n")
            f.write(f"Szenario: {self.scenario['scenario_name']}\n")
            f.write("=" * 80 + "\n\n")

            for entry in self.game_log:
                f.write(f"\n{'=' * 80}\n")
                f.write(f"ZUG #{entry['turn']} - {entry['timestamp']}\n")
                f.write(f"{'=' * 80}\n\n")

                f.write("ENTSCHEIDUNG:\n")
                for field, value in entry['input'].items():
                    f.write(f"\n{field}:\n{value}\n")

                f.write(f"\n\nFOLGEN:\n{entry['simulation']}\n")

            if final_evaluation:
                f.write(f"\n\n{'=' * 80}\n")
                f.write("FINALE BEWERTUNG\n")
                f.write(f"{'=' * 80}\n\n")
                f.write(final_evaluation)

        print(f"\n✅ Log gespeichert: {log_file}\n")

    def run(self):
        """Hauptspielschleife"""
        print("\n" + "🚨" * 40)
        print("   NOTFALL-RESPONSE SIMULATOR")
        print("🚨" * 40 + "\n")

        # First-Run-Setup
        if self.setup_mgr.is_first_run():
            self.setup_mgr.run_first_time_setup([
                self.assistant_model,
                self.simulator_model
            ])

        # Lizenz-Check
        if not self.license_mgr.check_license():
            exit(1)

        print("⚙️  Prüfe Ollama...")
        try:
            print("  → Teste Assistenz-KI (DeepSeek-R1 14B)...")
            self.call_llm(self.assistant_model, "Test", "", strict_mode=True)
            print("  → Teste Simulator-KI (qwen2.5:14b)...")
            self.call_llm(self.simulator_model, "Test", "")
            print("✅ Beide KI-Modelle bereit!\n")
        except:
            print("❌ Ollama nicht erreichbar!")
            print("\nStarte mit: ollama serve")
            print("\nOder installiere Modelle:")
            print("  ollama pull deepseek-r1:14b")
            print("  ollama pull qwen2.5:14b\n")
            exit(1)

        # Szenario-Auswahl
        self.config_path = self.select_scenario()
        self.scenario = self.load_scenario()

        self.display_scenario()
        input("Drücke ENTER um zu starten...")

        max_turns = self.scenario.get('max_turns', 10)

        while self.turn_number <= max_turns:
            player_input = self.get_player_input()
            final_input = self.refine_loop(player_input)
            simulation_result = self.simulate_turn(final_input)

            print("\n" + "=" * 80)
            print("   🎮 LAGE-ENTWICKLUNG")
            print("=" * 80)
            print(simulation_result)
            print("=" * 80 + "\n")

            self.game_log.append({
                'turn': self.turn_number,
                'timestamp': datetime.now().isoformat(),
                'input': final_input,
                'simulation': simulation_result
            })

            if self.turn_number < max_turns:
                print(f"\nFortschritt: Zug {self.turn_number}/{max_turns}")
                print("\nOptionen:")
                print("  [ENTER] Nächster Zug")
                print("  [e] Einsatz beenden")
                print("  [q] Abbrechen\n")

                choice = input(">>> ").strip().lower()

                if choice == 'e':
                    break
                elif choice == 'q':
                    print("\n⚠️  Abgebrochen.\n")
                    exit(0)

                self.turn_number += 1
            else:
                print(f"\n⚠️  Max. Zuganzahl erreicht!")
                break

        # Finale Bewertung
        print("\n" + "=" * 80)
        print("   📊 FINALE BEWERTUNG")
        print("=" * 80 + "\n")

        final_evaluation = self.evaluate_performance()

        print("\n" + "=" * 80)
        print("   🎓 DEINE LEISTUNG")
        print("=" * 80)
        print(final_evaluation)
        print("=" * 80 + "\n")

        self.save_logs(final_evaluation)
        print("✅ Training abgeschlossen!\n")


if __name__ == "__main__":
    sim = EmergencySimulator()
    sim.run()