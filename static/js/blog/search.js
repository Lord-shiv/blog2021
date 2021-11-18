const searchField = document.querySelector('#a-search-id');
const searchResults = document.querySelector('.search-results');
const searchResultsHead = document.querySelector('.s-results-head');
searchResultsHead.style.display="none";

const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

if (searchField){
searchField.addEventListener('keyup', (e)=>{
    const searchValue = e.target.value;
    if (searchValue.trim().length>=0){
        console.log('searchValue', searchValue);

        fetch("/a_search/", {
            body: JSON.stringify({searchText: searchValue}),
            method: "POST",
        })

        .then((res) => res.json())
        .then((data) => {
            console.log(data);
            var lengthContent = 90;
            var text = data[0]?.content__;
            if (text){
                var shortText = $.trim(text).substring(0, lengthContent).split(" ").slice(0, -1).join(" ") + "...";
            }


            var lengthTitle = 30;
            var title = data[0]?.title__;
            var shortTitle = $.trim(title).substring(0, lengthTitle).split(" ").slice(0, -1).join(" ") + "...";
            console.log("hey >>++++++++++++++++++++++++++>-- ", data.length);

            if (data.length === 0) {
                searchResultsHead.style.display="block";
                searchResultsHead.innerHTML=`No results found`;
                searchResults.innerHTML = ''
            } else {
                searchResultsHead.style.display="none";
                searchResults.innerHTML = ''


                data.forEach((item) => {
                    var monthNumber = (item.created_at__month) - 1;
                    var DateMonth = monthNames[monthNumber];



                    var lengthContent = 60;
                    var text = item?.content__;
                    var shortText = $.trim(text).substring(0, lengthContent).split(" ").slice(0, -1).join(" ") + "...";
                            
        
                    var lengthTitle = 30;
                    var title = item?.title__;
                    var shortTitle = $.trim(title).substring(0, lengthTitle).split(" ").slice(0, -1).join(" ") + "...";
                    console.log("hey >>++++++++++++++++++++++++++>-- ", data.length);

                    searchResults.innerHTML += `
                        <div class="col-lg-4">
                            <div class="s-card s-card-margin">
                                <div class="s-card-header no-border">
                                    <h5 class="s-card-title">${ item.category__name_ }</h5>
                                    <p class="text-muted mt-4"> &nbsp; &nbsp; #${ item.tags__name }</p>
                                </div>
                                <div class="s-card-body pt-0">
                                    <div class="widget-49">
                                        <div class="widget-49-title-wrapper">
                                            <div class="widget-49-date-primary">
                                                <span class="widget-49-date-day">${ item.created_at__date }</span>
                                                <span class="widget-49-date-month">${ DateMonth }</span>
                                            </div>
                                            <div class="widget-49-meeting-info">
                                                <span class="widget-49-pro-title text-uppercase"><strong>${ shortTitle }</strong> </span>
                                                <span class="widget-49-meeting-time"><em><strong>"${ item.author__user__username }"</strong> published on <strong>${ item.created_at__date}-${ item.created_at__month }-${ item.created_at__year}</strong></em></span>
                                            </div>
                                        </div>
                                        <ol class="widget-49-meeting-points pt-0 mt-3">
                                            <p class="text-muted">${ shortText }</p>
                                        </ol>
                                        <div class="widget-49-meeting-action pb-2">
                                            <a href="/post/${item.slug}" class="btn btn-sm btn-flash-border-primary">read morea..  <i class="far fa-angle-double-right"></i></a>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>`
                })
            }
        });
    } else {
        console.log('error while searching');
    }
});
}




$("#id_q").change(function () {
    $.ajax({
        url: "/search/",   //Replace this with your search URL
        type: "get",       // Querying means getting in HTTP terms
        data: $("#search").serialize(),    // This transforms your search form into a JSON dictionary.
        success: function (data){
            s_results = get.ElementById('s_results');
            if (data.results){
                $('#s_results').innerHTML=`<small><p> class="text-success mt-2">{{ results.author }} {{ results.title }}`
            }
        }, // Do sth here.
        error: function (xHR, textStatus) {
            console.log('something went wrong while searching!')
        } // Handle server-side errors here.
    });
})