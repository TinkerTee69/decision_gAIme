import os
import json
import yaml
import requests
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple


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

        # Ressourcen-Tracking
        self.available_resources = self._extract_resources()
        self.resource_status = self._initialize_resource_status()

    def load_scenario(self) -> Dict:
        """Lädt das Szenario aus der Config-Datei"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"❌ Config-Datei '{self.config_path}' nicht gefunden!")
            exit(1)

    def _extract_resources(self) -> Dict:
        """Extrahiert verfügbare Ressourcen aus der Config"""
        player = self.scenario.get('player_blue', {})
        return {
            'forces': player.get('forces', {}),
            'constraints': player.get('constraints', []),
            'initial_position': player.get('initial_position', [])
        }

    def _initialize_resource_status(self) -> Dict:
        """Initialisiert Ressourcen-Status (was ist noch verfügbar)"""
        forces = self.available_resources['forces']
        status = {}

        for category, description in forces.items():
            status[category] = {
                'description': description,
                'status': 'verfügbar',
                'deployed': False,
                'losses': None
            }

        return status

    def _create_forbidden_terms(self) -> Dict[str, List[str]]:
        """Erstellt Liste verbotener militärischer Begriffe"""
        return {
            'luftwaffe': [
                'eurofighter', 'tornado', 'kampfflugzeug', 'jet', 'fighter',
                'kampfhubschrauber', 'helikopter', 'helicopter', 'heli', 'apache',
                'tigerhubschrauber', 'kampfhubschrauber', 'transporthubschrauber',
                'luftangriff', 'bombardierung', 'luftschlag', 'luftunterstützung',
                'drohnenangriff', 'bewaffnete drohne', 'kampfdrohne'
            ],
            'artillerie_schwer': [
                'panzerhaubitze', 'pzh', 'pzh2000', 'haubitze 155', 'artillerie 155',
                'selbstfahrhaubitze', 'schwere artillerie', 'feldhaubitze',
                'mlrs', 'raketenwerfer', 'mars', 'himars'
            ],
            'marine': [
                'kriegsschiff', 'fregatte', 'korvette', 'u-boot', 'marine',
                'schiff', 'flotte', 'marineeinheit'
            ],
            'strategisch': [
                'marschflugkörper', 'cruise missile', 'taurus', 'rakete',
                'ballistisch', 'atomwaffe', 'nuklear'
            ],
            'verstärkung': [
                'verstärkung', 'brigade', 'division', 'regiment',
                'luftlande', 'fallschirmjäger', 'zusätzliche truppen'
            ]
        }

    def _check_forbidden_terms(self, player_input: Dict[str, str]) -> Tuple[bool, List[str]]:
        """Prüft ob verbotene Begriffe im Input sind"""
        forbidden = self._create_forbidden_terms()
        found_forbidden = []

        # Kombiniere alle Input-Felder
        full_text = " ".join(player_input.values()).lower()

        for category, terms in forbidden.items():
            for term in terms:
                # Wort-Grenze beachten
                pattern = r'\b' + re.escape(term) + r'\b'
                if re.search(pattern, full_text):
                    found_forbidden.append(f"{term} ({category})")

        return len(found_forbidden) > 0, found_forbidden

    def _extract_weapon_systems(self) -> Dict[str, List[str]]:
        """Extrahiert EXAKTE verfügbare Waffensysteme aus Config"""
        forces = self.available_resources['forces']

        weapon_systems = {
            'verfügbar': [],
            'nicht_verfügbar': []
        }

        # Parse verfügbare Systeme aus Beschreibungen
        artillery_desc = forces.get('artillery', '').lower()
        if 'mörser' in artillery_desc or 'mortar' in artillery_desc:
            if '120mm' in artillery_desc:
                weapon_systems['verfügbar'].append('120mm Mörser (Reichweite ~7km)')

        infantry_desc = forces.get('infantry', '').lower()
        if 'spz' in infantry_desc or 'schützenpanzer' in infantry_desc:
            weapon_systems['verfügbar'].append('Schützenpanzer (Infanterie-Transport)')

        armor_desc = forces.get('armor', '').lower()
        if 'panzer' in armor_desc or 'kampfpanzer' in armor_desc:
            weapon_systems['verfügbar'].append('Kampfpanzer (z.B. Leopard 2)')

        recon_desc = forces.get('recon', '').lower()
        if 'drohne' in recon_desc:
            weapon_systems['verfügbar'].append('Aufklärungsdrohnen (UNBEWAFFNET)')

        # Explizit NICHT verfügbar
        weapon_systems['nicht_verfügbar'] = [
            'Panzerhaubitzen (PzH 2000, 155mm)',
            'Schwere Artillerie (über Mörser-Reichweite)',
            'MLRS / Raketenwerfer',
            'Eurofighter / Kampfflugzeuge',
            'Kampfhubschrauber (Tiger, Apache)',
            'Bewaffnete Drohnen',
            'Marine / Schiffe',
            'Marschflugkörper',
            'Strategische Waffen'
        ]

        return weapon_systems

    def _format_available_resources(self) -> str:
        """Formatiert verfügbare Ressourcen für KI-Prompts"""
        weapon_systems = self._extract_weapon_systems()

        output = "=== STRIKT VERFÜGBARE KRÄFTE ===\n\n"

        for category, info in self.resource_status.items():
            status_symbol = "✅" if info['status'] == 'verfügbar' else "⚠️"
            output += f"{status_symbol} {category.upper()}: {info['description']}\n"
            if info['deployed']:
                output += f"   └─ Status: Im Einsatz\n"
            if info['losses']:
                output += f"   └─ Verluste: {info['losses']}\n"

        output += "\n=== EXPLIZIT VERFÜGBARE WAFFENSYSTEME ===\n"
        for system in weapon_systems['verfügbar']:
            output += f"✅ {system}\n"

        output += "\n=== EXPLIZIT NICHT VERFÜGBAR ===\n"
        for system in weapon_systems['nicht_verfügbar']:
            output += f"❌ {system}\n"

        output += "\n=== EINSCHRÄNKUNGEN ===\n"
        for constraint in self.available_resources['constraints']:
            output += f"❌ {constraint}\n"

        output += "\n⚠️ KRITISCH: Nur die EXPLIZIT gelisteten Systeme sind verfügbar!\n"
        output += "⚠️ Panzerhaubitze ≠ Mörser! 155mm Artillerie ≠ 120mm Mörser!\n"
        output += "⚠️ Verwechsle NICHT ähnlich klingende Systeme!\n"

        return output

    def call_llm(self, model: str, prompt: str, system_prompt: str = "", strict_mode: bool = False) -> str:
        """Ruft lokales LLM via Ollama auf"""
        try:
            # Niedrigere Temperatur für Ressourcen-Checks (striktere Antworten)
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

        player = self.scenario['player_blue']
        print(f"🎯 DEINE ROLLE: {player['role']}")
        print(f"🎯 AUFTRAG: {player['objective']}\n")

        print("⚔️  VERFÜGBARE KRÄFTE:")
        for key, value in player['forces'].items():
            print(f"   • {key.capitalize()}: {value}")

        print("\n❌ NICHT VERFÜGBAR:")
        print("   • Luftwaffe (keine Eurofighter, Tornado, Kampfhubschrauber)")
        print("   • Marine (keine Schiffe)")
        print("   • Strategische Waffen (keine Marschflugkörper)")
        print("   • Weitere Verstärkungen außer den gelisteten")

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

        # Zeige Ressourcen-Übersicht
        print("📦 DEINE VERFÜGBAREN KRÄFTE:")
        for category, info in self.resource_status.items():
            status = "✅ Verfügbar" if not info['deployed'] else "⚠️ Im Einsatz"
            print(f"   {category.capitalize()}: {status}")
        print("\n💡 Tipp: Du hast KEINE Luftwaffe, Marine oder Verstärkungen!\n")

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

    def assistant_review(self, player_input: Dict[str, str]) -> str:
        """Assistenz-KI überprüft die Eingabe"""
        resources_info = self._format_available_resources()

        # Automatische Prüfung auf verbotene Begriffe
        has_forbidden, forbidden_list = self._check_forbidden_terms(player_input)

        if has_forbidden:
            warning = "\n🚨 AUTOMATISCHE WARNUNG 🚨\n"
            warning += "Folgende nicht-verfügbare Systeme wurden in deiner Eingabe erkannt:\n"
            for term in forbidden_list:
                warning += f"  ❌ {term}\n"
            warning += "\nDiese Systeme stehen dir NICHT zur Verfügung!\n"
            print(warning)

        system_prompt = f"""Du bist ein STRENGER militärischer Berater für taktische Simulationen.

