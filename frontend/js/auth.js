// ---------- UI HELPERS ----------
function togglePassword(id) {
    const input = document.getElementById(id);
    if (input.type === "password") {
        input.type = "text";
    } else {
        input.type = "password";
    }
}

function handleOtpInput(input, e) {
    const container = input.parentElement;
    const inputs = container.querySelectorAll('input');
    const index = Array.from(inputs).indexOf(input);

    if (input.value && index < 5) {
        inputs[index + 1].focus();
    } else if (e.key === "Backspace" && index > 0 && !input.value) {
        inputs[index - 1].focus();
    }
    input.value = input.value.toUpperCase();
}

function getOtpValue(selector = '.otp-box') {
    const inputs = document.querySelectorAll(selector);
    let otp = "";
    inputs.forEach(input => otp += input.value);
    return otp;
}

let otpTimerInterval;
function startOtpTimer(durationSeconds = 60) {
    clearInterval(otpTimerInterval);
    const display = document.getElementById('otp-timer');
    const resendBtn = document.getElementById('resend-btn');
    const timerContainer = document.getElementById('otp-timer-container');

    if (!display || !resendBtn) return;

    resendBtn.style.display = 'none';
    timerContainer.style.display = 'block';

    let timer = durationSeconds;
    const updateDisplay = () => {
        const mins = Math.floor(timer / 60);
        const secs = timer % 60;
        display.textContent = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;

        if (--timer < 0) {
            clearInterval(otpTimerInterval);
            timerContainer.style.display = 'none';
            resendBtn.style.display = 'block';
        }
    };

    updateDisplay();
    otpTimerInterval = setInterval(updateDisplay, 1000);
}

