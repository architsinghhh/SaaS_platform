// subscribe.js
function sendInquiry(event) {
    event.preventDefault(); // Prevent the default form submission

    // Get the email value from the input field
    const email = document.getElementById('email').value;

    // Check if email is not empty
    if (!email) {
        alert("Please enter a valid email address.");
        return;
    }

    // Send a POST request to your Flask backend
    fetch('http://127.0.0.1:5000/send-inquiry', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email: email }) // Send the email in JSON format
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok: ' + response.statusText);
        }
        return response.json(); // Parse the JSON response
    })
    .then(data => {
        alert(data.message || 'Inquiry email sent successfully!'); // Show success message
    })
    .catch(error => {
        alert('An error occurred: ' + error.message); // Show error message
    });
}