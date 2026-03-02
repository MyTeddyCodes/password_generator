
console.log("test now")

document.addEventListener('DOMContentLoaded', () => {
  const password_length_slider = document.getElementById('length-slider');
  const refreshBtn = document.querySelector("#refresh_button");

  // Password Length Slider
  password_length_slider.addEventListener('input', (event) => {
    document.getElementById('slider_num_value').textContent = event.target.value;

  });


  refreshBtn.addEventListener('click', async () => {
    console.log("refreshed clicked")
    const uppercaseEl = document.querySelector("#uppercase");
    const numbersEl = document.querySelector("#numbers");
    const symbolsEl = document.querySelector("#symbols");

    if (!uppercaseEl || !numbersEl || !symbolsEl) {
      console.error("One or more toggled elements were not found in the DOM")
      return;
    }

    const payload = {
      uppercase: uppercaseEl.checked,
      numbers: numbersEl.checked,
      symbols: symbolsEl.checked,
      password_length: parseInt(password_length_slider.value)
    }

    try {
      const response = await fetch('/generate_password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      document.querySelector("#password_display").textContent = data.generated_password

    } catch (error) {
      console.error("Failed to fetch password:", error);
    }
  });
});


