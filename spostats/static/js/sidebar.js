document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll('#sidebarMenu .nav-link').forEach(link => {
        link.addEventListener('click', () => {
            const sidebar = document.getElementById('sidebarMenu');
            if (sidebar.classList.contains('show')) {
                const bsCollapse = bootstrap.Collapse.getInstance(sidebar);
                bsCollapse.hide();
            }
        });
    });
});
