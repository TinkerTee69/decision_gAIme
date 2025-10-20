import os
import json
import yaml
import requests
from datetime import datetime
from typing import Dict, List, Optional


class TacticalSimulator:
    def __init__(self, config_path: str = "scenario_config.yaml"):
        self.config_path = config_path
        self.scenario = self.load_scenario()
        self.turn_number = 1
        self.player_log = []
        self.simulator_log = []

        # Ollama endpoints
        self.ollama_url = "http://localhost:11434/api/generate"
        self.assistant_model = "mistral:7b"
        self.simulator_model = "llama3.1:8b"

    def load_scenario(self) -> Dict:
        """Lädt das Szenario aus der Config-Datei"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"❌ Config-Datei '{self.config_path}' nicht gefunden!")
            exit(1)

    def call_llm(self, model: str, prompt: str, system_prompt: str = "") -> str:
        """Ruft lokales LLM via Ollama auf"""
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "system": system_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9
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

        player = self.scenario['player_blue']
        print(f"🎯 DEINE ROLLE: {player['role']}")
        print(f"🎯 AUFTRAG: {player['objective']}\n")

        print("⚔️  VERFÜGBARE KRÄFTE:")
        for key, value in player['forces'].items():
            print(f"   • {key.capitalize()}: {value}")

        print("\n⚠️  EINSCHRÄNKUNGEN:")
        for constraint in player['constraints']:
            print(f"   • {constraint}")

        print("\n🗺️  GELÄNDE:")
        for terrain in self.scenario['terrain']:
            print(f"   • {terrain}")

        print("\n🔍 BESONDERE FAKTOREN:")
        for factor in self.scenario['special_factors']:
            print(f"   • {factor}")

        print("\n" + "=" * 80 + "\n")

    def get_player_input(self) -> Dict[str, str]:
        """Holt strukturierte Eingabe vom Spieler"""
        print(f"\n{'=' * 80}")
        print(f"   ZUG #{self.turn_number}")
        print(f"{'=' * 80}\n")

        fields = {
            "SITUATION_ASSESSMENT": "Wie schätzt du die Lage ein?",
            "INTENT": "Was willst du erreichen?",
            "OPEN_ACTIONS": "Offene Aktionen (sichtbar für alle)",
            "COVERT_ACTIONS": "Verdeckte Aktionen (geheim)",
            "RESOURCE_ALLOCATION": "Ressourcen-Einsatz",
            "INTELLIGENCE_REQUESTS": "Aufklärungswünsche"
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
        formatted = f"=== ZUG {self.turn_number} ===\n\n"
        for field, value in player_input.items():
            formatted += f"{field}:\n{value}\n\n"
        return formatted

    def assistant_review(self, player_input: str) -> str:
        """Assistenz-KI überprüft die Eingabe"""
        system_prompt = f"""Du bist ein militärischer Berater für taktische Simulationen.

DEINE ROLLE:
- Überprüfe Spielerentscheidungen auf Realitätsnähe
- Weise auf unrealistische Elemente hin (z.B. unmögliche Reichweiten, fehlende Ausrüstung)
- Gib konstruktives Feedback, aber BEVORMUNDE NICHT
- Erkenne innovative Ansätze an
- Stelle sicher, dass der Auftrag erfüllt wird

SZENARIO-KONTEXT:
{json.dumps(self.scenario, ensure_ascii=False, indent=2)}

WICHTIG:
- Du bist BERATER, nicht Befehlshaber
- Trenne gute Ideen von schlechten
- Gib konkrete Verbesserungsvorschläge
- Achte auf: Taktik, Logistik, politische Einschränkungen
- Format: Strukturiertes Feedback mit klaren Kategorien

Antworte auf Deutsch."""

        user_prompt = f"""Überprüfe folgende Spielerentscheidung:

{player_input}

Bewerte:
1. Was ist realistisch und gut?
2. Was ist problematisch oder unrealistisch?
3. Werden Aufträge/Einschränkungen beachtet?
4. Konkrete Verbesserungsvorschläge

Gib strukturiertes Feedback."""

        print("\n🤖 Assistenz-KI analysiert deine Entscheidung...\n")
        return self.call_llm(self.assistant_model, user_prompt, system_prompt)

    def refine_loop(self, initial_input: Dict[str, str]) -> Dict[str, str]:
        """Überarbeitungsschleife mit Assistenz-KI"""
        current_input = initial_input

        while True:
            formatted_input = self.format_player_input(current_input)
            feedback = self.assistant_review(formatted_input)

            print("\n" + "=" * 80)
            print("   📊 ASSISTENZ-KI FEEDBACK")
            print("=" * 80)
            print(feedback)
            print("=" * 80 + "\n")

            print("Optionen:")
            print("  [1] Entscheidung überarbeiten")
            print("  [2] Entscheidung ist final - an Simulator senden")
            print("  [q] Abbrechen\n")

            choice = input(">>> ").strip().lower()

            if choice == '1':
                print("\n🔄 Welches Feld möchtest du überarbeiten?")
                print("   Verfügbare Felder:")
                for i, field in enumerate(current_input.keys(), 1):
                    print(f"   [{i}] {field}")
                print("   [a] Alle Felder neu eingeben")

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
                self.player_log.append({
                    'turn': self.turn_number,
                    'timestamp': datetime.now().isoformat(),
                    'input': current_input,
                    'feedback': feedback
                })
                return current_input

            elif choice == 'q':
                print("\n⚠️  Spiel abgebrochen.")
                exit(0)

    def simulate_turn(self, player_input: Dict[str, str]) -> str:
        """Simulator-KI wertet aus und entwickelt Szenario weiter"""
        system_prompt = f"""Du bist eine militärische Simulations-KI für taktische Szenarien.

