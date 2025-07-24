import csv
import random
import os
import string
import datetime
import json

#sinnvoller Kommentar für git

EINSTELLUNGEN_DATEI = "last_test_settings.json"

def lade_letzte_einstellungen():
    """Lädt die letzten Testeinstellungen aus einer JSON-Datei."""
    if os.path.exists(EINSTELLUNGEN_DATEI):
        with open(EINSTELLUNGEN_DATEI, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def speichere_letzte_einstellungen(einstellungen):
    """Speichert die aktuellen Testeinstellungen in einer JSON-Datei."""
    with open(EINSTELLUNGEN_DATEI, 'w', encoding='utf-8') as f:
        json.dump(einstellungen, f, indent=4)

def lade_fragen_aus_csv(dateipfad):
    """Lädt die Fragen aus der CSV-Datei und fügt die Original-Zeilennummer hinzu."""
    fragen_liste = []
    if not os.path.exists(dateipfad):
        print(f"FEHLER: Die Datei '{dateipfad}' wurde nicht gefunden.")
        return []
    try:
        with open(dateipfad, mode='r', encoding='utf-8') as csv_datei:
            csv_leser = csv.DictReader(csv_datei)
            for i, zeile in enumerate(csv_leser):
                if zeile.get('Question') == 'Question' or not zeile.get('Question'):
                    continue
                optionen = [zeile[f"Answer Option {j}"].strip() for j in range(1, 16) if zeile.get(f"Answer Option {j}") and zeile[f"Answer Option {j}"].strip()]
                korrekte_antworten = [s.strip() for s in zeile.get('Correct Response', '').split(',')]
                fragen_liste.append({
                    "nummer": i + 1,
                    "frage": zeile['Question'].strip(),
                    "typ": zeile['Question Type (multiple-choice or multi-select)'].strip(),
                    "optionen": optionen,
                    "korrekt": korrekte_antworten,
                    "erklaerung": zeile.get('Explanation', 'Keine Erklärung verfügbar.').strip()
                })
    except Exception as e:
        print(f"FEHLER beim Lesen der Datei: {e}")
    return fragen_liste

def aktualisiere_erklaerung_in_csv(dateiname, frage_nummer, neue_erklaerung):
    """Liest die gesamte CSV, ändert eine Erklärung und schreibt die Datei neu."""
    try:
        with open(dateiname, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            daten = list(reader)
        
        header = daten[0]
        if 'Explanation' not in header:
            print("FEHLER: Spalte 'Explanation' nicht in der CSV gefunden.")
            return False
        explanation_idx = header.index('Explanation')
        
        daten[frage_nummer][explanation_idx] = neue_erklaerung

        with open(dateiname, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(daten)
        
        print("\n>> Erklärung wurde erfolgreich in der CSV-Datei aktualisiert.")
        return True
    except Exception as e:
        print(f"\n>> FEHLER beim Aktualisieren der CSV-Datei: {e}")
        return False

def lese_mehrzeilige_eingabe():
    """Liest eine mehrzeilige Eingabe, bis 'ENDE' in einer neuen Zeile eingegeben wird."""
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
    """Findet die nächste verfügbare Wiederholungsnummer für einen Dateinamen."""
    i = 1
    while True:
        dateiname = f"{basename}_Whd_{i}.txt"
        if not os.path.exists(dateiname):
            return dateiname
        i += 1

def schreibe_log_datei(protokoll, punkte, anzahl_fragen, einstellungen):
    """Schreibt ein detailliertes Protokoll mit dynamischem Dateinamen."""
    jetzt = datetime.datetime.now()
    datums_str = jetzt.strftime("%y%m%d")
    
    basename = ""
    dateiname = ""
    seed = einstellungen.get('seed')

    if einstellungen['methode'] == 'sorted':
        start, ende = einstellungen['start_nr'], einstellungen['start_nr'] + einstellungen['anzahl'] - 1
        basename = f"Result_{datums_str}_{start}-{ende}"
    elif einstellungen['methode'] == 'random':
        # GEÄNDERT: Seed an den Dateinamen anhängen, falls vorhanden
        basename = f"Result_{datums_str}_Random_{seed}" if seed else f"Result_{datums_str}_Random"
    else:  # last_test
        original_methode = einstellungen.get('original_methode', 'sorted')
        if original_methode == 'random':
            # GEÄNDERT: Seed auch bei Wiederholungen an den Dateinamen anhängen
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
    """Führt die Prüfung durch und gibt den erreichten Punktestand zurück."""
    punkte = 0
    protokoll = []
    print(f"\n--- Prüfung im '{einstellungen['modus'].upper()}' Modus startet! Es gibt {len(fragen)} Fragen. ---")

    for i, frage_objekt in enumerate(fragen):
        print("\n" + "=" * 50 + f"\nFrage {i + 1} von {len(fragen)} (Original-Nr. {frage_objekt['nummer']}):")
        print(frage_objekt['frage'] + "\n" + "-" * 20)
        
        buchstaben_optionen = list(string.ascii_uppercase)[:len(frage_objekt['optionen'])]
        for buchstabe, option in zip(buchstaben_optionen, frage_objekt['optionen']):
            print(f"  {buchstabe}) {option}")
        
        hinweis = " (Mehrfachauswahl, z.B. A, C): " if frage_objekt['typ'] == 'multi-select' else " (Eine Auswahl): "
        user_antwort_str = input(f"Deine Antwort{hinweis}").upper()
        user_auswahl = sorted([s.strip() for s in user_antwort_str.split(',')])
        korrekte_buchstaben = sorted([buchstaben_optionen[int(idx) - 1] for idx in frage_objekt['korrekt']])
        
        ist_korrekt = (user_auswahl == korrekte_buchstaben)
        protokoll.append({
            "frage_objekt": frage_objekt,
            "deine_antwort": user_auswahl,
            "korrekte_antwort": korrekte_buchstaben,
            "ist_korrekt": ist_korrekt
        })

        if ist_korrekt:
            punkte += 1
            if einstellungen['modus'] == "practice":
                print("✅ Richtig!")
        else:
            if einstellungen['modus'] == "practice":
                print(f"❌ Falsch. Richtig wäre: {', '.join(korrekte_buchstaben)}")
        
        if einstellungen['modus'] == "practice":
            print("\n--- Erklärung ---\n" + frage_objekt['erklaerung'])
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

    if einstellungen['modus'] == "exam":
        falsche_antworten = [p for p in protokoll if not p["ist_korrekt"]]
        if falsche_antworten:
            print("\n\n--- Überprüfung der falschen Antworten ---")
            for fehler in falsche_antworten:
                obj = fehler["frage_objekt"]
                print("\n" + "=" * 50 + f"\nFRAGE (Nr. {obj['nummer']}): {obj['frage']}")
                print(f"  Deine Antwort:     {', '.join(fehler['deine_antwort'])}")
                print(f"  Korrekte Antwort:  {', '.join(fehler['korrekte_antwort'])}")
                print("\n  Erklärung:\n" + obj['erklaerung'])
        else:
            print("\n🎉 Herzlichen Glückwunsch! Alle Fragen wurden richtig beantwortet! 🎉")
    
    schreibe_log_datei(protokoll, punkte, len(fragen), einstellungen)
    return punkte

if __name__ == "__main__":
    dateiname = "questions.csv"
    print("--- Willkommen zum Snowflake-Prüfungssimulator ---")
    alle_fragen = lade_fragen_aus_csv(dateiname)
    
    if not alle_fragen:
        print("\nProgramm wird beendet.")
    else:
        max_fragen = len(alle_fragen)
        einstellungen = {}
        letzte_einstellungen = lade_letzte_einstellungen()

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

        if not einstellungen:
            while True:
                methode_wahl = input("\nWie sollen die Fragen ausgewählt werden?\n  1) Sorted (aus einer Spanne)\n  2) Random\nWahl: ")
                if methode_wahl == "1":
                    einstellungen['methode'] = 'sorted'
                    break
                elif methode_wahl == "2":
                    einstellungen['methode'] = 'random'
                    break
                else:
                    print("Ungültige Wahl.")
            
            while True:
                modus_wahl = input("\nWähle einen Modus:\n  1) Practice (Feedback nach jeder Frage)\n  2) Exam (Auswertung am Ende)\nWahl: ")
                if modus_wahl == "1":
                    einstellungen['modus'] = 'practice'
                    break
                elif modus_wahl == "2":
                    einstellungen['modus'] = 'exam'
                    break
                else:
                    print("Ungültige Wahl.")

            while True:
                try:
                    anzahl_str = input(f"\nWie viele Fragen möchtest du? (Enter für alle {max_fragen}): ")
                    einstellungen['anzahl'] = int(anzahl_str) if anzahl_str else max_fragen
                    if 0 < einstellungen['anzahl'] <= max_fragen:
                        break
                    else:
                        print(f"Bitte eine Zahl zwischen 1 und {max_fragen} eingeben.")
                except ValueError:
                    print("Ungültige Eingabe.")

            einstellungen['seed'] = None
            if einstellungen['methode'] == 'sorted':
                max_start = max_fragen - einstellungen['anzahl'] + 1
                while True:
                    try:
                        start_nr = int(input(f"Gib die Start-Nummer an (1 bis {max_start}): "))
                        if 1 <= start_nr <= max_start:
                            einstellungen['start_nr'] = start_nr
                            break
                        else:
                            print(f"Start-Nummer muss zwischen 1 und {max_start} liegen.")
                    except ValueError:
                        print("Ungültige Zahl.")
            elif einstellungen['methode'] == 'random':
                seed_input = input("Gib einen Seed (Zahl oder Text) ein (Enter für zufällig): ")
                if seed_input:
                    einstellungen['seed'] = seed_input

        seed = einstellungen.get('seed')
        if seed:
            random.seed(seed)

        if einstellungen.get('original_methode', einstellungen['methode']) == 'sorted':
            start_index = einstellungen['start_nr'] - 1
            fragen_fuer_runde = alle_fragen[start_index : start_index + einstellungen['anzahl']]
        else:  # random
            random.shuffle(alle_fragen)
            fragen_fuer_runde = alle_fragen[:einstellungen['anzahl']]
        
        punkte = starte_pruefung(fragen_fuer_runde, einstellungen, dateiname)
        
        if einstellungen['methode'] != 'last_test':
            einstellungen['letzter_score'] = {'punkte': punkte, 'anzahl': len(fragen_fuer_runde)}
            speichere_letzte_einstellungen(einstellungen)

    input("\nDrücke Enter, um das Programm zu schließen.")