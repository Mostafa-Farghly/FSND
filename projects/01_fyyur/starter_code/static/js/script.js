window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};

venueDeleteBtn = document.getElementById('venue-delete-btn');
venueDeleteBtn.onclick = function(e) {
  const venue_id = e.target.dataset['id'];
  fetch('/venues/' + venue_id, {
    method: 'DELETE'
  })
  .then(function(response) {
    return response.json();
  })
  .then(function(jsonResponse) {
    if(jsonResponse['success']) {
      //TODO
      window.location.replace('/');
    }
    else {
      //TODO
      window.location.replace('/venues/' + venue_id);
    }
  })
  .catch(function() {
    //TODO
    window.location.replace('/venues/' + venue_id);
  })
}
