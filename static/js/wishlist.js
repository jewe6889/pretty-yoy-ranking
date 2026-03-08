/**
 * wishlist.js – client-side logic for the anime wishlist page.
 *
 * Features:
 *  • Loads Genre and Tag pills from the API, sorted by occurrence count desc.
 *  • Each pill shows the genre/tag name plus its count in a smaller font.
 *  • Pills rows are horizontally scrollable.
 *  • Clicking a pill toggles it as an active filter (AND logic across the
 *    same dimension, independent across genres vs tags).
 *  • Title search and status drop-down work alongside pill filters.
 *  • Clears all filters at once via the "Clear all" button.
 */

(function () {
  "use strict";

  // ── State ────────────────────────────────────────────────────────────────
  const state = {
    activeGenres: new Set(),
    activeTags: new Set(),
    search: "",
    status: "",
  };

  // Debounce timer for the search input
  let searchTimer;

  // ── DOM refs ─────────────────────────────────────────────────────────────
  const genresPillsEl = document.getElementById("genres-pills");
  const tagsPillsEl = document.getElementById("tags-pills");
  const entriesEl = document.getElementById("wishlist-entries");
  const resultsCountEl = document.getElementById("results-count");
  const activeFiltersEl = document.getElementById("active-filters");
  const activeFiltersListEl = document.getElementById("active-filters-list");
  const clearFiltersBtn = document.getElementById("clear-filters");
  const searchInput = document.getElementById("search-input");
  const statusSelect = document.getElementById("status-select");

  // ── Helpers ───────────────────────────────────────────────────────────────

  /**
   * Fetch JSON from a URL; throws on HTTP error.
   * @param {string} url
   * @returns {Promise<any>}
   */
  async function fetchJSON(url) {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status} fetching ${url}`);
    return res.json();
  }

  /**
   * Build a query-string from the current filter state.
   * @returns {string}  e.g. "?genres=Action,Drama&tags=Shounen&search=one"
   */
  function buildQueryString() {
    const params = new URLSearchParams();
    if (state.activeGenres.size) params.set("genres", [...state.activeGenres].join(","));
    if (state.activeTags.size) params.set("tags", [...state.activeTags].join(","));
    if (state.status) params.set("status", state.status);
    if (state.search) params.set("search", state.search);
    const qs = params.toString();
    return qs ? `?${qs}` : "";
  }

  /** Return a CSS class string for a status value. */
  function statusClass(status) {
    const map = {
      wishlist: "entry-status--wishlist",
      watching: "entry-status--watching",
      completed: "entry-status--completed",
    };
    return map[status.toLowerCase()] ?? "entry-status--wishlist";
  }

  // ── Pill rendering ────────────────────────────────────────────────────────

  /**
   * Render a list of {name, count} objects as clickable pills into a container.
   * Pills are already sorted descending by count from the API.
   *
   * @param {HTMLElement} container
   * @param {Array<{name: string, count: number}>} items
   * @param {Set<string>} activeSet  – reference to the matching state set
   */
  function renderPills(container, items, activeSet) {
    container.innerHTML = "";

    if (!items.length) {
      container.innerHTML = '<span class="pills-loading">No items found.</span>';
      return;
    }

    items.forEach(({ name, count }) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "pill" + (activeSet.has(name) ? " pill--active" : "");
      btn.setAttribute("aria-pressed", activeSet.has(name) ? "true" : "false");

      const nameSpan = document.createElement("span");
      nameSpan.textContent = name;

      const countSpan = document.createElement("span");
      countSpan.className = "pill-count";
      countSpan.textContent = count;

      btn.appendChild(nameSpan);
      btn.appendChild(countSpan);

      btn.addEventListener("click", () => {
        if (activeSet.has(name)) {
          activeSet.delete(name);
        } else {
          activeSet.add(name);
        }
        // Toggle pill style immediately (no full re-render needed)
        btn.classList.toggle("pill--active");
        btn.setAttribute("aria-pressed", activeSet.has(name) ? "true" : "false");

        refreshEntries();
        updateActiveFiltersBanner();
      });

      container.appendChild(btn);
    });
  }

  // ── Active-filters banner ─────────────────────────────────────────────────

  function updateActiveFiltersBanner() {
    const allFilters = [
      ...[...state.activeGenres].map((g) => ({ label: g, kind: "genre" })),
      ...[...state.activeTags].map((t) => ({ label: t, kind: "tag" })),
    ];

    if (!allFilters.length) {
      activeFiltersEl.hidden = true;
      return;
    }

    activeFiltersEl.hidden = false;
    activeFiltersListEl.innerHTML = allFilters
      .map(
        ({ label }) =>
          `<span class="active-filter-tag">${escapeHTML(label)}</span>`
      )
      .join("");
  }

  /** Minimal HTML escaping to prevent XSS when rendering dynamic text. */
  function escapeHTML(str) {
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // ── Entries rendering ─────────────────────────────────────────────────────

  async function refreshEntries() {
    entriesEl.innerHTML = '<li class="entry-placeholder">Loading…</li>';
    resultsCountEl.textContent = "";

    try {
      const entries = await fetchJSON(`/wishlist/api/entries${buildQueryString()}`);
      renderEntries(entries);
    } catch (err) {
      entriesEl.innerHTML = `<li class="entry-empty">Failed to load entries. ${escapeHTML(err.message)}</li>`;
    }
  }

  function renderEntries(entries) {
    resultsCountEl.textContent = `${entries.length} entr${entries.length === 1 ? "y" : "ies"}`;

    if (!entries.length) {
      entriesEl.innerHTML = '<li class="entry-empty">No entries match the current filters.</li>';
      return;
    }

    entriesEl.innerHTML = "";
    entries.forEach((entry) => {
      const li = document.createElement("li");
      li.className = "entry-card";

      const scoreHtml = entry.score != null
        ? `<span class="entry-score">★ ${entry.score}</span>`
        : "";

      const genreHtml = (entry.genres || [])
        .map((g) => `<span class="entry-genre-pill">${escapeHTML(g)}</span>`)
        .join("");

      const tagHtml = (entry.tags || [])
        .map((t) => `<span class="entry-tag-pill">${escapeHTML(t)}</span>`)
        .join("");

      li.innerHTML = `
        <div class="entry-title">${escapeHTML(entry.title)}</div>
        <div class="entry-meta">
          <span class="entry-status ${statusClass(entry.status)}">${escapeHTML(entry.status)}</span>
          ${entry.episodes ? `<span>${entry.episodes} eps</span>` : ""}
          ${scoreHtml}
        </div>
        ${genreHtml || tagHtml ? `<div class="entry-tags-row">${genreHtml}${tagHtml}</div>` : ""}
      `;

      entriesEl.appendChild(li);
    });
  }

  // ── Initialisation ────────────────────────────────────────────────────────

  async function loadPills() {
    try {
      const [genres, tags] = await Promise.all([
        fetchJSON("/wishlist/api/genres"),
        fetchJSON("/wishlist/api/tags"),
      ]);
      renderPills(genresPillsEl, genres, state.activeGenres);
      renderPills(tagsPillsEl, tags, state.activeTags);
    } catch (err) {
      genresPillsEl.innerHTML = `<span class="pills-loading">Failed to load genres.</span>`;
      tagsPillsEl.innerHTML = `<span class="pills-loading">Failed to load tags.</span>`;
    }
  }

  function init() {
    // Wire up search input with debounce
    searchInput.addEventListener("input", () => {
      clearTimeout(searchTimer);
      searchTimer = setTimeout(() => {
        state.search = searchInput.value.trim();
        refreshEntries();
      }, 250);
    });

    // Wire up status select
    statusSelect.addEventListener("change", () => {
      state.status = statusSelect.value;
      refreshEntries();
    });

    // Clear all filters
    clearFiltersBtn.addEventListener("click", () => {
      state.activeGenres.clear();
      state.activeTags.clear();
      state.search = "";
      state.status = "";
      searchInput.value = "";
      statusSelect.value = "";

      // Re-render pills to remove active state
      loadPills();
      updateActiveFiltersBanner();
      refreshEntries();
    });

    // Initial data load
    loadPills();
    refreshEntries();
  }

  // Run once DOM is ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
