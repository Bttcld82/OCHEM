import requests

s = requests.Session()

# Login come analyst1
r = s.post(
    'http://127.0.0.1:5000/auth/login',
    data={'email': 'analyst1@ochem.local', 'password': 'password123'},
    allow_redirects=True
)
print('Login URL finale:', r.url)

# 3 inserimenti per ciclo 2025-01 / LAB_ALPHA
dati = [
    ('NH4',  'SPETTRO', '2.48',  '0.05', 'Test NH4'),
    ('NO3',  'CROMATO', '14.85', '0.20', 'Test NO3'),
    ('TOC',  'POTENZ',  '12.30', '0.10', 'Test TOC'),
]

for param, tecnica, valore, incertezza, note in dati:
    r = s.post(
        'http://127.0.0.1:5000/dati/LAB_ALPHA/insert',
        data={
            'cycle_code':      '2025-01',
            'parameter_code':  param,
            'technique_code':  tecnica,
            'measured_value':  valore,
            'uncertainty':     incertezza,
            'notes':           note,
        },
        allow_redirects=True
    )
    print(f'{param}: HTTP {r.status_code}  ->  {r.url}')
