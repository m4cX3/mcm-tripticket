function toggleFields() {
    var ownVehicleFields = document.getElementById("ownVehicleFields");
    var mcmVehicleFields = document.getElementById("mcmVehicleFields");
    var ownVehicleTable = document.getElementById("ownVehicleTable");
    var mcmVehicleTable = document.getElementById("mcmVehicleTable");
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
    } else if (mcmVehicleRadio.checked) {
        mcmVehicleFields.style.display = "block";
        ownVehicleFields.style.display = "none";
        clearTableRows(ownVehicleTable); // Clear Own vehicle table
    }
}

function updateQuantity(vehicleName, change) {
    const quantityInput = document.getElementById(vehicleName + '_quantity');
    const availableQuantity = parseInt(quantityInput.getAttribute('max'));
    let newQuantity = parseInt(quantityInput.value) + change;

    if (newQuantity >= 0 && newQuantity <= availableQuantity) {
        quantityInput.value = newQuantity;
        document.getElementById(vehicleName + '_selected_quantity').value = newQuantity;
    }
}



function addRow(tableId) {
    var table = document.getElementById(tableId);
    var newRow = table.insertRow(table.rows.length - 1); // Insert before the last row (button row)

    var cell1 = newRow.insertCell(0);
    var cell2 = newRow.insertCell(1);
    var cell3 = newRow.insertCell(2);
    var cell4 = newRow.insertCell(3);

    cell1.innerHTML = '<input type="text" name="start_date[]" placeholder="Insert starting date here">';
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