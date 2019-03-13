var getImageHtml = function(url, name)
{
    var name = name || url.split('/').pop().split('.')[0].replace(/[^A-Za-z]/g, ' ');
    var html = '<figure class="image is-96x96">'
            + '<img src="/images/'+url+'">'
            + '<figcaption>'+name+'</figcaption>'
            + '</figure>';
    return html;
}


var handleResults = function(response)
{
    console.log(response);
    var data = JSON.parse(response);
    if (typeof(data) != 'object' || !('path' in data) ) {
        console.log('empty response... returning false');
        return false;
    }
    var path_html = '<div class="columns">';
    path_html += data['path'].map(function(img_url) {
        return '<div class="column">' + getImageHtml(img_url) + '</div>';
    })
    path_html += '</div>';

    var info_html = '<div class="columns">';
    info_html += '<div class="column"></div>';  // add dummy column
    info_html += data['distances'].map(function(dist) {
        return '<div class="column">Distance: ' + dist + '</div>';
    }).join(' ');
    info_html += '<div class="column"></div>';  // add dummy column
    info_html += '</div>';

    document.getElementById('results-container').innerHTML = path_html + info_html;
}


var getRequest = function(url, callback)
{
    var request = new XMLHttpRequest();
    request.onreadystatechange = function() {
        if (request.readyState == 4 && request.status == 200) {
            callback(request.response);
        }
    };
    request.open('GET', url);
    request.send();
}

var selectImage = function(img_url)
{
    var req_url = '/get_results?image=' + encodeURIComponent(img_url);
    console.log('requesting results for image: '+img_url);
    getRequest(req_url, handleResults)
}

var init = function()
{
    var container = document.getElementById('starting-images-container');
    var html = '<div class="columns">';
    var num_per_row = Math.ceil(starting_images.length/3);
    var i = 0;
    starting_images.forEach(function(item) {
        i += 1;
        html += '<div class="column">'
            + '<a href="javascript:selectImage(\''+item['url']+'\');">'
            + getImageHtml(item['url'], item['name'])
            + '</a>'
            + '</div>';
        if (i%num_per_row == 0) {
            html += '</div><div class="columns">';
        }
    });
    html += '</div>';
    container.innerHTML = html;
}

// there is a problem with this: dash components haven't loaded yet
window.addEventListener('DOMContentLoaded', init, false);
//setTimeout(init, 1000);