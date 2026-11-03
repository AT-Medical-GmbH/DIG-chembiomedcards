# ChemBioMed Cards – Masterverzeichnis

**Projekt:** ChemBioMed Cards  
**Betreiber:** AT Medical GmbH  
**Stand:** 2026-05-16  
**Status:** Planungs- und Produktionsverzeichnis

Dieses Dokument ist das zentrale, lesbare Masterverzeichnis der geplanten Lernkarten. Es ergänzt die maschinenlesbare Registry `cards.master.csv` und dient als fachliches Produktionsverzeichnis für Redaktion, Layout, Review, Printproduktion und Onlineplattform.

## Gesamtumfang

| Bereich | Bezeichnung | Zielumfang |
|---|---|---:|
| AC | Allgemeine und anorganische Chemie | 220 Karten |
| OC | Organische Chemie | 230 Karten |
| BC | Biochemie | 320 Karten |
| MB | Molekularbiologie der Zelle | 180 Karten |
| APC | Angewandte Chemie, Ernährung & Medizin | 260 Karten |
| PH | Pharmakologie | 242 Karten |
| **Gesamt** |  | **1.452 Karten** |

## Einheitliches Kartenschema

| Feld | Bedeutung |
|---|---|
| `card_id` | eindeutige Kartennummer, z. B. `oc_012` |
| `slug` | eindeutiger Dateiname ohne Front-/Back-Suffix, z. B. `oc_012_primaerer_alkohol` |
| `module` | Hauptbereich: AC, OC, BC, MB, APC, PH |
| `chapter` | fachliches Unterkapitel |
| `card_type` | Strukturkarte, Reaktionskarte, Vergleichskarte, Übersichtskarte, Klinik-/Fallkarte |
| `level` | Grundlagen, Intermediate, Advanced, Clinical |
| `front_asset` | Pfad zur Vorderseite |
| `back_asset` | Pfad zur Rückseite |
| `qr_url` | stabile QR-/Redirect-URL |
| `lms_url` | Ziel für ausführliche Vertiefung im LMS |
| `print_status` | Produktionsstatus Print |
| `web_status` | Produktionsstatus Online |
| `review_status` | fachlicher Reviewstatus |

## Dateilogik

Beispiel für Karte `oc_012`:

```text
card_id: oc_012
slug: oc_012_primaerer_alkohol
front_asset: cards/OC/front/oc_012_primaerer_alkohol_front.png
back_asset: cards/OC/back/oc_012_primaerer_alkohol_back.png
qr_url: https://chembiomed-cards.de/c/oc012
lms_url: https://learn.at-medical.de/chembiomed/oc/oc_012_primaerer_alkohol
```

---

# AC – Allgemeine und anorganische Chemie

Zielumfang: **220 Karten**

## AC-01 Grundlagen der Materie

| ID | Slug / Dateiname | Titel | Typ | Niveau |
|---|---|---|---|---|
| `ac_001` | `ac_001_atomaufbau` | Atomaufbau | structure | grundlagen |
| `ac_002` | `ac_002_proton_neutron_elektron` | Proton, Neutron, Elektron | structure | grundlagen |
| `ac_003` | `ac_003_ordnungszahl_massenzahl_und_isotope` | Ordnungszahl, Massenzahl und Isotope | structure | grundlagen |
| `ac_004` | `ac_004_isotope_in_medizin_und_diagnostik` | Isotope in Medizin und Diagnostik | clinical | intermediate |
| `ac_005` | `ac_005_elektronenhuelle_und_orbitale` | Elektronenhülle und Orbitale | structure | grundlagen |
| `ac_006` | `ac_006_elektronenkonfiguration` | Elektronenkonfiguration | overview | grundlagen |
| `ac_007` | `ac_007_valenzelektronen` | Valenzelektronen | structure | grundlagen |
| `ac_008` | `ac_008_periodensystem_ueberblick` | Periodensystem – Überblick | overview | grundlagen |
| `ac_009` | `ac_009_hauptgruppen_und_nebengruppen` | Hauptgruppen und Nebengruppen | overview | grundlagen |
| `ac_010` | `ac_010_metalle_nichtmetalle_halbmetalle` | Metalle, Nichtmetalle, Halbmetalle | comparison | grundlagen |

## AC-02 Periodische Trends

