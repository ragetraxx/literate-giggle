function fetchStations() {
  const query = document.getElementById("search-input").value.trim();

  if (!query) {
    alert("Please enter a country code or station name.");
    return;
  }

  // FIXED: Added 'json' to the base URL path
  const apiBaseUrl = 'https://de2.api.radio-browser.info/json';
  let url;

  if (query.length === 2) {
    // Search by country code (e.g., 'PH') + Sort by popularity
    url = `${apiBaseUrl}/stations/bycountrycodeexact/${query.toUpperCase()}?order=votes&reverse=true`;
  } else {
    // Search by name (e.g., 'Power') + Sort by popularity
    url = `${apiBaseUrl}/stations/byname/${encodeURIComponent(query)}?order=votes&reverse=true`;
  }

  fetch(url)
    .then(response => {
      if (!response.ok) throw new Error('Network response was not ok');
      return response.json();
    })
    .then(data => displayStations(data))
    .catch(error => {
      console.error("Error fetching stations:", error);
      document.getElementById("search-results").innerHTML = "<p>Error loading stations. Please try again.</p>";
    });
}

function displayStations(stations) {
  const container = document.getElementById("search-results");
  container.innerHTML = "";

  if (stations.length === 0) {
    container.innerHTML = "<p>No stations found.</p>";
    container.style.display = "flex";
    return;
  }

  stations.forEach(station => {
    const stationItem = document.createElement("div");
    stationItem.classList.add("station");
    
    // Using url_resolved is better as it bypasses playlist files (.pls/.m3u)
    stationItem.onclick = () => playRadio(station.url_resolved, station.name, station.favicon);

    stationItem.innerHTML = `
      <img src="${station.favicon || 'default.png'}" onerror="this.src='default.png';" alt="Logo" />
      <p>${station.name}</p>
    `;
    container.appendChild(stationItem);
  });

  container.style.display = "flex";
}

function playRadio(url, name, logo) {
  if (!url) {
    alert("This station has no available stream.");
    return;
  }

  const player = document.getElementById("radio-player");
  
  document.getElementById("player-title").innerText = name;
  document.getElementById("player-logo").src = logo || "default.png";
  player.src = url;
  document.getElementById("player-container").style.display = "flex";

  // Error handling for the audio element itself
  player.play().catch(e => {
    console.error("Playback failed:", e);
    alert("Stream could not be played. It might be offline or blocked by your browser.");
  });
}

function closePlayer() {
  const player = document.getElementById("radio-player");
  document.getElementById("player-container").style.display = "none";
  player.pause();
  player.src = ""; // Stop buffering in the background
}

function playStation(streamUrl, title, logo) {
  playRadio(streamUrl, title, logo);
}

function filterFeaturedStations() {
  const query = document.getElementById("search-input").value.trim().toLowerCase();
  const stations = document.querySelectorAll("#featured-stations .station");

  stations.forEach(station => {
    const name = station.textContent.toLowerCase();
    station.style.display = name.includes(query) ? "flex" : "none";
  });
}
