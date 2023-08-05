
document.addEventListener('DOMContentLoaded', () => {
    const forms = document.querySelectorAll('form');

    forms.forEach((form, index) => {

        form.addEventListener('submit', (event) => {
            event.preventDefault();
            let success_p = document.getElementById(`success-p-${index-1}`);
            let submit_btn = document.getElementById(`submit-btn-${index-1}`);
            submit_btn.innerText = "Adding...";
            const formData = new FormData(form);

            fetch("/admin1/save-link-to-db/", {
                method: "POST",
                body: formData
            })
                .then(response => response.json())
                .then(data => {
                    // console.log("response from Django : ", data);
                    submit_btn.style.display = "none";
                    if(data.success){
                        success_p.style.display = "block";
                    } else{
                        success_p.style.display = "block";
                        success_p.classList.add('btn-danger')
                        success_p.innerText='Already Exist' 
                    }
                    
                })
                .catch(error => {
                    console.log('error : ', error);
                    button.innerText = "Try Again";
                })
        })
    })
})