| ID | Slug / Dateiname | Titel | Typ | Niveau |
|---|---|---|---|---|
| `ac_011` | `ac_011_atomradius` | Atomradius | overview | grundlagen |
| `ac_012` | `ac_012_ionisierungsenergie` | Ionisierungsenergie | overview | grundlagen |
| `ac_013` | `ac_013_elektronegativitaet` | Elektronegativität | overview | grundlagen |
| `ac_014` | `ac_014_elektronenaffinitaet` | Elektronenaffinität | overview | grundlagen |
| `ac_015` | `ac_015_metallcharakter` | Metallcharakter | overview | grundlagen |
| `ac_016` | `ac_016_periodische_trends_gesamt` | Periodische Trends im Überblick | overview | grundlagen |
| `ac_017` | `ac_017_bedeutung_elektronegativitaet_bindung` | Elektronegativität und Bindungstyp | comparison | intermediate |
| `ac_018` | `ac_018_ionenbildung` | Ionenbildung | structure | grundlagen |

## AC-03 bis AC-18 – weitere AC-Module

Die vollständige AC-Planung umfasst zusätzlich:

- Chemische Bindungen
- Molekülgeometrie und Ladung
- Stoffmenge, Konzentration und Lösungen
- Säuren, Basen und pH
- Redoxchemie
- Elektrolyte und medizinisch relevante Ionen
- Komplexchemie und Koordination
- Reaktionskinetik und Gleichgewicht
- Gase, Diffusion und medizinische Relevanz
- Thermodynamik und Energie
- Elektrochemie
- Analytische Chemie
- Radioaktivität und medizinische Physik-Chemie
- Materialchemie und Grenzflächen
- Laborpraxis und Sicherheit
- Umweltchemie und Alltag

---

# OC – Organische Chemie

Zielumfang: **230 Karten**

## OC-01 Kohlenwasserstoff-Grundgerüste

| ID | Slug / Dateiname | Titel | Typ | Niveau |
|---|---|---|---|---|
| `oc_001` | `oc_001_alkan` | Alkan | structure | grundlagen |
| `oc_002` | `oc_002_alken` | Alken | structure | grundlagen |
| `oc_003` | `oc_003_alkin` | Alkin | structure | grundlagen |
| `oc_004` | `oc_004_aromat_arylgruppe` | Aromat / Arylgruppe | structure | grundlagen |
| `oc_005` | `oc_005_phenylgruppe` | Phenylgruppe | structure | grundlagen |
| `oc_006` | `oc_006_benzylgruppe` | Benzylgruppe | structure | grundlagen |
| `oc_007` | `oc_007_alkylgruppe` | Alkylgruppe | structure | grundlagen |
| `oc_008` | `oc_008_cycloalkan` | Cycloalkan | structure | grundlagen |
| `oc_009` | `oc_009_isomerie_kettenisomerie` | Kettenisomerie | overview | grundlagen |
| `oc_010` | `oc_010_cis_trans_isomerie` | cis/trans-Isomerie | comparison | intermediate |

## OC-02 Alkohole und Sauerstoffgruppen

| ID | Slug / Dateiname | Titel | Typ | Niveau |
|---|---|---|---|---|
| `oc_011` | `oc_011_alkohol_hydroxygruppe` | Alkohol / Hydroxygruppe | structure | grundlagen |
| `oc_012` | `oc_012_primaerer_alkohol` | Primärer Alkohol | structure | grundlagen |
| `oc_013` | `oc_013_sekundaerer_alkohol` | Sekundärer Alkohol | structure | grundlagen |
| `oc_014` | `oc_014_tertiaerer_alkohol` | Tertiärer Alkohol | structure | grundlagen |
| `oc_015` | `oc_015_einwertiger_alkohol` | Einwertiger Alkohol | structure | grundlagen |
| `oc_016` | `oc_016_zweiwertiger_alkohol_diol` | Zweiwertiger Alkohol / Diol | structure | grundlagen |
| `oc_017` | `oc_017_dreiwertiger_alkohol_triol` | Dreiwertiger Alkohol / Triol | structure | grundlagen |
| `oc_018` | `oc_018_polyol_mehrwertiger_alkohol` | Polyol / Mehrwertiger Alkohol | structure | grundlagen |
| `oc_019` | `oc_019_phenol` | Phenol | structure | grundlagen |
| `oc_020` | `oc_020_ether` | Ether | structure | grundlagen |
| `oc_021` | `oc_021_acetal` | Acetal | structure | intermediate |
| `oc_022` | `oc_022_hemiacetal` | Hemiacetal | structure | intermediate |
| `oc_023` | `oc_023_ketal` | Ketal | structure | intermediate |
| `oc_024` | `oc_024_hemiketal` | Hemiketal | structure | intermediate |

