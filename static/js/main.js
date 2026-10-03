/* SmartTourist – main.js */
'use strict';

// ── Navbar scroll ─────────────────────────────────────────────────────────────
window.addEventListener('scroll', () => {
  document.getElementById('mainNav')?.classList.toggle('scrolled', window.scrollY > 50);
});

// ── On DOM ready ──────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  // Auto-dismiss toasts
  document.querySelectorAll('.toast.show').forEach(el => {
    setTimeout(() => bootstrap.Toast.getOrCreateInstance(el).hide(), 4000);
  });

  // Fade-up scroll animations
  const obs = new IntersectionObserver(entries => {
    entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('visible'); obs.unobserve(e.target); } });
  }, { threshold: 0.1 });
  document.querySelectorAll('.listing-card,.dest-card,.guide-card,.svc-card,.step-card,.stat-card')
    .forEach(el => { el.classList.add('fade-up'); obs.observe(el); });

  // Gallery
  initGallery();

  // Unread notification badge
  loadNotifCount();

  // Set min datetime to now for booking forms
  document.querySelectorAll('input[type="datetime-local"]').forEach(el => {
    const now = new Date(); now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    el.min = now.toISOString().slice(0, 16);
  });

  // Hero search tab switching
  document.querySelectorAll('.s-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.s-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      const form = tab.closest('form');
      if (form && tab.dataset.target) form.action = '/' + tab.dataset.target + '/';
    });
  });
});

// ── Weather ───────────────────────────────────────────────────────────────────
function loadWeather(loc) {
  const div = document.getElementById('weatherData');
  if (!div) return;
  div.innerHTML = '<div class="text-center p-3"><i class="fas fa-spinner fa-spin"></i></div>';
  fetch('/ai/weather/?location=' + encodeURIComponent(loc))
    .then(r => r.json())
    .then(d => {
      div.innerHTML = `
        <div class="w-temp">${Math.round(d.temperature)}°C</div>
        <div class="w-desc">${d.description}</div>
        <div class="w-details">
          <div><i class="fas fa-tint"></i>${d.humidity}%</div>
          <div><i class="fas fa-wind"></i>${d.wind_speed} km/h</div>
          <div><i class="fas fa-thermometer-half"></i>Feels ${Math.round(d.feels_like)}°C</div>
        </div>`;
    })
    .catch(() => { div.innerHTML = '<p class="text-center text-muted p-3">Weather unavailable</p>'; });
}

// ── Chatbot ───────────────────────────────────────────────────────────────────
let _session = localStorage.getItem('_cbSession') || _uuid();
localStorage.setItem('_cbSession', _session);
let _cbOpen = false;

function toggleChatbot() {
  const body = document.getElementById('cbBody');
  const icon = document.getElementById('cbIcon');
  _cbOpen = !_cbOpen;
  body.style.display = _cbOpen ? 'block' : 'none';
  if (icon) icon.className = _cbOpen ? 'fas fa-chevron-up ms-auto' : 'fas fa-chevron-down ms-auto';
}

function sendChat() {
  const inp = document.getElementById('cbInput');
  const msg = inp.value.trim();
  if (!msg) return;
  _appendMsg(msg, 'user');
  inp.value = '';
  _appendTyping();
  fetch('/ai/chatbot/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': _csrf() },
    body: JSON.stringify({ message: msg, session_id: _session })
  })
  .then(r => r.json())
  .then(d => { _removeTyping(); _appendMsg(d.response || 'Sorry, try again.', 'bot'); })
  .catch(() => { _removeTyping(); _appendMsg('Connection error. Please try again.', 'bot'); });
}

