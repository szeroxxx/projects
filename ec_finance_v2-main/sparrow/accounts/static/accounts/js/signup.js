$('#frmsignup').submit(function (e) {
    var postData = $(this).serializeArray();
    var formURL = $(this).attr('action');
    // var validator = $('#frmsignup').validate();
    // validator.form();
    // if (!validator.valid()) {
    //   return false;
    // }
    $.ajax({
        dataType: 'json',
        type: 'POST',
        url: formURL,
        data: postData,
        beforeSend: function () {
            $('#loading-image').show();
        },
        complete: function () {
            $('#loading-image').hide();
        },
        success: function (data) {
            success = data.code == 0 ? false : true;
            if (success == true) {
                $('#msg').removeClass('alert-danger').addClass('alert-success').show().text(data.msg);
                $('input:not([type=image],[type=button],[type=submit])').val('');
            } else {
                $('#msg').removeClass('alert-success').addClass('alert-danger').show().text(data.msg);
            }
        },
        error: function (data) {
            $('#msg').removeClass('alert-success').addClass('alert-danger').show().text(data.msg);
            console.log(data);
        },
    });
    e.preventDefault();
});

$('#ajaxform').submit(); // Submit  the FORM
