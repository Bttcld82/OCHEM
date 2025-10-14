/**
 * Control Charts JavaScript Module
 * Gestisce i grafici di controllo Z-Score con filtri multipli
 */

// Variabili globali per lo stato dell'applicazione
let currentTablePage = 1;
const tablePerPage = 25;
let refreshInterval;

// ===== INIZIALIZZAZIONE =====

document.addEventListener('DOMContentLoaded', function() {
    // Crea sempre il grafico vuoto all'inizializzazione
    createEmptyChart();
    
    // Carica i filtri e inizializza i dati
    initializeFiltersAndData();
    
    // Carica i dati del grafico dopo un breve delay
    setTimeout(() => {
        updateChart(); // Carica i dati iniziali con tutti i parametri
    }, 500);
    
    // Avvia auto-refresh
    startAutoRefresh();
});

// Inizializza i filtri al caricamento pagina
function initializeFiltersAndData() {
    // Carica le opzioni iniziali per i filtri
    loadFilterOptions();
    
    // Aggiorna contatori iniziali
    updateFilterStats();
    
    // Carica dati iniziali della tabella
    loadTableData(1);
}

// ===== GESTIONE GRAFICO =====

// Crea un grafico vuoto all'inizializzazione
function createEmptyChart() {
    const emptyData = [{
        x: [],
        y: [],
        mode: 'markers+lines',
        type: 'scatter',
        name: 'Z-Score',
        marker: {
            color: [],
            size: 8
        },
        line: {
            color: 'rgba(100,100,100,0.5)',
            width: 1
        }
    }];
    
    const layout = {
        title: {
            text: 'Control Chart - Z-Score nel Tempo',
            font: { size: 16 }
        },
        xaxis: {
            title: 'Data/Ora',
            type: 'date'
        },
        yaxis: {
            title: 'Z-Score',
            zeroline: true,
            zerolinecolor: 'rgba(0,0,0,0.1)',
            range: [-4, 4]  // Range di default per z-scores
        },
        hovermode: 'closest',
        showlegend: true,
        legend: {
            x: 0.02,
            y: 0.98,
            bgcolor: 'rgba(255,255,255,0.8)'
        },
        margin: { t: 60, r: 40, b: 60, l: 60 },
        plot_bgcolor: 'rgba(248,249,250,1)',
        paper_bgcolor: 'white',
        font: { family: 'system-ui, -apple-system, sans-serif', size: 12 }
    };
    
    const config = {
        displayModeBar: true,
        displaylogo: false,
        modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d', 'autoScale2d'],
        toImageButtonOptions: {
            format: 'png',
            filename: `control_chart_${window.labCode}_${new Date().toISOString().split('T')[0]}`,
            height: 600,
            width: 1200,
            scale: 2
        }
    };
    
    Plotly.newPlot('control-chart', emptyData, layout, config);
}

// Funzione per aggiornare il grafico via AJAX con multifiltri
function updateChart() {
    const selectedParams = getSelectedValues('parameters-filter');
    const selectedTechniques = getSelectedValues('techniques-filter');
    const selectedCycles = getSelectedValues('cycles-filter');
    const daysFilter = document.getElementById('days-filter').value;
    const updateBtn = document.getElementById('update-btn');
    const updateText = document.getElementById('update-text');
    
    // Mostra loading
    updateBtn.disabled = true;
    updateText.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Caricamento...';
    
    // Costruisci parametri URL
    const params = new URLSearchParams();
    selectedParams.forEach(p => params.append('parameters[]', p));
    selectedTechniques.forEach(t => params.append('techniques[]', t));
    selectedCycles.forEach(c => params.append('cycles[]', c));
    if (daysFilter) params.append('days', daysFilter);
    
    // Costruisci URL API
    const apiUrl = `/l/${window.labCode}/stats/api/chart-data?${params.toString()}`;
    
    fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Aggiorna il grafico con i nuovi dati
                updatePlotlyChart(data.data);
                
                // Aggiorna le statistiche con i filtri correnti
                updateStatistics();
                
                // Aggiorna la tabella risultati
                loadTableData(1);
                
                // Aggiorna il titolo del grafico con i filtri selezionati
                updateChartTitle(data.filters);
            } else {
                console.error('Errore API:', data.error);
                alert('Errore nel caricamento dati: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Errore di connessione:', error);
            alert('Errore di connessione. Riprova.');
        })
        .finally(() => {
            updateBtn.disabled = false;
            updateText.innerHTML = '<i class="fas fa-sync-alt"></i> Aggiorna Grafico';
        });
}

