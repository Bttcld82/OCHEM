#!/usr/bin/env python3
"""
Seed dati UNICHIM - Cicli PT reali da catalogo UNICHIM 2024/2025 e 2025/2026.

Inserisce:
  - Provider UNICHIM
  - Unità di misura
  - Matrici analitiche
  - Parametri tipici per categoria
  - Cicli PT con codici ufficiali UNICHIM
  - Associazioni ciclo-parametro con placeholder xpt=0.0, sigma_pt=1.0

I valori xpt e sigma_pt sono placeholder da aggiornare quando si ottengono
i valori assegnati da UNICHIM (riservati ai partecipanti registrati).

Fonte codici cicli: https://prove.unichim.it (calendario 2024-2026)
"""

import sys
from pathlib import Path
from datetime import datetime

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))


# ─── UNITÀ DI MISURA ──────────────────────────────────────────────────────────

UNITS = [
    ('mg/L',       'Milligrammi per litro'),
    ('µg/L',       'Microgrammi per litro'),
    ('ng/L',       'Nanogrammi per litro'),
    ('pH',         'Unità pH'),
    ('µS/cm',      'Microsiemens per centimetro'),
    ('NTU',        'Nephelometric Turbidity Units'),
    ('mg/kg',      'Milligrammi per chilogrammo s.s.'),
    ('µg/kg',      'Microgrammi per chilogrammo s.s.'),
    ('mg/Nm³',     'Milligrammi per metro cubo normalizzato'),
    ('µg/m³',      'Microgrammi per metro cubo'),
    ('%',          'Percentuale in massa'),
    ('mm²/s',      'Viscosità cinematica (cSt)'),
    ('kg/m³',      'Chilogrammi per metro cubo (densità)'),
    ('kPa',        'Kilopascal'),
    ('°C',         'Gradi Celsius'),
    ('MJ/m³',      'Megajoule per metro cubo'),
    ('mg/L CaCO3', 'Milligrammi per litro come CaCO3'),
    ('TEQ ng/kg',  'Equivalenti tossici nanogrammi per chilogrammo'),
    ('CFU/100mL',  'Unità formanti colonie per 100 mL'),
    ('CFU/L',      'Unità formanti colonie per litro'),
    ('UFC/g',      'Unità formanti colonie per grammo'),
    ('UFC/25g',    'Unità formanti colonie per 25 grammi'),
    ('-',          'Adimensionale'),
]

# ─── MATRICI ANALITICHE ───────────────────────────────────────────────────────

MATRICES = [
    ('ACQUA',    'Acqua (potabile, superficiale, sotterranea)'),
    ('ACQREF',   'Acque reflue'),
    ('SUOLO',    'Suolo e sedimenti'),
    ('ARIA',     'Aria ambiente'),
    ('EMISS',    'Emissioni gassose al camino'),
    ('BIOGAS',   'Gas naturale, biogas, gas di processo'),
    ('PETROL',   'Prodotti petroliferi e lubrificanti'),
    ('RIFIUTI',  'Rifiuti solidi, fanghi e leachate'),
    ('PRODOTTI', 'Prodotti organici (compost, fertilizzanti)'),
    ('ALIM',     'Alimenti e superfici alimentari'),
]

# ─── PARAMETRI ───────────────────────────────────────────────────────────────
# (code, name, unit_code, matrix_text)

