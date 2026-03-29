const fetchDashboardData = async () => {
    try {
        const { data } = await API.get('/dashboard/');
        
        // Stats
        document.getElementById('health-score').innerText = `${data.health.score}/100`;
        document.getElementById('health-feedback').innerText = data.health.summary;
        document.getElementById('total-spent').innerText = `₹${data.total_spent.toLocaleString()}`;
        document.getElementById('estimated-savings').innerText = `₹${(data.total_income - data.total_spent).toLocaleString()}`;
        document.getElementById('forecast-total').innerText = `₹${data.forecast.next_month_forecast.toLocaleString()}`;
        
        // Insights
        const insightsContainer = document.getElementById('insights-container');
        insightsContainer.innerHTML = data.insights.map(ins => `
            <div class="p-4 bg-body-tertiary rounded-4 d-flex align-items-center gap-3 border-start border-warning border-4">
                <i data-lucide="info" size="18" class="text-warning"></i>
                <p class="m-0 small fw-medium text-body">${ins}</p>
            </div>
        `).join('') || '<p class="text-muted text-center py-5">No insights available for this month.</p>';

        // Charts
        renderTrendChart(data.monthly_trends, data.forecast.next_month_forecast);
        renderCategoryChart(data.category_distribution);
        
        // Goals Summary
        fetchGoalsSummary();

        lucide.createIcons();
    } catch (err) {
        console.error('Error fetching dashboard data:', err);
    }
};

let trendChartInstance = null;
const renderTrendChart = (trends, forecast) => {
    const canvas = document.getElementById('trendChart');
    if (!canvas) return;
    const drawCtx = canvas.getContext('2d');
    
    if (trendChartInstance) {
        trendChartInstance.destroy();
    }
    
    // Format labels: 2024-03 -> Mar 24
    const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    const formatLabel = (dateStr) => {
        if (!dateStr || dateStr === 'Next Month (Pred.)') return dateStr || '';
        const parts = dateStr.split('-');
        if (parts.length < 2) return dateStr;
        const [year, month] = parts;
        return `${months[parseInt(month) - 1]} ${year.slice(-2)}`;
    };

    const labels = trends.map(t => formatLabel(t.name));
    const data = trends.map(t => t.amount);
    
    labels.push('Next Month (Pred.)');
    data.push(forecast);

    const chartGradient = drawCtx.createLinearGradient(0, 0, 0, 350);
    chartGradient.addColorStop(0, 'rgba(0, 245, 255, 0.25)');
    chartGradient.addColorStop(0.5, 'rgba(0, 245, 255, 0.06)');
    chartGradient.addColorStop(1, 'rgba(0, 245, 255, 0)');

    trendChartInstance = new Chart(drawCtx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Spending Trajectory',
                data: data,
                fill: true,
                backgroundColor: chartGradient,
                borderColor: '#00f5ff',
                borderWidth: 2.5,
                pointBackgroundColor: '#00f5ff',
                pointBorderColor: '#020510',
                pointBorderWidth: 2,
                pointRadius: 5,
                pointHoverRadius: 9,
                pointHoverBackgroundColor: '#ff00ff',
                tension: 0.4,
                segment: {
                    borderDash: (seg) => seg.p0DataIndex >= (trends.length - 1) ? [6, 4] : undefined,
                    borderColor: (seg) => seg.p0DataIndex >= (trends.length - 1) ? 'rgba(255,0,255,0.7)' : '#00f5ff'
                }
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { intersect: false, mode: 'index' },
            plugins: { 
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(2, 5, 16, 0.95)',
                    titleColor: '#00f5ff',
                    titleFont: { size: 12, weight: '700', family: "'Share Tech Mono', monospace" },
                    bodyColor: '#a855f7',
                    bodyFont: { size: 14, weight: '700' },
                    borderColor: 'rgba(0, 245, 255, 0.3)',
                    borderWidth: 1,
                    padding: 14,
                    displayColors: false,
                    callbacks: {
                        label: (tooltipCtx) => `₹${tooltipCtx.raw.toLocaleString()}`
                    }
                }
            },
            scales: {
                y: { 
                    grid: { color: 'rgba(0, 245, 255, 0.06)', drawBorder: false }, 
                    ticks: { 
                        font: { size: 10, family: "'Share Tech Mono', monospace" },
                        color: 'rgba(0, 245, 255, 0.5)',
                        callback: (val) => '₹' + val.toLocaleString()
                    },
                    border: { dash: [4, 4] }
                },
                x: { 
                    grid: { color: 'rgba(168, 85, 247, 0.06)', drawBorder: false }, 
                    ticks: { font: { size: 10, family: "'Share Tech Mono', monospace" }, color: 'rgba(0, 245, 255, 0.4)' },
                    border: { dash: [4, 4] }
                }
            }
        }
    });
};

