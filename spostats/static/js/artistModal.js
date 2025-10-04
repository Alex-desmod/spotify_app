document.addEventListener("DOMContentLoaded", () => {
  const artistLinks = document.querySelectorAll(".artist-link");

  artistLinks.forEach(link => {
    link.addEventListener("click", async event => {
      event.preventDefault();

      const artistId = link.dataset.artistId;
      if (!artistId) {
        console.error("No artistId");
        return;
      }

      try {
        const response = await fetch(`/artist/${artistId}/`);
        if (!response.ok) throw new Error("Request to the server error");

        const artist = await response.json();

        // Fill the modal
        document.getElementById("artistName").textContent = artist.name || "Unknown Artist";
        document.getElementById("artistImage").src = artist.images?.[0]?.url || "";
        document.getElementById("artistGenres").textContent = artist.genres?.join(", ") || "–";
        document.getElementById("artistFollowers").textContent = artist.followers?.total?.toLocaleString() || "–";

        // Popularity
        const popularity = artist.popularity ?? 0;
        document.getElementById("artistPopularity").textContent = popularity;
        const popularityBar = document.getElementById("artistPopularityBar");
        if (popularityBar) {
          popularityBar.style.width = `${popularity}%`;
        }

        // Spotify link
        const spotifyLink = document.getElementById("artistSpotifyLink");
        if (spotifyLink && artist.external_urls?.spotify) {
          spotifyLink.href = artist.external_urls.spotify;
        }

        // Show the modal
        const modal = new bootstrap.Modal(document.getElementById("artistModal"));
        modal.show();

      } catch (error) {
        console.error("Artist load error:", error);
      }
    });
  });
});
