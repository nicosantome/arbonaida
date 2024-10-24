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
    const day = now.getDay();
    const hour = now.getHours();

    if (day === 1) {
        now.setDate(now.getDate() + 1);
    } else if (day >= 2 && day <= 6) {
        if (hour >= 20) {
            now.setDate(now.getDate() + 1);
        }
    } else if (day === 0) {
        if (hour >= 13) {
            now.setDate(now.getDate() + 2);
        }
    }

    const defaultDate = now.toLocaleDateString('en-CA')
    return defaultDate;
}

    function checkAvailability() {
            const numPeople = document.getElementById("num-people").value;
            const date = document.getElementById("date").value;
            const location = document.querySelector('input[name="location"]:checked').value;

            fetch(`/check_availability?num_people=${numPeople}&date=${date}&location=${location}`)
                .then(response => response.json())
                .then(data => {
                    const timeSlotsContainer = document.getElementById("time-slots");
                    timeSlotsContainer.innerHTML = ""; // Limpiar cualquier contenido previo

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
                                document.getElementById("reserve-button").disabled = false;
                            });

                            label.appendChild(input);
                            label.appendChild(document.createTextNode(timeslot));
                            timeSlotsContainer.appendChild(label);
                        });

                        const timeSlots = document.querySelectorAll('input[name="timeslot"]');
                        timeSlots.forEach(input => {
                            if (input.checked) {
                                isTimeslotSelected = true;
                            }
                        });

                        const reserveButton = document.getElementById("reserve-button");
                        reserveButton.disabled = !isTimeslotSelected;

                    } else {
                        console.error('No hay horarios disponibles para la fecha seleccionada:', data);
                        const reserveButton = document.getElementById("reserve-button");
                        reserveButton.disabled = true;
                    }
                })
                .catch(error => {
                    console.error('Error fetching availability:', error);
                    const reserveButton = document.getElementById("reserve-button");
                    reserveButton.disabled = true;
                });
        }

    // Ejecutar checkAvailability al cargar la página
    checkAvailability();

    // Event listener para capturar cambios en el contenedor de horarios
    const timeSlotsContainer = document.getElementById("time-slots");
    timeSlotsContainer.addEventListener("click", function(event) {

        // Verificar si el elemento que originó el evento es un input tipo radio con nombre 'timeslot'
        if (event.target && event.target.type === "radio" && event.target.name === "timeslot") {
            const reserveButton = document.getElementById("reserve-button");
            reserveButton.disabled = false; // Habilitar el botón Reservar
        }
    });

    // Ejecutar checkAvailability cuando se cambian la cantidad de personas, la fecha o la ubicación
    document.getElementById("num-people").addEventListener("change", checkAvailability);
    document.getElementById("date").addEventListener("change", checkAvailability);

    const location_btns = document.querySelectorAll("#location .btn")
    location_btns.forEach(function(button) {
    button.addEventListener('click', function(event) {
        // Evitar que el evento de clic se dispare dos veces
        event.preventDefault();

        // Remover la clase 'focus' de todos los botones
        location_btns.forEach(function(btn) {
            btn.classList.remove('focus');
        });

        // Agregar la clase 'focus' al botón clickeado
        this.classList.add('focus');

        // Forzar el cambio de radio manualmente si no es automático
        const input = this.querySelector('input');
        if (input && !input.checked) {
            input.checked = true;
        }

        // Ejecutar checkAvailability() solo una vez
        checkAvailability();
    });
});


    });

