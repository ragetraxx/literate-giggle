function fetchStations() {
    const countryCode = document.getElementById("countryCode").value.trim().toUpperCase();
    if (!countryCode) {
        alert("Please enter a country code!");
        return;
    }

    fetch("stations.json")
        .then(response => response.json())
        .then(data => {
            const stationsList = document.getElementById("stationsList");
            stationsList.innerHTML = ""; // Clear previous results
            
            const filteredStations = data.filter(station => station.code === countryCode);

            if (filteredStations.length === 0) {
                stationsList.innerHTML = "<p>No stations found.</p>";
                return;
            }

            filteredStations.forEach(station => {
                const stationElement = document.createElement("div");
                stationElement.classList.add("station");
                stationElement.innerHTML = `
                    <img src="${station.logo || 'default-logo.png'}" alt="${station.name}">
                    <p>${station.name}</p>
                `;
                stationElement.onclick = () => playRadio(station);
                stationsList.appendChild(stationElement);
            });
        })
        .catch(error => console.error("Error loading stations:", error));
}

function playRadio(station) {
    const playerContainer = document.getElementById("playerContainer");
    const audioPlayer = document.getElementById("audioPlayer");
    const stationLogo = document.getElementById("stationLogo");

    audioPlayer.src = station.url;
    stationLogo.src = station.logo || "default-logo.png";

    playerContainer.style.display = "flex";
    stationLogo.classList.remove("stopped"); // Start rotation
    audioPlayer.play();

    audioPlayer.onpause = () => stationLogo.classList.add("stopped");
}

function closePlayer() {
    const playerContainer = document.getElementById("playerContainer");
    const audioPlayer = document.getElementById("audioPlayer");
    const stationLogo = document.getElementById("stationLogo");

    audioPlayer.pause();
    playerContainer.style.display = "none";
    stationLogo.classList.add("stopped"); // Stop rotation
}