function _appendMsg(text, role) {
  const c = document.getElementById('cbMessages');
  if (!c) return;
  const d = document.createElement('div');
  d.className = role === 'bot' ? 'cb-bot' : 'cb-user';
  d.innerHTML = role === 'bot'
    ? `<div class="cb-icon"><i class="fas fa-robot"></i></div><div class="cb-bubble">${text.replace(/\n/g,'<br>')}</div>`
    : `<div class="cb-bubble">${_esc(text)}</div>`;
  c.appendChild(d);
  c.scrollTop = c.scrollHeight;
}
function _appendTyping() {
  const c = document.getElementById('cbMessages');
  if (!c) return;
  const d = document.createElement('div');
  d.className = 'cb-bot'; d.id = 'cbTyping';
  d.innerHTML = '<div class="cb-icon"><i class="fas fa-robot"></i></div><div class="cb-bubble"><span class="typing-dots"><span></span><span></span><span></span></span></div>';
  c.appendChild(d); c.scrollTop = c.scrollHeight;
}
function _removeTyping() { document.getElementById('cbTyping')?.remove(); }

document.addEventListener('keydown', e => {
  if (e.key === 'Enter' && document.activeElement?.id === 'cbInput') sendChat();
});

// ── SOS ───────────────────────────────────────────────────────────────────────
function showSOS() { new bootstrap.Modal(document.getElementById('sosModal')).show(); }

// ── Favorites ─────────────────────────────────────────────────────────────────
function toggleFav(type, id, btn) {
  const fd = new FormData();
  fd.append('item_type', type); fd.append('item_id', id);
  fd.append('csrfmiddlewaretoken', _csrf());
  fetch('/api/toggle-favorite/', { method: 'POST', body: fd })
    .then(r => r.json())
    .then(d => {
      if (d.status === 'added')   { btn.classList.add('active');    btn.innerHTML = '<i class="fas fa-heart"></i>';  showToast('Added to favorites!','success'); }
      if (d.status === 'removed') { btn.classList.remove('active'); btn.innerHTML = '<i class="far fa-heart"></i>'; showToast('Removed from favorites','info'); }
    })
    .catch(() => { window.location.href = '/accounts/login/?next=' + window.location.pathname; });
}

// ── Booking price calculator ──────────────────────────────────────────────────
function calcPrice(ppd, pph) {
  const s  = document.getElementById('id_start_datetime');
  const e  = document.getElementById('id_end_datetime');
  const rt = document.getElementById('id_rental_type');
  const out= document.getElementById('priceEstimate');
  if (!s || !e || !out) return;
  const start = new Date(s.value), end = new Date(e.value);
  if (isNaN(start) || isNaN(end) || end <= start) { out.textContent = '—'; return; }
  const hrs  = (end - start) / 3600000;
  const days = hrs / 24;
  const type = rt ? rt.value : 'daily';
  const amt  = type === 'hourly' ? pph * hrs : ppd * Math.ceil(days);
  out.textContent = '₹' + amt.toFixed(2);
}

// ── Availability check ────────────────────────────────────────────────────────
function checkAvail(vid) {
  const s = document.getElementById('id_start_datetime')?.value;
  const e = document.getElementById('id_end_datetime')?.value;
  const b = document.getElementById('availBadge');
  if (!s || !e || !b) return;
  b.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Checking...';
  b.className = 'badge bg-secondary ms-2';
  fetch(`/vehicles/${vid}/availability/?start=${encodeURIComponent(s)}&end=${encodeURIComponent(e)}`)
    .then(r => r.json())
    .then(d => {
      if (d.available) { b.innerHTML='<i class="fas fa-check-circle me-1"></i>Available'; b.className='badge bg-success ms-2'; }
      else             { b.innerHTML='<i class="fas fa-times-circle me-1"></i>Unavailable'; b.className='badge bg-danger ms-2'; }
    });
}

