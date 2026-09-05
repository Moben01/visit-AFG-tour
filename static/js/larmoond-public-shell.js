(function () {
  "use strict";

  const allowedActions = new Set(["private_journey_cta", "whatsapp_contact"]);
  const allowedPlacements = new Set([
    "header_desktop",
    "header_mobile",
    "footer",
    "homepage_hero",
    "homepage_tour",
    "homepage_tours_empty",
    "homepage_final",
  ]);

  function trackPublicAction(action, placement) {
    if (!allowedActions.has(action) || !allowedPlacements.has(placement)) return;

    const payload = Object.freeze({
      event: "public_cta_click",
      action,
      placement,
    });

    window.dispatchEvent(new CustomEvent("larmoond:public-action", { detail: payload }));
    if (Array.isArray(window.dataLayer)) window.dataLayer.push(payload);
  }

  document.addEventListener("click", (event) => {
    const control = event.target.closest("[data-analytics-event]");
    if (!control) return;
    trackPublicAction(control.dataset.analyticsEvent, control.dataset.analyticsPlacement);
  });

  document.addEventListener("DOMContentLoaded", () => {
    const navigation = document.getElementById("larmoondPrimaryNavigation");
    const toggle = document.querySelector(".lm-mobile-toggle");
    if (!navigation || !toggle) return;

    const icon = toggle.querySelector("i");
    const setMenuState = (isOpen) => {
      toggle.setAttribute("aria-label", isOpen ? toggle.dataset.closeLabel : toggle.dataset.openLabel);
      if (icon) {
        icon.classList.toggle("fa-bars", !isOpen);
        icon.classList.toggle("fa-xmark", isOpen);
      }
    };

    navigation.addEventListener("shown.bs.collapse", () => setMenuState(true));
    navigation.addEventListener("hidden.bs.collapse", () => setMenuState(false));

    document.addEventListener("keydown", (event) => {
      if (event.key !== "Escape" || !navigation.classList.contains("show")) return;
      const collapse = window.bootstrap?.Collapse.getOrCreateInstance(navigation, { toggle: false });
      if (collapse) collapse.hide();
      toggle.focus();
    });

    navigation.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => {
        if (!window.matchMedia("(max-width: 1279.98px)").matches) return;
        const collapse = window.bootstrap?.Collapse.getInstance(navigation);
        if (collapse) collapse.hide();
      });
    });
  });
})();
