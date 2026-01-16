
const API_URL = "/search";
 
async function searchVideos() {
    const queryInput = document.getElementById("query");
    const resultsDiv = document.getElementById("results");
    const spinner = document.getElementById("loading-spinner");
 
    const query = queryInput.value.trim();
 
    if (!query) {
        alert("Please enter a search query");
        return;
    }
 
    resultsDiv.innerHTML = "";
    spinner.classList.remove("hidden");
 
    try {
        const response = await fetch(`${API_URL}?query=${encodeURIComponent(query)}`);
 
        if (!response.ok) {
            throw new Error("Failed to fetch results");
        }
 
        const data = await response.json();
 
        spinner.classList.add("hidden");
 
        if (!data.results || data.results.length === 0) {
            resultsDiv.innerHTML = `
<div style="grid-column: 1/-1; text-align:center; color:#ccc;">
<h3>No results found</h3>
<p>Try searching for something else.</p>
</div>
            `;
            return;
        }
 
        displayResults(data.results);
 
    } catch (error) {
        console.error(error);
        spinner.classList.add("hidden");
        resultsDiv.innerHTML = `
<div style="grid-column: 1/-1; text-align:center; color:#ff5555;">
<h3>Connection Error</h3>
<p>Could not connect to the backend server.</p>
</div>
        `;
    }
}
 
function displayResults(videos) {
    const resultsDiv = document.getElementById("results");
    resultsDiv.innerHTML = "";
 
    videos.forEach((video, index) => {
        const card = document.createElement("div");
        card.className = "video-card";
        card.style.animation = `fadeInUp 0.5s ease-out ${index * 0.1}s backwards`;
 
        const similarityScore = (video.score * 100).toFixed(0);
 
        card.innerHTML = `
<div class="score-badge">${similarityScore}% Match</div>
<img src="${video.thumbnail}" alt="thumbnail">
<div class="video-info">
<h3>${video.title}</h3>
<p>${video.description || "No description available."}</p>
<a href="https://www.youtube.com/watch?v=${video.video_id}" target="_blank" class="video-btn">
<i class="fab fa-youtube"></i> Watch Now
</a>
</div>
        `;
 
        resultsDiv.appendChild(card);
    });
}
 
document.getElementById("query").addEventListener("keypress", function (event) {
    if (event.key === "Enter") {
        searchVideos();
    }
});