PARAMETERS = [
    # --- Fisico-chimici in acqua ---
    ('PH',       'pH',                                        'pH',         'Acqua'),
    ('COND',     'Conducibilità elettrica',                   'µS/cm',      'Acqua'),
    ('TURB',     'Torbidità',                                 'NTU',        'Acqua'),
    ('BOD5',     'BOD5 - Domanda biochimica di ossigeno',     'mg/L',       'Acqua'),
    ('COD',      'COD - Domanda chimica di ossigeno',         'mg/L',       'Acqua'),
    ('TOC',      'TOC - Carbonio organico totale',            'mg/L',       'Acqua'),
    ('TSS',      'Solidi sospesi totali',                     'mg/L',       'Acqua'),
    ('TDS',      'Solidi disciolti totali',                   'mg/L',       'Acqua'),
    ('ALK',      'Alcalinità totale',                         'mg/L CaCO3', 'Acqua'),
    ('NH4',      'Azoto ammoniacale (NH4+)',                  'mg/L',       'Acqua'),
    ('NO3',      'Nitrati (NO3-)',                            'mg/L',       'Acqua'),
    ('NO2',      'Nitriti (NO2-)',                            'mg/L',       'Acqua'),
    ('PO4',      'Ortofosfati (PO43-)',                      'mg/L',       'Acqua'),
    ('SO4',      'Solfati (SO42-)',                          'mg/L',       'Acqua'),
    ('CLOR',     'Cloruri (Cl-)',                             'mg/L',       'Acqua'),
    ('DURE',     'Durezza totale',                            'mg/L CaCO3', 'Acqua'),
    # --- Cianuri in acqua ---
    ('CN_TOT',   'Cianuri totali',                           'µg/L',       'Acqua'),
    ('CN_LIB',   'Cianuri liberi',                           'µg/L',       'Acqua'),
    # --- Cloro specie in acqua ---
    ('CLO_LIB',  'Cloro libero residuo',                     'mg/L',       'Acqua'),
    ('CLO_TOT',  'Cloro totale',                             'mg/L',       'Acqua'),
    ('NH2CL',    'Monoclorammina',                           'mg/L',       'Acqua'),
    # --- PFAS in acqua ---
    ('PFOA',     'PFOA - Acido perfluoroottanoico',          'ng/L',       'Acqua'),
    ('PFOS',     'PFOS - Acido perfluoroottansolfonico',     'ng/L',       'Acqua'),
    ('PFNA',     'PFNA - Acido perfluorononanoico',          'ng/L',       'Acqua'),
    ('PFHXS',    'PFHxS - Acido perfluoroesansolfonico',     'ng/L',       'Acqua'),
    ('PFAS_TOT', 'PFAS totali (somma)',                      'ng/L',       'Acqua'),
    # --- Solventi in acqua ---
    ('BENZ',     'Benzene (in acqua)',                       'µg/L',       'Acqua'),
    ('TOLU',     'Toluene (in acqua)',                       'µg/L',       'Acqua'),
    ('EBNZ',     'Etilbenzene (in acqua)',                   'µg/L',       'Acqua'),
    ('XILEN',    'Xilene - somma isomeri (in acqua)',        'µg/L',       'Acqua'),
    ('TCE',      'Tricloroetilene',                          'µg/L',       'Acqua'),
    ('PCE',      'Tetracloroetilene',                        'µg/L',       'Acqua'),
    # --- Metalli in suolo/sedimento ---
    ('PB',       'Piombo (Pb)',                              'mg/kg',      'Suolo'),
    ('CD',       'Cadmio (Cd)',                              'mg/kg',      'Suolo'),
    ('CR_TOT',   'Cromo totale (Cr tot)',                    'mg/kg',      'Suolo'),
    ('CRVI',     'Cromo esavalente (Cr VI)',                 'mg/kg',      'Suolo'),
    ('NI',       'Nichel (Ni)',                              'mg/kg',      'Suolo'),
    ('CU',       'Rame (Cu)',                                'mg/kg',      'Suolo'),
    ('ZN',       'Zinco (Zn)',                               'mg/kg',      'Suolo'),
    ('AS',       'Arsenico (As)',                            'mg/kg',      'Suolo'),
    ('HG',       'Mercurio (Hg)',                            'mg/kg',      'Suolo'),
    ('SE',       'Selenio (Se)',                             'mg/kg',      'Suolo'),
    ('SB',       'Antimonio (Sb)',                           'mg/kg',      'Suolo'),
    # --- Idrocarburi in suolo ---
    ('HC_TOT',   'Idrocarburi totali (C10-C40)',             'mg/kg',      'Suolo'),
    ('HC_LEG',   'Idrocarburi leggeri (C6-C9)',              'mg/kg',      'Suolo'),
    # --- IPA in suolo (16 EPA) ---
    ('NAPH',     'Naftalene',                                'µg/kg',      'Suolo'),
    ('ACENP',    'Acenaftilene',                             'µg/kg',      'Suolo'),
    ('FLRN',     'Fluorantene',                              'µg/kg',      'Suolo'),
    ('PYRE',     'Pirene',                                   'µg/kg',      'Suolo'),
    ('BAP',      'Benzo[a]pirene',                           'µg/kg',      'Suolo'),
    ('IPA_TOT',  'IPA totali (16 EPA)',                      'µg/kg',      'Suolo'),
    # --- PCB in suolo ---
    ('PCB_TOT',  'PCB totali (7 congeneri)',                 'µg/kg',      'Suolo'),
    ('PCB28',    'PCB 28',                                   'µg/kg',      'Suolo'),
    ('PCB52',    'PCB 52',                                   'µg/kg',      'Suolo'),
    ('PCB101',   'PCB 101',                                  'µg/kg',      'Suolo'),
    ('PCB138',   'PCB 138',                                  'µg/kg',      'Suolo'),
    ('PCB153',   'PCB 153',                                  'µg/kg',      'Suolo'),
    ('PCB180',   'PCB 180',                                  'µg/kg',      'Suolo'),
    # --- Diossine ---
    ('PCDD_TEQ', 'PCDD/F - Equivalenti tossici (TEQ)',       'TEQ ng/kg',  'Suolo'),
    ('TCDD',     '2,3,7,8-Tetraclorodibenzo-p-diossina',    'TEQ ng/kg',  'Suolo'),
    # --- POPs (pesticidi organoclorurati) ---
    ('DDT_TOT',  'DDT totale (somma isomeri)',               'µg/kg',      'Suolo'),
    ('ALDRIN',   'Aldrin',                                   'µg/kg',      'Suolo'),
    ('DIELDR',   'Dieldrin',                                 'µg/kg',      'Suolo'),
    # --- Fisico-chimici in suolo / prodotti ---
    ('PH_S',     'pH (suolo o prodotto solido)',             'pH',         'Suolo'),
    ('C_ORG',    'Carbonio organico',                        '%',          'Suolo'),
    # --- VOC in aria ambiente ---
    ('BENZ_A',   'Benzene in aria',                          'µg/m³',      'Aria'),
    ('TOLU_A',   'Toluene in aria',                          'µg/m³',      'Aria'),
    ('EBNZ_A',   'Etilbenzene in aria',                      'µg/m³',      'Aria'),
    ('XYL_A',    'Xilene in aria',                           'µg/m³',      'Aria'),
    ('STIR_A',   'Stirene in aria',                          'µg/m³',      'Aria'),
    # --- Emissioni al camino ---
    ('PM_TOT',   'Polveri totali (emissioni)',               'mg/Nm³',     'Emissioni gassose'),
    ('SO2',      'Anidride solforosa - SO2',                 'mg/Nm³',     'Emissioni gassose'),
    ('NOX',      'Ossidi di azoto - NOx',                   'mg/Nm³',     'Emissioni gassose'),
    ('CO_E',     'Monossido di carbonio (emissioni)',        'mg/Nm³',     'Emissioni gassose'),
    ('HCL_E',    'Acido cloridrico HCl (emissioni)',         'mg/Nm³',     'Emissioni gassose'),
    ('HF_E',     'Acido fluoridrico HF (emissioni)',         'mg/Nm³',     'Emissioni gassose'),
    # --- Gas naturale / biogas ---
    ('CH4',      'Metano (CH4)',                             '%',          'Gas naturale'),
    ('C2H6',     'Etano (C2H6)',                             '%',          'Gas naturale'),
    ('C3H8',     'Propano (C3H8)',                           '%',          'Gas naturale'),
    ('C4H10',    'Butano n+iso (C4H10)',                     '%',          'Gas naturale'),
    ('CO2_G',    'CO2 in miscela gassosa',                   '%',          'Gas naturale'),
    ('N2_G',     'Azoto in miscela gassosa',                 '%',          'Gas naturale'),
    ('H2S_G',    'H2S in miscela gassosa',                   'mg/Nm³',     'Gas naturale'),
    ('PCS',      'Potere calorifico superiore (PCS)',         'MJ/m³',      'Gas naturale'),
    # --- Prodotti petroliferi e lubrificanti ---
    ('RON',      'Research Octane Number (RON)',              '-',          'Prodotti petroliferi'),
    ('DENS15',   'Densità a 15°C',                           'kg/m³',      'Prodotti petroliferi'),
    ('PVAP',     'Pressione di vapore Reid',                  'kPa',        'Prodotti petroliferi'),
    ('VIS40',    'Viscosità cinematica a 40°C',              'mm²/s',      'Prodotti petroliferi'),
    ('VIS100',   'Viscosità cinematica a 100°C',             'mm²/s',      'Prodotti petroliferi'),
    ('PPOUR',    'Punto di scorrimento (Pour Point)',         '°C',         'Prodotti petroliferi'),
    ('PFLAS',    'Punto di infiammabilità',                   '°C',         'Prodotti petroliferi'),
    # --- Microbiologia acque ---
    ('ECOLI',    'Escherichia coli',                          'CFU/100mL',  'Acqua'),
    ('COLIT',    'Coliformi totali',                          'CFU/100mL',  'Acqua'),
    ('ENTEROC',  'Enterococchi intestinali',                  'CFU/100mL',  'Acqua'),
    ('CBT',      'Conta batterica totale a 22°C',            'CFU/100mL',  'Acqua'),
    ('LEGSP',    'Legionella spp.',                           'CFU/L',      'Acqua'),
    ('LEGPN',    'Legionella pneumophila',                    'CFU/L',      'Acqua'),
    # --- Microbiologia alimenti ---
    ('ECOLI_F',  'Escherichia coli (alimenti)',               'UFC/g',      'Alimenti'),
    ('SALM',     'Salmonella spp.',                           'UFC/25g',    'Alimenti'),
    ('LISTM',    'Listeria monocytogenes',                    'UFC/g',      'Alimenti'),
    # --- Compost e fertilizzanti ---
    ('N_TOT',    'Azoto totale Kjeldahl (NTK)',              '%',          'Prodotti organici'),
    ('P2O5',     'Pentossido di fosforo (P2O5)',              '%',          'Prodotti organici'),
    ('K2O',      'Ossido di potassio (K2O)',                  '%',          'Prodotti organici'),
    ('C_ORG_P',  'Carbonio organico (prodotti solidi)',       '%',          'Prodotti organici'),
    ('CN_RAP',   'Rapporto C/N',                              '-',          'Prodotti organici'),
]


