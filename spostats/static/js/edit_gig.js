document.addEventListener("DOMContentLoaded", () => {
    const editButtons = document.querySelectorAll(".edit-gig-btn");
    const form = document.getElementById("editGigForm");
    const deleteBtn = document.getElementById("deleteGig");
    const modal = document.getElementById("editGigModal");

    let gigId = null;

    // fill the modal form
    editButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            gigId = btn.dataset.id;
            form.querySelector("#artist_name").value = btn.dataset.artist || "";
            form.querySelector("#venue").value = btn.dataset.venue || "";
            form.querySelector("#city").value = btn.dataset.city || "";
            form.querySelector("#country").value = btn.dataset.country || "";
            form.querySelector("#event_date").value = btn.dataset.date || "";
        });
    });

    // refresh the entry
    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        if (!gigId) return alert("Gig ID not found");

        const formData = new FormData(form);
        formData.append("action", "update");

        const response = await fetch(`/my-gigs/${gigId}/edit/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": formData.get("csrfmiddlewaretoken"),
            },
            body: formData
        });

        const data = await response.json();
        if (data.success) {
            bootstrap.Modal.getInstance(modal).hide();
            location.reload();
        } else {
            alert("Error updating gig");
        }
    });

    // delete the entry
    deleteBtn.addEventListener("click", async () => {
        if (!gigId) return alert("No gig selected");
        if (!confirm("Are you sure you want to delete this gig?")) return;

        const formData = new FormData();
        formData.append("action", "delete");

        const response = await fetch(`/my-gigs/${gigId}/edit/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
            },
            body: formData
        });

        const data = await response.json();
        if (data.deleted) {
            bootstrap.Modal.getInstance(modal).hide();
            location.reload();
        } else {
            alert("Error deleting gig");
        }
    });
});