## OC-03 Carbonylchemie

| ID | Slug / Dateiname | Titel | Typ | Niveau |
|---|---|---|---|---|
| `oc_025` | `oc_025_carbonylgruppe` | Carbonylgruppe | structure | grundlagen |
| `oc_026` | `oc_026_aldehyd` | Aldehyd | structure | grundlagen |
| `oc_027` | `oc_027_keton` | Keton | structure | grundlagen |
| `oc_028` | `oc_028_chinon` | Chinon | structure | intermediate |
| `oc_029` | `oc_029_enol` | Enol | structure | intermediate |
| `oc_030` | `oc_030_enolat` | Enolat | structure | intermediate |
| `oc_031` | `oc_031_keto_enol_tautomerie` | Keto-Enol-Tautomerie | reaction | intermediate |

## OC-04 bis OC-18 – weitere OC-Module

Die vollständige OC-Planung umfasst zusätzlich:

- Carbonsäuren und Derivate
- Stickstoffgruppen
- Schwefel- und Phosphorgruppen
- Halogene und Spezialgruppen
- Organische Reaktionen
- Vergleichs- und Übersichtskarten
- Stereochemie
- Reaktionsmechanismen Grundlagen
- Substitution, Addition, Eliminierung
- Aromatenchemie
- Zuckerchemie organisch vertieft
- Lipidchemie organisch vertieft
- Arzneistoffchemie Basis
- Naturstoffchemie
- Polymere und Biomaterialien

## OC-Pilotset – verbindlicher Startblock

| ID | Slug / Dateiname | Titel | Typ | Niveau |
|---|---|---|---|---|
| `oc_012` | `oc_012_primaerer_alkohol` | Primärer Alkohol | structure | grundlagen |
| `oc_013` | `oc_013_sekundaerer_alkohol` | Sekundärer Alkohol | structure | grundlagen |
| `oc_014` | `oc_014_tertiaerer_alkohol` | Tertiärer Alkohol | structure | grundlagen |
| `oc_096` | `oc_096_primaer_sekundaer_tertiaer_alkohol` | Primärer, sekundärer und tertiärer Alkohol | comparison | grundlagen |
| `oc_071` | `oc_071_oxidation_primaerer_alkohol` | Oxidation primärer Alkohole | reaction | intermediate |
| `oc_073` | `oc_073_oxidation_sekundaerer_alkohol` | Oxidation sekundärer Alkohole | reaction | intermediate |
| `oc_075` | `oc_075_tertiaerer_alkohol_keine_einfache_oxidation` | Tertiäre Alkohole – keine einfache Oxidation | reaction | intermediate |
| `oc_026` | `oc_026_aldehyd` | Aldehyd | structure | grundlagen |
| `oc_027` | `oc_027_keton` | Keton | structure | grundlagen |
| `oc_099` | `oc_099_aldehyd_vs_keton` | Aldehyd vs. Keton | comparison | grundlagen |

---

# BC – Biochemie

Zielumfang: **320 Karten**

## BC-Kernmodule

Die Biochemie enthält:

- Wasser, Lösungen, Osmose und Körperflüssigkeiten
- Elektrolyte, Membranpotenzial und Erregbarkeit
- Säure-Basen-Haushalt und BGA
- Redox, Sauerstoff und mitochondriale Energie
- Kohlenhydrate und Glukosestoffwechsel
- Citratzyklus, Acetyl-CoA und zentrale Stoffwechselwege
- Lipide, Fettsäuren und Ketonkörper
- Aminosäuren, Proteine und Stickstoff
- Nukleinsäuren, Genetik und Molekularbiologie
- Enzyme, Kofaktoren und Vitamine
- Ernährung, Alltag und klinische Relevanz
- Laborwerte und Diagnostik
- hormonelle Regulation des Stoffwechsels
- Zellulärer Stress und Proteostase
- Immunmetabolismus und Entzündung
- Blut, Hämoglobin und Gerinnung
- Organbezogene Biochemie
- Vitamine und Mikronährstoffe vollständig
- Zelluläre Energie in Spezialzuständen
- Biochemische Methoden
- Biochemie der Zellalterung