// Funzione per aggiornare il grafico Plotly
function updatePlotlyChart(chartData) {
    const chartDiv = document.getElementById('control-chart');
    
    if (!chartData.x || chartData.x.length === 0) {
        // Mostra messaggio "nessun dato"
        chartDiv.innerHTML = `
            <div class="d-flex flex-column align-items-center justify-content-center" style="height: 400px;">
                <div class="text-center text-muted">
                    <i class="fas fa-chart-line fa-4x mb-3 opacity-50"></i>
                    <h5>Nessun Dato Disponibile</h5>
                    <p>Non sono presenti dati per generare il grafico di controllo.<br>
                    Carica alcuni risultati per visualizzare i grafici.</p>
                    <button class="btn btn-primary btn-sm" onclick="window.location.href='/l/${window.labCode}/stats/upload'">
                        <i class="fas fa-upload"></i> Carica Risultati
                    </button>
                </div>
            </div>
        `;
        return;
    }
    
    // Prepara i dati per Plotly
    const trace1 = {
        x: chartData.x,
        y: chartData.y,
        mode: 'markers+lines',
        type: 'scatter',
        name: 'Z-Score',
        marker: {
            color: chartData.colors,
            size: 8,
            line: { color: 'rgba(0,0,0,0.3)', width: 1 }
        },
        line: { width: 2, color: 'rgba(31,119,180,0.8)' },
        hovertemplate: '<b>%{text}</b><br>Z-Score: %{y:.3f}<br>Data: %{x}<extra></extra>',
        text: chartData.parameter_codes
    };
    
    // Linee di controllo
    const xRange = chartData.x;
    const traces = [trace1];
    
    if (xRange.length > 0) {
        traces.push({
            x: [xRange[0], xRange[xRange.length-1]],
            y: [3, 3],
            mode: 'lines',
            type: 'scatter',
            name: 'Limite +3σ',
            line: { color: 'red', width: 2, dash: 'dash' },
            hoverinfo: 'skip'
        });
        
        traces.push({
            x: [xRange[0], xRange[xRange.length-1]],
            y: [-3, -3],
            mode: 'lines',
            type: 'scatter',
            name: 'Limite -3σ',
            line: { color: 'red', width: 2, dash: 'dash' },
            hoverinfo: 'skip'
        });
        
        traces.push({
            x: [xRange[0], xRange[xRange.length-1]],
            y: [0, 0],
            mode: 'lines',
            type: 'scatter',
            name: 'Target (z=0)',
            line: { color: 'green', width: 1, dash: 'dot' },
            hoverinfo: 'skip'
        });
    }
    
    const layout = {
        title: {
            text: 'Control Chart - Z-Score nel Tempo',
            font: { size: 16, color: '#333' }
        },
        xaxis: {
            title: 'Data/Ora',
            type: 'date',
            gridcolor: 'rgba(128,128,128,0.2)'
        },
        yaxis: {
            title: 'Z-Score',
            zeroline: true,
            zerolinecolor: 'rgba(0,0,0,0.3)',
            gridcolor: 'rgba(128,128,128,0.2)'
        },
        hovermode: 'closest',
        showlegend: true,
        legend: { x: 0.02, y: 0.98, bgcolor: 'rgba(255,255,255,0.8)' },
        margin: { t: 60, r: 40, b: 60, l: 60 },
        plot_bgcolor: 'rgba(248,249,250,1)',
        paper_bgcolor: 'white'
    };
    
    const config = {
        responsive: true,
        displayModeBar: true,
        modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
        displaylogo: false
    };
    
    Plotly.react(chartDiv, traces, layout, config);
}

