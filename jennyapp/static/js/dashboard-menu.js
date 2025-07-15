// dashboard-menu.js: JS for Tailwind dashboard.html off-canvas sidebar and user menu

console.log('dashboard-menu.js loaded');
document.addEventListener('DOMContentLoaded', function () {
    // Off-canvas sidebar for mobile
    // Only one dialog for sidebar, so just select by role
    const sidebarDialog = document.querySelector('div[role="dialog"]');
    // Find the open sidebar button by its sr-only span text
    const sidebarOpenBtn = Array.from(document.querySelectorAll('button')).find(btn => {
        const sr = btn.querySelector('.sr-only');
        return sr && sr.textContent.trim().toLowerCase().includes('open sidebar');
    });
    let sidebarCloseBtn = null;
    if (sidebarDialog) {
        sidebarCloseBtn = Array.from(sidebarDialog.querySelectorAll('button')).find(btn => {
            const sr = btn.querySelector('.sr-only');
            return sr && sr.textContent.trim().toLowerCase().includes('close sidebar');
        });
    }
    // Hide sidebar by default
    if (sidebarDialog) sidebarDialog.style.display = 'none';
    if (sidebarOpenBtn && sidebarDialog) {
        sidebarOpenBtn.addEventListener('click', function () {
            sidebarDialog.style.display = 'block';
        });
    }
    if (sidebarCloseBtn && sidebarDialog) {
        sidebarCloseBtn.addEventListener('click', function () {
            sidebarDialog.style.display = 'none';
        });
    }
    // Hide sidebar when clicking backdrop
    if (sidebarDialog) {
        const backdrop = sidebarDialog.querySelector('.fixed.inset-0');
        if (backdrop) {
            backdrop.addEventListener('click', function () {
                sidebarDialog.style.display = 'none';
            });
        }
    }

    // User menu dropdown (top right)
    const userMenuBtn = document.getElementById('user-menu-button');
    const userMenu = userMenuBtn && userMenuBtn.parentElement.querySelector('div[role="menu"]');
    let userMenuOpen = false;
    if (userMenuBtn && userMenu) {
        userMenuBtn.addEventListener('click', function (e) {
            e.stopPropagation();
            userMenuOpen = !userMenuOpen;
            userMenu.style.display = userMenuOpen ? 'block' : 'none';
            userMenuBtn.setAttribute('aria-expanded', userMenuOpen);
        });
        document.addEventListener('click', function (e) {
            if (userMenuOpen && !userMenu.contains(e.target) && !userMenuBtn.contains(e.target)) {
                userMenu.style.display = 'none';
                userMenuOpen = false;
                userMenuBtn.setAttribute('aria-expanded', 'false');
            }
        });
        userMenu.style.display = 'none';
    }
});