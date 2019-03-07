

var selectImage = function(image_id)
{
    document.getElementById('selected-image').innerHTML = JSON.stringify({'image': image_id});
}

var handle_results = function()
{
    var raw_state = document.getElementById("output-hidden-state").getAttribute('accessKey');
    var state = JSON.parse(decodeURIComponent(raw_state));
}

var init = function()
{
    console.log('nothing to do')
}


// there is a problem with this: dash components haven't loaded yet
//window.addEventListener('DOMContentLoaded', init, false);

//setTimeout(init, 1000);