// ---------- AUTH STATE ----------
async function checkAuth() {
    if (!token) return setLoggedOut();
    try {
        const res = await fetch(`${API}/auth/me`, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        if (res.ok) {
            user = await res.json();
            setLoggedIn();
        } else {
            setLoggedOut();
        }
    } catch (e) { setLoggedOut(); }
}

function setLoggedIn() {
    const authOut = document.getElementById('auth-out');
    const authIn = document.getElementById('auth-in');
    if (authOut) authOut.style.display = 'none';
    if (authIn) authIn.style.display = 'flex';

    const userNav = document.getElementById('nav-user');
    if (userNav) userNav.textContent = `OP-${user.name}`;

    const historyNav = document.getElementById('nav-history');
    if (historyNav) historyNav.style.display = 'block';

    const profileNav = document.getElementById('nav-profile');
    if (profileNav) profileNav.style.display = 'block';

    fillProfileFields();
}

function setLoggedOut() {
    token = null;
    user = null;
    localStorage.removeItem("tl_token");

    const authOut = document.getElementById('auth-out');
    const authIn = document.getElementById('auth-in');
    if (authOut) authOut.style.display = 'flex';
    if (authIn) authIn.style.display = 'none';

    const historyNav = document.getElementById('nav-history');
    if (historyNav) historyNav.style.display = 'none';

    const profileNav = document.getElementById('nav-profile');
    if (profileNav) profileNav.style.display = 'none';

    navigate('home');
}

function logout() { setLoggedOut(); }

// ---------- ACTIONS ----------
async function doRegister() {
    const name = document.getElementById('reg-name').value;
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-pass').value;
    const confirmPass = document.getElementById('reg-pass-confirm').value;
    const err = document.getElementById('reg-err');

    if (password !== confirmPass) {
        err.textContent = "Passwords do not match.";
        err.style.display = 'block';
        return;
    }

    try {
        await apiPost('/auth/register', { name, email, password });
        pendingEmail = email;
        swapModal('register-modal', 'otp-modal');
        startOtpTimer(60);
    } catch (e) {
        err.textContent = e.message;
        err.style.display = 'block';
    }
}

async function doResendOTP() {
    if (!pendingEmail) return;
    try {
        await apiPost('/auth/resend-otp', { email: pendingEmail });
        showToast("NEW OTP DISPATCHED.");
        startOtpTimer(60);

        // Clear boxes
        document.querySelectorAll('.otp-box').forEach(b => b.value = "");
        document.querySelectorAll('.otp-box')[0].focus();
    } catch (e) {
        showToast("ERROR: " + e.message);
    }
}

async function doVerifyOTP() {
    const otp = getOtpValue();
    const err = document.getElementById('otp-err');

    if (otp.length < 6) {
        err.textContent = "Please enter full 6-character code.";
        err.style.display = 'block';
        return;
    }

    try {
        const data = await apiPost('/auth/verify-otp', { email: pendingEmail, otp });
        token = data.access_token;
        localStorage.setItem("tl_token", token);
        user = data.user;
        closeModal('otp-modal');
        setLoggedIn();
        showToast("IDENTITY VERIFIED. WELCOME OPERATIVE.");
    } catch (e) {
        err.textContent = e.message;
        err.style.display = 'block';
    }
}

async function doLogin() {
    const email = document.getElementById('log-email').value;
    const password = document.getElementById('log-pass').value;
    const err = document.getElementById('log-err');
    try {
        const data = await apiPost('/auth/login', { email, password });
        token = data.access_token;
        localStorage.setItem("tl_token", token);
        user = data.user;
        closeModal('login-modal');
        setLoggedIn();
        showToast(`CONGRATULATIONS: Welcome back, ${user.name}`);
    } catch (e) {
        if (e.message.includes('Account not verified')) {
            pendingEmail = email;
            swapModal('login-modal', 'otp-modal');
            startOtpTimer(60);
        } else {
            err.textContent = e.message;
            err.style.display = 'block';
        }
    }
}

async function doForgotPassword() {
    const email = document.getElementById('forgot-email').value;
    const err = document.getElementById('forgot-err');
    const suc = document.getElementById('forgot-suc');
    try {
        const data = await apiPost('/auth/forgot-password', { email });
        err.style.display = 'none';
        suc.textContent = data.msg;
        suc.style.display = 'block';
        setTimeout(() => {
            if (document.getElementById('res-email')) {
                document.getElementById('res-email').value = email;
            }
            swapModal('forgot-modal', 'reset-modal');
            suc.style.display = 'none';
        }, 2000);
    } catch (e) {
        err.textContent = e.message;
        err.style.display = 'block';
    }
}

async function doResetPassword() {
    const email = document.getElementById('res-email').value;
    const otp = document.getElementById('res-otp').value;
    const new_password = document.getElementById('res-pass').value;
    const err = document.getElementById('res-err');
    const suc = document.getElementById('res-suc');
    try {
        const data = await apiPost('/auth/reset-password', { email, otp, new_password });
        err.style.display = 'none';
        suc.textContent = data.msg;
        suc.style.display = 'block';
        setTimeout(() => {
            swapModal('reset-modal', 'login-modal');
            suc.style.display = 'none';
        }, 2000);
    } catch (e) {
        err.textContent = e.message;
        err.style.display = 'block';
    }
}

// ---------- PROFILE ACTIONS ----------
function fillProfileFields() {
    if (!user) return;
    const nameDisp = document.getElementById('prof-name-display');
    if (!nameDisp) return; // Not on profile page

    nameDisp.textContent = user.name;
    document.getElementById('prof-email-display').textContent = user.email;
    document.getElementById('prof-count').textContent = user.analyses_count || 0;

    document.getElementById('upd-name').value = user.name || "";
    document.getElementById('upd-phone').value = user.phone || "";
    document.getElementById('upd-bio').value = user.bio || "";
    document.getElementById('upd-linkedin').value = user.linked_in || "";
    document.getElementById('upd-photo').value = user.profile_photo || "";

    const profId = document.getElementById('prof-id-display');
    if (profId) profId.textContent = user.id;

    const delWarn = document.getElementById('deletion-warning');
    if (delWarn) {
        if (user.deletion_at) {
            delWarn.style.display = 'block';
            document.getElementById('deletion-date').textContent = new Date(user.deletion_at).toLocaleString();
        } else {
            delWarn.style.display = 'none';
        }
    }

    if (user.profile_photo) {
        document.getElementById('prof-photo-display').src = user.profile_photo;
    } else {
        document.getElementById('prof-photo-display').src = `https://api.dicebear.com/7.x/bottts/svg?seed=${user.email}`;
    }
}

async function updateProfile() {
    const payload = {
        name: document.getElementById('upd-name').value,
        phone: document.getElementById('upd-phone').value,
        bio: document.getElementById('upd-bio').value,
        linked_in: document.getElementById('upd-linkedin').value,
        profile_photo: document.getElementById('upd-photo').value
    };

    showLoader("UPDATING PROFILE...");
    try {
        const res = await fetch(`${API}/auth/update-profile`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        hideLoader();
        if (!res.ok) throw new Error(data.detail || "Update failed");

        showToast("PROFILE PROTOCOL UPDATED.");
        await checkAuth(); // Refresh user state
    } catch (e) {
        hideLoader();
        showToast("ERROR: " + e.message);
    }
}

// ---------- DELETE ACCOUNT ----------
async function requestDelete() {
    const err = document.getElementById('del-err');
    showLoader("INITIATING 48H NEUTRALIZATION PROTOCOL...");
    try {
        const res = await fetch(`${API}/auth/delete-request`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ email: user.email })
        });
        const data = await res.json();
        hideLoader();
        if (!res.ok) throw new Error(data.detail || "Request failed");

        document.getElementById('del-request-view').style.display = 'none';
        document.getElementById('del-confirm-view').style.display = 'block';
        err.style.display = 'none';
        showToast("SECURITY OTP DISPATCHED.");
    } catch (e) {
        hideLoader();
        err.textContent = e.message;
        err.style.display = 'block';
    }
}