function updateChartTitle(filters) {
    const chartHeader = document.querySelector('.card-header h5');
    let newTitle = '<i class="fas fa-chart-line"></i> Control Chart Z-Score';
    
    const filterParts = [];
    
    if (filters.parameters && filters.parameters.length > 0) {
        const paramText = filters.parameters.length === 1 ? filters.parameters[0] : `${filters.parameters.length} parametri`;
        filterParts.push(`📊 ${paramText}`);
    }
    
    if (filters.techniques && filters.techniques.length > 0) {
        filterParts.push(`⚗️ ${filters.techniques.length} ${filters.techniques.length === 1 ? 'tecnica' : 'tecniche'}`);
    }
    
    if (filters.cycles && filters.cycles.length > 0) {
        filterParts.push(`🔄 ${filters.cycles.length} ${filters.cycles.length === 1 ? 'ciclo' : 'cicli'}`);
    }
    
    if (filterParts.length > 0) {
        newTitle += ` - ${filterParts.join(', ')}`;
    }
    chartHeader.innerHTML = newTitle;
}

// ===== UTILITÀ GRAFICO =====

function downloadChart() {
    Plotly.downloadImage('control-chart', {
        format: 'png',
        width: 1200,
        height: 600,
        filename: `control_chart_${window.labCode}_${new Date().toISOString().split('T')[0]}`
    });
}

function toggleFullscreen() {
    const chartDiv = document.getElementById('control-chart');
    if (!document.fullscreenElement) {
        chartDiv.requestFullscreen().then(() => {
            // Ridimensiona il grafico quando va in fullscreen
            setTimeout(() => {
                Plotly.Plots.resize('control-chart');
            }, 100);
        });
    } else {
        document.exitFullscreen();
    }
}

// ===== GESTIONE FILTRI =====