DEINE ROLLE:
- Überprüfe Spielerentscheidungen PENIBEL auf Ressourcen-Verfügbarkeit
- Sei EXTREM STRIKT bei Waffensystem-Bezeichnungen
- WICHTIG: Verwechsle NICHT ähnlich klingende Systeme!
- Erkenne innovative Ansätze an, aber NUR mit verfügbaren Mitteln

VERFÜGBARE RESSOURCEN DES SPIELERS:
{resources_info}

KRITISCHE UNTERSCHEIDUNGEN (häufige Verwechslungen):
❌ PANZERHAUBITZE (PzH 2000, 155mm, ~30km Reichweite) → NICHT verfügbar!
✅ MÖRSER (120mm, ~7km Reichweite) → Verfügbar!

❌ SCHWERE ARTILLERIE (155mm+) → NICHT verfügbar!
✅ LEICHTE ARTILLERIE (120mm Mörser) → Verfügbar!

❌ KAMPFHUBSCHRAUBER (Tiger, Apache) → NICHT verfügbar!
✅ AUFKLÄRUNGSDROHNEN (unbewaffnet!) → Verfügbar!

❌ BEWAFFNETE DROHNEN → NICHT verfügbar!
✅ AUFKLÄRUNGSDROHNEN (nur Kamera) → Verfügbar!

