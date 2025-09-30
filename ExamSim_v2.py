import csv
import random
import os
import string
import datetime
import json

# --- Globale Konstanten ---
FRAGEN_DATEI = "questions.csv"    # CSV-Datei, in der die Prüfungsfragen gespeichert sind
EINSTELLUNGEN_DATEI = "last_test_settings.json"   # JSON mit den zuletzt verwendeten Testeinstellungen

# ANSI-Escape-Codes für Textformatierung im Terminal (fett, kursiv, zurücksetzen)
BOLD = '\033[1m'
ITALIC = '\033[3m'
RESET = '\033[0m'  # Rücksetzen auf Normalschrift

def lade_letzte_einstellungen():
    """Lädt die letzten Benutzereinstellungen des Tests aus der JSON-Datei, falls vorhanden."""
    if os.path.exists(EINSTELLUNGEN_DATEI):
        with open(EINSTELLUNGEN_DATEI, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def speichere_letzte_einstellungen(einstellungen):
    """Speichert die aktuellen Testeinstellungen als JSON."""
    with open(EINSTELLUNGEN_DATEI, 'w', encoding='utf-8') as f:
        json.dump(einstellungen, f, indent=4)

def lade_fragen_aus_csv(dateipfad):
    """
    Lädt alle Fragen aus der angegebenen CSV-Datei ein.
    Jede Zeile wird geprüft und bei Inkonsistenzen bzw. Fehlern übersprungen.
    """
    fragen_liste = []
    if not os.path.exists(dateipfad):
        print(f"FEHLER: Die Datei '{dateipfad}' wurde nicht gefunden.")
        return []
    try:
        with open(dateipfad, mode='r', encoding='utf-8') as csv_datei:
            csv_leser = csv.DictReader(csv_datei)
            for i, zeile in enumerate(csv_leser):
                frage_kurz = zeile.get('Question', 'Unbekannte Frage')[:40] + '...'
                zeilen_nr = i + 2  # +2 wegen Header und 0-basiertem Index

                # Leere oder ungültige Zeilen überspringen
                if zeile.get('Question') == 'Question' or not zeile.get('Question'):
                    continue

                # Bis zu 15 Antwortoptionen auslesen
                optionen = [zeile[f"Answer Option {j}"].strip()
                            for j in range(1, 16)
                            if zeile.get(f"Answer Option {j}") and zeile[f"Answer Option {j}"].strip()]
                korrekte_antworten_str = [s.strip() for s in zeile.get('Correct Response', '').split(',')]

                # Sauberer Umgang mit Fragen ohne Antwortoptionen/Korrektlösung
                if not optionen:
                    print(f"WARNUNG: Zeile {zeilen_nr}: Frage '{frage_kurz}' wird übersprungen (keine Antwortoptionen).")
                    continue
                if not korrekte_antworten_str or not korrekte_antworten_str[0]:
                    print(f"WARNUNG: Zeile {zeilen_nr}: Frage '{frage_kurz}' wird übersprungen (keine korrekte Antwort angegeben).")
                    continue

                # Indizes der korrekten Antwort prüfen
                is_valid = True
                for idx_str in korrekte_antworten_str:
                    try:
                        idx_int = int(idx_str)
                        if not (1 <= idx_int <= len(optionen)):
                            print(f"WARNUNG: Zeile {zeilen_nr}: Frage '{frage_kurz}' wird übersprungen (Index '{idx_int}' liegt außerhalb des Bereichs von {len(optionen)} Optionen).")
                            is_valid = False
                            break
                    except (ValueError, TypeError):
                        print(f"WARNUNG: Zeile {zeilen_nr}: Frage '{frage_kurz}' wird übersprungen (ungültiger Index '{idx_str}').")
                        is_valid = False
                        break

                if not is_valid:
                    continue

                fragen_liste.append({
                    "nummer": zeilen_nr - 1,  # laufende Nummer
                    "frage": zeile['Question'].strip(),
                    "typ": zeile['Question Type (multiple-choice or multi-select)'].strip(),
                    "optionen": optionen,
                    "korrekt": korrekte_antworten_str,
                    "erklaerung": zeile.get('Explanation', 'Keine Erklärung verfügbar.').strip()
                })
    except Exception as e:
        print(f"FEHLER beim Lesen der Datei: {e}")
    return fragen_liste

def aktualisiere_erklaerung_in_csv(dateiname, frage_nummer, neue_erklaerung):
    """
    Sucht die entsprechende Zeilennummer in der CSV und ersetzt die Erklärung.
    (Die ganze Datei wird eingelesen und neu geschrieben.)
    """
    try:
        with open(dateiname, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            daten = list(reader)
        header = daten[0]
        if 'Explanation' not in header:
            print("FEHLER: Spalte 'Explanation' nicht in der CSV gefunden.")
            return False
        explanation_idx = header.index('Explanation')
        daten[frage_nummer][explanation_idx] = neue_erklaerung  # Update der Erklärung

        with open(dateiname, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(daten)

        print("\n>> Erklärung wurde erfolgreich in der CSV-Datei aktualisiert.")
        return True
    except Exception as e:
        print(f"\n>> FEHLER beim Aktualisieren der CSV-Datei: {e}")
        return False

def lese_mehrzeilige_eingabe():
    """Erlaubt es dem User, eine mehrzeilige Eingabe zu machen, bis 'ENDE' eingetippt wird."""
    print("Gib die neue Erklärung ein (mehrzeilig möglich).")
    print("Tippe 'ENDE' in eine neue, leere Zeile und drücke Enter, um die Eingabe abzuschließen.")
    zeilen = []
    while True:
        try:
            zeile = input()
            if zeile.strip().upper() == 'ENDE':
                break
            zeilen.append(zeile)
        except EOFError:
            break
    return "\n".join(zeilen)

def get_naechste_wiederholungsnummer(basename):
    """
    Erzeugt einen neuen Dateinamen mit fortlaufender Nummer für Wiederholungsprotokolle,
    damit vorherige Ergebnisse nicht überschrieben werden.
    """
    i = 1
    while True:
        dateiname = f"{basename}_Whd_{i}.txt"
        if not os.path.exists(dateiname):
            return dateiname
        i += 1

def schreibe_log_datei(protokoll, punkte, anzahl_fragen, einstellungen):
    """
    Protokolliert die Ergebnisse der Prüfungsrunde, inklusive Fragen, Antworten und Erklärung.
    Speichert alles in einer neuen Textdatei.
    """
    jetzt = datetime.datetime.now()
    datums_str = jetzt.strftime("%y%m%d")
    basename = ""
    dateiname = ""
    seed = einstellungen.get('seed')

    if einstellungen['methode'] == 'sorted':
        start, ende = einstellungen['start_nr'], einstellungen['start_nr'] + einstellungen['anzahl'] - 1
        basename = f"Result_{datums_str}_{start}-{ende}"
    elif einstellungen['methode'] == 'random':
        basename = f"Result_{datums_str}_Random_{seed}" if seed else f"Result_{datums_str}_Random"
    else:
        original_methode = einstellungen.get('original_methode', 'sorted')
        if original_methode == 'random':
            basename = f"Result_{datums_str}_Random_{seed}" if seed else f"Result_{datums_str}_Random"
        else:
            start, ende = einstellungen['start_nr'], einstellungen['start_nr'] + einstellungen['anzahl'] - 1
            basename = f"Result_{datums_str}_{start}-{ende}"
        dateiname = get_naechste_wiederholungsnummer(basename)
    if einstellungen['methode'] != 'last_test':
        dateiname = f"{basename}.txt"

    with open(dateiname, 'w', encoding='utf-8') as f:
        f.write("=" * 50 + "\n### Prüfungsprotokoll ###\n")
        f.write(f"Datum: {jetzt.strftime('%d.%m.%Y, %H:%M:%S Uhr')}\n")
        f.write(f"Modus: {einstellungen['modus'].capitalize()}\n")
        methode_fuer_log = einstellungen['methode']
        if methode_fuer_log == 'last_test':
            methode_fuer_log = f"Wiederholung ({einstellungen.get('original_methode', '')})"
        f.write(f"Auswahl: {methode_fuer_log.capitalize()} ({einstellungen['anzahl']} Fragen)\n")
        if (einstellungen['methode'] == 'random' or einstellungen.get('original_methode') == 'random') and seed:
            f.write(f"Random Seed: {seed}\n")

        f.write("\n--- Endergebnis ---\n")
        f.write(f"Punkte: {punkte} von {anzahl_fragen}\n")
        prozent = (punkte / anzahl_fragen) * 100 if anzahl_fragen > 0 else 0
        f.write(f"Erfolgsquote: {prozent:.2f}%\n" + "=" * 50 + "\n\n")

        # Für jede Frage schreibt das Protokoll die Details
        for eintrag in protokoll:
            obj = eintrag["frage_objekt"]
            status = "Richtig" if eintrag["ist_korrekt"] else "Falsch"
            f.write(f"--- Frage Nr. {obj['nummer']} ({status}) ---\n")
            f.write(f"Frage: {obj['frage']}\n")
            f.write(f"Deine Antwort:     {', '.join(eintrag['deine_antwort'])}\n")
            f.write(f"Korrekte Antwort:  {', '.join(eintrag['korrekte_antwort'])}\n\n")
            f.write("Erklärung:\n" + obj['erklaerung'] + "\n" + "-" * 50 + "\n\n")
    print(f"\nEin detailliertes Protokoll wurde in der Datei '{dateiname}' gespeichert.")

def starte_pruefung(fragen, einstellungen, dateiname):
    """
    Führt die eigentliche Prüfungsschleife durch:
    * Fragt jede Frage ab
    * Vergleicht gegen richtige Antwort(en)
    * Gibt Feedback & Noten, optional sofort oder am Ende.
    """
    punkte = 0
    protokoll = []
    print(f"\n--- Prüfung im '{einstellungen['modus'].upper()}' Modus startet! Es gibt {len(fragen)} Fragen. ---")

    for i, frage_objekt in enumerate(fragen):
        print("\n" + "=" * 50 + f"\n{BOLD}Frage {i + 1} von {len(fragen)} (Original-Nr. {frage_objekt['nummer']}):{RESET}")
        print(frage_objekt['frage'] + "\n" + "-" * 20)
        # Fragen und Antwortoptionen anzeigen
        buchstaben_optionen = list(string.ascii_uppercase)[:len(frage_objekt['optionen'])]
        for buchstabe, option in zip(buchstaben_optionen, frage_objekt['optionen']):
            print(f"  {buchstabe}) {option}")
        print("-" * 20)

        user_auswahl = []
        for attempt in range(3):
            hinweis = " (Mehrfachauswahl, z.B. A, C): " if frage_objekt['typ'] == 'multi-select' else " (Eine Auswahl): "
            user_antwort_str = input(f"Deine Antwort{hinweis}").upper()
            cleaned_input_for_validation = user_antwort_str.replace(" ", "").replace(",", "")
            allowed_chars_for_validation = "".join(buchstaben_optionen)
            if all(char in allowed_chars_for_validation for char in cleaned_input_for_validation):
                user_auswahl = sorted([s.strip() for s in user_antwort_str.split(',') if s.strip()])
                break
            else:
                remaining_attempts = 2 - attempt
                if remaining_attempts > 0:
                    print(f"!! Ungültige Eingabe. Bitte nur Buchstaben von A bis {buchstaben_optionen[-1]} und Kommas verwenden. Du hast noch {remaining_attempts} Versuch(e).")
                else:
                    print("!! Zu viele ungültige Eingaben. Die Antwort wird als falsch gewertet.")

        korrekte_buchstaben = sorted([buchstaben_optionen[int(idx) - 1] for idx in frage_objekt['korrekt']])
        ist_korrekt = (user_auswahl == korrekte_buchstaben)
        protokoll.append({
            "frage_objekt": frage_objekt, "deine_antwort": user_auswahl,
            "korrekte_antwort": korrekte_buchstaben, "ist_korrekt": ist_korrekt
        })

        # Benutzer-Feedback anzeigen
        if ist_korrekt:
            punkte += 1
            if einstellungen['modus'] == "practice":
                print("✅ Richtig!")
        else:
            if einstellungen['modus'] == "practice":
                print(f"❌ Falsch. Richtig wäre: {BOLD}{', '.join(korrekte_buchstaben)}{RESET}")
        if einstellungen['modus'] == "practice":
            print(f"\n--- Erklärung ---\n{ITALIC}" + frage_objekt['erklaerung'] + f"{RESET}")
            while True:
                aktion = input("\nDrücke 'c' zum Ändern der Erklärung, oder Enter zum Fortfahren: ").lower()
                if aktion == 'c':
                    neue_erklaerung = lese_mehrzeilige_eingabe()
                    if aktualisiere_erklaerung_in_csv(dateiname, frage_objekt['nummer'], neue_erklaerung):
                        frage_objekt['erklaerung'] = neue_erklaerung
                elif aktion == '':
                    break
        else:
            print("... Antwort gespeichert.")

    print("\n" + "#" * 50 + "\n### Prüfung beendet! ###")
    print(f"Dein Ergebnis: {punkte} von {len(fragen)} Punkten.")
    prozent = (punkte / len(fragen)) * 100 if len(fragen) > 0 else 0
    print(f"Das entspricht einer Erfolgsquote von {prozent:.2f}%.\n" + "#" * 50)

    # Bei "exam"-Modus: Übersicht zu falschen Antworten anzeigen
    if einstellungen['modus'] == "exam":
        falsche_antworten = [p for p in protokoll if not p["ist_korrekt"]]
        if falsche_antworten:
            print("\n\n--- Überprüfung der falschen Antworten ---")
            for fehler in falsche_antworten:
                obj = fehler["frage_objekt"]
                print("\n" + "=" * 50 + f"\n{BOLD}FRAGE (Nr. {obj['nummer']}):{RESET} {obj['frage']}")
                # Antwortoptionen anzeigen
                buchstaben_fuer_optionen = list(string.ascii_uppercase)[:len(obj['optionen'])]
                for buchstabe, option in zip(buchstaben_fuer_optionen, obj['optionen']):
                    print(f"  {buchstabe}) {option}")
                print("-" * 20)
                print(f"  Deine Antwort:     {BOLD}{', '.join(fehler['deine_antwort'])}{RESET}")
                print(f"  Korrekte Antwort:  {BOLD}{', '.join(fehler['korrekte_antwort'])}{RESET}")
                print(f"\n  {BOLD}Erklärung:{RESET}\n{ITALIC}" + obj['erklaerung'] + f"{RESET}")
        else:
            print("\n🎉 Herzlichen Glückwunsch! Alle Fragen wurden richtig beantwortet! 🎉")
    schreibe_log_datei(protokoll, punkte, len(fragen), einstellungen)
    return punkte

if __name__ == "__main__":
    os.system('')  # Terminal-Fähigkeiten auf Windows aktivieren
    dateiname = FRAGEN_DATEI
    print("--- Willkommen zum Snowflake-Prüfungssimulator ---")
    alle_fragen = lade_fragen_aus_csv(dateiname)

    if not alle_fragen:
        print("\nProgramm wird beendet.")
    else:
        max_fragen = len(alle_fragen)
        einstellungen = {}
        letzte_einstellungen = lade_letzte_einstellungen()

        # Wiederholungsfunktion, falls letzte Einstellungen gespeichert sind
        if letzte_einstellungen:
            score_text = ""
            if 'letzter_score' in letzte_einstellungen:
                score = letzte_einstellungen['letzter_score']
                score_text = f" (Dein letztes Ergebnis: {score['punkte']}/{score['anzahl']})"
            wahl = input(f"Möchtest du die letzte Prüfung wiederholen?{score_text} (j/n): ").lower()
            if wahl == 'j':
                einstellungen = letzte_einstellungen
                einstellungen['original_methode'] = einstellungen['methode']
                einstellungen['methode'] = 'last_test'

        # Einstellungen definieren
        if not einstellungen:
            while True:
                methode_wahl = input("\nWie sollen die Fragen ausgewählt werden?\n  1) Sorted (aus einer Spanne)\n  2) Random\nWahl: ")
                if methode_wahl == "1": einstellungen['methode'] = 'sorted'; break
                elif methode_wahl == "2": einstellungen['methode'] = 'random'; break
                else: print("Ungültige Wahl.")
            while True:
                modus_wahl = input("\nWähle einen Modus:\n  1) Practice (Feedback nach jeder Frage)\n  2) Exam (Auswertung am Ende)\nWahl: ")
                if modus_wahl == "1": einstellungen['modus'] = 'practice'; break
                elif modus_wahl == "2": einstellungen['modus'] = 'exam'; break
                else: print("Ungültige Wahl.")
            while True:
                try:
                    anzahl_str = input(f"\nWie viele Fragen möchtest du? (Enter für alle {max_fragen}): ")
                    einstellungen['anzahl'] = int(anzahl_str) if anzahl_str else max_fragen
                    if 0 < einstellungen['anzahl'] <= max_fragen: break
                    else: print(f"Bitte eine Zahl zwischen 1 und {max_fragen} eingeben.")
                except ValueError: print("Ungültige Eingabe.")
            einstellungen['seed'] = None
            if einstellungen['methode'] == 'sorted':
                max_start = max_fragen - einstellungen['anzahl'] + 1
                while True:
                    try:
                        start_nr = int(input(f"Gib die Start-Nummer an (1 bis {max_start}): "))
                        if 1 <= start_nr <= max_start:
                            einstellungen['start_nr'] = start_nr; break
                        else: print(f"Start-Nummer muss zwischen 1 und {max_start} liegen.")
                    except ValueError: print("Ungültige Zahl.")
            elif einstellungen['methode'] == 'random':
                seed_input = input("Gib einen Seed (Zahl oder Text) ein (Enter für zufällig): ")
                if seed_input: einstellungen['seed'] = seed_input

        seed = einstellungen.get('seed')
        if seed:
            random.seed(seed)

        # Fragen für diese Runde wählen
        if einstellungen.get('original_methode', einstellungen['methode']) == 'sorted':
            start_index = einstellungen['start_nr'] - 1
            fragen_fuer_runde = alle_fragen[start_index : start_index + einstellungen['anzahl']]
        else:
            random.shuffle(alle_fragen)
            fragen_fuer_runde = alle_fragen[:einstellungen['anzahl']]

        punkte = starte_pruefung(fragen_fuer_runde, einstellungen, dateiname)
        einstellungen['letzter_score'] = {'punkte': punkte, 'anzahl': len(fragen_fuer_runde)}
        if einstellungen.get('original_methode'):
            einstellungen['methode'] = einstellungen['original_methode']
            del einstellungen['original_methode']

        speichere_letzte_einstellungen(einstellungen)

    input("\nDrücke Enter, um das Programm zu schließen.")
