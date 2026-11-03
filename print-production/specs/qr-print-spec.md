# QR-Code Druckspezifikation

## Mindestgröße und Platzierung

Der QR-Code auf jeder Karte hat eine Mindestgröße von **15×15 mm** im Fertigformat. Die empfohlene Größe beträgt 18×18 mm. Der QR-Code wird in der unteren rechten Ecke der Karte platziert, innerhalb der Sicherheitszone (mindestens 5 mm Abstand zur Schnittlinie). Ein Quiet-Zone-Abstand von mindestens **4 Modulen** (das entspricht 4 hellen Zellen am Rand des QR-Codes) muss eingehalten werden.

## Auflösung und Farbe

QR-Codes werden in **Schwarz auf Weiß** gedruckt. Eine Farbumkehr (weißer QR-Code auf dunklem Hintergrund) ist nicht erlaubt, da viele Scanner damit Probleme haben. Die Mindestauflösung für den QR-Code beträgt **300 dpi**; **600 dpi** wird empfohlen. Der QR-Code wird als Vektorgrafik (SVG oder eingebetteter Vektorpfad in PDF) geliefert, um Unschärfen durch Pixelierung zu vermeiden.

## Fehlerkorrektur und Testpflicht

Das Mindest-Fehlerkorrekturlevel ist **Level M** (15 % Wiederherstellungskapazität); **Level Q** (25 %) wird empfohlen, um die Lesbarkeit auch bei leichter Beschädigung der Karte sicherzustellen. Vor jedem Druckauftrag muss ein Testscan mit mindestens drei verschiedenen Scanner-Apps (z. B. iOS-Kamera, Android-Kamera, separater QR-Scanner) durchgeführt werden. Der Test muss bei unterschiedlichen Lichtsitu­ationen und mit einem Abstand von mindestens 20 cm erfolgen.

## QR-Redirect-URL

Die im QR-Code kodierte URL lautet: `https://chembiomed-cards.de/c/<card-id>`, z. B. `https://chembiomed-cards.de/c/oc-012`. Diese URL ist dauerhaft und darf nie geändert werden. Der QR-Code-Inhalt wird vor Produktionsstart anhand der finalen Karten-IDs aus dem Kartenregister (cards.master.csv) generiert.

## Modul PH: Verknüpfungsstandard QR → WikiMedica (v0.2)

Für Pharma Cards (Modul PH) gilt ab 2026-10-31 abweichend vom Abschnitt „QR-Redirect-URL“ und
von „Schwarz auf Weiß“ der Verknüpfungsstandard v0.2 (Entscheidung Andreas Tremml):

| Punkt | Vorgabe |
|---|---|
| Ziel Wirkstoffkarten | `https://at-medical.de/w/wirkstoff/<wirkstoff_slug>` |
| Ziel übrige Karten | `https://at-medical.de/w/begriff/<begriff_slug>`, auch Wirkstoffgruppen (`front_type: drug_class`) |
| Slug-Regel | Kleinschreibung, ä→ae, ö→oe, ü→ue, ß→ss, Klammerzusätze weg, griechische Buchstaben ausgeschrieben, sonst Bindestrich; deutsche INN |
| Pflege | Slug-Feld in der Karten-YAML; `qr_url` wird mit `make ph-qr-sync` daraus erzeugt, der Validator prüft die Übereinstimmung |
| Größe | Code ≥ 15 × 15 mm plus 4 Module Ruhezone (gesamt ca. 18–19 mm); darunter Bezeichnung und Kurz-URL im Klartext |
| Farbe / Korrektur | #0b4f8a auf Weiß, Fehlerkorrektur M, kein Logo im Code |
| Platzierung | Vorderseite rechts unten, innerhalb der 5-mm-Sicherheitszone |

Maßgeblich für die Slugs ist das zentrale Linkregister. Ab 2026-11-01 gleicht eine tägliche
Prüfung auf ATMED-core die `qr_url` aller PH-Karten dagegen ab. **Gedruckt wird erst, wenn die
Weiterleitung `/w/` live ist.** Die Scanner-Testpflicht oben gilt unverändert.
