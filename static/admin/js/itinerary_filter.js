document.addEventListener('DOMContentLoaded', function () {
    const transportField = document.getElementById('id_transport');
    const typeTransportField = document.getElementById('id_type_of_transport');

    if (!transportField || !typeTransportField) return;

    function filterTransportOptions() {
        const selectedType = typeTransportField.value;

        for (let option of transportField.options) {
            const isFlight = option.text.toLowerCase().includes('flight');
            const isCar = option.text.toLowerCase().includes('car');

            if (selectedType === 'Airplane') {
                option.style.display = isFlight ? 'block' : 'none';
            } else if (selectedType === 'Car') {
                option.style.display = isCar ? 'block' : 'none';
            } else {
                option.style.display = 'none';
            }
        }
    }

    typeTransportField.addEventListener('change', filterTransportOptions);

    // Trigger once on load
    filterTransportOptions();
});