# ─── CICLI UNICHIM ────────────────────────────────────────────────────────────
# (code, name, status, start_date, end_date)
# published = ciclo completato; draft = ciclo in corso / programmato
# xpt e sigma_pt sono assegnati da UNICHIM ai partecipanti: usare placeholder 0/1

D_PUB_START = datetime(2024, 10, 1)
D_PUB_END   = datetime(2025, 4, 30)
D_DFT_START = datetime(2025, 10, 1)
D_DFT_END   = datetime(2026, 4, 30)

CYCLES = [
    # ── Acqua ──────────────────────────────────────────────────────────────────
    ('WATER-APAR-3',   'Apparenza e parametri fisici in acqua - ciclo 3',         'published', D_PUB_START, D_PUB_END),
    ('WATER-SOLV-15',  'Solventi organici in acqua - ciclo 15',                   'published', D_PUB_START, D_PUB_END),
    ('WATER-SOLV-16',  'Solventi organici in acqua - ciclo 16',                   'draft',     D_DFT_START, D_DFT_END),
    ('WATER-CIAC-25',  'Cianuri in acqua - ciclo 25',                             'published', D_PUB_START, D_PUB_END),
    ('WATER-CIAC-26',  'Cianuri in acqua - ciclo 26',                             'draft',     D_DFT_START, D_DFT_END),
    ('WATER-CISP-45',  'Clorospeciazione in acqua - ciclo 45',                    'published', D_PUB_START, D_PUB_END),
    ('WATER-CISP-46',  'Clorospeciazione in acqua - ciclo 46',                    'draft',     D_DFT_START, D_DFT_END),
    ('WATER-PFAS-4',   'PFAS in acqua - ciclo 4',                                 'published', D_PUB_START, D_PUB_END),
    ('WATER-PFAS-5',   'PFAS in acqua - ciclo 5',                                 'draft',     D_DFT_START, D_DFT_END),
    # ── Ambiente (suolo/sedimento) ─────────────────────────────────────────────
    ('ENVIR-APAR-3',   'Parametri fisico-chimici ambientali - ciclo 3',           'published', D_PUB_START, D_PUB_END),
    ('ENVIR-META-29',  'Metalli in matrici ambientali - ciclo 29',                'published', D_PUB_START, D_PUB_END),
    ('ENVIR-META-30',  'Metalli in matrici ambientali - ciclo 30',                'draft',     D_DFT_START, D_DFT_END),
    ('ENVIR-CROM-8',   'Cromo esavalente in matrici ambientali - ciclo 8',        'published', D_PUB_START, D_PUB_END),
    ('ENVIR-CROM-9',   'Cromo esavalente in matrici ambientali - ciclo 9',        'draft',     D_DFT_START, D_DFT_END),
    ('ENVIR-IDRO-29',  'Idrocarburi in matrici ambientali - ciclo 29',            'published', D_PUB_START, D_PUB_END),
    ('ENVIR-IDRO-30',  'Idrocarburi in matrici ambientali - ciclo 30',            'draft',     D_DFT_START, D_DFT_END),
    ('ENVIR-IPAS-37',  'IPA in matrici ambientali - ciclo 37',                    'published', D_PUB_START, D_PUB_END),
    ('ENVIR-IPAS-38',  'IPA in matrici ambientali - ciclo 38',                    'draft',     D_DFT_START, D_DFT_END),
    ('ENVIR-POPS-2',   'Inquinanti organici persistenti (POPs) - ciclo 2',        'published', D_PUB_START, D_PUB_END),
    ('ENVIR-DIOX-30',  'Diossine e furani (PCDD/F) - ciclo 30',                   'published', D_PUB_START, D_PUB_END),
    ('ENVIR-DIOX-31',  'Diossine e furani (PCDD/F) - ciclo 31',                   'draft',     D_DFT_START, D_DFT_END),
    ('ENVIR-PCBS-31',  'PCB in matrici ambientali - ciclo 31',                    'published', D_PUB_START, D_PUB_END),
    ('ENVIR-PCBS-32',  'PCB in matrici ambientali - ciclo 32',                    'draft',     D_DFT_START, D_DFT_END),
    # ── Microbiologia ──────────────────────────────────────────────────────────
    ('MICRO-POTW-19',  'Microbiologia acqua potabile - ciclo 19',                 'published', D_PUB_START, D_PUB_END),
    ('MICRO-POTW-20',  'Microbiologia acqua potabile - ciclo 20',                 'draft',     D_DFT_START, D_DFT_END),
    ('MICRO-WASW-19',  'Microbiologia acque reflue - ciclo 19',                   'published', D_PUB_START, D_PUB_END),
    ('MICRO-WASW-20',  'Microbiologia acque reflue - ciclo 20',                   'draft',     D_DFT_START, D_DFT_END),
    ('MICRO-SURW-19',  'Microbiologia acque superficiali - ciclo 19',             'published', D_PUB_START, D_PUB_END),
    ('MICRO-SURW-20',  'Microbiologia acque superficiali - ciclo 20',             'draft',     D_DFT_START, D_DFT_END),
    ('MICRO-LEGW-19',  'Legionella in acqua - ciclo 19',                          'published', D_PUB_START, D_PUB_END),
    ('MICRO-LEGW-20',  'Legionella in acqua - ciclo 20',                          'draft',     D_DFT_START, D_DFT_END),
    ('MICRO-FOOD-19',  'Microbiologia alimenti - ciclo 19',                       'published', D_PUB_START, D_PUB_END),
    ('MICRO-FOOD-20',  'Microbiologia alimenti - ciclo 20',                       'draft',     D_DFT_START, D_DFT_END),
    # ── Aria ed emissioni ──────────────────────────────────────────────────────
    ('AIR-VOCA-11',    'VOC in aria ambiente - ciclo 11',                         'published', D_PUB_START, D_PUB_END),
    ('AIR-VOFI-8',     'VOC su filtri (aria) - ciclo 8',                          'published', D_PUB_START, D_PUB_END),
    ('AIR-VOFI-9',     'VOC su filtri (aria) - ciclo 9',                          'draft',     D_DFT_START, D_DFT_END),
    ('AIR-EMIS-3',     'Emissioni gassose al camino - ciclo 3',                   'published', D_PUB_START, D_PUB_END),
    ('AIR-EMIS-4',     'Emissioni gassose al camino - ciclo 4',                   'draft',     D_DFT_START, D_DFT_END),
    ('AIR-VOTD-3',     'VOC nel sottosuolo - ciclo 3',                            'published', D_PUB_START, D_PUB_END),
    ('AIR-VOTD-4',     'VOC nel sottosuolo - ciclo 4',                            'draft',     D_DFT_START, D_DFT_END),
    # ── Prodotti petroliferi ───────────────────────────────────────────────────
    ('PETR-FUEL-67',   'Carburanti - ciclo 67',                                   'published', D_PUB_START, D_PUB_END),
    ('PETR-FUEL-68',   'Carburanti - ciclo 68',                                   'published', D_PUB_START, D_PUB_END),
    ('PETR-FUEL-69',   'Carburanti - ciclo 69',                                   'draft',     D_DFT_START, D_DFT_END),
    ('PETR-BITU-11',   'Bitumi - ciclo 11',                                       'published', D_PUB_START, D_PUB_END),
    ('PETR-BITU-12',   'Bitumi - ciclo 12',                                       'draft',     D_DFT_START, D_DFT_END),
    ('PETR-LUBE-49',   'Lubrificanti - ciclo 49',                                 'published', D_PUB_START, D_PUB_END),
    ('PETR-LUBE-50',   'Lubrificanti - ciclo 50',                                 'draft',     D_DFT_START, D_DFT_END),
    # ── Gas ───────────────────────────────────────────────────────────────────
    ('GAS-GASQ-20',    'Gas naturale - qualità - ciclo 20',                       'published', D_PUB_START, D_PUB_END),
    ('GAS-GASQ-21',    'Gas naturale - qualità - ciclo 21',                       'draft',     D_DFT_START, D_DFT_END),
    ('GAS-PGPL-33',    'GPL (gas propano-butano) - ciclo 33',                     'published', D_PUB_START, D_PUB_END),
    ('GAS-PGPL-34',    'GPL (gas propano-butano) - ciclo 34',                     'draft',     D_DFT_START, D_DFT_END),
    ('GAS-GRAF-28',    'Gas di raffineria - ciclo 28',                            'published', D_PUB_START, D_PUB_END),
    ('GAS-GRAF-29',    'Gas di raffineria - ciclo 29',                            'draft',     D_DFT_START, D_DFT_END),
    # ── Rifiuti e fanghi ──────────────────────────────────────────────────────
    ('WASTE-LETE-6',   'Leachate da rifiuti - ciclo 6',                           'published', D_PUB_START, D_PUB_END),
    ('WASTE-LETE-7',   'Leachate da rifiuti - ciclo 7',                           'draft',     D_DFT_START, D_DFT_END),
    ('WASTE-CSSE-4',   'Compost, suoli e fanghi - ciclo 4',                       'published', D_PUB_START, D_PUB_END),
    ('WASTE-CSSE-5',   'Compost, suoli e fanghi - ciclo 5',                       'draft',     D_DFT_START, D_DFT_END),
    # ── Prodotti organici ─────────────────────────────────────────────────────
    ('PROD-COMP-20',   'Compost e ammendanti - ciclo 20',                         'published', D_PUB_START, D_PUB_END),
    ('PROD-COMP-21',   'Compost e ammendanti - ciclo 21',                         'draft',     D_DFT_START, D_DFT_END),
    ('PROD-FERT-24',   'Fertilizzanti - ciclo 24',                                'published', D_PUB_START, D_PUB_END),
    ('PROD-FERT-25',   'Fertilizzanti - ciclo 25',                                'draft',     D_DFT_START, D_DFT_END),
]


