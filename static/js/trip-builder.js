(function () {
  "use strict";

  const form = document.querySelector("[data-trip-builder]");
  if (!form) return;

  const panels = Array.from(form.querySelectorAll("[data-trip-step]"));
  const stepButtons = Array.from(document.querySelectorAll("[data-trip-step-button]"));
  const backButton = form.querySelector("[data-step-back]");
  const nextButton = form.querySelector("[data-step-next]");
  const submitButton = form.querySelector("[data-step-submit]");
  let currentStep = Math.max(
    0,
    panels.findIndex((panel) => panel.querySelector(".errorlist, .has-error"))
  );

  function showStep(index) {
    currentStep = Math.min(Math.max(index, 0), panels.length - 1);
    panels.forEach((panel, panelIndex) => {
      const active = panelIndex === currentStep;
      panel.hidden = !active;
      panel.classList.toggle("is-active", active);
    });
    stepButtons.forEach((button, buttonIndex) => {
      button.classList.toggle("is-active", buttonIndex === currentStep);
      button.classList.toggle("is-complete", buttonIndex < currentStep);
      button.setAttribute("aria-current", buttonIndex === currentStep ? "step" : "false");
    });
    backButton.hidden = currentStep === 0;
    nextButton.hidden = currentStep === panels.length - 1;
    submitButton.hidden = currentStep !== panels.length - 1;
    form.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function panelIsValid(panel) {
    const fields = Array.from(panel.querySelectorAll("input, select, textarea"));
    const invalid = fields.find((field) => !field.disabled && !field.checkValidity());
    if (invalid) {
      invalid.reportValidity();
      invalid.focus({ preventScroll: true });
      return false;
    }
    return true;
  }

  nextButton.addEventListener("click", function () {
    if (panelIsValid(panels[currentStep])) showStep(currentStep + 1);
  });
  backButton.addEventListener("click", function () {
    showStep(currentStep - 1);
  });
  stepButtons.forEach((button, index) => {
    button.addEventListener("click", function () {
      if (index <= currentStep || panelIsValid(panels[currentStep])) showStep(index);
    });
  });
  form.addEventListener("submit", function (event) {
    const invalidIndex = panels.findIndex((panel) => !panelIsValid(panel));
    if (invalidIndex !== -1) {
      event.preventDefault();
      showStep(invalidIndex);
    }
  });

  const stopList = form.querySelector("[data-route-stops]");
  const addStopButton = form.querySelector("[data-stop-add]");
  const emptyStop = document.getElementById("aaEmptyStop");
  const totalForms = form.querySelector("[name='stops-TOTAL_FORMS']");

  function visibleStops() {
    return Array.from(stopList.querySelectorAll("[data-route-stop]")).filter(
      (stop) => stop.style.display !== "none"
    );
  }

  function updateStopOrder() {
    visibleStops().forEach((stop, index) => {
      const number = stop.querySelector("[data-stop-number]");
      const position = stop.querySelector("[name$='-position']");
      if (number) number.textContent = index + 1;
      if (position) position.value = index + 1;
      const up = stop.querySelector("[data-stop-up]");
      const down = stop.querySelector("[data-stop-down]");
      if (up) up.disabled = index === 0;
      if (down) down.disabled = index === visibleStops().length - 1;
    });
    addStopButton.disabled = visibleStops().length >= 12;
  }

  function bindStop(stop) {
    const remove = stop.querySelector("[data-stop-remove]");
    const up = stop.querySelector("[data-stop-up]");
    const down = stop.querySelector("[data-stop-down]");
    remove.addEventListener("click", function () {
      if (visibleStops().length <= 1) return;
      const deleteField = stop.querySelector("[name$='-DELETE']");
      if (deleteField) {
        deleteField.checked = true;
        stop.style.display = "none";
      } else {
        stop.remove();
      }
      updateStopOrder();
    });
    up.addEventListener("click", function () {
      const previous = stop.previousElementSibling;
      if (previous) stopList.insertBefore(stop, previous);
      updateStopOrder();
    });
    down.addEventListener("click", function () {
      const next = stop.nextElementSibling;
      if (next) stopList.insertBefore(next, stop);
      updateStopOrder();
    });
  }

  stopList.querySelectorAll("[data-route-stop]").forEach(bindStop);
  addStopButton.addEventListener("click", function () {
    if (visibleStops().length >= 12) return;
    const index = Number(totalForms.value);
    const wrapper = document.createElement("div");
    wrapper.innerHTML = emptyStop.innerHTML.replaceAll("__prefix__", String(index)).trim();
    const stop = wrapper.firstElementChild;
    stopList.appendChild(stop);
    totalForms.value = index + 1;
    bindStop(stop);
    updateStopOrder();
    stop.querySelector("select").focus();
  });

  const selectionInputs = form.querySelectorAll("[name='entry-selection_mode']");
  const entrySelect = form.querySelector("[name='entry-selected_entry_point']");
  const selfEntry = form.querySelector("[data-entry-self]");
  const otherEntry = form.querySelector("[data-entry-other]");

  function updateEntryFields() {
    const checked = form.querySelector("[name='entry-selection_mode']:checked");
    const isSelf = checked && checked.value === "self";
    selfEntry.hidden = !isSelf;
    entrySelect.required = Boolean(isSelf);
    const isOther = isSelf && entrySelect.value === "other";
    otherEntry.hidden = !isOther;
    const otherInput = otherEntry.querySelector("input");
    if (otherInput) otherInput.required = Boolean(isOther);
  }

  selectionInputs.forEach((input) => input.addEventListener("change", updateEntryFields));
  entrySelect.addEventListener("change", updateEntryFields);
  updateEntryFields();
  updateStopOrder();
  showStep(currentStep === -1 ? 0 : currentStep);
})();