DEINE AUFGABE:
- Simuliere die Folgen der Spieleraktionen realistisch
- Entwickle das Szenario logisch weiter
- WICHTIG: Verdeckte Aktionen (COVERT_ACTIONS) werden NICHT direkt genannt!
  → Zeige nur die AUSWIRKUNGEN (z.B. "Infrastruktur ausgefallen, Ursache unklar")
- Simuliere Gegenreaktionen plausibel
- Berücksichtige Zufall, Nebel des Krieges, unerwartete Entwicklungen

SZENARIO-KONTEXT:
{json.dumps(self.scenario, ensure_ascii=False, indent=2)}

AUSGABE-FORMAT:
Beschreibe die neue Lage nach den Spieleraktionen:
1. Was ist passiert? (Ergebnisse der offenen Aktionen)
2. Neue Entwicklungen (Gegnerreaktionen, unerwartete Ereignisse)
3. Aktuelle Lagesituation
4. Aufklärungsergebnisse (auf INTELLIGENCE_REQUESTS antworten)

WICHTIG: 
- Verdeckte Aktionen werden nur über ihre WIRKUNG sichtbar
- Realistische Zeitverläufe beachten
- Keine Spieler-Bevormundung, nur Simulation

Antworte auf Deutsch, erzählerisch und immersiv."""

        formatted_input = self.format_player_input(player_input)

        user_prompt = f"""Simuliere die Folgen dieser Spieleraktionen:

{formatted_input}

Entwickle das Szenario realistisch weiter. Beschreibe die neue Lage."""

        print("\n🎮 Simulator-KI berechnet die Entwicklungen...\n")
        return self.call_llm(self.simulator_model, user_prompt, system_prompt)

    def save_logs(self):
        """Speichert die Spielverläufe in Textdateien"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Spieler-Log
        player_file = f"spieler_log_{timestamp}.txt"
        with open(player_file, 'w', encoding='utf-8') as f:
            f.write(f"SPIELER-LOG: {self.scenario['scenario_name']}\n")
            f.write("=" * 80 + "\n\n")

            for entry in self.player_log:
                f.write(f"\n{'=' * 80}\n")
                f.write(f"ZUG #{entry['turn']} - {entry['timestamp']}\n")
                f.write(f"{'=' * 80}\n\n")

                f.write("EINGABE:\n")
                for field, value in entry['input'].items():
                    f.write(f"\n{field}:\n{value}\n")

                f.write(f"\n\nASSISTENZ-FEEDBACK:\n{entry['feedback']}\n")

        # Simulator-Log
        simulator_file = f"simulator_log_{timestamp}.txt"
        with open(simulator_file, 'w', encoding='utf-8') as f:
            f.write(f"SIMULATOR-LOG: {self.scenario['scenario_name']}\n")
            f.write("=" * 80 + "\n\n")

            for entry in self.simulator_log:
                f.write(f"\n{'=' * 80}\n")
                f.write(f"ZUG #{entry['turn']} - {entry['timestamp']}\n")
                f.write(f"{'=' * 80}\n\n")
                f.write(entry['simulation'])
                f.write("\n\n")

        print(f"\n✅ Logs gespeichert:")
        print(f"   📄 {player_file}")
        print(f"   📄 {simulator_file}\n")

    def run(self):
        """Hauptspielschleife"""
        print("\n" + "🎯" * 40)
        print("   TAKTISCHER SIMULATOR - OFFIZIERSAUSBILDUNG")
        print("🎯" * 40 + "\n")

        print("⚙️  Prüfe Ollama-Verbindung...")
        try:
            test = self.call_llm(self.assistant_model, "Test", "")
            print("✅ Ollama läuft!\n")
        except:
            print("❌ Ollama nicht erreichbar! Starte mit: 'ollama serve'")
            exit(1)

        self.display_scenario()

        input("Drücke ENTER um zu starten...")

        while True:
            # Spieler-Eingabe
            player_input = self.get_player_input()

            # Assistenz-Review und Überarbeitung
            final_input = self.refine_loop(player_input)

            # Simulation
            simulation_result = self.simulate_turn(final_input)

            # Ergebnis anzeigen
            print("\n" + "=" * 80)
            print("   🎮 SIMULATOR-ERGEBNIS")
            print("=" * 80)
            print(simulation_result)
            print("=" * 80 + "\n")

            # Log speichern
            self.simulator_log.append({
                'turn': self.turn_number,
                'timestamp': datetime.now().isoformat(),
                'simulation': simulation_result
            })

            # Nächster Zug
            self.turn_number += 1

            print("\nOptionen:")
            print("  [ENTER] Nächster Zug")
            print("  [s] Spiel beenden und Logs speichern")
            print("  [q] Abbrechen ohne Speichern\n")

            choice = input(">>> ").strip().lower()

            if choice == 's':
                self.save_logs()
                print("\n✅ Spiel beendet. Auf Wiedersehen!\n")
                break
            elif choice == 'q':
                print("\n⚠️  Spiel abgebrochen ohne Speichern.\n")
                break


if __name__ == "__main__":
    sim = TacticalSimulator()
    sim.run()