// Dropdown menu functionality for Tailwind header

document.addEventListener('DOMContentLoaded', function () {
    // Desktop Product flyout
    const productBtn = document.querySelector('button[aria-expanded][class*="gap-x-1"]');
    const productMenu = productBtn && productBtn.parentElement.querySelector('div.absolute');
    let productMenuOpen = false;

    if (productBtn && productMenu) {
        productBtn.addEventListener('click', function (e) {
            e.stopPropagation();
            productMenuOpen = !productMenuOpen;
            productMenu.style.display = productMenuOpen ? 'block' : 'none';
            productBtn.setAttribute('aria-expanded', productMenuOpen);
        });
        // Hide menu when clicking outside
        document.addEventListener('click', function (e) {
            if (productMenuOpen && !productMenu.contains(e.target) && !productBtn.contains(e.target)) {
                productMenu.style.display = 'none';
                productMenuOpen = false;
                productBtn.setAttribute('aria-expanded', 'false');
            }
        });
        // Hide by default
        productMenu.style.display = 'none';
    }

    // Mobile menu open/close
    const mobileMenuBtn = document.querySelector('button.inline-flex.items-center.justify-center');
    const mobileMenu = document.querySelector('div[role="dialog"].lg\\:hidden');
    let mobileMenuCloseBtn = null;
    if (mobileMenu) {
        mobileMenuCloseBtn = Array.from(mobileMenu.querySelectorAll('button')).find(btn => {
            const sr = btn.querySelector('.sr-only');
            return sr && sr.textContent.trim().toLowerCase().includes('close menu');
        });
    }
    if (mobileMenuBtn && mobileMenu) {
        mobileMenuBtn.addEventListener('click', function () {
            mobileMenu.style.display = 'block';
        });
    }
    if (mobileMenuCloseBtn && mobileMenu) {
        mobileMenuCloseBtn.addEventListener('click', function () {
            mobileMenu.style.display = 'none';
        });
    }
    if (mobileMenu) mobileMenu.style.display = 'none';

    // Mobile Product submenu
    const mobileProductBtn = mobileMenu && Array.from(mobileMenu.querySelectorAll('button')).find(btn => btn.getAttribute('aria-controls') === 'products');
    const mobileProductMenu = mobileMenu && mobileMenu.querySelector('#products');
    let mobileProductMenuOpen = false;
    if (mobileProductBtn && mobileProductMenu) {
        mobileProductBtn.addEventListener('click', function (e) {
            e.stopPropagation();
            mobileProductMenuOpen = !mobileProductMenuOpen;
            mobileProductMenu.style.display = mobileProductMenuOpen ? 'block' : 'none';
            mobileProductBtn.setAttribute('aria-expanded', mobileProductMenuOpen);
            const icon = mobileProductBtn.querySelector('svg');
            if (icon) {
                icon.style.transform = mobileProductMenuOpen ? 'rotate(180deg)' : '';
            }
        });
        mobileProductMenu.style.display = 'none';
    }
});
