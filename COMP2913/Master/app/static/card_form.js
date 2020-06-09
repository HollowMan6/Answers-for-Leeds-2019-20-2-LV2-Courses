const cardDropdown = document.getElementById("payment_card");
const newCardForm = document.querySelector("label[for=new_payment_card]").parentElement.parentElement;
const newCardOptionText = "+ Add payment card";

function setCardFormVisible() {
    const selected = cardDropdown.options[cardDropdown.selectedIndex].innerText === newCardOptionText;
    newCardForm.style.display = selected ? "block" : "none";
    for (const formGroup of newCardForm.getElementsByClassName("form-group required")) {
        for (const control of formGroup.childNodes) {
            control.required = selected;
        }
    }
}

window.addEventListener('load', function () {
    setCardFormVisible();
    cardDropdown.addEventListener("change", setCardFormVisible);
});
