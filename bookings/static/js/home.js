document.addEventListener("DOMContentLoaded", function () {
    // Flatpickr configuration
    flatpickr("#date", {
        enableTime: false,
        dateFormat: "Y-m-d",
        defaultDate: calculateDefaultDate()
    });

    function calculateDefaultDate() {
        // Get the current date and time in the local time zone
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
                timeSlotsContainer.innerHTML = ""; // Clear any previous content

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
                    console.error('No available time slots for the selected date:', data);
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

    // Execute checkAvailability when the page loads
    checkAvailability();

    // Event listener to capture changes in the time slots container
    const timeSlotsContainer = document.getElementById("time-slots");
    timeSlotsContainer.addEventListener("click", function(event) {
        // Check if the event target is a radio input with name 'timeslot'
        if (event.target && event.target.type === "radio" && event.target.name === "timeslot") {
            const reserveButton = document.getElementById("reserve-button");
            reserveButton.disabled = false; // Enable the Reserve button
        }
    });

    // Execute checkAvailability when the number of people, date, or location changes
    document.getElementById("num-people").addEventListener("change", checkAvailability);
    document.getElementById("date").addEventListener("change", checkAvailability);

    const location_btns = document.querySelectorAll("#location .btn")
    location_btns.forEach(function(button) {
        button.addEventListener('click', function(event) {
            // Prevent the click event from firing twice
            event.preventDefault();

            // Remove the 'focus' class from all buttons
            location_btns.forEach(function(btn) {
                btn.classList.remove('focus');
            });

            // Add the 'focus' class to the clicked button
            this.classList.add('focus');

            // Force the radio change manually if it's not automatic
            const input = this.querySelector('input');
            if (input && !input.checked) {
                input.checked = true;
            }

            // Execute checkAvailability() only once
            checkAvailability();
        });
    });
});