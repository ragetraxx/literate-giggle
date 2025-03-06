document.addEventListener("DOMContentLoaded", loadSavedStations);

function searchStations() {
    let countryCode = document.getElementById("countryCode").value.trim().toUpperCase();
    if (!countryCode) {
        alert("Please enter a country code.");
        return;
    }

    fetch(`https://de1.api.radio-browser.info/json/stations/bycountrycodeexact/${countryCode}`)
        .then(response => response.json())
        .then(data => {
            let resultsDiv = document.getElementById("results");
            resultsDiv.innerHTML = "";

            let stations = data.filter(station => station.url).map(station => ({
                name: station.name || "Unknown",
                url: station.url,
                logo: station.favicon || "default.png",
                country: station.country || "Unknown"
            }));

            stations.forEach(station => {
                let stationDiv = document.createElement("div");
                stationDiv.className = "station";
                stationDiv.innerHTML = `
                    <img src="${station.logo}" alt="${station.name}">
                    <p>${station.name}</p>
                `;
                stationDiv.onclick = () => playStation(station);

                resultsDiv.appendChild(stationDiv);
            });

            saveStations(stations);
        })
        .catch(error => console.error("Error fetching stations:", error));
}

function saveStations(stations) {
    localStorage.setItem("savedStations", JSON.stringify(stations));
    loadSavedStations();
}

function loadSavedStations() {
    let savedResultsDiv = document.getElementById("savedResults");
    savedResultsDiv.innerHTML = "";

    let stations = JSON.parse(localStorage.getItem("savedStations")) || [];
    stations.forEach(station => {
        let stationDiv = document.createElement("div");
        stationDiv.className = "station";
        stationDiv.innerHTML = `
            <img src="${station.logo}" alt="${station.name}">
            <p>${station.name}</p>
        `;
        stationDiv.onclick = () => playStation(station);

        savedResultsDiv.appendChild(stationDiv);
    });
}

function playStation(station) {
    document.getElementById("popup").classList.remove("hidden");
    document.getElementById("stationImage").src = station.logo;
    let audioPlayer = document.getElementById("audioPlayer");
    audioPlayer.src = station.url;
    audioPlayer.play();
}

function stopPlayback() {
    document.getElementById("popup").classList.add("hidden");
    let audioPlayer = document.getElementById("audioPlayer");
    audioPlayer.pause();
    audioPlayer.src = "";
}