## BC-Beispielanker

| ID | Slug / Dateiname | Titel | Typ | Niveau |
|---|---|---|---|---|
| `bc_001` | `bc_001_wasser_als_biologisches_loesungsmittel` | Wasser als biologisches Lösungsmittel | overview | grundlagen |
| `bc_025` | `bc_025_ph_wert_des_blutes` | pH-Wert des Blutes | clinical | intermediate |
| `bc_060` | `bc_060_glykolyse` | Glykolyse | overview | intermediate |
| `bc_073` | `bc_073_acetyl_coa` | Acetyl-CoA | structure | intermediate |
| `bc_097` | `bc_097_aminosaeure_grundstruktur` | Aminosäure-Grundstruktur | structure | grundlagen |
| `bc_188` | `bc_188_insulin_signalweg` | Insulin-Signalweg | overview | advanced |
| `bc_227` | `bc_227_haemoglobin_struktur` | Hämoglobin-Struktur | structure | intermediate |
| `bc_256` | `bc_256_vitamin_a` | Vitamin A | overview | grundlagen |
| `bc_293` | `bc_293_proteinbestimmung` | Proteinbestimmung | method | advanced |
| `bc_320` | `bc_320_rapamycin_mtor_aging` | Rapamycin, mTOR und Aging | clinical | advanced |

---

# MB – Molekularbiologie der Zelle

Zielumfang: **180 Karten**

## MB-Kernmodule

- Zellbiologische Grundlagen
- Zellmembran
- Membrantransport
- Signaltransduktion und Rezeptoren
- Zellkontakte und Barrieren
- Ernährung und Zellantwort
- Zellzyklus und Zellteilung
- DNA, Replikation und Reparatur
- Genexpression
- Epigenetik molekularbiologisch
- Zellkommunikation erweitert
- Zellorganellen vertieft
- Membrantransport klinisch-molekular
- Molekularbiologische Methoden

## MB-Beispielanker

| ID | Slug / Dateiname | Titel | Typ | Niveau |
|---|---|---|---|---|
| `mb_001` | `mb_001_die_zelle_als_organisationseinheit` | Die Zelle als Organisationseinheit | overview | grundlagen |
| `mb_011` | `mb_011_zellmembran_als_dynamische_grenzflaeche` | Zellmembran als dynamische Grenzfläche | structure | grundlagen |
| `mb_023` | `mb_023_membrantransport_ueberblick` | Membrantransport – Überblick | overview | grundlagen |
| `mb_040` | `mb_040_membran_als_plattform_fuer_rezeptoren` | Membran als Plattform für Rezeptoren | overview | intermediate |
| `mb_084` | `mb_084_dna_doppelhelix` | DNA-Doppelhelix | structure | grundlagen |
| `mb_101` | `mb_101_zentrales_dogma` | Zentrales Dogma | overview | grundlagen |
| `mb_119` | `mb_119_epigenetik_molekular` | Epigenetik molekular | overview | advanced |
| `mb_161` | `mb_161_pcr` | PCR | method | intermediate |
| `mb_180` | `mb_180_molekularbiologie_in_der_diagnostik` | Molekularbiologie in der Diagnostik | clinical | advanced |

---

# APC – Angewandte Chemie, Ernährung & Medizin

Zielumfang: **260 Karten**

## APC-Kernmodule

- Ernährung und Stoffwechsel im Alltag
- Nutrigenetik und Nutrigenomik
- Epigenetik und Lebensstil
- Gender Medicine und individuelle Unterschiede
- Mikrobiom, Darm und Immunstoffwechsel
- Pathophysiologie und klinische Anwendung
- Pharmakologie, Toxikologie und Alltag
- Lebensphasen und besondere Gruppen
- Gender Medicine erweitert
- Epigenetik und Prävention erweitert
- Personalisierte Ernährung und Beratung
- Ernährungsmedizinische Krankheitsbilder
- Intensivmedizin und Pflegepraxis
- Public Health, Prävention und Alltag
- Klinische Toxikologie erweitert
- Digitale und moderne Medizin
- Kommunikation, Ethik und Marktanwendung
- Fallkarten

## APC-Beispielanker

