function updateStrengthUI(label, percentage) {
  const labelEl = document.querySelector("#strength_label");
  const percentEl = document.querySelector("#strength_percent");

  labelEl.textContent = label;
  percentEl.textContent = percentage + "%";

  let colorClass = 'text-emerald-500';

  if (label.toLowerCase().includes('weak')) {
    colorClass = 'text-rose-500';
  } else if (label.toLowerCase().includes('medium')) {
    colorClass = 'text-amber-500';
  } else if (label.toLowerCase().includes('strong')) {
    colorClass = 'text-emerald-500';
  }

  const colors = ['text-rose-500', 'text-amber-500', 'text-emerald-500', 'text-slate-500'];
  [labelEl, percentEl].forEach(el => {
    el.classList.remove(...colors);
    el.classList.add(colorClass);
  });
}

function updateProgressBar(percent) {
  const progressBar = document.querySelector("#progress_bar");
  if (progressBar) {
    progressBar.style.width = percent + "%";
  }
}

async function fetchHomeData() {
  const url = "http://127.0.0.1:8000/api/password_default_data"

  try {
    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json();

    document.querySelector("#password_display").textContent = data.password;
    updateStrengthUI(data.strength, data.strength_value);
    updateProgressBar(data.strength_value);

  }
  catch (error) {
    console.error("Home Fetch failed:", error);
  }
}

function savePasswordPopup() {
  const saveBtn = document.querySelector("#saveToVault");
  const popup = document.querySelector("#savePasswordPopup");

  if (saveBtn && popup) {
    saveBtn.onclick = function(event) {
      // Corrected: use .style.display = "block" instead of assigning to .style
      event.stopPropagation(); // Prevents the click from immediately reaching the 'window'
      popup.style.display = "block";
      passwordValue = document.querySelector("#password_display").textContent;
      document.querySelector("#popupPassword").value = passwordValue;
    };

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        popup.style.display = "none";
      }
    });

    // Hide if clicking anywhere outside the popup
    window.onclick = function(event) {
      // If the user clicks something that ISN'T the popup and ISN'T a child of the popup
      if (event.target !== popup && !popup.contains(event.target)) {
        popup.style.display = "none";
      }
    };
  }

}

document.addEventListener('DOMContentLoaded', () => {
  fetchHomeData();
  const password_length_slider = document.getElementById('length-slider');
  const refreshBtn = document.querySelector("#refresh_button");

  // Password Length Slider
  password_length_slider.addEventListener('input', (event) => {
    document.getElementById('slider_num_value').textContent = event.target.value;

  });


  refreshBtn.addEventListener('click', async () => {
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
      updateStrengthUI(data.strength, data.strength_value);
      updateProgressBar(data.strength_value);

    } catch (error) {
      console.error("Failed to fetch password:", error);
    }
  });
  savePasswordPopup();
});


