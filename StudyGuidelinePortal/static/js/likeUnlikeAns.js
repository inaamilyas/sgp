const ans_like_form_arr = document.querySelectorAll(".ans-like-form");

    ans_like_form_arr.forEach((ans_like_form)=>{
        ans_like_form.addEventListener('submit',(e)=>{
            e.preventDefault();
            const formData = new FormData(ans_like_form);
            let i = ans_like_form[2].childNodes[0]

            fetch("/ans-like/", {
                method: "POST",
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                console.log("response from Django : ", data);
                if(data.liked){
                    i.classList.add('text-primary')
                } else{
                    i.classList.remove('text-primary')
                }
            })
            .catch(error => {
                console.log('error : ', error);
            })
        });
    });