BEISPIELE FÜR ABLEHNUNGEN:

Spieler sagt: "Panzerhaubitzen beschießen Feind"
→ ABLEHNEN: "❌ Du hast KEINE Panzerhaubitzen! Verfügbar sind nur 120mm Mörser mit max. 7km Reichweite."

Spieler sagt: "155mm Artillerie auf Ziel"
→ ABLEHNEN: "❌ Du hast KEINE 155mm Artillerie! Verfügbar sind nur 120mm Mörser."

Spieler sagt: "Drohnen greifen an"
→ ABLEHNEN: "❌ Deine Drohnen sind UNBEWAFFNET (nur Aufklärung). Keine Bewaffnung verfügbar."

Spieler sagt: "Helikopter transportieren Truppen"
→ ABLEHNEN: "❌ Du hast KEINE Helikopter. Transport nur mit Schützenpanzern möglich."

PRÜF-REIHENFOLGE:
1. RESSOURCEN-CHECK (OBERSTE PRIORITÄT!)
   - Prüfe JEDES genannte Waffensystem
   - Verwechsle NICHT ähnliche Bezeichnungen
   - Sei pedantisch: Panzerhaubitze ≠ Mörser!

2. REALITÄTS-CHECK
   - Ist die Aktion zeitlich machbar?
   - Sind genug Kräfte verfügbar?
   - Passt die Logistik?

3. TAKTIK-CHECK
   - Werden Aufträge beachtet?
   - Ist die Taktik sinnvoll?
   - Gibt es bessere Alternativen?

FORMAT:
Beginne IMMER mit dem Ressourcen-Check!

❌ RESSOURCEN-PROBLEME (falls vorhanden):
[Liste aller nicht-verfügbaren Systeme die genannt wurden]

