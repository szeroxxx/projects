
function profileInit() {
	var profile = {};

    sparrow.registerCtrl('profileCtrl',function($scope, $rootScope, $route, $routeParams, $compile, $templateCache, ModalService){        
        $rootScope.pageTitle = "Profile";                
        $scope.addViewButtons('');
        $scope.notificationModelTitle  = ''

        $scope.saveProfile = function (event) {
            event.preventDefault();
            sparrow.postForm({id: -1},$('#frmProfile'), $scope, setProfile);

        };
   
        $('#id_change_password').click(function(){
            $('#passwordChangeModel').modal('show');
            $('#changepasswordModalLabel').text('Change password');
            $('#changepassword_form').text('New password');
            $('#confimrchangedpassword_form').text('Confirm password');
            $('#passwordSave').hide();
        });

        $('#changePass').click(function(event){
            event.preventDefault();
            var password= $('input[id="changepassword"]').val();
            var confirm_password=$('input[id="confirmchangepassword"]').val();
            if($('#frmchangedpassword').valid()){
                sparrow.post("/accounts/change_password/", {password:password}, true, function(data) { 
                if (data.code==1){
                    location.reload();
                }
               })
            }
        });

        $('#manage-notifications-lines').on('shown.bs.collapse', function() {
            $(".servicedrop").addClass('glyphicon-chevron-up').removeClass('glyphicon-chevron-down');
        });

        $('#manage-notifications-lines').on('hidden.bs.collapse', function() {
            $(".servicedrop").addClass('glyphicon-chevron-down').removeClass('glyphicon-chevron-up');
        });

        $scope.saveBgImage = function() {
            if($('div.bgimage-border').length > 0)
            {
                var imageName = $('div.bgimage-border').find('img').attr('data-name');
                var imageSrc =  $('div.bgimage-border').find('img').attr('src');
                $('#imageSelection').css('display','block');
                $('#imageSelection').find('img').attr('src', imageSrc);
                $('#id_bgImage').val(imageName);
                $('#BgImageModel').modal('hide');
            }
        };

        $scope.onAddEmail = function(){
            $('#notificationModel').modal('show');
            $scope.notificationModelTitle = "Add email for notification";
            $scope.notifyEmail = true;
            $scope.verifyOTP = false;
            $scope.notifyMobile = false;
            $scope.timeOut = false;
            $scope.timer = false; 
            $scope.notifyData = ''
        }

        $scope.onDeleteMobMail = function(notification){
            var postData = {
                notification:notification,
            }
            sparrow.showConfirmDialog(ModalService, "You will not receive any " +notification+ " notifications.", "Delete record", function(confirmAction){
                if(confirmAction) {
                    sparrow.post("/accounts/notification_delete/", postData, false, function(data) {
                        if(data.code == 1){
                        $route.reload();
                        sparrow.showMessage("appMsg", sparrow.MsgType.Success, data.msg, 10); 
                        }  
                    })
                }
            })
        }

        $scope.onAddMobile= function(){
            $('#notificationModel').modal('show');
            $scope.notificationModelTitle = "Add mobile number for notification";
            $scope.notifyEmail = false;
            $scope.verifyOTP = false;
            $scope.notifyMobile = true;
            $scope.timeOut = false;
            $scope.timer = false; 
            $scope.notifyData = ''
        }

        $scope.saveNotificationData = function(){
            $scope.ForEmail = false
            $scope.ForMob = false
            if ($scope.notifyEmail){
                var email = $('#id_notfiy_email').val().trim();
                if(email == ''){
                    sparrow.showMessage("appMsg", sparrow.MsgType.Error, 'Email is mandatory', 5); 
                    return false
                }
                
                $scope.notifyData = email;
                $scope.email = email;
                $scope.ForEmail = true;
            }
            if ($scope.notifyMobile){
                var mobile_no = $('#id_notfiy_mobile').val().trim();
                if(mobile_no == ''){
                    sparrow.showMessage("appMsg", sparrow.MsgType.Error, 'Mobile number is mandatory', 5); 
                    return false
                }
                $scope.notifyData = mobile_no;
                $scope.mobile_no = mobile_no;
                $scope.ForMob = true;
            }
            var postData = {
                email:email,
                mobile_no:mobile_no,
                is_email : $scope.notifyEmail ,
                is_mobile_no : $scope.notifyMobile
            }
            sparrow.post("/accounts/send_notification_token/", postData, false, function(data) {
                if (data.code==1){
                    $scope.$apply(function(){
                        $scope.notificationModelTitle = "Validate OTP(One Time Passcode)";
                        $scope.notifyEmail = false;
                        $scope.notifyMobile = false;
                        $scope.verifyOTP = true;     
                        $scope.timer = false; 
                        $scope.timeOut = false;

                        timer(120);  
                        function timer(remaining) {
                            var m = Math.floor(remaining / 60);
                            var s = remaining % 60;

                            m = m < 10 ? '0' + m : m;
                            s = s < 10 ? '0' + s : s;
                            
                            $('#timer').text(m + ':' + s);
                            
                            remaining -= 1;
                            $scope.timer = true;

                            if(remaining >= 0) {
                            setTimeout(function() {
                                timer(remaining);
                            }, 1000);
                            return;
                            }
                            $scope.$apply(function(){
                                $scope.notifyEmail = false;
                                $scope.notifyMobile = false;
                                $scope.verifyOTP = true;     
                                $scope.timer = false; 
                                $scope.timeOut = true;
                            });
                        }
                                         
                    });
                }
            });
        }

        $scope.verifyOtp = function(){
            var otp = $('#id_otp').val().trim();
            var postData = {
                email: $scope.email,
                mobile_no: $scope.mobile_no,
                is_email : $scope.ForEmail ,
                is_mobile_no : $scope.ForMob ,
                otp : otp
            }
            sparrow.post("/accounts/notification_authentication/", postData, true, function(data) {
                if(data.code == 1){
                    $('#notificationModel').modal('hide');
                    location.reload();
                }
            }); 
        }
        
        function setProfile(data){
            if(data.avatar !=undefined && data.avatar!=''){
                $('#avatar_image').attr('src','/resources/profile_images/'+data.avatar);
                
            }
            if(data.code == 1){
                location.reload();
            }   
        }

        $('#app_container').on('click', '#clearImageSelection', function() {
            event.preventDefault();
            $('#id_bgImage').val('');
            $('#imageSelection').css('display','none');
        });

        $('#app_container').on('click', '#select_backgorund', function() {
            event.preventDefault();
            $('#BgImageLabel').html('Select background image');
            sparrow.post("/accounts/get_background_images/", {}, false, function(data) {
                data = $.parseJSON(data);
                html = '';
                counter = 0;
                $.each(data, function(i, item) {
                    if(counter%4 == 0){
                        html += '<div class="row" style="padding:10px;">';
                    }
                    html +=
                    '<div class="col-sm-3 col-md-3" style="height:160px;"><div class="image-parent" ><img style="width:100%;" data-name="' +
                    item.name +
                    '" src="' +
                    item.src +
                    '" /></div></div>';
                    if(counter%4 == 3 || counter == data.length-1){
                        html += '</div>';
                    }
                    counter++;
                });
                $('#BgImage_form').html(html);
                $('#BgImageModel').modal('show'); 
            }, 'html');
        });

        $('#app_container').on('click', '#BgImage_form img', function() {
            $('#BgImage_form div.image-parent').removeClass('bgimage-border');
            $(this).parent().addClass('bgimage-border');
        });

        $('#frmProfile').off('change', '#user_img')
        $('#frmProfile').on('change', '#user_img', function(e) {
            sparrow.setImagePreview(this, 'avatar_image')     
        })

        var options = {
            customBG: '#ffffff',
            doRender: 'div div',
            renderCallback: function($elm, toggled) {
                var colors = this.color.colors;
                var targetId = $elm.parent().parent().attr('target-id');
                $('#'+targetId).val('#'+colors.HEX);
            }
        };
        $('#linkColor,#buttonColor,#themeColor,#rowColor').colorPicker(options);
    }); 

	return profile;
}

var profile = profileInit();