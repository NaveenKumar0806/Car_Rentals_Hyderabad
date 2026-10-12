// Small UX helpers: loading indicator on booking submit, navbar active link.
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("booking-form");
  if (form) {
    form.addEventListener("submit", (e) => {
      const btn = form.querySelector('button[type="submit"]');
      if (btn) { btn.disabled = true; btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Processing…'; }
    });
  }
  const path = window.location.pathname;
  document.querySelectorAll(".navbar-nav .nav-link").forEach((a) => {
    if (a.getAttribute("href") === path) a.classList.add("active");
  });
});
