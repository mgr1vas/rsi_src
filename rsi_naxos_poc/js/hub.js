// Smooth "futuristic" page-leave transition before navigating away.
document.querySelectorAll('a[data-nav]').forEach(link => {
    link.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        if (!href || href === '#') return;
        e.preventDefault();
        document.body.classList.add('leaving');
        setTimeout(() => { window.location.href = href; }, 420);
    });
});