// ── Admin Charts ─────────────────────────────────────────────────────────────
function initBookingChart(labels, vb, hb, gb) {
  const ctx = document.getElementById('bookingChart');
  if (!ctx) return;
  new Chart(ctx, {
    type: 'bar',
    data: { labels, datasets: [
      { label:'Vehicle Bookings', data:vb, backgroundColor:'rgba(26,107,74,.8)',  borderRadius:6 },
      { label:'Hotel Bookings',   data:hb, backgroundColor:'rgba(244,160,36,.8)', borderRadius:6 },
      { label:'Guide Bookings',   data:gb, backgroundColor:'rgba(41,128,185,.8)', borderRadius:6 },
    ]},
    options: { responsive:true, maintainAspectRatio:false,
      plugins:{ legend:{ position:'top' } },
      scales:{ y:{ beginAtZero:true, grid:{ color:'#f0f0f0' } }, x:{ grid:{ display:false } } }
    }
  });
}

function initRevenueChart(labels, data) {
  const ctx = document.getElementById('revenueChart');
  if (!ctx) return;
  new Chart(ctx, {
    type: 'line',
    data: { labels, datasets:[{ label:'Revenue (₹)', data,
      borderColor:'rgba(26,107,74,1)', backgroundColor:'rgba(26,107,74,.08)',
      borderWidth:2, pointBackgroundColor:'rgba(26,107,74,1)', pointRadius:5, tension:.4, fill:true }]},
    options: { responsive:true, maintainAspectRatio:false,
      plugins:{ legend:{ display:false } },
      scales:{ y:{ beginAtZero:true, ticks:{ callback: v=>'₹'+v.toLocaleString() }, grid:{ color:'#f0f0f0' } }, x:{ grid:{ display:false } } }
    }
  });
}

// ── Notifications ─────────────────────────────────────────────────────────────
function loadNotifCount() {
  const b = document.getElementById('notifBadge');
  const bd = document.getElementById('notifBadgeDropdown');
  if (!b && !bd) return;
  fetch('/notifications/unread-count/')
    .then(r => r.json())
    .then(d => {
      if (d.count > 0) {
        const text = d.count > 9 ? '9+' : d.count;
        if (b) { b.textContent = text; b.classList.remove('d-none'); }
        if (bd) { bd.textContent = text; bd.classList.remove('d-none'); }
      } else {
        if (b) b.classList.add('d-none');
        if (bd) bd.classList.add('d-none');
      }
    }).catch(()=>{});
}

// ── Gallery ───────────────────────────────────────────────────────────────────
function initGallery() {
  const main   = document.getElementById('mainImg');
  const thumbs = document.querySelectorAll('.gallery-thumb');
  if (!main || !thumbs.length) return;
  thumbs.forEach(t => t.addEventListener('click', () => {
    main.src = t.dataset.src || t.src;
    thumbs.forEach(x => x.classList.remove('active'));
    t.classList.add('active');
  }));
}

// ── Admin block toggle ────────────────────────────────────────────────────────
function toggleBlock(uid, btn) {
  fetch(`/admin-panel/users/${uid}/block/`, {
    method:'POST', headers:{'X-CSRFToken':_csrf(),'Content-Type':'application/json'}
  })
  .then(r=>r.json())
  .then(d=>{
    if(d.status==='blocked')   { btn.textContent='Unblock'; btn.className='btn btn-sm btn-success'; showToast('User blocked','warning'); }
    else                       { btn.textContent='Block';   btn.className='btn btn-sm btn-danger';  showToast('User unblocked','success'); }
  });
}

// ── Vendor booking action ─────────────────────────────────────────────────────
function manageBooking(bid, action, btn) {
  fetch(`/vehicles/vendor/booking/${bid}/${action}/`, {
    method:'POST', headers:{'X-CSRFToken':_csrf(),'Content-Type':'application/json'}
  })
  .then(r=>r.json())
  .then(d=>{
    if(d.status==='success'){
      showToast(`Booking ${action==='accept'?'accepted':'rejected'}!`, action==='accept'?'success':'warning');
      setTimeout(()=>location.reload(), 1200);
    }
  });
}

