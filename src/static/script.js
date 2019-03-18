var getImageHtml = function(url, name)
{
    var name = name || url.split('/').pop().split('.')[0].replace(/[^A-Za-z]/g, ' ');
    var html = '<figure class="image is-96x96 is-expanded">'
            + '<img src="/images/'+url+'">'
            + '<figcaption><center>'+name+'</center></figcaption>'
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
    //showStaticPath(data);
    showAnimation(data);
}

var showAnimation = function(data)
{
    var path_html = data['path'].map(function(img_url) {
        return '<img src="/images/'+img_url+'">';
    }).join(' ');

    document.getElementById('animation-container').innerHTML = path_html;
    /*
    document.querySelectorAll("#animation-container > img:first-child")[0].className = 'opaque';
    for (var i=0; i<data['path'].length; i++) {
        window.setTimeout(function() {
            document.querySelectorAll("#animation-container > img:nth-child("+i+")")[0].className = '';
            document.querySelectorAll("#animation-container > img:nth-child("+(i+1)+")")[0].className = 'opaque';
        }, (i+1)*1000);
    }
    */
    document.querySelector("#animation-container > img:first-child").className = 'opaque';

    var delay = 2000;
    window.setTimeout(function() {
        switchToNextImage(2, data['path'].length, delay)
    }, delay);
    /*
    for (var i=1; i<data['path'].length-1; i++) {
        var qs1 = "#animation-container > img:nth-child("+i+")";
        var qs2 = "#animation-container > img:nth-child("+(i+1)+")";
        window.setTimeout(function() {
            console.log(i);
            var elm = document.querySelector(qs1);
            elm.className = '';
            var elm = document.querySelector(qs2);
            elm.className = 'opaque';
        }, (i)*1000);
    }
    */
}

var switchToNextImage = function(current_idx, max_idx, delay)
{
    console.log(current_idx)
    document.querySelector("#animation-container > img:nth-child("+(current_idx-1)+")").className = '';
    document.querySelector("#animation-container > img:nth-child("+current_idx+")").className = 'opaque';
    if (current_idx < max_idx) {
        window.setTimeout(function() {
            switchToNextImage(current_idx+1, max_idx, delay)
        }, delay);
    }
}

var showStaticPath = function(data)
{
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
    var html = '<div class="columns is-centered">';
    var num_per_row = Math.ceil(starting_images.length/3);
    var i = 0;
    starting_images.forEach(function(item) {
        i += 1;
        html += '<div class="column is-mobile">'
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