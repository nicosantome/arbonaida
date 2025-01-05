//This JS handles the admin.html file

document.addEventListener("DOMContentLoaded", function () {
    // Evnt listener for each "Modify" button (one in each booking listed) to open the edit modal
    document.querySelectorAll('.edit-booking-btn').forEach(button => {
        button.addEventListener('click', () => {
            const bookingId = button.getAttribute('data-booking-id');
            const numPeople = button.getAttribute('data-num-people');
            const date = button.getAttribute('data-date');
            const location = button.getAttribute('data-location');
            const timeslot = button.getAttribute('data-timeslot');

            // This opens the edit modal populated with the booking data
            openEditModal(bookingId, numPeople, date, location, timeslot);
        });
    });

    // This opens the edit modal populated with the booking data
    function openEditModal(bookingId, numPeople, date, location, timeslot) {
        const editForm = document.getElementById('editReservationForm');
        const editNumPeople = document.getElementById('edit-num-people');
        const editDate = document.getElementById('edit-date');
        const editTimeslot = document.getElementById('edit-timeslot');

        // Set the form action to the correct endpoint for editing the booking
        editForm.action = `/admin/edit/${bookingId}`;


        // This displays default values from the booking in the edit modal
        editNumPeople.value = numPeople;
        editDate.value = date;

        // Handle location radio button selection
        document.querySelectorAll('#edit-location input').forEach(radio => {
            if (radio.value === location) {
                radio.checked = true;
                radio.parentElement.classList.add('active');
            } else {
                radio.parentElement.classList.remove('active');
            }
        });

        // Fetch and update available time slots
        updateTimeslots(bookingId, date, numPeople, location, timeslot);

        // Open the bootstrap modal
        const modal = new bootstrap.Modal(document.getElementById('editReservationModal'));
        modal.show();

        // Add event listeners to dynamically update time slots when form values change
        editNumPeople.addEventListener('change', () => {
            updateTimeslots(bookingId, editDate.value, editNumPeople.value, getSelectedLocation(), timeslot);
        });
        editDate.addEventListener('change', () => {
            updateTimeslots(bookingId, editDate.value, editNumPeople.value, getSelectedLocation(), timeslot);
        });
        document.querySelectorAll('#edit-location .btn').forEach(button => {
            button.addEventListener('click', () => {
                updateTimeslots(bookingId, editDate.value, editNumPeople.value, getSelectedLocation(), timeslot);
            });
        });
    }

    // Helper function to get the currently selected location
    function getSelectedLocation() {
        const selectedLocation = document.querySelector('#edit-location input:checked');
        return selectedLocation ? selectedLocation.value : null;
    }

    // Function to fetch and display available time slots in the modal dropdown
    function updateTimeslots(bookingId, date, numPeople, location, currentTimeslot) {
        const timeslotSelect = document.getElementById('edit-timeslot');
        timeslotSelect.innerHTML = ''; // Clear existing options

        // Fetch available time slots based on booking parameters
        fetch(`/check_availability?date=${date}&num_people=${numPeople}&location=${location}&booking_id=${bookingId}`)
            .then(response => response.json())
            .then(data => {
             // Check if available times exist
                if (Array.isArray(data.available_times) && data.available_times.length > 0) {
                    let currentTimeslotAvailable = false;

                    // Placeholder "Select"
                    const placeholderOption = document.createElement('option');
                    placeholderOption.value = '';
                    placeholderOption.textContent = 'Select';
                    placeholderOption.disabled = true;
                    timeslotSelect.appendChild(placeholderOption);

                    data.available_times.forEach(time => {
                        const option = document.createElement('option');
                        option.value = time.start_time;
                        option.textContent = time.start_time;

                        // Select current timeslot if available
                        if (time.start_time === currentTimeslot) {
                            option.selected = true;
                            currentTimeslotAvailable = true;
                        }

                        timeslotSelect.appendChild(option);
                    });

                    // If current timeslot is not available, this forces user to select
                    if (!currentTimeslotAvailable) {
                        placeholderOption.selected = true;
                    }
                } else {
                    // If no available time slots
                    const noTimeslotOption = document.createElement('option');
                    noTimeslotOption.textContent = 'No availability';
                    noTimeslotOption.disabled = true;
                    timeslotSelect.appendChild(noTimeslotOption);
                }
            })
            .catch(err => console.error('Error fetching available times:', err));
    }
});
