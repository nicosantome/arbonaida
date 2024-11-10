document.addEventListener("DOMContentLoaded", function() {
    // Añadir evento de clic a cada botón "Modificar"
    document.querySelectorAll('.edit-booking-btn').forEach(button => {
        button.addEventListener('click', () => {
            const bookingId = button.getAttribute('data-booking-id');
            const numPeople = button.getAttribute('data-num-people');
            const date = button.getAttribute('data-date');
            const location = button.getAttribute('data-location');
            const timeslot = button.getAttribute('data-timeslot');
            console.log(timeslot)

            // Llamar a la función para abrir el modal y prellenar los datos
            openEditModal(bookingId, numPeople, date, location, timeslot);
        });
    });

    // Función para abrir el modal de edición y prellenar los datos de la reserva
    function openEditModal(bookingId, numPeople, date, location, timeslot) {
        // Establecer valores en el formulario del modal
        const editNumPeople = document.getElementById('edit-num-people');
        const editDate = document.getElementById('edit-date');
        const editTimeslot = document.getElementById('edit-timeslot');

        editNumPeople.value = numPeople;
        editDate.value = date;


        // Actualizar el action del formulario con el bookingId
        const editForm = document.getElementById('editReservationForm');
        editForm.action = `/admin/edit/${bookingId}`;
        editForm.setAttribute('data-booking-id', bookingId);

        // Marcar la opción de ubicación seleccionada
        document.querySelectorAll('#edit-location input').forEach(radio => {
            if (radio.value === location) {
                radio.checked = true;
                radio.parentElement.classList.add('active');
            } else {
                radio.parentElement.classList.remove('active');
            }
        });

        // Llenar los timeslots disponibles
        updateTimeslots(bookingId, editDate.value, editNumPeople.value, location, timeslot);

        // Añadir EventListeners para actualizar los timeslots dinámicamente
        editNumPeople.addEventListener('change', () => updateTimeslots(bookingId, editDate.value, editNumPeople.value, getSelectedLocation(), timeslot));
        editDate.addEventListener('change', () => updateTimeslots(bookingId, editDate.value, editNumPeople.value, getSelectedLocation(), timeslot));
        document.getElementById('edit-location').addEventListener('change', event => {
    if (event.target.matches('input[type="radio"]')) {
        updateTimeslots(bookingId, editDate.value, editNumPeople.value, getSelectedLocation(), timeslot);
    }
});

        // Abrir el modal
        const modal = new bootstrap.Modal(document.getElementById('editReservationModal'));
        modal.show();
    }

    // Función para obtener el valor de ubicación seleccionado
    function getSelectedLocation() {
        const selectedLocation = document.querySelector('#edit-location input:checked');
        return selectedLocation ? selectedLocation.value : null;
    }

    // Función para actualizar los timeslots disponibles
    function updateTimeslots(bookingId, date, numPeople, location, currentTimeslot) {

        const timeslotSelect = document.getElementById('edit-timeslot');
        timeslotSelect.innerHTML = ''; // Limpiar opciones existentes

        fetch(`/check_availability?date=${date}&num_people=${numPeople}&location=${location}&booking_id=${bookingId}`)
            .then(response => response.json())
            .then(data => {
                if (Array.isArray(data.available_times) && data.available_times.length > 0) {
                    data.available_times.forEach(time => {
                        const option = document.createElement('option');
                        option.value = time.start_time;
                        option.textContent = time.start_time;
                        console.log('time.start_time:', time.start_time, typeof time.start_time);
                        console.log('currentTimeslot:', currentTimeslot, typeof currentTimeslot);


                        // Seleccionar el timeslot actual si coincide
                        if (time.start_time === currentTimeslot) {
                            option.selected = true;
                        }

                        timeslotSelect.appendChild(option);
                    });
                } else {
                    const noTimeslotOption = document.createElement('option');
                    noTimeslotOption.textContent = 'No hay horarios disponibles';
                    noTimeslotOption.disabled = true;
                    timeslotSelect.appendChild(noTimeslotOption);
                }
            })
            .catch(err => console.error('Error fetching available times:', err));
    }
});
