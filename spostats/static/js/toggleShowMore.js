// general handler for the "Show more / Show less" button
document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-toggle-button]").forEach(button => {
        const targetSelector = button.getAttribute("data-bs-target");
        const target = document.querySelector(targetSelector);

        if (target) {
            target.addEventListener("shown.bs.collapse", () => {
                button.textContent = "Show less";
            });

            target.addEventListener("hidden.bs.collapse", () => {
                button.textContent = "Show more";
            });
        }
    });
});
