

function DefaultSuccessFunctionAJAX(data) {
    //console.log('Submission was successful.');
    console.log(data);
}
function DefaultErrorFunctionAJAX(data) {
    //console.log('Submission was successful.');
    console.log(data);
}

function SubmitFormAJAX(form_id, success_func = DefaultSuccessFunctionAJAX, error_func = DefaultSuccessFunctionAJAX) {
    
    var form = $("[id='"+form_id+"']");
    //console.log("Inside AJAX");
    var data = form.serialize();
    data = data + "&ajax=True";
    console.log(data);
    $.ajax({
        type: form.attr('method'),
        url: form.attr('action'),
        data: data,
        success: success_func,
        error: error_func,
    });
}

console.log("You are in base.js (base.html)");
