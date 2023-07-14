const username = document.getElementById('username');
const password = document.getElementById('password');
const loginBtn = document.getElementById('login-btn');

let validUsername = false;
let ValidPass = false;

// Username Validation 
username.addEventListener('input', (e) => {
    usernameVal = username.value.trim()
    if (usernameVal === "") {
        setErrorMsg(username, 'Username cannot be blank');
        validUsername = false;
    } else if (usernameVal.length <= 3) {
        setErrorMsg(username, 'Username must be of atleast 4 characters');
        validUsername = false;
    } else {
        setSuccessMsg(username);
        // console.log('username is valid')
        validUsername = true;

    }
    enableLoginBtn(validUsername, ValidPass)
});


// Password Validation 
password.addEventListener('input', (e) => {
    passwordVal = password.value.trim();
    if (passwordVal === "") {
        setErrorMsg(password, 'Password cannot be blank');
        ValidPass = false;
    } else if (passwordVal.length < 4) {
        setErrorMsg(password, 'Password must have atleast 4 characters');
        ValidPass = false;
    } else {
        setSuccessMsg(password);
        ValidPass = true;
    }
    enableLoginBtn(validUsername, ValidPass)
});

function enableLoginBtn(validUsername, ValidPass) {
    if ( validUsername && ValidPass ) {
        // Enable button 
        loginBtn.disabled = false;
    } else {
        // Disable button again
        loginBtn.disabled = true;
    }
}

// Set Error Message Function
function setErrorMsg(input, errorMsg) {
    const formGroup = input.parentElement;
    const small = formGroup.querySelector('small');
    small.innerText = errorMsg;
    formGroup.className = "form-group error";
}

// Set Success Message Function
function setSuccessMsg(input) {
    const formGroup = input.parentElement;
    formGroup.className = "form-group success";
}