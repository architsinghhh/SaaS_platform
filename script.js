const body = document.querySelector("body");
const modal = document.querySelector(".modal");
const modalButton = document.querySelector(".modal-button");
const closeButton = document.querySelector(".close-button");
const scrollDown = document.querySelector(".scroll-down");
let isOpened = false;

// Open and close modal functions
const openModal = () => {
    modal.classList.add("is-open");
    body.style.overflow = "hidden";
};

const closeModal = () => {
    modal.classList.remove("is-open");
    body.style.overflow = "initial";
};

// Show modal when user scrolls down
window.addEventListener("scroll", () => {
    if (window.scrollY > window.innerHeight / 3 && !isOpened) {
        isOpened = true;
        scrollDown.style.display = "none";
        openModal();
    }
});

// Close modal on button click or escape key
modalButton.addEventListener("click", openModal);
closeButton.addEventListener("click", closeModal);

document.onkeydown = (evt) => {
    evt = evt || window.event;
    if (evt.keyCode === 27) closeModal();
};

const redirectToIndexBtn = document.getElementById('redirectToIndex');

// Add an event listener to the button
redirectToIndexBtn.addEventListener('click', () => {
  window.location.href = 'theme_rtl/demos/agency_1/index.html';
});

// Toggle password visibility
loginBtn.addEventListener('click', async function () {
  const username = document.querySelector('#username').value;
  const password = document.querySelector('#password').value;

  console.log('Username:', username);
  console.log('Password:', password);

  if (!username || !password) {
      alert('Please enter both username and password.');
      return;
  }

  try {
      const response = await fetch('http://127.0.0.1:5000/login', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
          },
          body: JSON.stringify({ username, password }),
      });

      console.log('Response:', response); // Log the response for debugging

      if (!response.ok) {
          const errorData = await response.json();
          alert(`Login failed: ${errorData.message}`);
          return;
      }

      const result = await response.json();
      console.log(result);

      if (result.token) {
          localStorage.setItem('token', result.token);
          window.location.href = 'afterlogin.html'; // Redirect upon successful login
      } else {
          alert('Login failed. Please check your credentials.');
      }
  } catch (error) {
      alert('An error occurred during login. Please try again.');
      console.error(error);
  }
});
