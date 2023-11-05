
const fanme = document.getElementById('fanme');
const lname = document.getElementById('lname');
const username = document.getElementById('username');
const email = document.getElementById('email');
const cemail = document.getElementById('confirm-email');
const password = document.getElementById('password');
const cpassword = document.getElementById('confirm-password');
const signupBtn = document.getElementById('signup-btn');


let validEmail = false;
let validConfEmail = false;
let validUsername = false;
let validFname = false;
let validLname = false;
let validPass = false;
let validConfPass = false;

// Email Validation Function 
const isEmail = (emailVal) => {
    if (!emailVal.includes('@') || !emailVal.includes('.')) return false;

    let atSymbol = emailVal.indexOf('@');
    if (atSymbol < 1) return false; //@ symbol at the start

    let dot = emailVal.lastIndexOf('.');
    if (dot === emailVal.length - 1) return false; //. symbol at the end
    if (dot <= atSymbol + 2) return false; //@ and . symbol are next to each other

    return true;
}

// Checking that given string only contains letters/characters 
function containsCharacters(text) {
    // Regualar Expression which have only letters
    let letters = /^[A-Za-z\s]+$/;

    // Matching the given text with regular expression 
    if (text.match(letters)) {
        return true;
    } else {
        return false;
    }
}


// Firstname Validation 
fname.addEventListener('input', (e) => {
    fnameVal = fname.value.trim();
    if (fnameVal === "") {
        setErrorMsg(fname, 'First Name cannot be blank');
        validFname = false;
    } else if (!containsCharacters(fnameVal)) {
        setErrorMsg(fname, 'First Name only contains characters (A-Z, a-z)');
        validFname = false;
    }
    else {
        setSuccessMsg(fname);
        validFname = true;
    }
    enableSignupBtn(validFname, validLname, validUsername, validEmail, validConfEmail, validPass, validConfPass);
});


// Lastname Validation 
lname.addEventListener('input', (e) => {
    lnameVal = lname.value.trim()
    if (lnameVal === "") {
        setErrorMsg(lname, 'Last Name cannot be blank');
        validLname = false;
    } else if (!containsCharacters(lnameVal)) {
        setErrorMsg(lname, 'Last Name only contains characters (A-Z, a-z)');
        validFname = false;
    } else {
        setSuccessMsg(lname);
        validLname = true;
    }
    enableSignupBtn(validFname, validLname, validUsername, validEmail, validConfEmail, validPass, validConfPass);
});

// Username Validation 
username.addEventListener('input', (e) => {
    // console.log(username.value)
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
    enableSignupBtn(validFname, validLname, validUsername, validEmail, validConfEmail, validPass, validConfPass);
});

// Email Validation 
email.addEventListener('input', (e) => {
    emailVal = email.value.trim();
    if (emailVal === "") {
        setErrorMsg(email, 'Email cannot be blank');
        validEmail = false;
    } else if (!isEmail(emailVal)) {
        setErrorMsg(email, 'Email is invalid');
        validEmail = false;
    } else {
        setSuccessMsg(email);
        validEmail = true;
    }
    enableSignupBtn(validFname, validLname, validUsername, validEmail, validPass, validConfPass)
});

// Password Validation 
password.addEventListener('input', (e) => {
    passwordVal = password.value.trim();
    if (passwordVal === "") {
        setErrorMsg(password, 'Password cannot be blank');
        validPass = false;
    } else if (passwordVal.length < 4) {
        setErrorMsg(password, 'Password must have atleast 8 characters');
        validPass = false;
    } else {
        setSuccessMsg(password);
        validPass = true;
    }
    enableSignupBtn(validFname, validLname, validUsername, validEmail, validConfEmail, validPass, validConfPass);
});

// Confirm Password Validation 
cpassword.addEventListener('input', (e) => {
    cpasswordVal = cpassword.value.trim()
    if (cpasswordVal === "") {
        validConfPass = false;
        setErrorMsg(cpassword, 'Confirm Password cannot be blank');

    } else if (passwordVal !== cpasswordVal) {
        setErrorMsg(cpassword, 'Passwords are different');
        validConfPass = false;
    } else {
        setSuccessMsg(cpassword);
        validConfPass = true;
    }
    enableSignupBtn(validFname, validLname, validUsername, validEmail, validConfEmail, validPass, validConfPass);
});

// Confirm Email Validation 
cemail.addEventListener('input', (e) => {
    cemailVal = cemail.value.trim()
    if (cemailVal === "") {
        validConfEmail = false;
        setErrorMsg(cemail, 'Confirm Email cannot be blank');

    } else if (emailVal !== cemailVal) {
        setErrorMsg(cemail, 'Emails are different');
        validConfEmail = false;
    } else {
        setSuccessMsg(cemail);
        validConfEmail = true;
    }
    enableSignupBtn(validFname, validLname, validUsername, validEmail, validConfEmail, validPass, validConfPass);
});

// Function to enable Signup btn 
function enableSignupBtn(validFname, validLname, validUsername, validEmail, validPass, validConfPass) {
    if (validFname && validLname && validUsername && validEmail && validPass && validConfPass) {
        // Enable button 
        signupBtn.disabled = false;
    } else {
        // Disable button again
        signupBtn.disabled = true;
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

