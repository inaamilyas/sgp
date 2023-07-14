lesson_details_slug = document.getElementById('lesson_details_slug').innerText;
lesson_views_span = document.getElementById('lesson-views-span');
setTimeout(()=>{
    $.ajax({
        type: 'GET',
        url: `/count-lesson-views/${lesson_details_slug}/`,
        success: function (response) {
            console.log('success', response)
            lesson_views_span.innerText = response.lesson_views;
        },
        error: function (error) {
            console.log('error', error)
        },
    });
}, 5000);
    
// window.onbeforeunload(()=>{
//     console.log("Window unload")
// })