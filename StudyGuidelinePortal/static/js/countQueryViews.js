query_details_slug = document.getElementById('query-details-slug').innerText;
query_views_span = document.getElementById('query-views-span');
setTimeout(()=>{
    $.ajax({
        type: 'GET',
        url: `/count-query-views/${query_details_slug}/`,
        success: function (response) {
            console.log('success', response)
            query_views_span.innerText = response.query_views;
        },
        error: function (error) {
            console.log('error', error)
        },
    });
}, 5000);
    