| ID | Slug / Dateiname | Titel | Typ | Niveau |
|---|---|---|---|---|
| `apc_001` | `apc_001_makronaehrstoffe_im_alltag` | Makronährstoffe im Alltag | overview | grundlagen |
| `apc_016` | `apc_016_nutrigenetik_grundprinzip` | Nutrigenetik – Grundprinzip | overview | intermediate |
| `apc_028` | `apc_028_epigenetik_grundlagen` | Epigenetik – Grundlagen | overview | intermediate |
| `apc_040` | `apc_040_gender_medicine_grundlagen` | Gender Medicine – Grundlagen | clinical | intermediate |
| `apc_054` | `apc_054_mikrobiom_grundlagen` | Mikrobiom – Grundlagen | overview | intermediate |
| `apc_065` | `apc_065_insulinresistenz` | Insulinresistenz | clinical | advanced |
| `apc_096` | `apc_096_kindheit_wachstum_stoffwechsel` | Kindheit: Wachstum und Stoffwechsel | clinical | intermediate |
| `apc_137` | `apc_137_personalisierte_ernaehrung` | Personalisierte Ernährung | clinical | advanced |
| `apc_169` | `apc_169_stressstoffwechsel_intensivmedizin` | Stressstoffwechsel in der Intensivmedizin | clinical | advanced |
| `apc_239` | `apc_239_fall_hypoglykaemie` | Fallkarte: Hypoglykämie | case | clinical |
| `apc_260` | `apc_260_fall_cgm_reaktive_hypoglykaemie` | Fallkarte: CGM und reaktive Hypoglykämie | case | clinical |

---

# PH – Pharmakologie

Zielumfang: **242 Karten**

PH ist als spätere eigene Produktlinie vorgesehen. Sie ist strukturell im Repository, in der Registry und in der Paketlogik vorbereitet, wird aber erst nach den Kernmodulen AC/OC/BC/MB/APC inhaltlich ausgebaut.

## PH-Kernmodule

- Allgemeine Pharmakologie
- Pharmakokinetik
- Pharmakodynamik
- Rezeptoren und Signalwege
- Arzneistoffgruppen
- Nebenwirkungen und Interaktionen
- Notfall- und Intensivpharmakologie
- Pharmakologie der Ernährung und Stoffwechselmedizin
- Arzneistoffchemie als Brücke zu OC/APC

## PH-Beispielanker

| ID | Slug / Dateiname | Titel | Typ | Niveau |
|---|---|---|---|---|
| `ph_001` | `ph_001_allgemeine_pharmakologie` | Allgemeine Pharmakologie | overview | grundlagen |
| `ph_002` | `ph_002_pharmakokinetik_ueberblick` | Pharmakokinetik – Überblick | overview | grundlagen |
| `ph_003` | `ph_003_pharmakodynamik_ueberblick` | Pharmakodynamik – Überblick | overview | grundlagen |
| `ph_004` | `ph_004_rezeptorbindung` | Rezeptorbindung | structure | intermediate |
| `ph_005` | `ph_005_dosis_wirkungs_kurve` | Dosis-Wirkungs-Kurve | overview | intermediate |

---

# Produktionsstatus und nächste Schritte

## Statuswerte

| Status | Bedeutung |
|---|---|
| `planned` | Karte geplant, noch nicht produziert |
| `draft` | Entwurf vorhanden |
| `in_review` | fachliche Prüfung läuft |
| `approved` | fachlich freigegeben |
| `print_ready` | druckfertig |
| `web_ready` | onlinefähig |

## Nächste Schritte

1. Die vollständige CSV-Registry als technische Datenquelle ergänzen oder aus diesem Masterverzeichnis generieren.
2. Die ersten 10 OC-Pilotkarten vollständig produzieren.
3. QR-Redirect-MVP für `https://chembiomed-cards.de/c/<short_id>` umsetzen.
4. Landingpage auf ATMED-core deployen.
5. PH-Struktur beibehalten, aber inhaltlich erst später ausbauen.

## Hinweis

Dieses Masterverzeichnis ist absichtlich menschenlesbar. Für Automatisierung, QR-Erzeugung, Export und Webplattform bleibt eine maschinenlesbare Registry zusätzlich erforderlich.

---

<!-- PRODUZIERTE-KARTEN:START -->

## Produzierte Karten (automatisch aus `data/cards/`)

