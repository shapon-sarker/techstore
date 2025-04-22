document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('sidebar');
    const topbar = document.querySelector('.topbar');
    const mainContent = document.querySelector('.main-content');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const themeToggle = document.getElementById('themeToggle');

    // Sidebar Toggle
    sidebarToggle.addEventListener('click', function() {
        sidebar.classList.toggle('collapsed');
        topbar.classList.toggle('full-width');
        mainContent.classList.toggle('expanded');
    });

    // Theme Toggle
    themeToggle.addEventListener('click', function() {
        const html = document.documentElement;
        const isDark = html.getAttribute('data-bs-theme') === 'dark';
        html.setAttribute('data-bs-theme', isDark ? 'light' : 'dark');
        themeToggle.querySelector('i').className = isDark ? 'fas fa-moon' : 'fas fa-sun';
    });

    // Mobile Responsive
    if (window.innerWidth <= 768) {
        sidebar.classList.add('collapsed');
        topbar.classList.add('full-width');
        mainContent.classList.add('expanded');
    }

    window.addEventListener('resize', function() {
        if (window.innerWidth <= 768) {
            sidebar.classList.add('collapsed');
            topbar.classList.add('full-width');
            mainContent.classList.add('expanded');
        }
    });
}); 