✅ VERFÜGBARE ALTERNATIVEN:
[Was KANN er stattdessen nutzen]

[Dann weitere Bewertung...]

Antworte auf Deutsch. Sei STRENG aber konstruktiv."""

        formatted_input = self.format_player_input(player_input)

        user_prompt = f"""Überprüfe folgende Spielerentscheidung STRIKT auf Ressourcen-Verfügbarkeit:

{formatted_input}

WICHTIG: 
1. Prüfe ZUERST ob alle genannten Systeme verfügbar sind!
2. Verwechsle NICHT Panzerhaubitze mit Mörser!
3. Prüfe JEDEN militärischen Begriff!
4. Sei PEDANTISCH bei Waffensystem-Bezeichnungen!

Beginne deine Antwort mit dem Ressourcen-Check."""

        print("\n🤖 Assistenz-KI analysiert STRIKT deine Entscheidung...\n")
        return self.call_llm(self.assistant_model, user_prompt, system_prompt, strict_mode=True)

    def refine_loop(self, initial_input: Dict[str, str]) -> Dict[str, str]:
        """Überarbeitungsschleife mit Assistenz-KI"""
        current_input = initial_input

        while True:
            # Automatische Prüfung VOR der KI
            has_forbidden, forbidden_list = self._check_forbidden_terms(current_input)

            if has_forbidden:
                print("\n" + "=" * 80)
                print("   🚨 AUTOMATISCHE RESSOURCEN-PRÜFUNG")
                print("=" * 80)
                print("\n❌ Folgende nicht-verfügbare Systeme wurden erkannt:")
                for term in forbidden_list:
                    print(f"   • {term}")
                print("\n⚠️  Die KI wird diese Systeme ablehnen!")
                print("=" * 80 + "\n")

            formatted_input = self.format_player_input(current_input)
            feedback = self.assistant_review(current_input)

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
                    'feedback': feedback,
                    'forbidden_terms': forbidden_list if has_forbidden else None
                })
                return current_input

            elif choice == 'q':
                print("\n⚠️  Spiel abgebrochen.")
                exit(0)

    def simulate_turn(self, player_input: Dict[str, str]) -> str:
        """Simulator-KI wertet aus und entwickelt Szenario weiter"""
        resources_info = self._format_available_resources()

        # Automatische Prüfung auf verbotene Begriffe
        has_forbidden, forbidden_list = self._check_forbidden_terms(player_input)

        system_prompt = f"""Du bist eine STRIKTE militärische Simulations-KI für taktische Szenarien.

DEINE AUFGABE:
- Simuliere die Folgen der Spieleraktionen realistisch
- OBERSTE PRIORITÄT: LEHNE Aktionen mit nicht-verfügbaren Ressourcen SOFORT AB!
- Sei EXTREM PEDANTISCH bei Waffensystem-Bezeichnungen
- WICHTIG: Verdeckte Aktionen (COVERT_ACTIONS) werden NICHT direkt genannt!
  → Zeige nur die AUSWIRKUNGEN (z.B. "Infrastruktur ausgefallen, Ursache unklar")
- Simuliere Gegenreaktionen plausibel
- Berücksichtige Zufall, Nebel des Krieges, unerwartete Entwicklungen

VERFÜGBARE RESSOURCEN DES SPIELERS:
{resources_info}

SZENARIO-KONTEXT:
Auftrag: {self.scenario['player_blue']['objective']}
Gegner: {self.scenario['player_red']['role']}
Gelände: {', '.join(self.scenario['terrain'][:3])}

KRITISCHE UNTERSCHEIDUNGEN (VERWECHSLE NICHT!):
❌ PANZERHAUBITZE (155mm, ~30km) → NICHT verfügbar!
✅ MÖRSER (120mm, ~7km) → Verfügbar!

❌ SCHWERE ARTILLERIE → NICHT verfügbar!
✅ MÖRSER → Verfügbar!

