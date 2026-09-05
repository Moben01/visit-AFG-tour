(function () {
  "use strict";

  const shell = document.querySelector("[data-operations-shell]");
  if (!shell) return;

  const sidebar = shell.querySelector(".ops-sidebar");
  const openButton = shell.querySelector("[data-ops-sidebar-open]");
  const closeTargets = shell.querySelectorAll("[data-ops-sidebar-close]");
  const collapseButton = shell.querySelector("[data-ops-sidebar-collapse]");
  const desktopQuery = window.matchMedia("(min-width: 1025px)");

  const setMobileOpen = (open) => {
    shell.classList.toggle("is-sidebar-open", open);
    document.body.classList.toggle("ops-no-scroll", open);
    openButton?.setAttribute("aria-expanded", String(open));
    if (open) sidebar?.focus({ preventScroll: true });
  };

  const setCollapsed = (collapsed, persist) => {
    shell.classList.toggle("is-collapsed", collapsed);
    collapseButton?.setAttribute("aria-expanded", String(!collapsed));
    const icon = collapseButton?.querySelector("i");
    if (icon) {
      icon.className = collapsed
        ? "ti ti-layout-sidebar-left-expand"
        : "ti ti-layout-sidebar-left-collapse";
    }
    if (persist) {
      try {
        localStorage.setItem("larmoond-ops-sidebar", collapsed ? "collapsed" : "expanded");
      } catch (_) {
        // Storage can be unavailable in private browsing.
      }
    }
  };

  try {
    setCollapsed(
      desktopQuery.matches && localStorage.getItem("larmoond-ops-sidebar") === "collapsed",
      false
    );
  } catch (_) {
    setCollapsed(false, false);
  }

  openButton?.addEventListener("click", () => setMobileOpen(true));
  closeTargets.forEach((target) => target.addEventListener("click", () => setMobileOpen(false)));
  collapseButton?.addEventListener("click", () => {
    if (!desktopQuery.matches) {
      setMobileOpen(false);
      return;
    }
    setCollapsed(!shell.classList.contains("is-collapsed"), true);
  });

  desktopQuery.addEventListener("change", (event) => {
    setMobileOpen(false);
    if (!event.matches) setCollapsed(false, false);
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      setMobileOpen(false);
      document.querySelectorAll(".ops-profile-menu[open]").forEach((menu) => menu.removeAttribute("open"));
    }
  });

  sidebar?.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      if (!desktopQuery.matches) setMobileOpen(false);
    });
  });

  const searchForm = shell.querySelector("[data-ops-command-search]");
  const searchInput = shell.querySelector("[data-ops-nav-search]");
  const searchResults = shell.querySelector("[data-ops-search-results]");
  const mobileSearchButton = shell.querySelector("[data-ops-mobile-search]");
  const topbar = shell.querySelector(".ops-topbar");
  const navigationLinks = Array.from(shell.querySelectorAll(".ops-nav a"));

  const hideSearchResults = () => {
    if (searchResults) searchResults.hidden = true;
  };

  const renderSearchResults = () => {
    if (!searchInput || !searchResults) return;
    const query = searchInput.value.trim().toLocaleLowerCase();
    searchResults.replaceChildren();
    if (!query) {
      searchResults.hidden = true;
      return;
    }

    const matches = navigationLinks
      .filter((link) => link.textContent.trim().toLocaleLowerCase().includes(query))
      .slice(0, 8);

    matches.forEach((link) => {
      const result = document.createElement("a");
      result.href = link.href;
      const sourceIcon = link.querySelector("i");
      const icon = document.createElement("i");
      icon.className = sourceIcon?.className || "ti ti-arrow-right";
      const label = document.createElement("span");
      label.textContent = link.textContent.trim();
      result.append(icon, label);
      searchResults.append(result);
    });

    if (!matches.length) {
      const empty = document.createElement("span");
      empty.className = "ops-search-results__empty";
      empty.textContent = searchInput.getAttribute("data-empty-label") || "No dashboard section found";
      searchResults.append(empty);
    }
    searchResults.hidden = false;
  };

  searchForm?.addEventListener("submit", (event) => {
    event.preventDefault();
    searchResults?.querySelector("a")?.click();
  });
  searchInput?.addEventListener("input", renderSearchResults);
  searchInput?.addEventListener("focus", renderSearchResults);
  mobileSearchButton?.addEventListener("click", () => {
    const isOpen = topbar?.classList.toggle("is-searching");
    mobileSearchButton.setAttribute("aria-expanded", String(Boolean(isOpen)));
    if (isOpen) window.setTimeout(() => searchInput?.focus(), 0);
  });

  document.addEventListener("pointerdown", (event) => {
    if (searchForm && !searchForm.contains(event.target) && !mobileSearchButton?.contains(event.target)) {
      hideSearchResults();
      if (window.innerWidth <= 760) {
        topbar?.classList.remove("is-searching");
        mobileSearchButton?.setAttribute("aria-expanded", "false");
      }
    }
    document.querySelectorAll(".ops-profile-menu[open]").forEach((menu) => {
      if (!menu.contains(event.target)) menu.removeAttribute("open");
    });
  });

  document.addEventListener("keydown", (event) => {
    const target = event.target;
    const isTyping = target instanceof HTMLInputElement || target instanceof HTMLTextAreaElement || target instanceof HTMLSelectElement || target?.isContentEditable;
    if (event.key === "/" && !isTyping && searchInput) {
      event.preventDefault();
      searchInput.focus();
    }
  });

  const dismissToast = (toast) => {
    if (!toast || toast.classList.contains("is-leaving")) return;
    toast.classList.add("is-leaving");
    window.setTimeout(() => toast.remove(), 220);
  };

  shell.querySelectorAll("[data-ops-toast]").forEach((toast) => {
    toast.querySelector("[data-ops-toast-close]")?.addEventListener("click", () => dismissToast(toast));
    window.setTimeout(() => dismissToast(toast), 6000);
  });
})();