_Erzeugt von `scripts/update_master_directory.py` – nicht von Hand bearbeiten. Quelle der Wahrheit sind die Kartendateien._

Stand: **116 Karten**.

### stoffwechsel_zentral

| ID | Slug / Dateiname | Titel | Tab | Review |
|---|---|---|---|---|
| `bc_061` | `bc_061_glucose` | Glucose | biochemie | needs_review |
| `bc_062` | `bc_062_glucose_6_phosphat` | Glucose-6-phosphat | biochemie | needs_review |
| `bc_063` | `bc_063_fructose_6_phosphat` | Fructose-6-phosphat | biochemie | needs_review |
| `bc_064` | `bc_064_pyruvat` | Pyruvat | biochemie | needs_review |
| `bc_065` | `bc_065_laktat` | Laktat | biochemie | needs_review |
| `bc_073` | `bc_073_acetyl_coa` | Acetyl-CoA | biochemie | needs_review |
| `bc_074` | `bc_074_coenzym_a` | Coenzym A | biochemie | needs_review |
| `bc_075` | `bc_075_citrat` | Citrat | biochemie | needs_review |
| `bc_076` | `bc_076_oxalacetat` | Oxalacetat | biochemie | needs_review |
| `bc_077` | `bc_077_alpha_ketoglutarat` | α-Ketoglutarat | biochemie | needs_review |
| `bc_078` | `bc_078_succinyl_coa` | Succinyl-CoA | biochemie | needs_review |
| `bc_079` | `bc_079_succinat` | Succinat | biochemie | needs_review |
| `bc_080` | `bc_080_fumarat` | Fumarat | biochemie | needs_review |
| `bc_081` | `bc_081_malat` | Malat | biochemie | needs_review |

### aminosaeuren_proteinogen

| ID | Slug / Dateiname | Titel | Tab | Review |
|---|---|---|---|---|
| `bc_098` | `bc_098_glycin` | Glycin | biochemie | needs_review |
| `bc_099` | `bc_099_alanin` | Alanin | biochemie | needs_review |
| `bc_100` | `bc_100_valin` | Valin | biochemie | needs_review |
| `bc_101` | `bc_101_leucin` | Leucin | biochemie | needs_review |
| `bc_102` | `bc_102_isoleucin` | Isoleucin | biochemie | needs_review |
| `bc_103` | `bc_103_serin` | Serin | biochemie | needs_review |
| `bc_104` | `bc_104_threonin` | Threonin | biochemie | needs_review |
| `bc_105` | `bc_105_cystein` | Cystein | biochemie | needs_review |
| `bc_106` | `bc_106_methionin` | Methionin | biochemie | needs_review |
| `bc_107` | `bc_107_prolin` | Prolin | biochemie | needs_review |
| `bc_108` | `bc_108_phenylalanin` | Phenylalanin | biochemie | needs_review |
| `bc_109` | `bc_109_tyrosin` | Tyrosin | biochemie | needs_review |
| `bc_110` | `bc_110_tryptophan` | Tryptophan | biochemie | needs_review |
| `bc_111` | `bc_111_histidin` | Histidin | biochemie | needs_review |
| `bc_112` | `bc_112_lysin` | Lysin | biochemie | needs_review |
| `bc_113` | `bc_113_arginin` | Arginin | biochemie | needs_review |
| `bc_114` | `bc_114_aspartat` | Aspartat / Asparaginsäure | biochemie | needs_review |
| `bc_115` | `bc_115_glutamat` | Glutamat / Glutaminsäure | biochemie | needs_review |
| `bc_116` | `bc_116_asparagin` | Asparagin | biochemie | needs_review |
| `bc_117` | `bc_117_glutamin` | Glutamin | biochemie | needs_review |

### aminosaeure_derivate

