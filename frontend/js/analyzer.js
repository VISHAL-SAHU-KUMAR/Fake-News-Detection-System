// ---------- ANALYSIS ----------
async function analyze() {
    const claim = document.getElementById('claim-input').value;
    if (!claim) return alert("Enter claim text.");

    const btn = document.getElementById('analyze-btn');
    btn.textContent = "PROCESSING...";
    btn.disabled = true;

    const resultCard = document.getElementById('result-card');
    if (resultCard) resultCard.style.display = 'none';

    const payload = { claim };
    if (user) payload.user_id = user.id;

    try {
        const data = await apiPost('/analyze', payload);
        showResult(data);
    } catch (e) {
        alert("Analysis Failed: " + e.message);
    } finally {
        btn.textContent = "ANALYZE DATA";
        btn.disabled = false;
    }
}

function showResult(data) {
    const rc = document.getElementById('result-card');
    if (rc) rc.style.display = 'none'; // Hide the old card if it exists

    // Populate Modal
    document.getElementById('modal-score').textContent = data.score || 0;
    document.getElementById('modal-verdict').textContent = data.verdict || "UNKNOWN";
    document.getElementById('modal-claim').textContent = `"${data.claim}"`;
    document.getElementById('modal-summary').textContent = data.summary || "No description provided.";
    document.getElementById('modal-hindi-summary').textContent = data.hindi_summary || "";
    document.getElementById('modal-ref-id').textContent = `#${data.request_id || '000000'}`;

    // Update Color and Ring
    let color = '#ffaa00';
    if (data.score > 70) color = '#00ffcc';
    else if (data.score < 40) color = '#ff0055';
    document.getElementById('modal-score-ring').style.borderColor = color;
    document.getElementById('modal-verdict').style.color = color;

    // Sources
    const sourcesCont = document.getElementById('modal-sources');
    sourcesCont.innerHTML = "";
    (data.sources || []).forEach(s => {
        const div = document.createElement('div');
        div.className = 'source-item-mini';
        div.style = "padding: 10px; background: rgba(255,255,255,0.02); border-left: 3px solid " + (s.status === 'verified' ? '#00ffcc' : s.status === 'false' ? '#ff0055' : '#ffaa00');
        div.innerHTML = `
            <div style="font-size: 13px; font-weight: 700;">${s.name}</div>
            <div style="font-size: 11px; color: #888;">${s.verdict}</div>
            ${s.url ? `<a href="${s.url}" target="_blank" style="font-size: 10px; color: var(--accent);">VIEW SOURCE</a>` : ''}
        `;
        sourcesCont.appendChild(div);
    });

    // Indicators
    const indCont = document.getElementById('modal-indicators');
    indCont.innerHTML = "";
    (data.indicators || []).forEach(ind => {
        const div = document.createElement('div');
        div.style = "display: flex; gap: 10px; align-items: center; padding: 10px; background: rgba(255,255,255,0.03); border-radius: 4px;";
        div.innerHTML = `
            <div style="font-size: 20px;">${ind.icon}</div>
            <div>
                <div style="font-size: 11px; font-weight: 700;">${ind.title}</div>
                <div style="font-size: 10px; color: #888;">${ind.desc}</div>
            </div>
            <div style="margin-left: auto; width: 8px; height: 8px; border-radius: 50%; background: ${ind.colorClass === 'green' ? '#00ffcc' : ind.colorClass === 'red' ? '#ff0055' : '#ffaa00'};"></div>
        `;
        indCont.appendChild(div);
    });

    // Tips
    const tipsCont = document.getElementById('modal-tips-list');
    tipsCont.innerHTML = "";
    (data.tips || []).forEach(t => {
        const li = document.createElement('li');
        li.textContent = t.text;
        li.style.marginBottom = "5px";
        tipsCont.appendChild(li);
    });

    openModal('analysis-modal');
}
