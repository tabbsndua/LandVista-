// Fetch initial site visits and subscribe to real-time updates
document.addEventListener('DOMContentLoaded', function () {
  const tbody = document.getElementById('visitsTbody');

  function renderVisitRow(v) {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${v.name || ''}</td>
      <td>${v.email || ''}</td>
      <td>${v.phone || ''}</td>
      <td>${v.property_title || ''}</td>
      <td>${v.visit_date || ''}</td>
      <td>${v.notes || ''}</td>
      <td>${v.created_at ? v.created_at.substring(0,19).replace('T',' ') : ''}</td>
    `;
    return tr;
  }

  function loadInitial() {
    fetch('/admin/api/site-visits').then(r => r.json()).then(data => {
      if (data && data.success) {
        tbody.innerHTML = '';
        data.visits.forEach(v => {
          tbody.appendChild(renderVisitRow(v));
        });
      } else {
        tbody.innerHTML = '<tr><td colspan="7">Failed to load visits</td></tr>';
      }
    }).catch(err => {
      console.error('Failed to load visits', err);
      tbody.innerHTML = '<tr><td colspan="7">Error loading visits</td></tr>';
    });
  }

  loadInitial();

  try {
    const socket = io();
    socket.on('site_visit_new', function (v) {
      // prepend new visit
      const row = renderVisitRow(v);
      if (tbody.firstChild && tbody.firstChild.textContent.trim() === 'Loading...') tbody.innerHTML = '';
      tbody.insertBefore(row, tbody.firstChild);
    });
  } catch (e) {
    console.warn('Socket.IO not available', e);
  }
});