# ─── MAPPA CICLO → PARAMETRI ─────────────────────────────────────────────────
# La chiave è il prefisso del codice ciclo (CATEGORY-TYPE).
# xpt=0.0 e sigma_pt=1.0 sono placeholder: aggiornare con i valori UNICHIM.

CYCLE_PARAMETERS = {
    'WATER-APAR': ['PH', 'COND', 'TURB', 'BOD5', 'COD', 'TOC', 'TSS', 'NH4', 'NO3', 'PO4', 'SO4', 'CLOR', 'ALK'],
    'WATER-SOLV': ['BENZ', 'TOLU', 'EBNZ', 'XILEN', 'TCE', 'PCE'],
    'WATER-CIAC': ['CN_TOT', 'CN_LIB'],
    'WATER-CISP': ['CLO_LIB', 'CLO_TOT', 'NH2CL'],
    'WATER-PFAS': ['PFOA', 'PFOS', 'PFNA', 'PFHXS', 'PFAS_TOT'],
    'ENVIR-APAR': ['PH_S', 'C_ORG', 'NH4', 'NO3', 'PO4'],
    'ENVIR-META': ['PB', 'CD', 'CR_TOT', 'CRVI', 'NI', 'CU', 'ZN', 'AS', 'HG', 'SE', 'SB'],
    'ENVIR-CROM': ['CR_TOT', 'CRVI'],
    'ENVIR-IDRO': ['HC_TOT', 'HC_LEG'],
    'ENVIR-IPAS': ['NAPH', 'ACENP', 'FLRN', 'PYRE', 'BAP', 'IPA_TOT'],
    'ENVIR-POPS': ['DDT_TOT', 'ALDRIN', 'DIELDR'],
    'ENVIR-DIOX': ['PCDD_TEQ', 'TCDD'],
    'ENVIR-PCBS': ['PCB_TOT', 'PCB28', 'PCB52', 'PCB101', 'PCB138', 'PCB153', 'PCB180'],
    'MICRO-POTW': ['ECOLI', 'COLIT', 'ENTEROC', 'CBT'],
    'MICRO-WASW': ['ECOLI', 'COLIT', 'ENTEROC'],
    'MICRO-SURW': ['ECOLI', 'COLIT', 'ENTEROC', 'CBT'],
    'MICRO-LEGW': ['LEGSP', 'LEGPN'],
    'MICRO-FOOD': ['ECOLI_F', 'SALM', 'LISTM'],
    'AIR-VOCA':   ['BENZ_A', 'TOLU_A', 'EBNZ_A', 'XYL_A', 'STIR_A'],
    'AIR-VOFI':   ['BENZ_A', 'TOLU_A', 'EBNZ_A', 'XYL_A'],
    'AIR-EMIS':   ['PM_TOT', 'SO2', 'NOX', 'CO_E', 'HCL_E', 'HF_E'],
    'AIR-VOTD':   ['BENZ_A', 'TOLU_A', 'EBNZ_A', 'XYL_A', 'TCE', 'PCE'],
    'PETR-FUEL':  ['RON', 'DENS15', 'PVAP', 'PFLAS'],
    'PETR-BITU':  ['DENS15', 'PFLAS', 'PPOUR'],
    'PETR-LUBE':  ['VIS40', 'VIS100', 'PPOUR'],
    'GAS-GASQ':   ['CH4', 'C2H6', 'C3H8', 'C4H10', 'CO2_G', 'N2_G', 'H2S_G', 'PCS'],
    'GAS-PGPL':   ['C3H8', 'C4H10', 'CO2_G', 'N2_G'],
    'GAS-GRAF':   ['CH4', 'C2H6', 'C3H8', 'H2S_G', 'CO2_G'],
    'WASTE-LETE': ['PB', 'CD', 'NI', 'ZN', 'AS', 'COD', 'NH4', 'NO3'],
    'WASTE-CSSE': ['N_TOT', 'P2O5', 'C_ORG', 'CN_RAP', 'PH_S', 'PB', 'CD', 'CU', 'ZN'],
    'PROD-COMP':  ['N_TOT', 'P2O5', 'K2O', 'C_ORG_P', 'CN_RAP', 'PH_S'],
    'PROD-FERT':  ['N_TOT', 'P2O5', 'K2O'],
}