| ID | Slug / Dateiname | Titel | Tab | Review |
|---|---|---|---|---|
| `bc_118` | `bc_118_kreatin` | Kreatin | biochemie | needs_review |
| `bc_119` | `bc_119_kreatinin` | Kreatinin | biochemie | needs_review |
| `bc_120` | `bc_120_homocystein` | Homocystein | biochemie | needs_review |
| `bc_121` | `bc_121_taurin` | Taurin | biochemie | needs_review |
| `bc_122` | `bc_122_beta_alanin` | β-Alanin | biochemie | needs_review |
| `bc_123` | `bc_123_hydroxyprolin` | Hydroxyprolin | biochemie | needs_review |
| `bc_124` | `bc_124_hydroxylysin` | Hydroxylysin | biochemie | needs_review |
| `bc_125` | `bc_125_selenocystein` | Selenocystein | biochemie | needs_review |
| `bc_126` | `bc_126_selenomethionin` | Selenomethionin | biochemie | needs_review |
| `bc_127` | `bc_127_ornithin` | Ornithin | biochemie | needs_review |
| `bc_128` | `bc_128_citrullin` | Citrullin | biochemie | needs_review |
| `bc_129` | `bc_129_argininosuccinat` | Argininosuccinat | biochemie | needs_review |
| `bc_130` | `bc_130_n_acetylglutamat` | N-Acetylglutamat | biochemie | needs_review |
| `bc_131` | `bc_131_n_acetylaspartat` | N-Acetylaspartat | biochemie | needs_review |

### stickstoffstoffwechsel

| ID | Slug / Dateiname | Titel | Tab | Review |
|---|---|---|---|---|
| `bc_132` | `bc_132_ammoniak_ammonium` | Ammoniak / Ammonium | biochemie | needs_review |
| `bc_133` | `bc_133_carbamoylphosphat` | Carbamoylphosphat | biochemie | needs_review |
| `bc_134` | `bc_134_harnstoff` | Harnstoff | biochemie | needs_review |
| `bc_135` | `bc_135_orotat` | Orotat | biochemie | needs_review |

### lipide

| ID | Slug / Dateiname | Titel | Tab | Review |
|---|---|---|---|---|
| `bc_140` | `bc_140_oelsaeure` | Ölsäure | biochemie | needs_review |
| `bc_141` | `bc_141_linolsaeure` | Linolsäure | biochemie | needs_review |
| `bc_142` | `bc_142_arachidonsaeure` | Arachidonsäure | biochemie | needs_review |
| `bc_143` | `bc_143_triacylglycerid` | Triacylglycerid (TAG) | biochemie | needs_review |
| `bc_144` | `bc_144_diacylglycerin` | Diacylglycerin (DAG) | biochemie | needs_review |
| `bc_145` | `bc_145_prostaglandin_e2` | Prostaglandin E2 | biochemie | needs_review |
| `bc_146` | `bc_146_thromboxan_a2` | Thromboxan A2 | biochemie | needs_review |
| `bc_147` | `bc_147_leukotrien_b4` | Leukotrien B4 | biochemie | needs_review |
| `bc_148` | `bc_148_beta_hydroxybutyrat` | β-Hydroxybutyrat | biochemie | needs_review |
| `bc_149` | `bc_149_malonyl_coa` | Malonyl-CoA | biochemie | needs_review |
| `bc_150` | `bc_150_hmg_coa` | HMG-CoA | biochemie | needs_review |
| `bc_151` | `bc_151_mevalonat` | Mevalonat | biochemie | needs_review |

### neurotransmitter

| ID | Slug / Dateiname | Titel | Tab | Review |
|---|---|---|---|---|
| `bc_160` | `bc_160_dopamin` | Dopamin | biochemie | needs_review |
| `bc_161` | `bc_161_adrenalin` | Adrenalin | biochemie | needs_review |
| `bc_162` | `bc_162_noradrenalin` | Noradrenalin | biochemie | needs_review |
| `bc_163` | `bc_163_serotonin` | Serotonin | biochemie | needs_review |
| `bc_164` | `bc_164_melatonin` | Melatonin | biochemie | needs_review |
| `bc_165` | `bc_165_histamin` | Histamin | biochemie | needs_review |
| `bc_166` | `bc_166_acetylcholin` | Acetylcholin | biochemie | needs_review |
| `bc_167` | `bc_167_gaba` | GABA | biochemie | needs_review |
| `bc_168` | `bc_168_5_hydroxytryptophan` | 5-Hydroxytryptophan (5-HTP) | biochemie | needs_review |
| `bc_169` | `bc_169_l_dopa` | L-DOPA | biochemie | needs_review |

### hormone

