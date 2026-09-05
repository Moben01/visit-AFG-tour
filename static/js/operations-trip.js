(function () {
  "use strict";
  const form = document.querySelector("[data-proposal-builder]");
  if (!form) return;
  const list = form.querySelector("[data-proposal-days]");
  const addButton = form.querySelector("[data-proposal-day-add]");
  const template = document.getElementById("opsEmptyProposalDay");
  const total = form.querySelector("[name='days-TOTAL_FORMS']");

  function nextDayNumber() {
    const values = Array.from(list.querySelectorAll("[name$='-day_number']"))
      .filter((field) => {
        const row = field.closest("[data-proposal-day]");
        const deleteField = row && row.querySelector("[name$='-DELETE']");
        return !deleteField || !deleteField.checked;
      })
      .map((field) => Number(field.value) || 0);
    return Math.max(0, ...values) + 1;
  }

  addButton.addEventListener("click", function () {
    const index = Number(total.value);
    const wrapper = document.createElement("div");
    wrapper.innerHTML = template.innerHTML.replaceAll("__prefix__", String(index)).trim();
    const row = wrapper.firstElementChild;
    list.appendChild(row);
    total.value = index + 1;
    const dayNumber = row.querySelector("[name$='-day_number']");
    if (dayNumber) dayNumber.value = nextDayNumber();
    const title = row.querySelector("[name$='-title']");
    if (title) title.focus();
  });
})();
