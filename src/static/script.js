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

    var delay = 1000;

    showDynamicPath(data, delay);

    window.setTimeout(function() {
        hideDynamicPath();
        showStaticPath(data);
    }, (data['path'].length+1) * delay);
}

var showDynamicPath = function(data, delay)
{
    var path_html = data['path'].map(function(img_url) {
        return '<img src="/images/'+img_url+'" class="inactive">';
    }).join(' ');

    document.getElementById('animation-container').style.height = '200px';
    document.getElementById('animation-container').innerHTML = path_html;
    document.querySelector("#animation-container > img:first-child").className = 'is-active';

    window.setTimeout(function() {
        switchToNextImage(2, data['path'].length, delay)
    }, delay);
}

var hideDynamicPath = function()
{
    document.getElementById('animation-container').innerHTML = '';
    document.getElementById('animation-container').style.height = '0px';
}

var switchToNextImage = function(current_idx, max_idx, delay)
{
    console.log(current_idx)
    document.querySelector("#animation-container > img:nth-child("+(current_idx-1)+")").className = 'was-active';
    document.querySelector("#animation-container > img:nth-child("+current_idx+")").className = 'is-active';
    if (current_idx < max_idx) {
        var todo = function() {
            switchToNextImage(current_idx+1, max_idx, delay)
        }
    } else {
        var todo = function() {
            document.querySelector("#animation-container > img:nth-child("+(current_idx-1)+")").className = 'was-active';
        }
    }
    window.setTimeout(todo, delay);
}

var showStaticPath = function(data)
{
    console.log('Showing static path');
    var path_html = '<div class="columns">';
    path_html += data['path'].map(function(img_url) {
        return '<div class="column">' + getImageHtml(img_url) + '</div>';
    }).join(' ');
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