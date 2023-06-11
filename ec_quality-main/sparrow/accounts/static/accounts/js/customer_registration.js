$('#frmFreeTrialDemo').submit(function (e) {
    if(!ValidCaptcha()){
        alert("Invalid Captcha input!");
        return false;
    }

    var postData = $(this).serializeArray();
    var formURL = $(this).attr('action');
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
            if (data.code == 1) {
                $('#frmFreeTrialDemo').hide();
                $('#msg1').show();
                $('input:not([type=image],[type=button],[type=submit])').val('');
            } else {
                $('#msg').removeClass('alert-success').addClass("danger").show().text(data.msg);
                setTimeout(function () { $("#msg").hide(); }, 5000);

            }
        },
        error: function (data) {
            $('#msg').removeClass('alert-success').addClass("danger").show().text(data.msg);
            setTimeout(function () { $("#msg").hide(); }, 5000);

        }
    });
    e.preventDefault();
});

$('#ajaxform').submit(); // Submit  the FORM
