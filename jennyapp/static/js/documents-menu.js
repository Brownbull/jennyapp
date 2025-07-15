// documents-menu.js: JS for Tailwind dashboard documents.html options dropdowns

document.addEventListener('DOMContentLoaded', function () {
    // Find all option menu buttons
    const optionButtons = document.querySelectorAll('button[id^="options-menu-"][aria-haspopup="true"]');
    optionButtons.forEach(function(btn) {
        const menuId = btn.getAttribute('id');
        const menu = btn.parentElement.querySelector('div[role="menu"]');
        let open = false;
        if (!menu) return;
        // Hide by default
        menu.style.display = 'none';
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            // Close all other menus
            document.querySelectorAll('div[role="menu"]').forEach(function(m) {
                if (m !== menu) m.style.display = 'none';
            });
            open = !open;
            menu.style.display = open ? 'block' : 'none';
            btn.setAttribute('aria-expanded', open);
        });
        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (open && !menu.contains(e.target) && !btn.contains(e.target)) {
                menu.style.display = 'none';
                open = false;
                btn.setAttribute('aria-expanded', 'false');
            }
        });
    });
});
