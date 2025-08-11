document.addEventListener('DOMContentLoaded', function () {
    const typeField = document.getElementById('id_type');
    const startDateRow = document.querySelector('.form-row.field-start_date');
    const endDateRow = document.querySelector('.form-row.field-end_date');

    function toggleDateFields() {
        if (typeField.value === 'schedule') {
            startDateRow.style.display = '';
            endDateRow.style.display = '';
        } else {
            startDateRow.style.display = 'none';
            endDateRow.style.display = 'none';
        }
    }

    // Initial toggle
    toggleDateFields();

    // Add event listener
    typeField.addEventListener('change', toggleDateFields);
});
