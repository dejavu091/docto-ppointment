(function(){
  function el(id){return document.getElementById(id);} 
  function showStatus(msg){ var s=el('nearest-status'); if(s) s.textContent=msg; }

  function renderResults(features, map){
    var list = el('nearest-list');
    list.innerHTML='';
    features.forEach(function(f){
      var props = f.properties || {};
      var coords = f.geometry && f.geometry.coordinates || [];
      var lon = coords[0], lat = coords[1];
      var name = props.name || props.formatted || 'Unnamed';
      var addr = props.formatted || '';

      var li = document.createElement('li');
      li.textContent = name + (addr ? ' — ' + addr : '');
      list.appendChild(li);

      if (typeof L !== 'undefined'){
        var marker = L.marker([lat, lon]).addTo(map).bindPopup('<strong>' + name + '</strong><br/>' + addr);
      }
    });
  }

  function requestNearbyHospitals(){
    showStatus('Requesting location permission...');
    if (!navigator.geolocation){
      showStatus('Geolocation not supported by your browser.');
      return;
    }
    navigator.geolocation.getCurrentPosition(function(position){
      var lat = position.coords.latitude;
      var lon = position.coords.longitude;
      var container = el('nearest-container');
      if (container) container.style.display = 'block';

      // Initialize Leaflet map
      var map = L.map('nearest-map').setView([lat, lon], 13);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
      }).addTo(map);
      L.marker([lat, lon]).addTo(map).bindPopup('You are here').openPopup();

      showStatus('Searching for hospitals near you...');

      var apiKey = (window.GEOAPIFY_API_KEY || document.body.dataset.geoapifyKey || '');
      // If template injected GEOAPIFY_API_KEY, set it on body dataset for the script to read
      if (!apiKey && window.GEOAPIFY_API_KEY_RAW){ apiKey = window.GEOAPIFY_API_KEY_RAW; }

      if (!apiKey){
        showStatus('Geoapify API key not set.');
        return;
      }

      var radius = 5000; // meters
      var url = 'https://api.geoapify.com/v2/places?categories=healthcare.hospital&filter=circle:' + lon + ',' + lat + ',' + radius + '&limit=15&apiKey=' + encodeURIComponent(apiKey);

      fetch(url).then(function(res){ return res.json(); }).then(function(data){
        var features = data.features || [];
        if (features.length){
          showStatus('Found ' + features.length + ' hospitals near you.');
          renderResults(features, map);
          try{ var first = features[0].geometry.coordinates; map.setView([first[1], first[0]], 13); }catch(e){}
        } else {
          showStatus('No nearby hospitals found.');
        }
      }).catch(function(err){
        console.error(err);
        showStatus('Error searching for hospitals.');
      });
    }, function(err){
      showStatus('Location permission denied or unavailable.');
    }, { enableHighAccuracy: true, timeout: 10000 });
  }

  // Allow Django template to inject API key by setting on document.body.dataset
  document.addEventListener('DOMContentLoaded', function(){
    var btn = el('find-hospitals');
    if (btn) btn.addEventListener('click', requestNearbyHospitals);
  });
})();
