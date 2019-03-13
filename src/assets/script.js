
var MutationObserver = window.MutationObserver || window.WebKitMutationObserver || window.MozMutationObserver;

var selectImage = function(image_id)
{
    //document.getElementById('selected-image').innerHTML = JSON.stringify({'image': image_id});
    document.getElementById('selected-image').setAttribute('accessKey', JSON.stringify({'image': image_id}));
}

var handleResults = function()
{
    var raw_data = document.getElementById("result-container").getAttribute('accessKey');
    if (raw_data == '' || raw_data == '{}') {
        return false;
    }
    var data = JSON.parse(decodeURIComponent(raw_data));

    console.log(data);
    alert(data);
}

var init = function()
{
    var mo = new MutationObserver(function(mutations) {
        console.log('mutation observed!')
        mutations.forEach(function(mutation) {
            if (mutation.attributeName == "accesskey") {  // note the small k for key!
                console.log("result data changed");
                handleResults();
            }
        });
    });
    mo.observe(document.getElementById("result-container"), {
        attributes: true,
        characterData: true
    });
}


// there is a problem with this: dash components haven't loaded yet
//window.addEventListener('DOMContentLoaded', init, false);
setTimeout(init, 1000);
