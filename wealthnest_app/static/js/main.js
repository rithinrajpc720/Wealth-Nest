/* WealthNest — main.js */

// ============ Theme Toggle ============
(function () {
  const stored = localStorage.getItem('wn-theme') || 'light';
  document.documentElement.setAttribute('data-theme', stored);
  window.toggleTheme = function () {
    const cur = document.documentElement.getAttribute('data-theme');
    const next = cur === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('wn-theme', next);
    const ic = document.querySelector('#theme-icon');
    if (ic) ic.textContent = next === 'dark' ? '🌞' : '🌙';
  };
  document.addEventListener('DOMContentLoaded', () => {
    const ic = document.querySelector('#theme-icon');
    if (ic) ic.textContent = stored === 'dark' ? '🌞' : '🌙';
  });
})();

// ============ Toasts ============
window.showToast = function (msg, type) {
  type = type || 'info';
  let cont = document.querySelector('.toast-container');
  if (!cont) {
    cont = document.createElement('div');
    cont.className = 'toast-container';
    document.body.appendChild(cont);
  }
  const toast = document.createElement('div');
  toast.className = 'wn-toast ' + type;
  toast.innerHTML = `<span>${msg}</span>`;
  cont.appendChild(toast);
  setTimeout(() => { toast.style.opacity = '0'; toast.style.transition = 'opacity 0.4s'; }, 3500);
  setTimeout(() => toast.remove(), 4000);
};

// ============ Confetti Burst ============
window.celebrate = function () {
  const colors = ['#F6C90E', '#FFD93D', '#10B981', '#8B5CF6', '#FF6B6B', '#1E1B4B'];
  const cont = document.createElement('div');
  cont.className = 'confetti-container';
  document.body.appendChild(cont);
  for (let i = 0; i < 80; i++) {
    const piece = document.createElement('div');
    piece.className = 'confetti-piece';
    piece.style.left = Math.random() * 100 + '%';
    piece.style.background = colors[Math.floor(Math.random() * colors.length)];
    piece.style.animationDelay = (Math.random() * 0.6) + 's';
    piece.style.animationDuration = (2 + Math.random() * 2) + 's';
    if (Math.random() > 0.5) piece.style.borderRadius = '50%';
    cont.appendChild(piece);
  }
  setTimeout(() => cont.remove(), 5000);
};

// ============ Coin Burst ============
window.coinBurst = function (x, y) {
  for (let i = 0; i < 8; i++) {
    const coin = document.createElement('div');
    coin.className = 'coin-burst';
    coin.textContent = '🪙';
    coin.style.left = (x || window.innerWidth / 2) + 'px';
    coin.style.top = (y || window.innerHeight / 2) + 'px';
    coin.style.setProperty('--dx', (Math.random() * 200 - 100) + 'px');
    coin.style.setProperty('--dy', (-Math.random() * 200 - 50) + 'px');
    coin.style.animationDelay = (i * 0.05) + 's';
    document.body.appendChild(coin);
    setTimeout(() => coin.remove(), 1700);
  }
};

// ============ Count-up animation ============
window.countUp = function (el, target, duration) {
  duration = duration || 1200;
  const start = 0;
  const startTime = performance.now();
  const isFloat = String(target).indexOf('.') !== -1;
  function step(t) {
    const elapsed = t - startTime;
    const p = Math.min(elapsed / duration, 1);
    const ease = 1 - Math.pow(1 - p, 3);
    const val = start + (target - start) * ease;
    el.textContent = isFloat ? val.toFixed(1) : Math.round(val).toLocaleString('en-IN');
    if (p < 1) requestAnimationFrame(step);
    else el.textContent = isFloat ? target.toFixed(1) : Number(target).toLocaleString('en-IN');
  }
  requestAnimationFrame(step);
};

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-countup]').forEach(el => {
    const target = parseFloat(el.dataset.countup);
    if (!isNaN(target)) {
      el.textContent = '0';
      setTimeout(() => countUp(el, target), 200);
    }
  });

  // Auto-show messages as toasts
  document.querySelectorAll('[data-toast]').forEach(el => {
    showToast(el.dataset.toast, el.dataset.toastType || 'info');
  });

  // Auto-celebrate
  if (document.body.dataset.celebrate === '1') {
    setTimeout(() => celebrate(), 300);
  }
});

// ============ Modals ============
window.openModal = function (id) {
  const m = document.getElementById(id);
  if (m) m.classList.add('active');
};
window.closeModal = function (id) {
  const m = document.getElementById(id);
  if (m) m.classList.remove('active');
};
document.addEventListener('click', e => {
  if (e.target.classList.contains('wn-modal-backdrop')) {
    e.target.classList.remove('active');
  }
});

// ============ Sidebar nav highlight ============
document.addEventListener('DOMContentLoaded', () => {
  const path = window.location.pathname;
  document.querySelectorAll('.wn-sidebar .nav-item[href]').forEach(item => {
    if (item.getAttribute('href') === path) item.classList.add('active');
  });
});

// ============ Form password show/hide ============
window.togglePassword = function (inputId, btn) {
  const inp = document.getElementById(inputId);
  if (!inp) return;
  inp.type = inp.type === 'password' ? 'text' : 'password';
  if (btn) btn.textContent = inp.type === 'password' ? '👁️' : '🙈';
};

// ============ Password strength ============
window.checkPwdStrength = function (val) {
  let s = 0;
  if (val.length >= 6) s++;
  if (val.length >= 10) s++;
  if (/[A-Z]/.test(val)) s++;
  if (/\d/.test(val)) s++;
  if (/[^A-Za-z0-9]/.test(val)) s++;
  return s;
};

// ============ Chart helpers ============
window.WN_CHART_COLORS = {
  indigo: '#1E1B4B',
  gold: '#F6C90E',
  green: '#10B981',
  coral: '#FF6B6B',
  purple: '#8B5CF6',
  amber: '#F59E0B',
  cyan: '#06B6D4',
};
window.makeGradient = function (ctx, color) {
  const g = ctx.createLinearGradient(0, 0, 0, 300);
  g.addColorStop(0, color + 'CC');
  g.addColorStop(1, color + '11');
  return g;
};

// ============ Achievement celebration ============
window.celebrateAchievement = function (name, icon) {
  celebrate();
  showToast(`${icon || '🏆'} Achievement Unlocked: ${name}!`, 'success');
};

// Coin burst when reward credit detected
document.addEventListener('click', e => {
  if (e.target.matches('[data-coin-burst]') || e.target.closest('[data-coin-burst]')) {
    const r = e.target.getBoundingClientRect();
    coinBurst(r.left + r.width / 2, r.top + r.height / 2);
  }
});

// Streak fire pulse
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.streak-fire').forEach(el => {
    setInterval(() => {
      el.style.transform = 'scale(1.05)';
      setTimeout(() => el.style.transform = '', 300);
    }, 4000);
  });
});

// CSRF helper
function getCsrfToken() {
  const c = document.cookie.split(';').find(x => x.trim().startsWith('csrftoken='));
  return c ? c.split('=')[1] : '';
}
window.getCsrfToken = getCsrfToken;
