// ---------- HISTORY ----------
async function fetchHistory() {
    if (!user) return;
    const grid = document.getElementById('history-grid');
    if (!grid) return;
    grid.innerHTML = '<p style="color:var(--muted);">Loading history...</p>';
    try {
        const res = await fetch(`${API}/history?user_id=${user.id}`);
        const data = await res.json();

        if (data.length === 0) {
            grid.innerHTML = '<p style="color:var(--muted);">No analyses found.</p>';
            return;
        }

        grid.innerHTML = data.map(i => {
            const d = new Date(i.created_at).toLocaleString();
            let color = '#ffaa00';
            if (i.score > 70) color = '#00ffcc'; else if (i.score < 40) color = '#ff0055';
            return `
<div class="history-card tilt-card" onclick="document.getElementById('claim-input').value='${i.claim.replace(/'/g, "\\'")}'; navigate('home');">
  <div class="h-date">${d}</div>
  <div class="h-claim">${i.claim}</div>
  <div style="display:flex; justify-content:space-between; align-items:center;">
     <span style="font-size:10px; color:${color}; font-weight:700;">${i.verdict}</span>
     <span class="h-score" style="color:${color};">${i.score}</span>
  </div>
</div>
`;
        }).join('');

        // Re-init tilt for new elements
        initHistoryTilt();

    } catch (e) {
        grid.innerHTML = `<p style="color:var(--danger)">Error loading history.</p>`;
    }
}

function initHistoryTilt() {
    document.querySelectorAll('.history-card').forEach(card => {
        card.addEventListener('mousemove', e => {
            const rect = card.getBoundingClientRect();
            const rotateX = (((e.clientY - rect.top) - rect.height / 2) / (rect.height / 2)) * -5;
            const rotateY = (((e.clientX - rect.left) - rect.width / 2) / (rect.width / 2)) * 5;
            card.style.transform = `perspective(500px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
        });
        card.addEventListener('mouseleave', () => card.style.transform = `none`);
    });
}
