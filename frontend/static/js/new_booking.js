function calculatePlaceholder() {
    var currentDate = new Date();
    var dayOfWeek = currentDate.getDay();
    var placeholderDate = new Date(currentDate);
    var placeholderTime;

    // Logic to determine placeholder date and time based on the day of the week
    switch (dayOfWeek) {
        case 0: // Sunday
            if (currentDate.getHours() < 13) {
                placeholderTime = '13:00'; // Before 13:00
            } else {
                placeholderDate.setDate(currentDate.getDate() + 1); // Next day
                placeholderTime = '13:00'; // After 13:00
            }
            break;
        case 1: // Monday
            placeholderDate.setDate(currentDate.getDate() + 1); // Next day
            placeholderTime = '13:00'; // Placeholder time for Monday
            break;
        case 2: // Tuesday
        case 3: // Wednesday
        case 4: // Thursday
        case 5: // Friday
            if (currentDate.getHours() < 13) {
                placeholderTime = '13:00'; // Before 13:00
            } else if (currentDate.getHours() < 20) {
                placeholderTime = '20:00'; // Between 13:00 and 20:00
            } else {
                placeholderDate.setDate(currentDate.getDate() + 1); // Next day
                placeholderTime = '13:00'; // After 20:00
            }
            break;
        case 6: // Saturday
            if (currentDate.getHours() < 13) {
                placeholderTime = '13:00'; // Before 13:00
            } else {
                placeholderDate.setDate(currentDate.getDate() + 2); // Next Tuesday
                placeholderTime = '13:00'; // After 13:00
            }
            break;
    }

    // Format the placeholder date
    var formattedPlaceholderDate = placeholderDate.toISOString().slice(0, 10);

    // Set the placeholder values to the date and time input fields
    document.getElementById('date').setAttribute('value', formattedPlaceholderDate);
    document.getElementById('time').setAttribute('value', placeholderTime);
}

// Call the function when the page is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    calculatePlaceholder();
});
document.addEventListener('DOMContentLoaded', function() {
    // Obtener el campo de fecha
    var dateInput = document.getElementById('date');

    // Agregar un event listener para el cambio de valor en el campo de fecha
    dateInput.addEventListener('change', function() {
        // Obtener el valor seleccionado en el campo de fecha
        var selectedDate = new Date(dateInput.value);

        // Verificar si el día seleccionado es un Lunes (día de la semana = 1)
        if (selectedDate.getDay() === 1) {
            // Mostrar alerta indicando que los lunes están cerrados
            alert('Los lunes están cerrados.');
        }
    });
});
