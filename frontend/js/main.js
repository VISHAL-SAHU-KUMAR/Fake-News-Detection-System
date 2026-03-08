// ---------- INITIALIZATION ----------

document.addEventListener('DOMContentLoaded', async () => {
    // 1. Load shell components
    try {
        const navRes = await fetch('components/nav.html');
        const navHtml = await navRes.text();
        document.getElementById('nav-wrapper').innerHTML = navHtml;

        const modalRes = await fetch('components/modals.html');
        const modalHtml = await modalRes.text();
        document.getElementById('modals-wrapper').innerHTML = modalHtml;

    } catch (e) {
        console.error("Shell initialization failed:", e);
    }

    // 2. Start initial navigation
    await navigate('home');

    // 3. Start authentication check (this will update Navbar)
    await checkAuth();
});