❌ KAMPFHUBSCHRAUBER → NICHT verfügbar!
✅ AUFKLÄRUNGSDROHNEN (unbewaffnet) → Verfügbar!

ABLEHNUNGS-REGELN (EXTREM WICHTIG!):

1. Spieler nennt NICHT-VERFÜGBARES System:
   → "🚫 AKTION ABGELEHNT: [System] nicht verfügbar."
   → Erkläre was er STATTDESSEN hätte nutzen können
   → Simuliere NICHT als wäre es verfügbar!

2. Spieler verwechselt Systeme:
   Beispiel: "Panzerhaubitze" statt "Mörser"
   → "🚫 KORREKTUR: Du hast keine Panzerhaubitzen. Meintest du deine 120mm Mörser?"
   → Wenn er es meinte: Simuliere mit Mörsern
   → Wenn nicht: Ablehnung

3. Spieler will Unmögliches:
   Beispiel: "Mörser schießen auf 15km"
   → "🚫 UNMÖGLICH: 120mm Mörser haben max. 7km Reichweite. Ziel außerhalb Reichweite."

BEISPIELE FÜR ABLEHNUNGEN:

Input: "Panzerhaubitzen beschießen Feindstellungen"
Output: "🚫 AKTION ABGELEHNT
Die Panzerhaubitzen-Aktion konnte nicht durchgeführt werden.
Grund: Keine Panzerhaubitzen verfügbar.

Du verfügst über: 4x 120mm Mörser (Reichweite 7km).
Falls du diese meintest, bitte neu formulieren."

Input: "Eurofighter greifen an"
Output: "🚫 AKTION ABGELEHNT
Luftangriff nicht durchführbar.
Grund: Keine Luftwaffe verfügbar.

Alternative: Mörser-Feuerunterstützung oder Panzer-Direktfeuer."

AUSGABE-FORMAT:

1. 🚫 ABGELEHNTE AKTIONEN (falls vorhanden)
   [Liste aller nicht-durchführbaren Aktionen mit Grund]

2. ✅ DURCHGEFÜHRTE AKTIONEN
   [Simulation der MÖGLICHEN Aktionen]

3. 🎭 ENTWICKLUNGEN
   [Gegnerreaktionen, Zufallsereignisse]

4. 📊 NEUE LAGESITUATION
   [Aktueller Status]

5. 🔍 AUFKLÄRUNGSERGEBNISSE
   [Antworten auf INTELLIGENCE_REQUESTS]

WICHTIG:
- Verdeckte Aktionen nur über WIRKUNG zeigen
- Realistische Zeitverläufe
- STRIKTE Ressourcen-Kontrolle!
- Bei Zweifeln → ABLEHNEN!

Antworte auf Deutsch, erzählerisch aber STRIKT."""

        formatted_input = self.format_player_input(player_input)

        # Warnung einbauen falls verbotene Begriffe gefunden
        forbidden_warning = ""
        if has_forbidden:
            forbidden_warning = "\n⚠️ WARNUNG: Folgende nicht-verfügbare Systeme wurden erkannt:\n"
            for term in forbidden_list:
                forbidden_warning += f"  - {term}\n"
            forbidden_warning += "Diese MÜSSEN in der Simulation abgelehnt werden!\n\n"

        user_prompt = f"""{forbidden_warning}Simuliere die Folgen dieser Spieleraktionen:

{formatted_input}

KRITISCH: 
1. Prüfe ZUERST jedes genannte Waffensystem!
2. Lehne ALLE nicht-verfügbaren Systeme AB!
3. Verwechsle NICHT Panzerhaubitze mit Mörser!
4. Nur verfügbare Aktionen simulieren!

Beginne mit den Ablehnungen (falls vorhanden), dann Simulation."""

        print("\n🎮 Simulator-KI berechnet die Entwicklungen...\n")
        return self.call_llm(self.simulator_model, user_prompt, system_prompt, strict_mode=True)

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