window.onload = function() {
    var dateInput = document.getElementById('date');

    function formatDate(date) {
        return (
            date.getFullYear() +
            '-' +
            ((date.getMonth() + 1) < 10 ? '0' : '') +
            (date.getMonth() + 1) +
            '-' +
            (date.getDate() < 10 ? '0' : '') +
            date.getDate()
        );
    }

    function handleDateChange() {
        var currentDate = new Date();
        var currentHour = currentDate.getHours();

        if (currentHour >= 22) {
            currentDate.setDate(currentDate.getDate() + 1);
        }

        var formattedDate = formatDate(currentDate);
        dateInput.value = formattedDate;

        // Fetch data for the selected date
        fetchReservationData(formattedDate);
    }

    function fetchReservationData(dateValue) {
      console.log('Fetching')
        fetch('/getReservationData', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(dateValue)
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            }
            throw new Error('Network response was not ok.');
        })
        .then(data => {
            // Handle the received data (document exists for the given date)
            console.log('Reservation data:', data);
            // Update your UI or take actions based on the received data
        })
        .catch(error => {
            // Handle errors or non-existent document for the date
            console.error('Error fetching or no data for the date:', error);
        });
    }

    handleDateChange();
  dateInput.addEventListener('change', function() {
            fetchReservationData(formattedDate); // Se ejecutará cada vez que cambies la fecha
      });
  };

