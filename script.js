function fetchStations() {
  const query = document.getElementById("search-input").value.trim();

  if (!query) {
    alert("Please enter a country code or station name.");
    return;
  }

  let url;
  const apiBaseUrl = 'https://de2.api.radio-browser.info/';

  if (query.length === 2) {
    url = `${apiBaseUrl}/stations/bycountrycodeexact/${query.toUpperCase()}`;
  } else {
    url = `${apiBaseUrl}/stations/byname/${encodeURIComponent(query)}`;
  }

  fetch(url)
    .then(response => response.json())
    .then(data => displayStations(data))
    .catch(error => console.error("Error fetching stations:", error));
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
    stationItem.onclick = () => playRadio(station.url_resolved, station.name, station.favicon);

    stationItem.innerHTML = `
      <img src="${station.favicon || 'default.png'}" alt="Logo" />
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

  document.getElementById("player-title").innerText = name;
  document.getElementById("player-logo").src = logo || "default.png";
  document.getElementById("radio-player").src = url;
  document.getElementById("player-container").style.display = "flex";

  document.getElementById("radio-player").play();
}

function closePlayer() {
  document.getElementById("player-container").style.display = "none";
  document.getElementById("radio-player").pause();
}

function playStation(streamUrl, title, logo) {
  playRadio(streamUrl, title, logo);
}

function filterFeaturedStations() {
  const query = document.getElementById("search-input").value.trim().toLowerCase();
  const stations = document.querySelectorAll("#featured-stations .station");

  stations.forEach(station => {
    const name = station.textContent.toLowerCase();
    if (name.includes(query)) {
      station.style.display = "flex";
    } else {
      station.style.display = "none";
    }
  });
}
