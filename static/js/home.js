window.onload = function() {
    // Get current date
    var currentDate = new Date();
    var currentHour = currentDate.getHours();
    var currentDay = currentDate.getDate();
    var currentMonth = currentDate.getMonth() + 1; // Adding 1 since months go from 0 to 11

    if (currentHour >= 22) {
        // If it's past 10 PM, move to the next day
        currentDay = currentDay + 1;
        // Logic for the next month if needed
    }

    // Format the date in the desired format (example: '28-10-2023')
    var formattedDate = currentDay + '-' + currentMonth + '-' + currentDate.getFullYear();

    // Make a fetch request to the server with the current date
    fetch('/getReservationData', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ date: formattedDate }) // Send the date to the server
    })
    .then(response => response.json())
    .then(data => {
        // Handle the received data to display available hours in the dropdown
        // Update the dropdown with available hours based on the received data
    })
    .catch(error => {
        // Handle any error in the fetch request
        console.error('Error fetching data:', error);
    });
}
