document.addEventListener('DOMContentLoaded', function() {
    const addGigForm = document.getElementById('addGigForm');

    addGigForm.addEventListener('submit', async function(event) {
        event.preventDefault();

        const formData = {
            date: document.getElementById('addDate').value,
            artist: document.getElementById('addArtist').value,
            venue: document.getElementById('addVenue').value,
            city: document.getElementById('addCity').value,
            country: document.getElementById('addCountry').value,
        };

        const response = await fetch('/my-gigs/add/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(formData)
        });

        if (response.ok) {
            // close the modal window
            const modal = bootstrap.Modal.getInstance(document.getElementById('addGigModal'));
            modal.hide();

            // refresh the page or add a new entry dynamically
            location.reload();
        } else {
            alert('Failed to add gig. Please try again.');
        }
    });

    // function for CSRF-token
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }
});
