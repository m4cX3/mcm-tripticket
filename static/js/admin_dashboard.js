document.addEventListener("DOMContentLoaded", function() {
    const records = JSON.parse('{{ records | tojson | safe }}');

    // Prepare data arrays for the charts
    const dates = records.map(record => record.DateFilled);
    const approvals = records.map(record => record.Approval);
    const vehicleTypes = records.map(record => record.VehicleType);
    const destinations = records.map(record => record.Destinations);

    // Log data to console for debugging
    console.log('Records:', records);
    console.log('Dates:', dates);
    console.log('Approvals:', approvals);
    console.log('Vehicle Types:', vehicleTypes);

    // Bar Chart - Example of approval data over dates
    new Chart(document.getElementById("barChart"), {
        type: 'bar',
        data: {
            labels: dates,
            datasets: [{
                label: 'Approval Status',
                data: approvals,
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    // Pie Chart - Example for distribution of vehicle types
    const vehicleTypeCounts = {};
    vehicleTypes.forEach(type => vehicleTypeCounts[type] = (vehicleTypeCounts[type] || 0) + 1);

    new Chart(document.getElementById("pieChart"), {
        type: 'pie',
        data: {
            labels: Object.keys(vehicleTypeCounts),
            datasets: [{
                data: Object.values(vehicleTypeCounts),
                backgroundColor: [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)'
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true
        }
    });

    // Line Chart - Example for approval status over dates
    new Chart(document.getElementById("lineChart"), {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'Approval Status Over Time',
                data: approvals,
                backgroundColor: 'rgba(153, 102, 255, 0.2)',
                borderColor: 'rgba(153, 102, 255, 1)',
                borderWidth: 1,
                fill: false
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    const nameInput = document.getElementById("name");
    const startDateInput = document.getElementById("start-date");
    const endDateInput = document.getElementById("end-date");

    const filterRecords = () => {
        const filters = {
            name: nameInput.value,
            start_date: startDateInput.value,
            end_date: endDateInput.value
        };

        fetch('/admin_dashboard', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(filters),
        })
        .then(response => response.json())
        .then(data => {
            displayRecords(data.records);
        })
        .catch(error => console.error('Error:', error));
    };

    // Attach input event listeners
    nameInput.addEventListener('input', filterRecords);
    startDateInput.addEventListener('input', filterRecords);
    endDateInput.addEventListener('input', filterRecords);

    // Function to display the filtered records in the UI
    const displayRecords = (records) => {
        const recordsContainer = document.getElementById('records-container'); // Make sure you have a container to display records
        recordsContainer.innerHTML = ''; // Clear previous results

        if (records.length === 0) {
            recordsContainer.innerHTML = '<p>No records found.</p>'; // Show a message if no records are found
            return;
        }

        records.forEach(record => {
            const recordDiv = document.createElement('div');
            recordDiv.innerHTML = `
                <p>Date Filled: ${record.DateFilled}</p>
                <p>Requested By: ${record.RequestedBy}</p>
                <p>Vehicle Type: ${record.VehicleType}</p>
                <p>Start Date: ${record.StartDate}</p>
                <p>Destinations: ${record.Destinations}</p>
                <p>Approval: ${record.Approval}</p>
                <p>Remarks: ${record.Remarks}</p>
                <hr>
            `;
            recordsContainer.appendChild(recordDiv);
        });
    };
});
