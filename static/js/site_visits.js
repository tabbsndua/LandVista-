// Connect to Socket.IO and listen for new site visit events
document.addEventListener('DOMContentLoaded', function () {
  try {
    const socket = io();
    socket.on('site_visit_new', function (data) {
      console.log('New site visit received:', data);
      // Developer: update the admin UI here. Example:
      // const list = document.getElementById('site-visits-list');
      // if (list) { list.insertAdjacentHTML('afterbegin', `<li>${data.name} - ${data.property_title} - ${data.visit_date}</li>`); }
    });
  } catch (e) {
    console.warn('Socket.IO not available for site_visits.js', e);
  }
});
