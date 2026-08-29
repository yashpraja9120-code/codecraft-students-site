/**
 * YashTech — shared site behaviour.
 * No frameworks, no build step: plain DOM APIs so the site stays
 * fast and easy to host anywhere (including free static hosts).
 */

document.addEventListener("DOMContentLoaded", () => {
  initNavToggle();
  initFooterYear();
  initHeaderSearchForm();
  initBlogListing();
  initSearchPage();
  initContactForm();
  initFeedback();
  initVisitorTracking();
});

/* ---------- Mobile nav ---------- */
function initNavToggle() {
  const toggle = document.querySelector(".nav-toggle");
  const nav = document.querySelector(".main-nav");
  if (!toggle || !nav) return;

  toggle.addEventListener("click", () => {
    const isOpen = nav.classList.toggle("open");
    toggle.setAttribute("aria-expanded", String(isOpen));
  });

  nav.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      nav.classList.remove("open");
      toggle.setAttribute("aria-expanded", "false");
    });
  });
}

/* ---------- Footer year ---------- */
function initFooterYear() {
  document.querySelectorAll("[data-year]").forEach((el) => {
    el.textContent = new Date().getFullYear();
  });
}

/* ---------- Header search box: redirects to search.html?q= ---------- */
function initHeaderSearchForm() {
  const form = document.querySelector("[data-header-search]");
  if (!form) return;
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const q = form.querySelector("input").value.trim();
    const base = form.getAttribute("data-search-page") || "search.html";
    window.location.href = q ? `${base}?q=${encodeURIComponent(q)}` : base;
  });
}

/* ---------- Helpers ---------- */
function formatDate(iso) {
  const d = new Date(iso + "T00:00:00");
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}

function articleCardHTML(article) {
  return `
    <article class="article-card">
      <div class="tag-row">
        <span class="tag-pill">${article.category}</span>
      </div>
      <h3><a href="${article.slug}">${article.title}</a></h3>
      <p>${article.excerpt}</p>
      <div class="card-meta">
        <span>${formatDate(article.date)}</span>
        <span>&middot;</span>
        <span>${article.readTime}</span>
      </div>
      <a class="read-link" href="${article.slug}">Read article &rarr;</a>
    </article>`;
}

/* ---------- Blog listing page (with light client-side filter) ---------- */
function initBlogListing() {
  const grid = document.querySelector("[data-blog-grid]");
  if (!grid || typeof ARTICLES === "undefined") return;

  const params = new URLSearchParams(window.location.search);
  const initialQuery = params.get("q") || "";
  const filterInput = document.querySelector("[data-blog-filter]");
  const categoryButtons = document.querySelectorAll("[data-category-filter]");
  let activeCategory = "All";

  function render() {
    const query = (filterInput ? filterInput.value : "").trim().toLowerCase();
    const filtered = ARTICLES.filter((a) => {
      const matchesCategory = activeCategory === "All" || a.category === activeCategory;
      const haystack = `${a.title} ${a.excerpt} ${a.tags.join(" ")}`.toLowerCase();
      const matchesQuery = query === "" || haystack.includes(query);
      return matchesCategory && matchesQuery;
    });

    grid.innerHTML = filtered.map(articleCardHTML).join("") ||
      `<p class="no-results visible">No articles match that search yet. Try a different keyword.</p>`;

    const countEl = document.querySelector("[data-result-count]");
    if (countEl) countEl.textContent = `${filtered.length} article${filtered.length === 1 ? "" : "s"}`;
  }

  if (filterInput) {
    filterInput.value = initialQuery;
    filterInput.addEventListener("input", render);
  }

  categoryButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      categoryButtons.forEach((b) => b.classList.remove("btn-primary"));
      categoryButtons.forEach((b) => b.classList.add("btn-outline"));
      btn.classList.remove("btn-outline");
      btn.classList.add("btn-primary");
      activeCategory = btn.dataset.categoryFilter;
      render();
    });
  });

  render();
}

/* ---------- Dedicated /search.html page ---------- */
function initSearchPage() {
  const resultsEl = document.querySelector("[data-search-results]");
  if (!resultsEl || typeof ARTICLES === "undefined") return;

  const input = document.querySelector("[data-search-input]");
  const params = new URLSearchParams(window.location.search);
  const initialQuery = params.get("q") || "";
  if (input) input.value = initialQuery;

  function render() {
    const query = (input ? input.value : "").trim().toLowerCase();
    const metaEl = document.querySelector("[data-search-meta]");

    if (query === "") {
      resultsEl.innerHTML = "";
      if (metaEl) metaEl.textContent = "Start typing to search every article by title, topic, or tag.";
      return;
    }

    const filtered = ARTICLES.filter((a) => {
      const haystack = `${a.title} ${a.excerpt} ${a.tags.join(" ")} ${a.category}`.toLowerCase();
      return haystack.includes(query);
    });

    if (metaEl) {
      metaEl.textContent = `${filtered.length} result${filtered.length === 1 ? "" : "s"} for "${query}"`;
    }

    resultsEl.innerHTML = filtered.map(articleCardHTML).join("") ||
      `<p class="no-results visible">Nothing matched "${query}". Try a broader term like "python" or "ai".</p>`;
  }

  if (input) {
    input.addEventListener("input", render);
    input.focus();
  }
  render();
}

