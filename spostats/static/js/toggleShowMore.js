// general handler for the "Show more / Show less" button
document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-toggle-button]").forEach(button => {
        const targetSelector = button.getAttribute("data-bs-target");
        const target = document.querySelector(targetSelector);

        if (target) {
            target.addEventListener("shown.bs.collapse", () => {
                button.innerHTML = `<img src="/static/images/icons/fold.svg" alt="less" width="40">`;
            });

            target.addEventListener("hidden.bs.collapse", () => {
                button.innerHTML = `<img src="/static/images/icons/unfold.svg" alt="more" width="40">`;
            });
        }
    });
});
