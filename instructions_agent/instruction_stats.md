# 📊 Agent Instruction — VS Code Module `stats_bp` (MVP)

## 🎯 Objective
Implement the **Statistics Module** (`stats_bp`) for each laboratory, enabling:
1. Download of a **CSV template** for result entry;
2. **Upload** of published cycle results (validated by admin);
3. **Synchronous calculation** of z-score, sz², rsz, and derived statistics;
4. **Graphical visualization** (control charts ±3).

All within a multi-lab logic, protected by roles and modular blueprints.

---

## 📁 Structure to Create
```
app/
    blueprints/
        stats/
            __init__.py
            routes_stats.py
            services_stats.py  # calculation logic (pandas)
            templates/stats/
                upload_form.html
                results_table.html
                charts.html
            static/
                plots/  # optional: temp image storage
```

---

## 🔐 Security & Permissions
- All routes under `stats_bp` require:
    - `@login_required`
    - `@lab_role_required("analyst")` (minimum for upload/calculation)
    - `@lab_role_required("viewer")` for viewing charts only

---

## 🧩 Blueprint `stats_bp`
File: `app/blueprints/stats/routes_stats.py`

```python
from flask import Blueprint, render_template, request, send_file, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Lab, Cycle, CycleParameter, Result, ZScore, PtStats, UploadFile
from app.blueprints.auth.decorators import lab_role_required
from app.blueprints.stats.services_stats import process_results_csv
from datetime import datetime
import io

stats_bp = Blueprint("stats_bp", __name__, url_prefix="/l/<lab_code>/stats")
```

### 1️⃣ Route: Download Template CSV
**GET /l/<lab_code>/stats/template.csv**

- Provides labs with a CSV template matching published cycle parameters.
- Logic:
    - Fetch latest published Cycle.
    - For each CycleParameter, extract `parameter_code`, `assigned_xpt`, `assigned_spt`.
    - Generate CSV in memory (`io.StringIO`) with columns:
        ```
        parameter_code, result_value, technique_code, unit_code, date_performed
        ```
    - Send file with `Content-Disposition: attachment; filename=template_<lab_code>.csv`

### 2️⃣ Route: Upload Results
**GET/POST /l/<lab_code>/stats/upload**

- **GET:** Show upload form (`upload_form.html`) with description and file input.
- **POST:** 
    - Read uploaded file (`request.files["file"]`)
    - Pass to `process_results_csv()` (in `services_stats.py`)
    - Receives:
        - `df_clean`
        - `stats_summary` (dict)
    - Insert into DB:
        - `UploadFile` record (filename, rows, received_at, lab_code, user_id)
        - `Result`, `ZScore`, `PtStats` records
    - Flash success + redirect to `/l/<lab_code>/stats/results`

**Template `upload_form.html`:** Bootstrap form with file input and "Upload & Calculate" button.

### 3️⃣ Calculation Service (Pandas)
File: `app/blueprints/stats/services_stats.py`

Main function:
```python
def process_results_csv(file_stream, lab_code):
        import pandas as pd, numpy as np
        from datetime import datetime
        from io import StringIO
        MAD_K = 1.4826

        df = pd.read_csv(file_stream)
        df.columns = df.columns.str.strip().str.lower()

        # Basic validation
        required = ["parameter_code", "result_value"]
        missing = [c for c in required if c not in df.columns]
        if missing:
                raise ValueError(f"Missing required columns: {missing}")

        df["result_value"] = pd.to_numeric(df["result_value"], errors="coerce")
        df.dropna(subset=["result_value"], inplace=True)

        # Fetch XPT and SPT from DB (simulate here)
        df["xpt"] = df["parameter_code"].map(lambda _: 100.0)
        df["spt"] = df["parameter_code"].map(lambda _: 5.0)

        # Calculations
        df["z"] = (df["result_value"] - df["xpt"]) / df["spt"]
        df["sz2"] = df["z"] ** 2
        df["rsz"] = MAD_K * np.median(np.abs(df["z"] - np.median(df["z"])))

        summary = {
                "rows": len(df),
                "mean_z": df["z"].mean(),
                "median_z": df["z"].median(),
                "max_abs_z": df["z"].abs().max(),
                "rsz": df["rsz"].iloc[0],
        }

        return df, summary
```

### 4️⃣ Route: Results Visualization
**GET /l/<lab_code>/stats/results**

- Fetch latest results (`Result`) and related `ZScore`, `PtStats`.
- Render `results_table.html`:
    - Columns: `parameter_code`, `result_value`, `z`, `sz2`, `rsz`
    - Conditional coloring:
        - |Z| < 2 → green
        - 2 ≤ |Z| < 3 → orange
        - |Z| ≥ 3 → red

### 5️⃣ Route: Control Charts
**GET /l/<lab_code>/stats/charts**

- Query `ZScore` for `lab_code` ordered by date/cycle.
- Generate chart (Plotly):
    - X-axis: cycle or date
    - Y-axis: z
    - Lines: CL=0, UCL/LCL=±3
    - Point color by z value
- Render `charts.html` with embedded Plotly chart.

**Template `charts.html`:**
```jinja2
<h4>Z-Score Control Chart</h4>
<div id="chart-div">{{ plot_div|safe }}</div>
```

**Plotly (in service):**
```python
import plotly.graph_objects as go
fig = go.Figure()
fig.add_trace(go.Scatter(x=df['date_performed'], y=df['z'], mode='markers+lines', name='Z-score'))
fig.add_hline(y=0, line=dict(color='green', width=1))
fig.add_hline(y=3, line=dict(color='red', dash='dash'))
fig.add_hline(y=-3, line=dict(color='red', dash='dash'))
plot_div = fig.to_html(full_html=False)
```

---

## 🌱 Seed (Optional Update)
Add to `seed_data.py`:
- Some fake `Result` and `ZScore` for 1 lab (`lab_alpha`)
- Random values ±2 for parameters NH4, NO3, TOC
- `upload_file` with recent date

---

## 🧪 Manual Test
- Login as user with analyst role.
- `/l/lab_alpha/stats/template.csv` downloadable and correct.
- Upload CSV → calculation completes; results visible at `/stats/results`.
- `/stats/charts` shows ±3 control chart.
- Viewer user → can only see `/results` and `/charts`, not `/upload`.
- Non-lab user → 403 on all blueprint routes.

---

## ✅ Acceptance Criteria
- Template generated correctly from active cycle parameters.
- Upload works, calculation performed in pandas.
- Data saved in `Result`, `ZScore`, `PtStats`.
- Plotly chart integrated and working.
- All permissions respected.