// Carica opzioni filtri disponibili con dipendenze corrette
function loadFilterOptions() {
    const selectedParams = getSelectedValues('parameters-filter');
    
    const params = new URLSearchParams();
    selectedParams.forEach(p => params.append('parameters[]', p));
    
    fetch(`/l/${window.labCode}/stats/api/filter-options?${params.toString()}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateFilterOptions(data.options);
            }
        })
        .catch(error => {
            console.error('Errore caricamento opzioni filtri:', error);
        });
}

// Aggiorna le opzioni disponibili nei filtri dipendenti
function updateFilterOptions(options) {
    // Aggiorna parametri (al caricamento iniziale)
    const parametersSelect = document.getElementById('parameters-filter');
    if (parametersSelect.options.length === 0 && options.parameters) {
        options.parameters.forEach(param => {
            const option = document.createElement('option');
            option.value = param.code;
            option.textContent = param.name;
            option.selected = true; // Seleziona tutti i parametri di default
            parametersSelect.appendChild(option);
        });
    }
    
    // Aggiorna tecniche
    const techniquesSelect = document.getElementById('techniques-filter');
    const selectedTechniques = getSelectedValues('techniques-filter');
    techniquesSelect.innerHTML = '';
    
    options.techniques.forEach(tech => {
        const option = document.createElement('option');
        option.value = tech.code;
        option.textContent = tech.name;
        option.selected = selectedTechniques.includes(tech.code);
        techniquesSelect.appendChild(option);
    });
    
    // Aggiorna cicli
    const cyclesSelect = document.getElementById('cycles-filter');
    const selectedCycles = getSelectedValues('cycles-filter');
    cyclesSelect.innerHTML = '';
    
    options.cycles.forEach(cycle => {
        const option = document.createElement('option');
        option.value = cycle.code;
        option.textContent = cycle.name;
        option.selected = selectedCycles.includes(cycle.code);
        cyclesSelect.appendChild(option);
    });
}

// Ottiene valori selezionati da un select multiplo
function getSelectedValues(selectId) {
    const select = document.getElementById(selectId);
    return Array.from(select.selectedOptions).map(option => option.value);
}

// Aggiorna i filtri e le dipendenze
function updateFilters() {
    loadFilterOptions();
    updateFilterStats();
}

// Aggiorna le statistiche dei filtri
function updateFilterStats() {
    const paramsCount = getSelectedValues('parameters-filter').length;
    const techniquesCount = getSelectedValues('techniques-filter').length;
    const cyclesCount = getSelectedValues('cycles-filter').length;
    
    document.getElementById('selected-params-count').textContent = paramsCount;
    document.getElementById('selected-techniques-count').textContent = techniquesCount;
    document.getElementById('selected-cycles-count').textContent = cyclesCount;
    
    // Stima risultati (opzionale - richiederebbe API aggiuntiva)
    document.getElementById('expected-results-count').textContent = paramsCount > 0 ? '~' + (paramsCount * 10) : '-';
}

// ===== FUNZIONI PULSANTI FILTRI =====

function selectAllParameters() {
    const select = document.getElementById('parameters-filter');
    for (let option of select.options) {
        option.selected = true;
    }
    updateFilters();
}

function clearAllParameters() {
    const select = document.getElementById('parameters-filter');
    for (let option of select.options) {
        option.selected = false;
    }
    updateFilters();
}

function selectAllTechniques() {
    const select = document.getElementById('techniques-filter');
    for (let option of select.options) {
        if (!option.disabled) option.selected = true;
    }
    updateFilters();
}

function clearAllTechniques() {
    const select = document.getElementById('techniques-filter');
    for (let option of select.options) {
        option.selected = false;
    }
    updateFilters();
}

function selectAllCycles() {
    const select = document.getElementById('cycles-filter');
    for (let option of select.options) {
        if (!option.disabled) option.selected = true;
    }
    updateFilters();
}

function clearAllCycles() {
    const select = document.getElementById('cycles-filter');
    for (let option of select.options) {
        option.selected = false;
    }
    updateFilters();
}

function resetAllFilters() {
    clearAllParameters();
    clearAllTechniques();
    clearAllCycles();
    document.getElementById('days-filter').value = '30';
    updateFilters();
}

// ===== GESTIONE TABELLA RISULTATI =====

// Carica i dati della tabella
function loadTableData(page = 1) {
    const selectedParams = getSelectedValues('parameters-filter');
    const selectedTechniques = getSelectedValues('techniques-filter');
    const selectedCycles = getSelectedValues('cycles-filter');
    const daysFilter = document.getElementById('days-filter').value;
    
    // Mostra loading
    document.getElementById('table-loading').classList.remove('d-none');
    document.getElementById('results-table-container').classList.add('d-none');
    document.getElementById('no-data-message').classList.add('d-none');
    
    // Costruisci parametri URL
    const params = new URLSearchParams();
    selectedParams.forEach(p => params.append('parameters[]', p));
    selectedTechniques.forEach(t => params.append('techniques[]', t));
    selectedCycles.forEach(c => params.append('cycles[]', c));
    if (daysFilter) params.append('days', daysFilter);
    params.append('page', page);
    params.append('per_page', tablePerPage);
    
    fetch(`/l/${window.labCode}/stats/api/table-data?${params.toString()}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayTableData(data.data, data.pagination);
                updateTablePagination(data.pagination);
                
                // Aggiorna badge con il conteggio
                document.getElementById('table-count-badge').textContent = data.pagination.total_count;
            } else {
                console.error('Errore API tabella:', data.error);
                showNoDataMessage();
            }
        })
        .catch(error => {
            console.error('Errore caricamento tabella:', error);
            showNoDataMessage();
        })
        .finally(() => {
            document.getElementById('table-loading').classList.add('d-none');
        });
}

