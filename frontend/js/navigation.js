// ---------- NAVIGATION & COMPONENT LOADER ----------

// Cache for pages to avoid flickering
const pageCache = {};

async function loadComponent(id, url) {
    const res = await fetch(url);
    const html = await res.text();
    document.getElementById(id).innerHTML = html;
}

async function navigate(pageId) {
    // 1. Update active states in Navbar
    document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
    const navLink = document.getElementById(`nav-${pageId}`);
    if (navLink) navLink.classList.add('active');

    // 2. Load page content if not in cache (or just fetch it for simplicity in hackathon)
    // For TruthLens, we'll fetch every time to ensure state consistency, or use cache for speed.
    try {
        if (!pageCache[pageId]) {
            const res = await fetch(`pages/${pageId}.html`);
            if (!res.ok) throw new Error("Page not found");
            pageCache[pageId] = await res.text();
        }

        document.getElementById('page-content').innerHTML = pageCache[pageId];

        // 3. Trigger specific page logic
        if (pageId === 'history' && user) fetchHistory();
        if (pageId === 'profile' && user) fillProfileFields();

        // Always re-init tilt on new content
        if (typeof initTilt === 'function') initTilt();

    } catch (e) {
        console.error("Navigation error:", e);
        document.getElementById('page-content').innerHTML = `<div class="hero"><h1>404</h1><p>Module Not Found</p></div>`;
    }
}

// ---------- MODALS ----------
function openModal(id) {
    const el = document.getElementById(id);
    if (!el) return;
    el.style.display = 'flex';
    setTimeout(() => el.classList.add('show'), 10);
}

function closeModal(id) {
    const el = document.getElementById(id);
    if (!el) return;
    el.classList.remove('show');
    setTimeout(() => el.style.display = 'none', 300);
}

function swapModal(closeId, openId) {
    closeModal(closeId);
    setTimeout(() => openModal(openId), 300);
}
