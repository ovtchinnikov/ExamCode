# Prüfungssimulator Python Script

## Übersicht

Dieses Python-Programm ist ein flexibler Prüfungs- und Quiz-Simulator, der Multiple-Choice- und Mehrfachauswahl-Fragen aus einer CSV-Datei einliest und interaktiv im Terminal abfragt. Es unterstützt sowohl Übungs- („practice“) als auch Prüfungsmodus („exam“) und bietet Feedback, Auswertung und ausführliche Protokolle.

Das Programm ist universell einsetzbar für beliebige Prüfungsinhalte, beispielhaft z. B. für Snowflake Core, aber auch für andere Examen und Themengebiete.

## Funktionsumfang

- Einlesen von Fragen aus einer CSV-Datei mit flexibler Anzahl von Antwortoptionen und mehreren korrekten Antworten.
- Validierung der Frageninhalte und aussagekräftige Warnungen bei fehlerhaften Daten.
- Auswahl der Fragen entweder sortiert aus einer definierten Spanne oder zufällig (mit optionalem Seed für Reproduzierbarkeit).
- Zwei Betriebsmodi:
  - **Practice**: Sofortige Rückmeldung nach jeder Frage inklusive detaillierter Erklärung und Möglichkeit, Erklärungen zu aktualisieren.
  - **Exam**: Bewertung erst am Ende mit Übersicht der falschen Antworten und deren Erklärungen.
- Eingabekontrolle für Antwortformate (Buchstaben, Mehrfachauswahl).
- Speicherung der letzten Testeinstellungen und Ergebnisse zur einfachen Wiederholung.
- Ausführliches Prüfungsprotokoll als Textdatei mit Datum, Modus, Punkten, ausgewählten Fragen und Erklärungen.
- Anpassbares Fragen-CSV-Format, um Prüfungen beliebiger Art und Themen abzudecken.

## Voraussetzungen

- Python 3.x (getestet mit Python 3.7+)
- Terminal, das ANSI-Escape-Codes für Textformatierung unterstützt (für bessere Lesbarkeit).
- CSV-Datei mit Fragen im korrekten Format (siehe unten).

## Verwendung

1. **Vorbereitung der Fragen-CSV**

   Erstelle oder bearbeite eine CSV-Datei mit mindestens folgenden Spalten:
   - `Question`: Die Prüfungsfrage.
   - `Question Type (multiple-choice or multi-select)`: Fragetyp, entweder `multiple-choice` (einzige Antwort) oder `multi-select` (mehrere Antworten).
   - `Answer Option 1` bis maximal `Answer Option 15`: Antwortoptionen.
   - `Correct Response`: Kommagetrennte Nummern der korrekten Antwortoptionen (z.B. `1` oder `1,3`).
   - `Explanation`: Freitext mit Erklärung zur Antwort (optional, kann später ergänzt werden).

2. **Start des Programms**

   Starte das Python-Skript im Terminal/Command Prompt:
    python3 ExamSim_v2.py

3. **Konfiguration**

- Wähle aus, ob du die letzte Prüfung wiederholen möchtest (falls vorhanden).
- Entscheide dich für die Fragenauswahl-Methode: sortierte Spanne oder zufällig mit Seed.
- Wähle den Modus: Practice (Feedback nach jeder Frage) oder Exam (Auswertung am Ende).
- Definiere wie viele Fragen du beantworten möchtest.
- Falls sortierte Auswahl, gib die Startnummer der Fragen-Spanne an.
- Falls zufällig, optional einen Seed zur Reproduzierbarkeit eingeben.

4. **Durchführung der Prüfung**

- Antworten werden per Buchstaben eingegeben (bei Mehrfachauswahl mehrere Buchstaben durch Komma getrennt).
- Nach jeder Frage wird je nach Modus Feedback und ggf. Erklärung oder nur Zwischenspeicherung gegeben.
- Im Practice-Modus kann die Erklärung jederzeit nachträglich editiert und in der CSV aktualisiert werden.

5. **Auswertung und Protokolle**

- Am Ende erfolgt eine Übersicht der erzielten Punkte und Erfolgsquote.
- Im Exam-Modus werden falsche Antworten mit Erklärung angezeigt.
- Ein detailliertes Protokoll wird automatisch als Textdatei mit Zeitstempel gespeichert.

## Anpassungen für andere Examen

Die Fragen-CSV kann beliebige Inhalte enthalten, nicht nur Snowflake Core. Wichtig ist nur die Einhaltung des Spaltenformats:

| Spalte                                              | Beschreibung                                          |
|-----------------------------------------------------|-------------------------------------------------------|
| `Question`                                          | Text der Frage                                        |
| `Question Type (multiple-choice or multi-select)`   | Fragetyp: `multiple-choice` oder `multi-select`       |
| `Answer Option 1` ... `Answer Option 15`            | Antwortmöglichkeiten (beliebig viele bis 15)          |
| `Correct Response`                                  | Nummer(n) der richtigen Antwort(en), z.B. `1`, `2,4`  |
| `Explanation`                                       | Erklärung oder Lösungsbeschreibung                    |

So kann das Programm flexibel für Quiz, Prüfungen oder Schulungen eingesetzt werden.

## Dateistruktur

- `questions.csv` - Standarddateiname für Fragen, kann aber angepasst werden.
- `last_test_settings.json` - Speichert zuletzt genutzte Einstellungen und Ergebnisse.
- Ergebnisdateien `Result_YYMMDD_xxx.txt` - Protokolle mit Prüfungsergebnissen.

## Hinweise

- Die Konsole sollte UTF-8 und ANSI-Farbcodes unterstützen für optimale Anzeige.
- Fehlerhafte oder unvollständige Fragen in der CSV werden beim Laden übersprungen.
- Bitte vor Teststart Sicherungskopien der CSV erstellen, wenn Erklärungen editiert werden sollen.

## Lizenz & Kontakt

Open Source / frei nutzbar. Für Rückfragen oder Erweiterungen melden Sie sich gern bei Daniel Ovtchinnikov.
