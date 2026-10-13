// ========================================================
// AI SCREENING PLATFORM — INTERACTIVE STUDIO MICRO-INTERACTIONS
// ========================================================

document.addEventListener('DOMContentLoaded', () => {
    // 1. Navbar scroll glass elevation
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 40) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        }, { passive: true });
    }

    // 2. Interactive Triage Studio Hero Mode Switcher
    const tabButtons = document.querySelectorAll('.triage-tab-btn');
    const viewContainers = document.querySelectorAll('.triage-view-content');

    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetViewId = btn.getAttribute('data-target');

            tabButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            viewContainers.forEach(view => {
                if (view.id === targetViewId) {
                    view.style.display = 'block';
                    view.style.opacity = '0';
                    view.style.transform = 'translateY(8px)';
                    requestAnimationFrame(() => {
                        view.style.transition = 'opacity 0.25s ease, transform 0.25s ease';
                        view.style.opacity = '1';
                        view.style.transform = 'translateY(0)';
                    });
                } else {
                    view.style.display = 'none';
                }
            });
        });
    });

    // 3. Mini Sandbox Interactive "Run Test" trigger on Hero
    const heroRunBtn = document.getElementById('hero-run-code-btn');
    const heroTermOutput = document.getElementById('hero-term-status-badge');
    const heroAssertionLog = document.getElementById('hero-assertion-log');

    if (heroRunBtn && heroTermOutput && heroAssertionLog) {
        heroRunBtn.addEventListener('click', () => {
            heroRunBtn.innerHTML = 'Executing...';
            heroTermOutput.innerHTML = 'COMPILING';
            heroTermOutput.style.color = '#FFB703';

            setTimeout(() => {
                const randomLatency = (Math.random() * 3 + 2.1).toFixed(1);
                heroRunBtn.innerHTML = '✓ Ran Successfully';
                heroTermOutput.innerHTML = 'PASSED (0 ERRORS)';
                heroTermOutput.style.color = 'var(--lime)';
                heroAssertionLog.innerHTML = `> 12/12 assertions verified · Total runtime: ${randomLatency}ms`;

                setTimeout(() => {
                    heroRunBtn.innerHTML = '▶ Re-run Test Suite';
                }, 2000);
            }, 600);
        });
    }

    // 4. Smooth Anchor Scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            if (targetId.length > 1) {
                const targetElem = document.querySelector(targetId);
                if (targetElem) {
                    e.preventDefault();
                    targetElem.scrollIntoView({ behavior: 'smooth' });
                }
            }
        });
    });
});
