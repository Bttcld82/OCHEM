"""
Seed tecniche e parametri anagrafici per i circuiti CIAC e META.
Non tocca i CycleParameter: l'associazione ai cicli va fatta dall'admin.

Esecuzione:
    python scripts/seed_ciac_meta_anagrafica.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Technique, Parameter, Unit

app = create_app()

# ---------------------------------------------------------------------------
# DATI
# ---------------------------------------------------------------------------

TECNICHE_DA_AGGIUNGERE = [
    # code, name
    ("ICP-OES",  "Spettrometria di emissione ottica al plasma (ICP-OES)"),
    ("GF-AAS",   "Spettrometria di assorbimento atomico con fornetto di grafite (GF-AAS)"),
    ("F-AAS",    "Spettrometria di assorbimento atomico in fiamma (F-AAS)"),
    ("CONDU",    "Conduttimetria"),
    ("UV-VIS",   "Spettrometria UV-Visibile (UV-VIS)"),
    ("IR",       "Spettrometria all'infrarosso (IR)"),
    ("IC",       "Cromatografia ionica (IC)"),   # alias del CROMATO già presente
]

# Parametri da creare se non già presenti.
# (code, name, unit_code, descrizione)
# unit_code deve corrispondere a Unit.code nel DB.
#
# Nota: COND, PH, COD, TOC, CLOR, SO4, NO3 già presenti nel DB → si saltano.

PARAMETRI_CIAC = [
    # Metalli in acqua (µg/L)
    ("AL",      "Alluminio (Al)",                       "µg/L",    "Alluminio in acqua"),
    ("AS_W",    "Arsenico in acqua (As)",               "µg/L",    "Arsenico in acqua - circuito CIAC"),
    ("B_W",     "Boro (B)",                             "µg/L",    "Boro in acqua"),
    ("CD_W",    "Cadmio in acqua (Cd)",                 "µg/L",    "Cadmio in acqua - circuito CIAC"),
    ("CR_W",    "Cromo totale in acqua (Cr tot)",       "µg/L",    "Cromo totale in acqua - circuito CIAC"),
    ("CRVI_W",  "Cromo esavalente in acqua (Cr VI)",    "µg/L",    "Cromo esavalente in acqua - circuito CIAC"),
    ("CU_W",    "Rame in acqua (Cu)",                   "µg/L",    "Rame in acqua - circuito CIAC"),
    ("FE_W",    "Ferro in acqua (Fe)",                  "µg/L",    "Ferro in acqua - circuito CIAC"),
    ("HG_W",    "Mercurio in acqua (Hg)",               "µg/L",    "Mercurio in acqua - circuito CIAC"),
    ("MN_W",    "Manganese in acqua (Mn)",              "µg/L",    "Manganese in acqua - circuito CIAC"),
    ("NI_W",    "Nichel in acqua (Ni)",                 "µg/L",    "Nichel in acqua - circuito CIAC"),
    ("PB_W",    "Piombo in acqua (Pb)",                 "µg/L",    "Piombo in acqua - circuito CIAC"),
    ("SB_W",    "Antimonio in acqua (Sb)",              "µg/L",    "Antimonio in acqua - circuito CIAC"),
    ("SE_W",    "Selenio in acqua (Se)",                "µg/L",    "Selenio in acqua - circuito CIAC"),
    ("U_W",     "Uranio (U)",                           "µg/L",    "Uranio in acqua"),
    ("V_W",     "Vanadio in acqua (V)",                 "µg/L",    "Vanadio in acqua - circuito CIAC"),
    ("ZN_W",    "Zinco in acqua (Zn)",                  "µg/L",    "Zinco in acqua - circuito CIAC"),
    # Ioni e altri in acqua (mg/L)
    ("BRO",     "Bromuri",                              "mg/L",    "Bromuri in acqua"),
    ("CA",      "Calcio (Ca)",                          "mg/L",    "Calcio in acqua"),
    ("DUR_F",   "Durezza totale",                       "F°",      "Durezza in gradi francesi"),
    ("FLUO",    "Fluoruri",                             "mg/L",    "Fluoruri in acqua"),
    ("FOS_T",   "Fosforo totale",                       "mg/L",    "Fosforo totale in acqua"),
    ("IOD",     "Ioduri",                               "mg/L",    "Ioduri in acqua"),
    ("K_W",     "Potassio (K)",                         "mg/L",    "Potassio in acqua"),
    ("MG_W",    "Magnesio (Mg)",                        "mg/L",    "Magnesio in acqua"),
    ("NA_W",    "Sodio (Na)",                           "mg/L",    "Sodio in acqua"),
    ("NH4_W",   "Ammonio (NH4+)",                       "mg/L",    "Ammonio in acqua - circuito CIAC"),
    ("NITR",    "Nitrati (NO3-)",                       "mg/L",    "Nitrati in acqua naturale"),
    ("NTOT_W",  "Azoto totale (N tot)",                 "mg/L",    "Azoto totale in acqua di scarico"),
]

# Parametri META mancanti (mg/kg s.s.)
PARAMETRI_META_NUOVI = [
    ("BE",      "Berillio (Be)",        "mg/kg",   "Berillio in matrici ambientali"),
    ("CO",      "Cobalto (Co)",         "mg/kg",   "Cobalto in matrici ambientali"),
    ("SN",      "Stagno (Sn)",          "mg/kg",   "Stagno in matrici ambientali"),
    ("TL",      "Tallio (Tl)",          "mg/kg",   "Tallio in matrici ambientali"),
    ("V_KG",    "Vanadio (V)",          "mg/kg",   "Vanadio in matrici ambientali"),
]

# ---------------------------------------------------------------------------
# LOGICA
# ---------------------------------------------------------------------------

def seed():
    with app.app_context():
        added_tech = []
        skipped_tech = []
        added_params = []
        skipped_params = []
        errors = []

        # ------------------------------------------------------------------
        # 1. Tecniche
        # ------------------------------------------------------------------
        # Codice IC è già presente come CROMATO - aggiungo con code IC solo
        # se non esiste per permettere referenza diretta dai dati Excel
        existing_codes = {t.code for t in Technique.query.all()}

        for code, name in TECNICHE_DA_AGGIUNGERE:
            if code in existing_codes:
                skipped_tech.append(code)
                continue
            # IC è concettualmente alias di CROMATO - lo aggiungo comunque
            # con un code diverso per completezza lookup
            t = Technique(code=code, name=name)
            db.session.add(t)
            added_tech.append(code)

        # ------------------------------------------------------------------
        # 2. Verifica unità
        # ------------------------------------------------------------------
        unit_codes = {u.code for u in Unit.query.all()}

        # Aggiungo unità mancanti se necessario
        needed_units = set()
        for params_list in [PARAMETRI_CIAC, PARAMETRI_META_NUOVI]:
            for _, _, unit_code, _ in params_list:
                needed_units.add(unit_code)

        for u in needed_units:
            if u not in unit_codes:
                errors.append(f"UNITÀ MANCANTE: '{u}' — aggiungila prima dalla UI")

        if errors:
            print("ERRORI DA RISOLVERE PRIMA:")
            for e in errors:
                print(f"  {e}")
            return

        # ------------------------------------------------------------------
        # 3. Parametri
        # ------------------------------------------------------------------
        existing_param_codes = {p.code for p in Parameter.query.all()}

        for params_list in [PARAMETRI_CIAC, PARAMETRI_META_NUOVI]:
            for code, name, unit_code, description in params_list:
                if code in existing_param_codes:
                    skipped_params.append(code)
                    continue
                p = Parameter(
                    code=code,
                    name=name,
                    unit_code=unit_code,
                    description=description,
                    active=True,
                )
                db.session.add(p)
                added_params.append(code)

        db.session.commit()

        # ------------------------------------------------------------------
        # Report
        # ------------------------------------------------------------------
        print("=" * 60)
        print("SEED COMPLETATO")
        print("=" * 60)
        print(f"\nTECNICHE aggiunte ({len(added_tech)}):  {added_tech}")
        print(f"Tecniche già presenti ({len(skipped_tech)}): {skipped_tech}")
        print(f"\nPARAMETRI aggiunti ({len(added_params)}):")
        for c in added_params:
            print(f"  {c}")
        print(f"\nParametri già presenti ({len(skipped_params)}): {skipped_params}")
        print()
        print("PROSSIMO STEP: dall'admin associa i parametri ai cicli WATER-CIAC-25/26 e ENVIR-META-29/30")
        print("Parametri CIAC riutilizzabili già in DB: COND, PH, COD, TOC, CLOR, SO4, NO3")
        print("Parametri META già in DB: AS, CD, CR_TOT, CU, HG, NI, PB, SB, SE, ZN")


if __name__ == "__main__":
    seed()
