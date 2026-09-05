(function () {
  "use strict";

  document.addEventListener("DOMContentLoaded", function () {
    var tourEditor = document.querySelector("[data-tour-editor]");
    if (tourEditor) {
      var typeField = tourEditor.querySelector("#id_type");
      var scheduleFields = tourEditor.querySelectorAll("[data-schedule-field]");
      var flexibleNote = tourEditor.querySelector("[data-flexible-note]");

      function updateScheduleFields() {
        if (!typeField) return;
        var scheduled = typeField.value === "schedule";
        scheduleFields.forEach(function (field) {
          field.hidden = !scheduled;
        });
        if (flexibleNote) flexibleNote.hidden = scheduled;
      }

      if (typeField) {
        typeField.addEventListener("change", updateScheduleFields);
        updateScheduleFields();
      }

      var requestPrice = tourEditor.querySelector("[data-price-on-request]");
      var priceField = tourEditor.querySelector("[data-tour-price]");

      function updatePriceField() {
        if (!requestPrice || !priceField) return;
        priceField.disabled = requestPrice.checked;
        priceField.closest("[data-price-field]").classList.toggle("is-disabled", requestPrice.checked);
      }

      if (requestPrice && priceField) {
        requestPrice.addEventListener("change", updatePriceField);
        updatePriceField();
      }

      tourEditor.querySelectorAll('input[type="file"][accept*="image"]').forEach(function (input) {
        input.addEventListener("change", function () {
          var file = input.files && input.files[0];
          var preview = input.closest(".ops-image-uploader").querySelector("[data-image-preview]");
          if (!file || !preview) return;
          var oldUrl = preview.dataset.objectUrl;
          if (oldUrl) URL.revokeObjectURL(oldUrl);
          var objectUrl = URL.createObjectURL(file);
          preview.dataset.objectUrl = objectUrl;
          preview.innerHTML = "";
          var image = document.createElement("img");
          image.src = objectUrl;
          image.alt = "";
          preview.appendChild(image);
        });
      });
    }

    var list = document.querySelector("[data-itinerary-list]");
    if (!list) return;
    var dragged = null;

    function refreshDayNumbers() {
      list.querySelectorAll("[data-itinerary-day]").forEach(function (day, index) {
        var number = day.querySelector(".ops-day-number");
        if (number) number.textContent = String(index + 1).padStart(2, "0");
        var up = day.querySelector("[data-day-up]");
        var down = day.querySelector("[data-day-down]");
        if (up) up.disabled = index === 0;
        if (down) down.disabled = index === list.children.length - 1;
      });
    }

    list.addEventListener("dragstart", function (event) {
      dragged = event.target.closest("[data-itinerary-day]");
      if (!dragged) return;
      dragged.classList.add("is-dragging");
      event.dataTransfer.effectAllowed = "move";
      event.dataTransfer.setData("text/plain", dragged.querySelector('input[name="day_order"]').value);
    });

    list.addEventListener("dragend", function () {
      if (dragged) dragged.classList.remove("is-dragging");
      dragged = null;
      refreshDayNumbers();
    });

    list.addEventListener("dragover", function (event) {
      event.preventDefault();
      var target = event.target.closest("[data-itinerary-day]");
      if (!dragged || !target || target === dragged) return;
      var box = target.getBoundingClientRect();
      var insertAfter = event.clientY > box.top + box.height / 2;
      list.insertBefore(dragged, insertAfter ? target.nextSibling : target);
    });

    list.addEventListener("click", function (event) {
      var up = event.target.closest("[data-day-up]");
      var down = event.target.closest("[data-day-down]");
      if (!up && !down) return;
      var day = event.target.closest("[data-itinerary-day]");
      if (!day) return;
      if (up && day.previousElementSibling) {
        list.insertBefore(day, day.previousElementSibling);
      }
      if (down && day.nextElementSibling) {
        list.insertBefore(day.nextElementSibling, day);
      }
      refreshDayNumbers();
    });

    refreshDayNumbers();
  });
})();
