document.addEventListener("DOMContentLoaded", () => {
  const siteHeader = document.querySelector(".aa-site-header");
  if (siteHeader) {
    let headerFramePending = false;
    const updateStickyHeader = () => {
      siteHeader.classList.toggle("is-sticky", window.scrollY > 130);
      headerFramePending = false;
    };

    window.addEventListener("scroll", () => {
      if (headerFramePending) return;
      headerFramePending = true;
      window.requestAnimationFrame(updateStickyHeader);
    }, { passive: true });
    updateStickyHeader();
  }

  const hoverMenuQuery = window.matchMedia("(min-width: 1200px) and (hover: hover) and (pointer: fine)");
  const navigationDropdowns = [...document.querySelectorAll(".aa-category-row > .dropdown")];

  navigationDropdowns.forEach((dropdown) => {
    const toggle = dropdown.querySelector(".aa-category-link[data-bs-toggle='dropdown']");
    if (!toggle) return;

    let closeTimer;
    const getDropdownInstance = () => {
      if (!window.bootstrap?.Dropdown) return null;
      return window.bootstrap.Dropdown.getOrCreateInstance(toggle);
    };
    const openDropdown = () => {
      if (!hoverMenuQuery.matches) return;
      window.clearTimeout(closeTimer);

      navigationDropdowns.forEach((otherDropdown) => {
        if (otherDropdown === dropdown) return;
        const otherToggle = otherDropdown.querySelector(".aa-category-link[data-bs-toggle='dropdown']");
        const otherInstance = otherToggle && window.bootstrap?.Dropdown.getInstance(otherToggle);
        if (otherInstance) otherInstance.hide();
      });

      const instance = getDropdownInstance();
      if (instance) instance.show();
    };
    const closeDropdown = () => {
      if (!hoverMenuQuery.matches) return;
      window.clearTimeout(closeTimer);
      closeTimer = window.setTimeout(() => {
        const instance = getDropdownInstance();
        if (instance) instance.hide();
      }, 140);
    };

    dropdown.addEventListener("mouseenter", openDropdown);
    dropdown.addEventListener("mouseleave", closeDropdown);
    toggle.addEventListener("focus", openDropdown);
    dropdown.addEventListener("focusout", (event) => {
      if (!dropdown.contains(event.relatedTarget)) closeDropdown();
    });
  });

  document.querySelectorAll(".aa-message-stack").forEach((messageStack) => {
    messageStack.querySelectorAll(".alert").forEach((message) => {
      window.setTimeout(() => {
        const removeMessage = () => {
          if (!message.isConnected) return;
          message.remove();
          if (!messageStack.querySelector(".alert")) messageStack.remove();
        };

        message.setAttribute("aria-hidden", "true");
        message.classList.add("is-hiding");
        message.addEventListener("transitionend", removeMessage, { once: true });
        window.setTimeout(removeMessage, 350);
      }, 5000);
    });
  });

  document.querySelectorAll("[data-aa-scroll]").forEach((button) => {
    button.addEventListener("click", () => {
      const target = document.querySelector(button.dataset.aaTarget);
      if (!target) return;
      const direction = button.dataset.aaScroll === "previous" ? -1 : 1;
      target.scrollBy({ left: direction * Math.min(target.clientWidth * 0.8, 760), behavior: "smooth" });
    });
  });

  const tabButtons = [...document.querySelectorAll("[data-aa-tab]")];
  const exploreCards = [...document.querySelectorAll("#aaExploreGrid [data-aa-group]")];
  tabButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const selected = button.dataset.aaTab;
      tabButtons.forEach((item) => {
        const active = item === button;
        item.classList.toggle("active", active);
        item.setAttribute("aria-selected", active ? "true" : "false");
      });
      exploreCards.forEach((card) => {
        card.hidden = selected !== "all" && card.dataset.aaGroup !== selected;
      });
    });
  });

  const dateInput = document.querySelector('input[name="check_in"]');
  if (dateInput && !dateInput.min) {
    const now = new Date();
    const localDate = new Date(now.getTime() - now.getTimezoneOffset() * 60000);
    dateInput.min = localDate.toISOString().slice(0, 10);
  }

  const backToTop = document.querySelector(".back-to-top");
  if (backToTop) {
    const updateBackToTop = () => backToTop.classList.toggle("is-visible", window.scrollY > 500);
    window.addEventListener("scroll", updateBackToTop, { passive: true });
    updateBackToTop();
  }
});