# ─── FUNZIONI DI SEED ─────────────────────────────────────────────────────────

def _cycle_prefix(cycle_code: str) -> str:
    """Estrae il prefisso CATEGORY-TYPE da un codice ciclo (es. WATER-CIAC-25 → WATER-CIAC)."""
    parts = cycle_code.rsplit('-', 1)
    return parts[0] if len(parts) == 2 else cycle_code


def seed_units(db, Unit):
    created = 0
    for code, description in UNITS:
        if not Unit.query.filter_by(code=code).first():
            db.session.add(Unit(code=code, description=description))
            created += 1
    db.session.commit()
    print(f"  Unità di misura: {created} nuove")


def seed_matrices(db, Matrix):
    created = 0
    for code, description in MATRICES:
        if not Matrix.query.filter_by(code=code).first():
            db.session.add(Matrix(code=code, description=description))
            created += 1
    db.session.commit()
    print(f"  Matrici: {created} nuove")


def seed_provider(db, Provider):
    if not Provider.query.filter_by(code='UNICHIM').first():
        db.session.add(Provider(
            code='UNICHIM',
            name='UNICHIM - Associazione per l\'Unificazione nel settore dell\'Industria Chimica',
        ))
        db.session.commit()
        print("  Provider UNICHIM creato")
    else:
        print("  Provider UNICHIM già presente")