| ID | Slug / Dateiname | Titel | Tab | Review |
|---|---|---|---|---|
| `bc_170` | `bc_170_insulin` | Insulin | biochemie | needs_review |
| `bc_171` | `bc_171_glukagon` | Glukagon | biochemie | needs_review |
| `bc_172` | `bc_172_glp_1` | GLP-1 | biochemie | needs_review |
| `bc_173` | `bc_173_gip` | GIP | biochemie | needs_review |
| `bc_174` | `bc_174_ghrelin` | Ghrelin | biochemie | needs_review |
| `bc_175` | `bc_175_leptin` | Leptin | biochemie | needs_review |
| `bc_176` | `bc_176_adiponektin` | Adiponektin | biochemie | needs_review |
| `bc_177` | `bc_177_cortisol` | Cortisol | biochemie | needs_review |
| `bc_178` | `bc_178_aldosteron` | Aldosteron | biochemie | needs_review |
| `bc_179` | `bc_179_calcitriol` | Calcitriol | biochemie | needs_review |
| `bc_180` | `bc_180_triiodthyronin` | Triiodthyronin (T3) | biochemie | needs_review |
| `bc_181` | `bc_181_thyroxin` | Thyroxin (T4) | biochemie | needs_review |
| `bc_182` | `bc_182_testosteron` | Testosteron | biochemie | needs_review |
| `bc_183` | `bc_183_oestradiol` | Östradiol | biochemie | needs_review |
| `bc_184` | `bc_184_progesteron` | Progesteron | biochemie | needs_review |

### nukleotide_coenzyme

| ID | Slug / Dateiname | Titel | Tab | Review |
|---|---|---|---|---|
| `bc_200` | `bc_200_atp` | ATP | biochemie | needs_review |
| `bc_201` | `bc_201_gtp` | GTP | biochemie | needs_review |
| `bc_202` | `bc_202_camp` | cAMP | molekularbio | needs_review |
| `bc_203` | `bc_203_cgmp` | cGMP | molekularbio | needs_review |
| `bc_204` | `bc_204_ip3` | Inositoltrisphosphat (IP₃) | molekularbio | needs_review |
| `bc_205` | `bc_205_nad` | NAD⁺ | biochemie | needs_review |
| `bc_206` | `bc_206_nadh` | NADH | biochemie | needs_review |
| `bc_207` | `bc_207_fad` | FAD | biochemie | needs_review |
| `bc_208` | `bc_208_coenzym_q10` | Coenzym Q10 | biochemie | needs_review |
| `bc_209` | `bc_209_ubichinol` | Ubichinol | biochemie | needs_review |
| `bc_210` | `bc_210_s_adenosylmethionin` | S-Adenosylmethionin (SAM) | biochemie | needs_review |
| `bc_211` | `bc_211_calcium` | Calcium / Ca²⁺ | molekularbio | needs_review |
| `bc_212` | `bc_212_stickstoffmonoxid` | Stickstoffmonoxid (NO) | molekularbio | needs_review |

### vitamine

| ID | Slug / Dateiname | Titel | Tab | Review |
|---|---|---|---|---|
| `bc_256` | `bc_256_vitamin_a` | Vitamin A | biochemie | needs_review |
| `bc_257` | `bc_257_vitamin_b1` | Vitamin B1 | biochemie | needs_review |
| `bc_258` | `bc_258_vitamin_b2` | Vitamin B2 | biochemie | needs_review |
| `bc_259` | `bc_259_vitamin_b3` | Vitamin B3 | biochemie | needs_review |
| `bc_260` | `bc_260_vitamin_b5` | Vitamin B5 | biochemie | needs_review |
| `bc_261` | `bc_261_vitamin_b6` | Vitamin B6 | biochemie | needs_review |
| `bc_262` | `bc_262_vitamin_b7` | Vitamin B7 | biochemie | needs_review |
| `bc_263` | `bc_263_vitamin_b9` | Vitamin B9 | biochemie | needs_review |
| `bc_264` | `bc_264_vitamin_b12` | Vitamin B12 | biochemie | needs_review |
| `bc_265` | `bc_265_vitamin_c` | Vitamin C | biochemie | needs_review |
| `bc_266` | `bc_266_vitamin_d` | Vitamin D | biochemie | needs_review |
| `bc_267` | `bc_267_vitamin_e` | Vitamin E | biochemie | needs_review |
| `bc_268` | `bc_268_vitamin_k` | Vitamin K | biochemie | needs_review |
| `bc_269` | `bc_269_vitamin_s` | Vitamin S (Schokolade) | biochemie | needs_review |

<!-- PRODUZIERTE-KARTEN:END -->