const renderCategoryChart = (dist) => {
    const ctx = document.getElementById('categoryChart').getContext('2d');
    const colors = ['#00f5ff', '#a855f7', '#39ff14', '#ffd700', '#ff00ff', '#ff2d55', '#00c6ff'];

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: dist.map(d => d.name),
            datasets: [{
                data: dist.map(d => d.value),
                backgroundColor: colors.map(c => c + '99'),
                borderColor: colors,
                borderWidth: 1.5,
                hoverOffset: 18,
                hoverBorderWidth: 2.5,
                hoverBorderColor: '#ffffff'
            }]
        },
        options: {
            cutout: '72%',
            responsive: true,
            maintainAspectRatio: false,
            plugins: { 
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(2, 5, 16, 0.95)',
                    titleColor: '#00f5ff',
                    titleFont: { size: 12, weight: '700', family: "'Share Tech Mono', monospace" },
                    bodyColor: '#a855f7',
                    borderColor: 'rgba(0, 245, 255, 0.3)',
                    borderWidth: 1,
                    padding: 12,
                    boxPadding: 6,
                    usePointStyle: true,
                    callbacks: {
                        label: (ctx) => ` ₹${ctx.raw.toLocaleString()}`
                    }
                }
            },
            animation: {
                animateScale: true,
                animateRotate: true
            }
        }
    });

    const labelsContainer = document.getElementById('category-labels');
    labelsContainer.innerHTML = dist.map((d, i) => `
        <div class="category-legend-item d-flex align-items-center justify-content-between mb-2 p-2 rounded-3" 
             style="transition: all 0.3s; cursor: pointer;"
             onmouseover="this.style.background='rgba(0,245,255,0.05)'; this.style.transform='translateX(5px)'"
             onmouseout="this.style.background='transparent'; this.style.transform='translateX(0)'">
            <div class="d-flex align-items-center gap-2">
                <div class="legend-dot" style="width: 10px; height: 10px; border-radius: 3px; background: ${colors[i % colors.length]}; box-shadow: 0 0 8px ${colors[i % colors.length]}88;"></div>
                <span class="small fw-bold uppercase tracking-widest" style="color:rgba(0,245,255,0.65); font-family:'Share Tech Mono',monospace; font-size:10px;">${d.name}</span>
            </div>
            <span class="small fw-bold" style="color:#e2f3ff;">₹${d.value.toLocaleString()}</span>
        </div>
    `).join('');
};

const fetchGoalsSummary = async () => {
    try {
        const { data } = await API.get('/goals/');
        const container = document.getElementById('goals-summary');
        const neonColors = ['#00f5ff', '#a855f7', '#39ff14', '#ffd700', '#ff00ff'];
        container.innerHTML = data.map((goal, i) => {
            const perc  = Math.min(100, (goal.current_amount / goal.target_amount) * 100);
            const color = neonColors[i % neonColors.length];
            return `
                <div class="mb-4">
                    <div class="d-flex justify-content-between mb-2">
                        <span class="small fw-bold" style="color:#e2f3ff; font-family:'Inter',sans-serif;">${goal.name}</span>
                        <span class="small fw-bold font-mono" style="color:${color}; font-family:'Share Tech Mono',monospace; text-shadow: 0 0 8px ${color}80;">${perc.toFixed(0)}%</span>
                    </div>
                    <div class="progress rounded-pill shadow-none" style="height: 7px; background: rgba(0,245,255,0.06);">
                        <div class="progress-bar rounded-pill" style="width: ${perc}%; background: linear-gradient(90deg, ${color}, ${neonColors[(i+1)%neonColors.length]}); box-shadow: 0 0 10px ${color}80;"></div>
                    </div>
                </div>
            `;
        }).join('') || '<p class="empty-state text-center py-5">No goals set. Create one to track your savings!</p>';
    } catch (err) {
        console.error(err);
    }
};

fetchDashboardData();

// ── RE-RENDER CHARTS ON THEME CHANGE ─────────────────────────
window.addEventListener('themechange', (e) => {
    const isDark = e.detail.theme === 'dark';

    // Update trend chart colors live
    if (trendChartInstance) {
        const primaryLine = isDark ? '#00f5ff' : '#6366f1';
        const gridColor   = isDark ? 'rgba(0,245,255,0.06)' : 'rgba(99,102,241,0.07)';
        const tickColor   = isDark ? 'rgba(0,245,255,0.5)'  : '#94a3b8';
        const tooltipBg   = isDark ? 'rgba(2,5,16,0.95)' : 'rgba(255,255,255,0.97)';
        const tooltipTitle= isDark ? '#00f5ff' : '#6366f1';
        const tooltipBody = isDark ? '#a855f7' : '#64748b';
        const tooltipBorder=isDark ? 'rgba(0,245,255,0.3)' : 'rgba(99,102,241,0.2)';

        const ds = trendChartInstance.data.datasets[0];
        const ctx2 = trendChartInstance.ctx;
        const grad = ctx2.createLinearGradient(0, 0, 0, 350);
        grad.addColorStop(0,   isDark ? 'rgba(0,245,255,0.25)'     : 'rgba(99,102,241,0.2)');
        grad.addColorStop(0.5, isDark ? 'rgba(0,245,255,0.06)'     : 'rgba(99,102,241,0.05)');
        grad.addColorStop(1,   'rgba(0,0,0,0)');

        ds.backgroundColor       = grad;
        ds.borderColor           = primaryLine;
        ds.pointBackgroundColor  = primaryLine;
        ds.segment.borderColor   = (seg) =>
            seg.p0DataIndex >= (trendChartInstance.data.datasets[0].data.length - 2)
                ? (isDark ? 'rgba(255,0,255,0.7)' : 'rgba(14,165,233,0.7)')
                : primaryLine;

        const scales = trendChartInstance.options.scales;
        scales.y.grid.color   = gridColor;
        scales.x.grid.color   = isDark ? 'rgba(168,85,247,0.06)' : 'rgba(99,102,241,0.05)';
        scales.y.ticks.color  = tickColor;
        scales.x.ticks.color  = tickColor;

        const tip = trendChartInstance.options.plugins.tooltip;
        tip.backgroundColor = tooltipBg;
        tip.titleColor      = tooltipTitle;
        tip.bodyColor       = tooltipBody;
        tip.borderColor     = tooltipBorder;

        trendChartInstance.update();
    }
});
