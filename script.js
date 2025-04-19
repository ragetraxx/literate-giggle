function fetchStations() {
    const query = document.getElementById("search-input").value.trim();

    if (!query) {
        alert("Please enter a country code or station name.");
        return;
    }

    let url;
    const apiBaseUrl = 'http://fi1.api.radio-browser.info/json';

    if (query.length === 2) {
        // 2-letter country code
        url = `${apiBaseUrl}/stations/bycountrycodeexact/${query.toUpperCase()}`;
    } else {
        // Search by station name
        url = `${apiBaseUrl}/stations/byname/${encodeURIComponent(query)}`;
    }

    fetch(url)
        .then(response => response.json())
        .then(data => displayStations(data))
        .catch(error => console.error("Error fetching stations:", error));
}

function displayStations(stations) {
    const container = document.getElementById("station-list");
    container.innerHTML = "";

    if (stations.length === 0) {
        container.innerHTML = "<p>No stations found.</p>";
        return;
    }

    stations.forEach(station => {
        const stationItem = document.createElement("div");
        stationItem.classList.add("station");
        stationItem.innerHTML = `
            <img src="${station.favicon || 'default.png'}" alt="Logo">
            <p>${station.name}</p>
            <button onclick="playRadio('${station.url_resolved}', '${station.name}', '${station.favicon}')">▶ Play</button>
        `;
        container.appendChild(stationItem);
    });
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