def seed_parameters(db, Parameter):
    created = 0
    for code, name, unit_code, matrix_text in PARAMETERS:
        if not Parameter.query.filter_by(code=code).first():
            db.session.add(Parameter(
                code=code,
                name=name,
                unit_code=unit_code,
                matrix=matrix_text,
                active=True,
            ))
            created += 1
    db.session.commit()
    print(f"  Parametri: {created} nuovi")


def seed_cycles_and_params(db, Cycle, CycleParameter, Provider, Parameter):
    provider = Provider.query.filter_by(code='UNICHIM').first()
    provider_id = provider.id if provider else None

    cycles_created = 0
    links_created = 0
    links_skipped = 0

    for code, name, status, start_date, end_date in CYCLES:
        cycle = Cycle.query.filter_by(code=code).first()
        if not cycle:
            cycle = Cycle(
                code=code,
                name=name,
                status=status,
                start_date=start_date,
                end_date=end_date,
                provider_id=provider_id,
            )
            db.session.add(cycle)
            db.session.flush()  # per avere cycle.code disponibile subito
            cycles_created += 1

        # Associa parametri tramite il prefisso
        prefix = _cycle_prefix(code)
        param_codes = CYCLE_PARAMETERS.get(prefix, [])

        for param_code in param_codes:
            param = Parameter.query.filter_by(code=param_code).first()
            if not param:
                print(f"    [WARN] Parametro {param_code} non trovato, saltato per {code}")
                links_skipped += 1
                continue

            existing = CycleParameter.query.filter_by(
                cycle_code=code, parameter_code=param_code
            ).first()
            if not existing:
                db.session.add(CycleParameter(
                    cycle_code=code,
                    parameter_code=param_code,
                    xpt=0.0,       # placeholder – aggiornare con valore UNICHIM
                    sigma_pt=1.0,  # placeholder – aggiornare con valore UNICHIM
                ))
                links_created += 1

    db.session.commit()
    print(f"  Cicli: {cycles_created} nuovi")
    print(f"  Associazioni ciclo-parametro: {links_created} nuove" +
          (f" ({links_skipped} saltate per parametro mancante)" if links_skipped else ""))