// Mostra i dati nella tabella
function displayTableData(data, pagination) {
    const tbody = document.getElementById('results-table-body');
    
    if (!data || data.length === 0) {
        showNoDataMessage();
        return;
    }
    
    tbody.innerHTML = '';
    
    data.forEach(row => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td class="text-nowrap">${row.submitted_at}</td>
            <td>
                <span class="badge bg-secondary">${row.parameter_code}</span><br>
                <small class="text-muted">${row.parameter_name}</small>
            </td>
            <td>
                <span class="badge bg-info">${row.technique_code}</span><br>
                <small class="text-muted">${row.technique_name}</small>
            </td>
            <td>
                <span class="badge bg-primary">${row.cycle_code}</span><br>
                <small class="text-muted">${row.provider_name}</small>
            </td>
            <td class="text-end">
                <strong>${row.measured_value.toFixed(3)}</strong>
                ${row.uncertainty ? `<br><small class="text-muted">±${row.uncertainty.toFixed(3)}</small>` : ''}
            </td>
            <td class="text-center">
                <span class="badge bg-${row.performance_class} fs-6">${row.z_score}</span><br>
                <small class="text-${row.performance_class}">${row.performance_text}</small>
            </td>
            <td>
                <small class="text-muted">${row.notes}</small>
            </td>
        `;
        tbody.appendChild(tr);
    });
    
    document.getElementById('results-table-container').classList.remove('d-none');
}

// Mostra messaggio "nessun dato"
function showNoDataMessage() {
    document.getElementById('results-table-container').classList.add('d-none');
    document.getElementById('no-data-message').classList.remove('d-none');
    document.getElementById('table-count-badge').textContent = '0';
}

// Aggiorna la paginazione
function updateTablePagination(pagination) {
    const paginationInfo = document.getElementById('pagination-info');
    const paginationControls = document.getElementById('pagination-controls');
    
    // Info paginazione
    const start = ((pagination.page - 1) * pagination.per_page) + 1;
    const end = Math.min(pagination.page * pagination.per_page, pagination.total_count);
    paginationInfo.textContent = `Risultati ${start}-${end} di ${pagination.total_count}`;
    
    // Controlli paginazione
    paginationControls.innerHTML = '';
    
    if (pagination.total_pages <= 1) return;
    
    // Pulsante Previous
    const prevLi = document.createElement('li');
    prevLi.className = `page-item ${pagination.page <= 1 ? 'disabled' : ''}`;
    prevLi.innerHTML = `<a class="page-link" href="#" onclick="goToTablePage(${pagination.page - 1})">‹</a>`;
    paginationControls.appendChild(prevLi);
    
    // Numeri pagina
    const startPage = Math.max(1, pagination.page - 2);
    const endPage = Math.min(pagination.total_pages, pagination.page + 2);
    
    if (startPage > 1) {
        const li = document.createElement('li');
        li.className = 'page-item';
        li.innerHTML = `<a class="page-link" href="#" onclick="goToTablePage(1)">1</a>`;
        paginationControls.appendChild(li);
        
        if (startPage > 2) {
            const dots = document.createElement('li');
            dots.className = 'page-item disabled';
            dots.innerHTML = '<span class="page-link">...</span>';
            paginationControls.appendChild(dots);
        }
    }
    
    for (let i = startPage; i <= endPage; i++) {
        const li = document.createElement('li');
        li.className = `page-item ${i === pagination.page ? 'active' : ''}`;
        li.innerHTML = `<a class="page-link" href="#" onclick="goToTablePage(${i})">${i}</a>`;
        paginationControls.appendChild(li);
    }
    
    if (endPage < pagination.total_pages) {
        if (endPage < pagination.total_pages - 1) {
            const dots = document.createElement('li');
            dots.className = 'page-item disabled';
            dots.innerHTML = '<span class="page-link">...</span>';
            paginationControls.appendChild(dots);
        }
        
        const li = document.createElement('li');
        li.className = 'page-item';
        li.innerHTML = `<a class="page-link" href="#" onclick="goToTablePage(${pagination.total_pages})">${pagination.total_pages}</a>`;
        paginationControls.appendChild(li);
    }
    
    // Pulsante Next
    const nextLi = document.createElement('li');
    nextLi.className = `page-item ${pagination.page >= pagination.total_pages ? 'disabled' : ''}`;
    nextLi.innerHTML = `<a class="page-link" href="#" onclick="goToTablePage(${pagination.page + 1})">›</a>`;
    paginationControls.appendChild(nextLi);
}

// Vai a una pagina specifica
function goToTablePage(page) {
    if (page < 1) return;
    currentTablePage = page;
    loadTableData(page);
}

// Esporta dati tabella
function exportTableData(format) {
    const selectedParams = getSelectedValues('parameters-filter');
    const selectedTechniques = getSelectedValues('techniques-filter');
    const selectedCycles = getSelectedValues('cycles-filter');
    const daysFilter = document.getElementById('days-filter').value;
    
    // Costruisci parametri URL per export
    const params = new URLSearchParams();
    selectedParams.forEach(p => params.append('parameters[]', p));
    selectedTechniques.forEach(t => params.append('techniques[]', t));
    selectedCycles.forEach(c => params.append('cycles[]', c));
    if (daysFilter) params.append('days', daysFilter);
    params.append('format', format);
    params.append('per_page', 1000); // Export più dati
    
    // Crea link di download
    const exportUrl = `/l/${window.labCode}/stats/api/table-data?${params.toString()}`;
    
    // Per ora, avvisa l'utente - in futuro si può implementare un vero export
    alert(`Export ${format.toUpperCase()} - URL: ${exportUrl}`);
}

// ===== GESTIONE STATISTICHE =====

// Funzione per aggiornare le statistiche con i filtri correnti
function updateStatistics() {
    const selectedParams = getSelectedValues('parameters-filter');
    const selectedTechniques = getSelectedValues('techniques-filter');
    const selectedCycles = getSelectedValues('cycles-filter');
    const daysFilter = document.getElementById('days-filter').value;
    
    // Costruisci parametri URL per le statistiche
    const params = new URLSearchParams();
    selectedParams.forEach(p => params.append('parameters[]', p));
    selectedTechniques.forEach(t => params.append('techniques[]', t));
    selectedCycles.forEach(c => params.append('cycles[]', c));
    if (daysFilter) params.append('days', daysFilter);
    
    // Chiamata API per le statistiche
    const statsUrl = `/l/${window.labCode}/stats/api/statistics?${params.toString()}`;
    
    fetch(statsUrl)
        .then(response => response.json())
        .then(data => {
            if (data.success && data.statistics) {
                updateStatisticsDisplay(data.statistics);
            }
        })
        .catch(error => {
            console.error('Errore nella chiamata alle statistiche:', error);
        });
}

function updateStatisticsDisplay(stats) {
    // Aggiorna il display delle statistiche (se ci sono elementi nella UI)
    // Questa funzione può essere espansa in base agli elementi statistici nella UI
    console.log('Statistiche aggiornate:', stats);
}

// ===== EVENTI GLOBALI =====

// Ridimensiona grafico quando cambia la finestra
window.addEventListener('resize', function() {
    const chartDiv = document.getElementById('control-chart');
    if (chartDiv && chartDiv.data) {
        Plotly.Plots.resize('control-chart');
    }
});

// Auto-refresh ogni 5 minuti se la pagina è attiva
function startAutoRefresh() {
    refreshInterval = setInterval(() => {
        if (!document.hidden) {
            updateChart();
        }
    }, 5 * 60 * 1000); // 5 minuti
}

function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
}

document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        stopAutoRefresh();
    } else {
        startAutoRefresh();
    }
});

// ===== ESPORTAZIONE FUNZIONI GLOBALI =====

// Rende le funzioni disponibili globalmente per gli onclick nel template
window.updateChart = updateChart;
window.downloadChart = downloadChart;
window.toggleFullscreen = toggleFullscreen;
window.selectAllParameters = selectAllParameters;
window.clearAllParameters = clearAllParameters;
window.selectAllTechniques = selectAllTechniques;
window.clearAllTechniques = clearAllTechniques;
window.selectAllCycles = selectAllCycles;
window.clearAllCycles = clearAllCycles;
window.resetAllFilters = resetAllFilters;
window.updateFilters = updateFilters;
window.goToTablePage = goToTablePage;
window.exportTableData = exportTableData;