// formValidation.js

function enableButtonOnFormValidity(formId, buttonId) {
  console.log(formId,buttonId);
    var form = document.getElementById(formId);
    var submitButton = form.querySelector('#' + buttonId);
    form.addEventListener('input', function () {
      
      if (form.checkValidity()) {
        submitButton.disabled = false;
        console.log("i am here")
      } else {
        console.log("i am disabled")
        console.log(submitButton)
        submitButton.disabled = true;
        console.log("i am disabled")
      }
    });
  }
  