# Ruolo Owner Lab

L'**Owner Lab** e' il responsabile del laboratorio sulla piattaforma.

## Permessi

| Azione | Consentita |
|--------|-----------|
| Tutto cio' che fa un [[Ruolo Analyst\|Analyst]] | Si |
| Gestire gli utenti del laboratorio | Si |
| Invitare nuovi utenti al laboratorio | Si |
| Cambiare ruoli degli utenti del lab | Si |
| Rimuovere utenti dal laboratorio | Si |

## Vincoli di sicurezza

> [!warning] Ultimo Owner
> Deve esserci sempre almeno **un Owner** per ogni laboratorio. Il sistema impedisce di:
> - Rimuovere l'ultimo owner di un laboratorio
> - Cambiare il ruolo dell'ultimo owner a un livello inferiore

## Quando viene assegnato

- Automaticamente quando un utente registra un **nuovo laboratorio**
- Manualmente da un admin tramite il pannello di gestione

## Vedi anche
- [[Panoramica ruoli]]
- [[Ruolo Analyst]]
- [[Ruolo Admin]]