/* ---------- Contact form (front-end only demo handling) ---------- */
function initContactForm() {
  const form = document.querySelector("[data-contact-form]");
  if (!form) return;

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const successEl = document.querySelector("[data-contact-success]");
    if (successEl) {
      successEl.classList.add("visible");
      successEl.setAttribute("role", "status");
    }
    form.reset();
    /*
      This demo stores nothing and sends nothing — it only shows a
      confirmation message. To actually receive messages, connect this
      form to a form backend (Formspree, Netlify Forms, your own
      server endpoint, etc.) and post the fields there instead.
    */
  });
}

/* ---------- Feedback system ---------- */
function initFeedback() {
  const openButtons = document.querySelectorAll("[data-feedback-open]");
  if (!openButtons.length) return;

  let modal = document.querySelector("[data-feedback-modal]");

  if (!modal) {
    modal = document.createElement("div");
    modal.className = "feedback-modal";
    modal.setAttribute("data-feedback-modal", "");
    modal.setAttribute("aria-hidden", "true");

    modal.innerHTML = `
      <div class="feedback-overlay" data-feedback-close></div>

      <div class="feedback-box" role="dialog" aria-modal="true" aria-labelledby="feedback-title">
        <button class="feedback-close" type="button" data-feedback-close aria-label="Close feedback">
          &times;
        </button>

        <span class="eyebrow">your feedback</span>
        <h2 id="feedback-title">How was your experience?</h2>
        <p class="feedback-subtitle">A quick rating helps us improve the website.</p>

        <div class="feedback-stars" role="radiogroup" aria-label="Rating">
          <button type="button" data-rating="1" aria-label="1 star">★</button>
          <button type="button" data-rating="2" aria-label="2 stars">★</button>
          <button type="button" data-rating="3" aria-label="3 stars">★</button>
          <button type="button" data-rating="4" aria-label="4 stars">★</button>
          <button type="button" data-rating="5" aria-label="5 stars">★</button>
        </div>

        <textarea
          class="feedback-message"
          placeholder="Tell us more (optional)"
          maxlength="1000"
          aria-label="Optional feedback"
        ></textarea>

        <button class="btn btn-primary btn-block" type="button" data-feedback-submit>
          Submit Feedback
        </button>

        <p class="feedback-status" data-feedback-status role="status"></p>
      </div>
    `;

    document.body.appendChild(modal);
  }

  let selectedRating = 0;

  const stars = modal.querySelectorAll("[data-rating]");
  const messageInput = modal.querySelector(".feedback-message");
  const submitButton = modal.querySelector("[data-feedback-submit]");
  const status = modal.querySelector("[data-feedback-status]");

  function openModal() {
    modal.classList.add("open");
    modal.setAttribute("aria-hidden", "false");
    selectedRating = 0;
    stars.forEach((star) => star.classList.remove("selected"));
    messageInput.value = "";
    status.textContent = "";
  }

  function closeModal() {
    modal.classList.remove("open");
    modal.setAttribute("aria-hidden", "true");
  }

  openButtons.forEach((button) => {
    button.addEventListener("click", (e) => {
      e.preventDefault();
      openModal();
    });
  });

  modal.querySelectorAll("[data-feedback-close]").forEach((button) => {
    button.addEventListener("click", closeModal);
  });

  stars.forEach((star) => {
    star.addEventListener("click", () => {
      selectedRating = Number(star.dataset.rating);

      stars.forEach((item) => {
        item.classList.toggle(
          "selected",
          Number(item.dataset.rating) <= selectedRating
        );
      });
    });
  });

  submitButton.addEventListener("click", async () => {
    if (!selectedRating) {
      status.textContent = "Please select a star rating.";
      return;
    }

    submitButton.disabled = true;
    status.textContent = "Sending...";

    try {
      const response = await fetch("http://127.0.0.1:5000/api/feedback", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          rating: selectedRating,
          message: messageInput.value.trim()
        })
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.message || "Something went wrong.");
      }

      status.textContent = "Thanks for your feedback! ❤️";

      setTimeout(() => {
        closeModal();
      }, 1200);

    } catch (error) {
      console.error("Feedback error:", error);
      status.textContent = "Could not submit feedback. Please try again.";
    } finally {
      submitButton.disabled = false;
    }
  });
}
/* ---------- Visitor Tracking ---------- */
function initVisitorTracking() {
  let visitorId = localStorage.getItem("yashtech_visitor_id");

  if (!visitorId) {
    visitorId =
      "visitor_" +
      Date.now() +
      "_" +
      Math.random().toString(36).substring(2, 10);

    localStorage.setItem(
      "yashtech_visitor_id",
      visitorId
    );
  }

  fetch("http://127.0.0.1:5000/api/visit", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      visitor_id: visitorId,
      page: window.location.pathname
    })
  })
    .then(response => response.json())
    .then(data => {
      console.log("Visitor tracking:", data.message);
    })
    .catch(error => {
      console.error(
        "Visitor tracking error:",
        error
      );
    });
}