function toggleFields() {
    var ownVehicleFields = document.getElementById("ownVehicleFields");
    var mcmVehicleFields = document.getElementById("mcmVehicleFields");
    var ownVehicleRadio = document.getElementById("ownVehicle");
    var mcmVehicleRadio = document.getElementById("mcmVehicle");

    // Clear previous table rows
    function clearTableRows(table) {
        const rowsToKeep = 3; // Number of rows to keep: header + first input text row + one additional row
        const totalRows = table.rows.length;
    
        // Loop backwards through the rows
        for (let i = totalRows - 1; i >= 0; i--) {
            // Delete rows only if they are beyond the rows we want to keep
            if (i >= rowsToKeep && i < totalRows - 1) { // Ensures we keep the "Add" button (last row)
                table.deleteRow(i);
            }
        }
    }

    // Toggle visibility based on the selected radio button
    if (ownVehicleRadio.checked) {
        ownVehicleFields.style.display = "block";
        mcmVehicleFields.style.display = "none";
        clearTableRows(mcmVehicleTable); // Clear MCM vehicle table
        setRequiredFields(ownVehicleFields, true); // Set own vehicle fields as required
        setRequiredFields(mcmVehicleFields, false); // Remove requirement from MCM fields
    } else if (mcmVehicleRadio.checked) {
        mcmVehicleFields.style.display = "block";
        ownVehicleFields.style.display = "none";
        clearTableRows(ownVehicleTable); // Clear Own vehicle table
        setRequiredFields(mcmVehicleFields, true); // Set MCM fields as required
        setRequiredFields(ownVehicleFields, false); // Remove requirement from own vehicle fields
    }
}

function setRequiredFields(container, isRequired) {
    const inputs = container.querySelectorAll('input[type="text"], input[type="date"], input[type="number"], input[type="radio"]');
    inputs.forEach(input => {
        input.required = isRequired; // Set required attribute based on the parameter
    });
}

function updateQuantity(vehicleName, change) {
    let quantityInput = document.getElementById(vehicleName + "_quantity");
    let selectedQuantityInput = document.getElementById(vehicleName + "_selected_quantity");
    
    let newQuantity = parseInt(quantityInput.value) + change;
    let maxQuantity = parseInt(quantityInput.max);

    if (newQuantity < 0) {
        newQuantity = 0;
    } else if (newQuantity > maxQuantity) {
        newQuantity = maxQuantity;
    }

    quantityInput.value = newQuantity;
    selectedQuantityInput.value = newQuantity;

    filterVehicles();
}

function filterVehicles() {
    let vehicles = document.querySelectorAll(".vehicle");
    let hasSelected = false;

    vehicles.forEach(vehicle => {
        let input = vehicle.querySelector("input[type='number']");
        let quantity = parseInt(input.value);
        
        if (quantity > 0) {
            hasSelected = true;
        }
    });

    vehicles.forEach(vehicle => {
        let input = vehicle.querySelector("input[type='number']");
        let quantity = parseInt(input.value);

        if (hasSelected && quantity === 0) {
            vehicle.style.display = "none";
        } else {
            vehicle.style.display = "block";
        }
    });
}


function validateVehicleQuantities() {
    const mcmVehicleRadio = document.getElementById("mcmVehicle");
    
    // Only validate if "No" (MCM Vehicle) is selected
    if (mcmVehicleRadio.checked) {
        const vehicleInputs = document.querySelectorAll('input[name^="mcmVehicleQuantity"]');
        let isValid = false;

        vehicleInputs.forEach(input => {
            if (parseInt(input.value) > 0) {
                isValid = true; 
            }
        });

        if (!isValid) {
            alert("Please select at least one vehicle with a quantity greater than 0.");
            return false; // Prevent form submission
        }
    }

    return true; // Allow form submission if validation is passed or not required
}



function addRow(tableId) {
    var table = document.getElementById(tableId);
    var newRow = table.insertRow(table.rows.length - 1); // Insert before the last row (button row)

    var cell1 = newRow.insertCell(0);
    var cell2 = newRow.insertCell(1);
    var cell3 = newRow.insertCell(2);
    var cell4 = newRow.insertCell(3);

    cell1.innerHTML = '<input type="date" name="start_date[]" placeholder="Insert starting date here">';
    cell2.innerHTML = '<input type="text" name="start_time[]" placeholder="Insert starting time here">';
    cell3.innerHTML = '<input type="text" name="estimated_return[]" placeholder="Insert returning time here">';
    cell4.innerHTML = '<input type="text" name="destinations[]" placeholder="Insert name of destinations here">';
}

function deleteRow(tableId) {
    var table = document.getElementById(tableId);
    var totalRows = table.rows.length;

    // Check if there are rows to delete (keep header, first input row, and last button row)
    if (totalRows > 3) { // 3 = header + first input row + last button row
        table.deleteRow(totalRows - 2); // Delete the last data row (before the button row)
    } else {
        alert("Cannot delete any more rows."); // Alert if no more rows can be deleted
    }
}

document.addEventListener("DOMContentLoaded", function () {
    let today = new Date().toISOString().split('T')[0];
    document.getElementById("dateFilled").value = today;
});
