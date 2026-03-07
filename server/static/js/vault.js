async function fetchSavedPasswordData() {
  const url = "http://127.0.0.1:8000/api/retreive_password"
  const container = document.querySelector("#passwordListContainer");
  const template = document.querySelector("#passwordItemTemplate");

  try {
    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json();

    container.innerHTML = "";

    data.password_data.forEach(passwordData => {
      const clone = template.content.cloneNode(true);

      clone.querySelector("#accountName").textContent = passwordData.login;
      clone.querySelector("#username").textContent = passwordData.username;
      clone.querySelector("#password").textContent = passwordData.password;

      container.appendChild(clone);
    })

  }
  catch (error) {
    console.error("Saved Password Fetch failed:", error);
  }
}



document.addEventListener('DOMContentLoaded', () => {
  fetchSavedPasswordData();
});
