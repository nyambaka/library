// JavaScript code

// Function to confirm book return and calculate outstanding debt
function confirmReturn(transactionId, rentFee) {
    var confirmMessage = "Are you sure you want to return this book?";
    if (rentFee > 0) {
        confirmMessage += "\nRent fee: " + rentFee;
    }
    if (confirm(confirmMessage)) {
        // If confirmed, redirect to return book route with transaction ID
        window.location.href = "/transactions/return/" + transactionId;
    }
}

// Function to limit outstanding debt to KES 500
function limitDebt(debtInput) {
    var maxDebt = 500;
    if (debtInput.value > maxDebt) {
        alert("Outstanding debt cannot exceed " + maxDebt);
        debtInput.value = maxDebt;
    }
}

// Show dropdown on hover
var dropdowns = document.getElementsByClassName("dropdown");
for (var i = 0; i < dropdowns.length; i++) {
    dropdowns[i].addEventListener("mouseenter", function () {
        this.querySelector(".dropdown-menu").style.display = "block";
    });
    dropdowns[i].addEventListener("mouseleave", function () {
        this.querySelector(".dropdown-menu").style.display = "none";
    });
}