def print_summary(Cycle, Parameter, Matrix, Unit, CycleParameter):
    print()
    print("=" * 55)
    print("RIEPILOGO DATABASE UNICHIM")
    print("=" * 55)
    print(f"  Unità di misura ........... {Unit.query.count():>5}")
    print(f"  Matrici ................... {Matrix.query.count():>5}")
    print(f"  Parametri ................. {Parameter.query.count():>5}")
    print(f"  Cicli totali .............. {Cycle.query.count():>5}")
    print(f"    di cui published ......... {Cycle.query.filter_by(status='published').count():>4}")
    print(f"    di cui draft ............. {Cycle.query.filter_by(status='draft').count():>4}")
    print(f"  Associazioni ciclo-param .. {CycleParameter.query.count():>5}")
    print("=" * 55)
    print()
    print("NOTA: xpt e sigma_pt sono placeholder (0.0 / 1.0).")
    print("Aggiornare con i valori assegnati da UNICHIM dopo")
    print("aver ricevuto il materiale di prova del ciclo.")
    print("=" * 55)


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    from dotenv import load_dotenv
    load_dotenv(root_dir / '.env')

    from app import create_app, db
    from app.models import Unit, Matrix, Parameter, Provider, Cycle, CycleParameter

    app = create_app()

    print("Seed UNICHIM - cicli PT 2024/2025 e 2025/2026")
    print("=" * 55)

    with app.app_context():
        try:
            seed_provider(db, Provider)
            seed_units(db, Unit)
            seed_matrices(db, Matrix)
            seed_parameters(db, Parameter)
            seed_cycles_and_params(db, Cycle, CycleParameter, Provider, Parameter)
            print_summary(Cycle, Parameter, Matrix, Unit, CycleParameter)
            print("Seed completato.")
        except Exception as exc:
            db.session.rollback()
            print(f"ERRORE: {exc}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == '__main__':
    main()
