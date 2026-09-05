document.addEventListener("DOMContentLoaded", () => {
  const map = document.querySelector("#aaAfghanistanMap");
  if (!map) return;

  const pins = [...map.querySelectorAll(".aa-map-pin")];
  const routes = [...map.querySelectorAll(".aa-map-route")];
  const card = map.querySelector(".aa-map-card");
  const cardImage = card?.querySelector(".aa-map-card__image");
  const cardTitle = card?.querySelector(".aa-map-card__title");
  const cardSubtitle = card?.querySelector(".aa-map-card__subtitle");
  const cardLink = card?.querySelector(".aa-map-card__link");
  const plannerDestination = document.querySelector("#aaRouteDestination");
  const plannerDate = document.querySelector("#aaMapCheckIn");
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  let activeIndex = Math.max(0, pins.findIndex((pin) => pin.classList.contains("is-active")));
  let cycleTimer = null;
  let mapVisible = true;

  if (plannerDate && !plannerDate.min) {
    const today = new Date();
    const localToday = new Date(today.getTime() - today.getTimezoneOffset() * 60000)
      .toISOString()
      .slice(0, 10);
    plannerDate.min = localToday;
  }

  const syncPlannerDestination = (name) => {
    if (!plannerDestination || !name) return;
    const destinationName = name.trim().toLocaleLowerCase();
    const match = [...plannerDestination.options].find((option) => {
      const value = option.value.trim().toLocaleLowerCase();
      return value === destinationName || value.includes(destinationName) || destinationName.includes(value);
    });
    if (match?.value) plannerDestination.value = match.value;
  };

  const updateCard = (pin) => {
    if (!card || !pin) return;
    card.classList.add("is-switching");
    window.setTimeout(() => {
      const name = pin.dataset.name || "";
      if (cardImage) {
        cardImage.src = pin.dataset.image || cardImage.src;
        cardImage.alt = name;
      }
      if (cardTitle) cardTitle.textContent = name;
      if (cardSubtitle) cardSubtitle.textContent = pin.dataset.subtitle || "";
      if (cardLink) cardLink.href = pin.dataset.url || cardLink.href;
      card.classList.remove("is-switching");
    }, reducedMotion.matches ? 0 : 140);
  };

  const activatePin = (pin, options = {}) => {
    if (!pin) return;
    const routeName = pin.dataset.route;
    activeIndex = Math.max(0, pins.indexOf(pin));

    pins.forEach((item) => {
      const active = item === pin;
      item.classList.toggle("is-active", active);
      item.setAttribute("aria-pressed", active ? "true" : "false");
    });

    routes.forEach((route) => {
      route.classList.toggle("is-active", route.dataset.route === routeName);
    });

    updateCard(pin);
    if (options.syncPlanner !== false) syncPlannerDestination(pin.dataset.name);
  };

  const stopCycle = () => {
    if (cycleTimer) window.clearInterval(cycleTimer);
    cycleTimer = null;
  };

  const startCycle = () => {
    stopCycle();
    const candidates = pins;
    if (reducedMotion.matches || !mapVisible || candidates.length < 2) return;
    cycleTimer = window.setInterval(() => {
      const current = candidates.indexOf(pins[activeIndex]);
      const next = candidates[(current + 1 + candidates.length) % candidates.length];
      activatePin(next, { syncPlanner: false });
    }, 6500);
  };

  pins.forEach((pin) => {
    pin.addEventListener("click", () => {
      activatePin(pin);
      startCycle();
    });
    pin.addEventListener("focus", () => activatePin(pin));
    pin.addEventListener("keydown", (event) => {
      if (!['ArrowLeft', 'ArrowRight'].includes(event.key)) return;
      event.preventDefault();
      const candidates = pins;
      const current = Math.max(0, candidates.indexOf(pin));
      const direction = event.key === 'ArrowRight' ? 1 : -1;
      const next = candidates[(current + direction + candidates.length) % candidates.length];
      next?.focus();
    });
  });

  map.addEventListener("pointerenter", stopCycle);
  map.addEventListener("pointerleave", startCycle);
  map.addEventListener("focusin", stopCycle);
  map.addEventListener("focusout", (event) => {
    if (!map.contains(event.relatedTarget)) startCycle();
  });

  plannerDestination?.addEventListener("change", () => {
    const value = plannerDestination.value.trim().toLocaleLowerCase();
    if (!value) return;
    const pin = pins.find((item) => {
      const name = (item.dataset.name || "").toLocaleLowerCase();
      return value === name || value.includes(name) || name.includes(value);
    });
    if (pin) {
      activatePin(pin, { syncPlanner: false });
    }
  });

  reducedMotion.addEventListener?.("change", startCycle);

  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver((entries) => {
      mapVisible = entries.some((entry) => entry.isIntersecting);
      if (mapVisible) startCycle();
      else stopCycle();
    }, { threshold: 0.2 });
    observer.observe(map);
  } else {
    startCycle();
  }

  startCycle();
  activatePin(pins[activeIndex], { syncPlanner: false });
});
