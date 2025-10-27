document.addEventListener("DOMContentLoaded", () => {
    const editButtons = document.querySelectorAll(".edit-gig-btn");
    const form = document.getElementById("editGigForm");
    const deleteBtn = document.getElementById("deleteGig");

    let gigId = null;

    editButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            gigId = btn.dataset.id;
            document.getElementById("gig_id").value = gigId;
            document.getElementById("artist_name").value = btn.dataset.artist;
            document.getElementById("venue").value = btn.dataset.venue;
            document.getElementById("city").value = btn.dataset.city;
            document.getElementById("country").value = btn.dataset.country;
            document.getElementById("event_date").value = btn.dataset.date;
        });
    });

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const formData = new FormData(form);
        formData.append("action", "update");

        const response = await fetch(`/my-gigs/${gigId}/edit/`, {
            method: "POST",
            headers: {"X-CSRFToken": formData.get("csrfmiddlewaretoken")},
            body: formData
        });

        const data = await response.json();
        if (data.success) location.reload();
        else alert("Error updating gig");
    });

    deleteBtn.addEventListener("click", async () => {
        if (!confirm("Are you sure you want to delete this gig?")) return;

        const formData = new FormData();
        formData.append("action", "delete");

        const response = await fetch(`/my-gigs/${gigId}/edit/`, {
            method: "POST",
            headers: {"X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value},
            body: formData
        });

        const data = await response.json();
        if (data.deleted) location.reload();
    });
});
