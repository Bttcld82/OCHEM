# OCHEM

Piattaforma web per la gestione di **Proficiency Testing (PT)** tra laboratori chimici.

---

## Utenti di Test

Server di sviluppo: **http://127.0.0.1:5000**

### Amministratore

| Email | Password | Ruolo | Note |
|-------|----------|-------|------|
| `admin@ochem.com` | `admin123` | Admin globale | Consigliato |
| `admin@ochem.local` | `admin123` | Admin globale | Può dare problemi di validazione nel browser |

Accesso completo al pannello `/admin`: cicli, laboratori, parametri, utenti.

---

### Utenti Laboratorio

Tutti con password: **`password123`**

| Email | Nome | Ruolo | Laboratorio |
|-------|------|-------|-------------|
| `owner_lab_alpha@ochem.local` | Owner LAB_ALPHA | `owner_lab` | LAB_ALPHA |
| `analyst1@ochem.local` | Mario Rossi | `analyst` | LAB_ALPHA |
| `analyst2@ochem.local` | Luigi Bianchi | `analyst` | LAB_ALPHA |
| `viewer1@ochem.local` | Paolo Verdi | `viewer` | LAB_ALPHA |
| `viewer2@ochem.local` | Anna Neri | `viewer` | LAB_ALPHA |

#### Permessi per Ruolo

| Ruolo | Inserire dati | Modificare dati | Vedere statistiche | Invitare utenti |
|-------|:---:|:---:|:---:|:---:|
| `owner_lab` | ✓ | ✓ | ✓ | ✓ |
| `analyst` | ✓ | ✓ | ✓ | ✗ |
| `viewer` | ✗ | ✗ | ✓ | ✗ |

---

### Utenti Senza Password (non utilizzabili per il login)

Creati da vecchi script di seed, privi di password hash.

| Email | Note |
|-------|------|
| `mario.rossi@alpha.it` | Nessuna password impostata |
| `luigi.bianchi@beta.it` | Nessuna password impostata |

---

## Laboratori Disponibili

| Codice | Nome |
|--------|------|
| `LAB_ALPHA` | Laboratorio Alpha |
| `LAB_BETA` | Laboratorio Beta |
| `LAB_GAMMA` | Laboratorio Gamma |
| `LAB_DELTA` | Laboratorio Delta |
| `LAB_EPSILON` | Laboratorio Epsilon |

> Solo **LAB_ALPHA** ha utenti assegnati. Gli altri lab sono presenti in anagrafica
> ma non hanno ancora partecipanti.

---

## Link Utili

| Pagina | URL |
|--------|-----|
| Homepage | http://127.0.0.1:5000 |
| Login | http://127.0.0.1:5000/auth/login |
| Dashboard utente | http://127.0.0.1:5000/dashboard |
| Pannello Admin | http://127.0.0.1:5000/admin |
| Hub LAB_ALPHA | http://127.0.0.1:5000/l/LAB_ALPHA |
| Guida | http://127.0.0.1:5000/help |