async function requestIdentityKey() {
    showLoader("RETRIEVING NODE IDENTITY...");
    try {
        const res = await fetch(`${API}/auth/request-identity`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ email: user.email })
        });
        const data = await res.json();
        hideLoader();
        if (!res.ok) throw new Error(data.detail || "Retrieval failed");
        showToast("IDENTITY KEY SENT TO EMAIL.");
    } catch (e) {
        hideLoader();
        alert("Error: " + e.message);
    }
}

async function confirmDelete() {
    const otp = getOtpValue('.del-otp-box');
    const identity_key = document.getElementById('del-id-key').value;
    const err = document.getElementById('del-err');

    if (otp.length < 6) {
        err.textContent = "Security Error: Perfect 6-character OTP required.";
        err.style.display = 'block';
        return;
    }

    showLoader("SCHEDULING NODE NEUTRALIZATION...");
    try {
        const res = await fetch(`${API}/auth/delete-confirm`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                email: user.email,
                otp: otp,
                identity_key: identity_key
            })
        });
        const data = await res.json();
        hideLoader();
        if (!res.ok) throw new Error(data.detail || "Verification failed. Check OTP and ID Key.");

        showToast("Scheduled for Neutralization. 48 hours remaining.");
        closeModal('delete-modal');
        await checkAuth(); // Refresh profile to show warning
    } catch (e) {
        hideLoader();
        err.textContent = e.message;
        err.style.display = 'block';
    }
}

async function cancelDeletion() {
    if (!confirm("Are you sure you want to terminate the neutralization and recover this node?")) return;
    showLoader("TERMINATING PURGE PROTOCOLS...");
    try {
        const res = await fetch(`${API}/auth/cancel-deletion`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ email: user.email })
        });
        const data = await res.json();
        hideLoader();
        if (!res.ok) throw new Error(data.detail || "Recovery failed");

        showToast("NODE RECOVERY SUCCESSFUL.");
        await checkAuth(); // Hide warning
    } catch (e) {
        hideLoader();
        showToast("ERROR: " + e.message);
    }
}
