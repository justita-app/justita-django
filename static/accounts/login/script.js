var phoneNumberInput = document.getElementById("phoneNumberInput")

phoneNumberInput.addEventListener("input", event => {
    phoneNumberInput.value = phoneNumberInput.value.replace(/\D/g, '');
})