document.addEventListener("DOMContentLoaded", function () {
    // Configuración de Flatpickr
    flatpickr("#date", {
        enableTime: false,
        dateFormat: "Y-m-d",
        defaultDate: calculateDefaultDate()
    });

    function calculateDefaultDate() {
    // Obtener la fecha y hora actual en la zona horaria local
    const now = new Date();
    console.log(now);
    const day = now.getDay(); // 0 = Domingo, 1 = Lunes, 2 = Martes..., 6 = Sábado
    console.log(day); // 3
    const hour = now.getHours();
    console.log(hour); // 0

    if (day === 1) {
        // Si es Lunes, la fecha por defecto es el Martes
        now.setDate(now.getDate() + 1);
    } else if (day >= 2 && day <= 6) {
        console.log('This case')
        // Si es Martes a Sábado y antes de las 20:00, la fecha por defecto es hoy
        // Si es después de las 20:00, la fecha por defecto es mañana
        if (hour >= 20) {
            now.setDate(now.getDate() + 1);
        }
    } else if (day === 0) {
        // Si es Domingo y antes de las 13:00, la fecha por defecto es hoy
        // Si es después de las 13:00, la fecha por defecto es el próximo Martes
        if (hour >= 13) {
            now.setDate(now.getDate() + 2); // próximo Martes
        }
    }

    // Devuelve la fecha en formato Y-m-d
    console.log(now); // Wed Jun 26 2024 00:19:15 GMT+0200 (hora de verano de Europa central)
    const defaultDate = now.toLocaleDateString('en-CA')
    console.log(defaultDate); // 2024-06-25
    return defaultDate;
}

    function checkAvailability() {
        const numPeople = document.getElementById("num-people").value;
        const date = document.getElementById("date").value;
        const location = document.getElementById("location").checked ? "indoor" : "outdoor";

        fetch(`/check_availability?num_people=${numPeople}&date=${date}&location=${location}`)
            .then(response => response.json())
            .then(data => {
                const timeSlotsContainer = document.getElementById("time-slots");
                timeSlotsContainer.innerHTML = ""; // Limpiar cualquier contenido previo

                // Verificar si data.available_times es un array
                if (Array.isArray(data.available_times) && data.available_times.length > 0) {
                    let isTimeslotSelected = false;

                    data.available_times.forEach(entry => {
                        const timeslot = entry.start_time;

                        const label = document.createElement("label");
                        label.classList.add("btn", "btn-outline-primary");

                        const input = document.createElement("input");
                        input.type = "radio";
                        input.name = "timeslot";
                        input.value = timeslot;
                        input.autocomplete = "off";

                        input.addEventListener("change", function() {
                            isTimeslotSelected = true;
                            reserveButton.disabled = false;
                        });

                        label.appendChild(input);
                        label.appendChild(document.createTextNode(timeslot));
                        timeSlotsContainer.appendChild(label);
                    });

                    // Verificar si hay algún horario seleccionado inicialmente
                    const timeSlots = document.querySelectorAll('input[name="timeslot"]');
                    timeSlots.forEach(input => {
                        if (input.checked) {
                            isTimeslotSelected = true;
                        }
                    });

                    // Habilitar o deshabilitar el botón Reservar según si se ha seleccionado un horario
                    const reserveButton = document.querySelector('button[type="submit"]');
                    reserveButton.disabled = !isTimeslotSelected;

                } else {
                    console.error('No hay horarios disponibles para la fecha seleccionada:', data);
                    const reserveButton = document.querySelector('button[type="submit"]');
                    reserveButton.disabled = true; // Deshabilitar el botón si no hay horarios disponibles
                }
            })
            .catch(error => {
                console.error('Error fetching availability:', error);
                const reserveButton = document.querySelector('button[type="submit"]');
                reserveButton.disabled = true; // Deshabilitar el botón en caso de error
            });
    }

    // Ejecutar checkAvailability al cargar la página
    checkAvailability();

    // Event listener para capturar cambios en el contenedor de horarios
    const timeSlotsContainer = document.getElementById("time-slots");
    timeSlotsContainer.addEventListener("click", function(event) {
        console.log('Evento de cambio detectado en el contenedor #time-slots');
        console.log(event.target); // Mostrar el elemento que originó el evento

        // Verificar si el elemento que originó el evento es un input tipo radio con nombre 'timeslot'
        if (event.target && event.target.type === "radio" && event.target.name === "timeslot") {
            const reserveButton = document.querySelector('button[type="submit"]');
            reserveButton.disabled = false; // Habilitar el botón Reservar
        }
    });
    function openConfirmationModal() {
        const numPeople = document.getElementById("num-people").value;
        const date = document.getElementById("date").value;
        const location = document.getElementById("location").checked ? "Indoor" : "Outdoor";
        const selectedTimeslot = document.querySelector('input[name="timeslot"]:checked').value;

        const reservationInfo = `Reserva confirmada para ${numPeople} personas el día ${date} a las ${selectedTimeslot}. Ubicación: ${location}.`;

        document.getElementById("reservationInfo").textContent = reservationInfo;
        $('#confirmationModal').modal('show'); // Abrir el modal usando jQuery
    }

    // Escuchar el evento submit del formulario de reservas
    document.getElementById("reservation-form").addEventListener("submit", function (event) {
        event.preventDefault(); // Prevenir el envío del formulario por defecto
        openConfirmationModal();
    });

    // Ejecutar checkAvailability cuando se cambian la cantidad de personas, la fecha o la ubicación
    document.getElementById("num-people").addEventListener("change", checkAvailability);
    document.getElementById("date").addEventListener("change", checkAvailability);
    document.getElementById("location").addEventListener("change", checkAvailability);
});
