const lengthSlider =
document.querySelector('input[type="range"]');
const lengthValue = document.querySelector('.length-value');

lengthSlider.addEventListener('input', (event) => {
	lengthValue.textContent = event.target.value;
});

document.getElementById('save-vault-btn').addEventListener('click', () =>
{
	console.log("Teddy Password: Save to Vault button was clicked!");
});


// Selecting the action buttons
const saveBtn = document.getElementById('save-btn');
const copyBtn = document.getElementById('copy-btn');

//Logic for the Save button
if (saveBtn) {
        saveBtn.addEventListener('click', () => {
                console.log("Teddy Password: Save to Vault button was clicked!");
        });
}

//Logic for the Copy button
if (copyBtn) {
        copyBtn.addEventListener('click', () => {
                console.log('Teddy Password: Copybutton was clicked!');
        });
}// Selecting the action buttons
const saveBtn = document.getElementById('save-btn');
const copyBtn = document.getElementById('copy-btn');

//Logic for the Save button
if (saveBtn) {
        saveBtn.addEventListener('click', () => {
                console.log("Teddy Password: Save to Vault button was clicked!");
        });
}

//Logic for the Copy button
if (copyBtn) {
        copyBtn.addEventListener('click', () => {
                console.log('Teddy Password: Copybutton was clicked!');
        });
}:
