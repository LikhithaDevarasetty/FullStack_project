$(document).ready(function() {
    // Login form validation
    $('#loginForm').on('submit', function(e) {
        var username = $('#username').val().trim();
        var password = $('#password').val().trim();
        var isValid = true;

        if (!username) {
            alert('Please enter your username.');
            isValid = false;
        }

        if (!password) {
            alert('Please enter your password.');
            isValid = false;
        }

        if (!isValid) {
            e.preventDefault();
        }
    });

    // Register form validation
    $('#registerForm').on('submit', function(e) {
        var username = $('#username').val().trim();
        var email = $('#email').val().trim();
        var password = $('#password').val().trim();
        var isValid = true;

        if (!username) {
            alert('Please enter a username.');
            isValid = false;
        }

        if (!email || !isValidEmail(email)) {
            alert('Please enter a valid email.');
            isValid = false;
        }

        if (!password || password.length < 8) {
            alert('Password must be at least 8 characters long.');
            isValid = false;
        }

        if (!isValid) {
            e.preventDefault();
        }
    });

    // Booking form validation
    $('#bookingForm').on('submit', function(e) {
        var name = $('#name').val().trim();
        var email = $('#email').val().trim();
        var phone = $('#phone').val().trim();
        var travelers = $('#travelers').val();
        var date = $('#date').val();
        var isValid = true;

        if (!name) {
            alert('Please enter your full name.');
            isValid = false;
        }

        if (!email || !isValidEmail(email)) {
            alert('Please enter a valid email.');
            isValid = false;
        }

        if (!phone) {
            alert('Please enter your phone number.');
            isValid = false;
        }

        if (!travelers || travelers < 1) {
            alert('Please enter a valid number of travelers.');
            isValid = false;
        }

        if (!date) {
            alert('Please select a travel date.');
            isValid = false;
        }

        if (!isValid) {
            e.preventDefault();
        }
    });

    // Helper function for email validation
    function isValidEmail(email) {
        var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
});
