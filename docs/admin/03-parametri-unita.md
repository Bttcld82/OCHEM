---
title: "Parametri, Unità e Tecniche"
description: "Configurare l'anagrafica degli analiti, delle unità di misura e dei metodi analitici"
tags: [admin, parametri, unita, tecniche, anagrafica]
role: admin
order: 3
related:
  - admin/01-cicli
  - admin/00-panoramica
---

# Parametri, Unità e Tecniche

Prima di poter creare cicli PT, è necessario popolare l'**anagrafica** con gli elementi
che descrivono le misurazioni: analiti (parametri), unità di misura e metodi analitici (tecniche).

## Parametri Analitici

Un **parametro** rappresenta l'analita misurato (es. Cadmio, pH, Piombo, Azoto totale).

Vai su **Admin → Parametri → Nuovo** (`/admin/parameters/new`).

| Campo | Note |
|-------|------|
| Codice | Abbreviazione univoca (es. `CD`, `PH`) |
| Nome | Denominazione completa |
| Unità di misura | Collegata dalla lista Unità |
| Descrizione | Facoltativa |

I parametri vengono poi associati ai singoli cicli (con i valori `xpt` e `sigma_pt`).

## Unità di Misura

Le **unità** definiscono la grandezza in cui viene espresso il risultato (es. mg/L, µg/kg, pH).

Vai su **Admin → Unità → Nuova** (`/admin/units/new`).

| Campo | Esempio |
|-------|---------|
| Codice | `MGL` |
| Simbolo | `mg/L` |
| Nome | Milligrammi per litro |

## Tecniche Analitiche

La **tecnica** è il metodo strumentale usato dal laboratorio per la misura
(es. ICP-MS, AAS, HPLC, Titolazione).

Vai su **Admin → Tecniche → Nuova** (`/admin/techniques/new`).

| Campo | Esempio |
|-------|---------|
| Codice | `ICPMS` |
| Nome | ICP-Mass Spectrometry |

> La tecnica viene indicata dal laboratorio al momento dell'inserimento del risultato.
> Non influisce sul calcolo statistico, ma è utile per l'analisi dei dati.

## Matrici

Le **matrici** descrivono il campione analizzato (es. Acqua potabile, Suolo, Alimenti).

Vai su **Admin → Matrici** per gestirle.

## Ordine Consigliato di Configurazione

```
1. Unità di misura
2. Parametri (associando l'unità)
3. Tecniche
4. Matrici
5. Provider
→ Poi: Laboratori e Cicli
```

## Vedi anche

- [[admin/01-cicli|Gestione Cicli]] — come associare parametri a un ciclo con xpt e sigma_pt
