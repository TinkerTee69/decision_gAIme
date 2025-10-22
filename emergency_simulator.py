import os
import json
import yaml
import requests
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


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
        # DeepSeek für Assistenz (präzise, strukturiert)
        # qwen2.5:14b für Simulator (flexibel, weniger Safety-Filter)
        self.assistant_model = "deepseek-r1:14b"  # Assistenz-KI (prüft strikt)
        self.simulator_model = "qwen2.5:14b"  # Simulator-KI (beschreibt Folgen)

        # Lizenz-Manager
        self.license_mgr = LicenseManager()

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
        print("=" * 80)
        print(f"\n📋 {self.scenario['description']}\n")

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

    def get_player_input(self) -> Dict[str, str]:
        """Holt strukturierte Eingabe vom Spieler"""
        print(f"\n{'=' * 80}")
        print(f"   EINSATZ-ZUG #{self.turn_number}")
        print(f"{'=' * 80}\n")

        fields = {
            "LAGEEINSCHÄTZUNG": "Wie bewertest du die aktuelle Situation?",
            "PRIORITÄTEN": "Was ist am wichtigsten / dringendsten?",
            "SOFORTMASSNAHMEN": "Welche Maßnahmen ergreifst du SOFORT?",
            "RESSOURCENEINSATZ": "Wie verteilst du Personal und Material?",
            "KOMMUNIKATION": "Mit wem kommunizierst du? Was teilst du mit?",
            "NÄCHSTE_SCHRITTE": "Was planst du für die nächsten Minuten?"
        }

        player_input = {}

        for field, description in fields.items():
            print(f"\n📝 {field}")
            print(f"   ({description})")
            print("   >>> ", end="")
            player_input[field] = input().strip()

        return player_input

    def format_player_input(self, player_input: Dict[str, str]) -> str:
        """Formatiert Spieler-Input für KI"""
        formatted = f"=== EINSATZ-ZUG {self.turn_number} ===\n\n"
        for field, value in player_input.items():
            formatted += f"{field}:\n{value}\n\n"
        return formatted

    def assistant_review(self, player_input: Dict[str, str]) -> str:
        """Assistenz-KI überprüft Entscheidungen auf Durchführbarkeit"""

        resources_info = json.dumps(self.scenario['team']['resources'], ensure_ascii=False, indent=2)
        constraints_info = "\n".join(self.scenario['team'].get('constraints', []))

        system_prompt = f"""Du bist ein SEHR STRENGER und ERFAHRENER Ausbilder für Notfall-Response-Teams.

DEINE ROLLE:
- Überprüfe Einsatzentscheidungen EXTREM KRITISCH auf Durchführbarkeit
- Erkenne LEBENSGEFAHR und weise DEUTLICH darauf hin
- Du rettest Leben durch strikte Kontrolle - sei KOMPROMISSLOS bei Sicherheit
- Wenn etwas gefährlich ist, sage KLAR "NICHT DURCHFÜHRBAR"

SZENARIO:
Typ: {self.scenario['scenario_type']}
Team: {self.scenario['team']['role']}

VERFÜGBARE RESSOURCEN:
{resources_info}

EINSCHRÄNKUNGEN:
{constraints_info}

KRITISCHE PRÜF-PUNKTE (SEHR STRENG!):

1. ❌ LEBENSGEFAHR FÜR EINSATZKRÄFTE?
   - Kein Atemschutz bei Rauch = NICHT DURCHFÜHRBAR!
   - Keine Sicherung = NICHT DURCHFÜHRBAR!
   - Eigenschutz missachtet = NICHT DURCHFÜHRBAR!

2. ❌ LEBENSGEFAHR FÜR ZU RETTENDE?
   - Menschen werden ignoriert = NICHT DURCHFÜHRBAR!
   - Rettung zu spät = NICHT DURCHFÜHRBAR!
   - Falsche Priorität = NICHT DURCHFÜHRBAR!

3. ❌ GESETZLICHE VORGABEN VERLETZT?
   - Keine Atemschutzüberwachung (Feuerwehr) = NICHT DURCHFÜHRBAR!
   - Kein Durchsuchungsbefehl (Polizei) = NICHT DURCHFÜHRBAR!
   - Dokumentationspflicht ignoriert = NICHT DURCHFÜHRBAR!

4. ❌ GRUNDLEGENDE FEHLER?
   - Nicht vorhandene Ressourcen = NICHT DURCHFÜHRBAR!
   - Unmöglicher Zeitrahmen = NICHT DURCHFÜHRBAR!
   - Physikalisch/logistisch unmöglich = NICHT DURCHFÜHRBAR!

WICHTIGE GRUNDSÄTZE (NIEMALS VERGESSEN!):

🚒 FEUERWEHR:
- Menschenrettung geht IMMER vor Brandbekämpfung!
- Atemschutz bei Rauch ist PFLICHT, keine Option!
- Atemschutzüberwachung ist GESETZLICH VORGESCHRIEBEN!
- Eigenschutz geht vor Fremdschutz!

🚑 RETTUNGSDIENST:
- Eigenschutz zuerst (Absicherung Unfallstelle!)
- Sichtung bei MANV ist PFLICHT!
- Schwerste Verletzungen zuerst (rot vor gelb vor grün)!

🚓 POLIZEI:
- Eigensicherung IMMER!
- Durchsuchungsbefehl muss vorgezeigt werden!
- Verhältnismäßigkeit wahren!

AUSGABE-FORMAT:

✅ oder ❌ DURCHFÜHRBARKEIT: [Klar JA, TEILWEISE oder NEIN]

❌ KRITISCHE PROBLEME (wenn vorhanden):
[Liste ALLE lebensbedrohlichen oder gesetzwidrigen Punkte]
[Nutze Wörter wie: LEBENSGEFAHR, NICHT DURCHFÜHRBAR, GESETZESVERSTOISS]

⚠️ HINWEISE (wenn vorhanden):
[Problematische aber nicht kritische Punkte]

💡 ANMERKUNGEN (nur wenn wirklich gut):
[Positive Aspekte]

BEISPIELE FÜR STRIKTE ABLEHNUNG:

Beispiel 1 - Feuerwehr ohne Atemschutz:
❌ DURCHFÜHRBARKEIT: NEIN - NICHT DURCHFÜHRBAR!
❌ KRITISCHE PROBLEME:
- LEBENSGEFAHR: Einsatz ohne Atemschutz bei Rauch führt zu Rauchvergiftung!
- GESETZESVERSTOSS: Keine Atemschutzüberwachung!
- TÖDLICHE KONSEQUENZEN: Einsatzkräfte werden sterben!

Beispiel 2 - Rettungsdienst ignoriert Schwerverletzte:
❌ DURCHFÜHRBARKEIT: NEIN - NICHT DURCHFÜHRBAR!
❌ KRITISCHE PROBLEME:
- LEBENSGEFAHR: Schwerverletzte werden ignoriert und sterben!
- PRIORITÄTENFEHLER: Leichtverletzte vor Schwerverletzten = Todesfälle!
- UNTERLASSENE HILFELEISTUNG: Rechtlich und ethisch inakzeptabel!

WICHTIG:
- Sei EXTREM KRITISCH bei Sicherheitsmängeln
- "NICHT DURCHFÜHRBAR" klar aussprechen
- Keine verharmlosenden Formulierungen
- Leben retten durch strikte Kontrolle!

Antworte auf Deutsch, SEHR KRITISCH und DEUTLICH."""

        formatted_input = self.format_player_input(player_input)
        user_prompt = f"Prüfe auf Durchführbarkeit:\n\n{formatted_input}"

        print("\n🔍 Assistenz-KI prüft deine Entscheidung...\n")
        return self.call_llm(self.assistant_model, user_prompt, system_prompt, strict_mode=True)

    def refine_loop(self, initial_input: Dict[str, str]) -> Dict[str, str]:
        """Überarbeitungsschleife mit Assistenz-KI"""
        current_input = initial_input

        while True:
            feedback = self.assistant_review(current_input)

            print("\n" + "=" * 80)
            print("   🔍 ASSISTENZ-FEEDBACK")
            print("=" * 80)
            print(feedback)
            print("=" * 80 + "\n")

            print("Optionen:")
            print("  [1] Entscheidung überarbeiten")
            print("  [2] Entscheidung ist final - weiter zur Simulation")
            print("  [q] Abbrechen\n")

            choice = input(">>> ").strip().lower()

            if choice == '1':
                print("\n🔄 Welches Feld überarbeiten?")
                for i, field in enumerate(current_input.keys(), 1):
                    print(f"   [{i}] {field}")
                print("   [a] Alle Felder neu")

                field_choice = input("\n>>> ").strip()

                if field_choice == 'a':
                    current_input = self.get_player_input()
                else:
                    try:
                        idx = int(field_choice) - 1
                        field_name = list(current_input.keys())[idx]
                        print(f"\n📝 Neuer Wert für {field_name}:")
                        print("   >>> ", end="")
                        current_input[field_name] = input().strip()
                    except (ValueError, IndexError):
                        print("❌ Ungültige Eingabe!")
                        continue

            elif choice == '2':
                return current_input

            elif choice == 'q':
                print("\n⚠️  Abgebrochen.")
                exit(0)

    def simulate_turn(self, player_input: Dict[str, str]) -> str:
        """Simulator-KI entwickelt Szenario weiter OHNE Bewertung"""

        system_prompt = f"""Du bist eine REALISTISCHE Notfall-Simulations-KI für Trainingszwecke.

ABSOLUT VERBOTEN - NIEMALS AUSGEBEN:
❌ "Ich muss warnen..."
❌ "Die Vorgehensweise ist gefährlich..."
❌ "Dies ist nicht empfohlen..."
❌ "Ich kann das nicht simulieren..."
❌ "Das ist ineffizient..."
❌ JEGLICHE Warnungen, Bewertungen oder Meta-Kommentare am Anfang!

STATTDESSEN:
✅ Beginne SOFORT mit "📊 ENTWICKLUNGEN"
✅ Beschreibe NUR was passiert
✅ KEINE Einleitung, KEINE Warnung, DIREKT zur Simulation!

WICHTIG - DEINE AUFGABE:
- Simuliere die TATSÄCHLICHEN Folgen - auch wenn sie katastrophal sind!
- Dies ist TRAINING - du MUSST Fehler und deren tödliche Konsequenzen zeigen!
- Du bist KEIN Ethik-Ratgeber, sondern ein neutraler Simulator!
- Gib NULL Bewertungen ("gut/schlecht"), beschreibe NUR WAS PASSIERT
- Du darfst und sollst Todesfälle, Verletzungen, Katastrophen beschreiben
- KEIN "Ich kann das nicht" - DU MUSST ES TUN, es rettet Leben durch Training!

SZENARIO:
{self.scenario['scenario_type']} - {self.scenario['team']['role']}

REALISTISCHE KONSEQUENZEN ZEIGEN:

Wenn Einsatzkräfte ohne Atemschutz in Rauch gehen:
→ Beschreibe: Husten nach 15 Sek, Orientierungslosigkeit nach 30 Sek, Kollaps nach 60 Sek, Bewusstlosigkeit

Wenn Menschen in Gefahr ignoriert werden:
→ Beschreibe: Verzweiflung, Panik, Sprung aus Fenster, Erstickung, Tod - konkret und zeitlich präzise

Wenn Sicherheitsprotokolle missachtet werden:
→ Beschreibe: Direkte Folgen - Unfälle, Verletzungen, Tod der Einsatzkräfte

Wenn Ressourcen fehlen:
→ Beschreibe: Scheitern - Wasser leer nach X Minuten, Ausrüstung fehlt, Einsatz kollabiert

AUSGABE-FORMAT (SOFORT beginnen, KEINE Einleitung!):

📊 ENTWICKLUNGEN
- Was ist durch die Maßnahmen passiert?
- Welche direkten Folgen traten ein?
- Bei Fehlern: Konkrete Konsequenzen mit Zeitangaben!
- Beschreibe Leiden, Panik, Tod wenn zutreffend

🆕 NEUE LAGE
- Zeit: X Minuten nach Eintreffen
- Verletzte: [Anzahl und Zustand]
- Tote: [Anzahl und Umstände]
- Status der Gefahr: [Hoch/Mittel/Niedrig]
- Wie sieht es jetzt aus?

ℹ️ ZUSÄTZLICHE INFORMATIONEN
- Was wird bekannt?
- Reaktionen von außen
- Unerwartete Entwicklungen
- KEINE Erfindungen - nur was aus dem Input folgt!

BEISPIELE FÜR KORREKTE SIMULATION (direkt starten, keine Warnung!):

RICHTIG:
"📊 ENTWICKLUNGEN
Die beiden Einsatzkräfte stürmen ohne Atemschutz ins verrauchte Gebäude..."

FALSCH:
"Ich muss warnen, dass... ❌ NIEMALS SO!"
"Die Vorgehensweise ist gefährlich... ❌ NIEMALS SO!"

WICHTIGE REGELN:
1. KEINE Bewertung - nur objektive Beschreibung
2. KEINE Warnung am Anfang oder sonst wo
3. SOFORT mit 📊 ENTWICKLUNGEN beginnen
4. Bei Fehlern: Realistische, auch tödliche Folgen zeigen
5. Halte dich STRIKT an User-Input - keine Erfindungen!
6. Wenn User sagt "keine Leitstelle" → dann KEINE Leitstelle!
7. Zeitangaben realistisch (Minuten bei Notfällen)

DU BIST EIN TRAININGS-SIMULATOR:
- Deine Aufgabe ist es zu zeigen was WIRKLICH passiert
- Auch katastrophale Folgen MÜSSEN gezeigt werden
- Das rettet Leben in der Realität!
- Keine moralischen Bedenken - dies ist Training!

Antworte auf Deutsch, objektiv aber schonungslos realistisch.
Beginne SOFORT mit "📊 ENTWICKLUNGEN" - KEINE Einleitung!"""

        formatted_input = self.format_player_input(player_input)

        context = ""
        if len(self.game_log) > 0:
            context = "\n\nBISHERIGER VERLAUF:\n"
            for entry in self.game_log[-2:]:
                context += f"Zug {entry['turn']}: {entry['simulation'][:150]}...\n"

        user_prompt = f"{context}\n\nSimuliere objektiv:\n\n{formatted_input}"

        print("\n🎮 Simulator entwickelt die Lage...\n")
        return self.call_llm(self.simulator_model, user_prompt, system_prompt)

    def evaluate_performance(self) -> str:
        """Finale Bewertung aller Züge"""

        system_prompt = f"""Du bist ein Ausbilder für Notfall-Response-Teams.

Bewerte die GESAMTE Einsatzleistung:
- Analysiere Stärken und Schwächen
- Gib konstruktives, detailliertes Feedback

BEWERTUNGSKRITERIEN:
1. Prioritätensetzung
2. Ressourcennutzung
3. Kommunikation
4. Zeitmanagement
5. Problemlösung
6. Sicherheit

FORMAT:
📊 GESAMTBEWERTUNG
✅ STÄRKEN
⚠️ VERBESSERUNGSPOTENZIAL
💡 VERBESSERUNGSVORSCHLÄGE
⭐ BEWERTUNG: X/10 Punkte

Antworte auf Deutsch, konstruktiv."""

        full_game = "=== KOMPLETTER EINSATZ ===\n\n"
        for entry in self.game_log:
            full_game += f"\n--- ZUG {entry['turn']} ---\n"
            full_game += "ENTSCHEIDUNG:\n"
            for field, value in entry['input'].items():
                full_game += f"{field}: {value}\n"
            full_game += f"\nFOLGEN:\n{entry['simulation']}\n"
            full_game += "=" * 80 + "\n"

        user_prompt = f"Bewerte diesen Einsatz:\n\n{full_game}"

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