// ── Hotel owner booking action ────────────────────────────────────────────────
function manageHotelBooking(bid, action, btn) {
  fetch(`/hotels/hotel-dashboard/booking/${bid}/${action}/`, {
    method:'POST', headers:{'X-CSRFToken':_csrf(),'Content-Type':'application/json'}
  })
  .then(r=>r.json())
  .then(d=>{
    if(d.status==='success'){
      showToast(`Booking ${action==='confirm'?'confirmed':'cancelled'}!`, action==='confirm'?'success':'warning');
      setTimeout(()=>location.reload(), 1200);
    }
  });
}

// ── Hotel owner room availability toggle ──────────────────────────────────────
function toggleRoom(rid) {
  fetch(`/hotels/hotel-dashboard/room/${rid}/toggle/`, {
    method:'POST', headers:{'X-CSRFToken':_csrf(),'Content-Type':'application/json'}
  }).then(()=>location.reload());
}

// ── Vehicle owner availability toggle ─────────────────────────────────────────
function toggleVehicle(vid) {
  fetch(`/vehicles/vendor/${vid}/toggle/`, {
    method:'POST', headers:{'X-CSRFToken':_csrf(),'Content-Type':'application/json'}
  }).then(()=>location.reload());
}

// ── Guide booking action ──────────────────────────────────────────────────────
function manageGuideBooking(bid, action, btn) {
  fetch(`/guides/guide-dashboard/booking/${bid}/${action}/`, {
    method:'POST', headers:{'X-CSRFToken':_csrf(),'Content-Type':'application/json'}
  })
  .then(r=>r.json())
  .then(d=>{
    if(d.status==='success'){
      showToast(`Booking ${action==='accept'?'accepted':'rejected'}!`, action==='accept'?'success':'warning');
      setTimeout(()=>location.reload(), 1200);
    }
  });
}

// ── Guide availability toggle ─────────────────────────────────────────────────
function toggleGuide() {
  fetch(`/guides/guide-dashboard/toggle/`, {
    method:'POST', headers:{'X-CSRFToken':_csrf(),'Content-Type':'application/json'}
  }).then(()=>location.reload());
}

// ── Admin mobile sidebar drawer ────────────────────────────────────────────────
function toggleAdminSidebar() {
  const sb = document.querySelector('.admin-sidebar');
  let bd = document.querySelector('.admin-backdrop');
  if (!bd) {
    bd = document.createElement('div');
    bd.className = 'admin-backdrop';
    bd.onclick = () => toggleAdminSidebar();
    document.body.appendChild(bd);
  }
  sb?.classList.toggle('open');
  bd.classList.toggle('open');
}

// ── Toast helper ──────────────────────────────────────────────────────────────
function showToast(msg, type='info') {
  const colors = {success:'bg-success',error:'bg-danger',warning:'bg-warning text-dark',info:'bg-info'};
  let c = document.querySelector('.toast-container');
  if(!c){ c=document.createElement('div'); c.className='toast-container position-fixed top-0 end-0 p-3'; c.style.zIndex='1100'; document.body.appendChild(c); }
  const t = document.createElement('div');
  t.className = `toast show align-items-center text-white ${colors[type]||'bg-primary'}`;
  t.setAttribute('role','alert');
  t.innerHTML = `<div class="d-flex"><div class="toast-body">${_esc(msg)}</div><button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button></div>`;
  c.appendChild(t);
  setTimeout(()=>{ bootstrap.Toast.getOrCreateInstance(t).hide(); t.remove(); }, 3500);
}

// ── Utils ─────────────────────────────────────────────────────────────────────
function _csrf() {
  const v = `; ${document.cookie}`;
  const p = v.split('; csrftoken=');
  if(p.length===2) return p.pop().split(';').shift();
  return '';
}
function _esc(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
function _uuid() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c=>{
    const r=Math.random()*16|0; return(c==='x'?r:(r&0x3|0x8)).toString(16);
  });
}
