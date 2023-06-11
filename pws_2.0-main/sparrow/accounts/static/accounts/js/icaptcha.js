var tCtx = document.getElementById('textCanvas').getContext('2d'),
imageElem = document.getElementById('captchaImage');

var captchaCode = '';
/* Function to Generat Captcha */  
function GenerateCaptcha() {  
    var chr1 = Math.ceil(Math.random() * 10) + '';  
    var chr2 = Math.ceil(Math.random() * 10) + '';  
    var chr3 = Math.ceil(Math.random() * 10) + '';  

    var str = new Array(4).join().replace(/(.|$)/g, function () { return ((Math.random() * 36) | 0).toString(36)[Math.random() < .5 ? "toString" : "toUpperCase"](); });  
    //var captchaCode = str + chr1 + ' ' + chr2 + ' ' + chr3;    // for bigger captcha
    captchaCode = str + chr1;  

    //Puts the captcha code into the hidden canvas and then into image.

    var gradient = tCtx.createLinearGradient(0, 0, 120, 0);
    gradient.addColorStop("0", "pink");
    gradient.addColorStop("0.5", "green");
    gradient.addColorStop("1.0", "red");

    tCtx.canvas.width = 120;
    tCtx.font = "25px Verdana";
    tCtx.fillStyle = gradient;
    tCtx.fillText(captchaCode, 0, 30);
    imageElem.src = tCtx.canvas.toDataURL();

}  

/* Validating Captcha Function */  
function ValidCaptcha() {  
    var inputValue = removeSpaces(document.getElementById('txtCaptcha').value);  
    console.log(captchaCode);
    console.log(inputValue);
    if (captchaCode == inputValue) return true;  
    return false;  
}  

/* Remove spaces from Captcha Code */  
function removeSpaces(string) {  
    return string.split(' ').join('');  
}  
