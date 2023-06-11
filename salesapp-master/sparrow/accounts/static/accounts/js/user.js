function userInit() {
	var user = {};

    sparrow.registerCtrl('userCtrl',function($scope, $rootScope, $route, $routeParams, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, ModalService){        
        $scope.addViewButtons('');
        var config = {
            pageTitle: ""
        }
        $scope.saveUser = function (event) {
            event.preventDefault();
            // var user_current_perm = $('#user_permissions option').map(function() { return this.value; }).get().join(',');
            // var user_work_current_perm = $('#user_work_perm option').map(function() { return this.value; }).get().join(',');
            var user_role_ids = []
            var user_type = $('#id_customer_type option:selected').val();
            var is_customer = $('#id_is_customer').val();
            if(user_type == undefined && is_customer == 'True'){
                user_type = 2;
            }
            $('input[name=group]').each(function(i,obj) {
                user_role_ids.push(parseInt($(obj).val()));
            })
            
            var postData = {
                id: $routeParams.id,
                user_role_ids: user_role_ids,
                user_type : user_type,
                // user_current_perm: user_current_perm,
                // user_work_current_perm: user_work_current_perm
            }

            sparrow.postForm(postData, $('#frmUser'), $scope, function(data) {
                if(data.code == 1){
                    window.location.hash = "#/accounts/user/"+ data.id;
                    $route.reload();
                    if(data.is_reload){
                        location.reload()
                    }
                }
            },'appMsg');
        };

        if($routeParams.id == 0) {
            $('#id_change_password_field').hide()
        }

        $('#id_change_password').click(function(){
            $('#passwordChangeModel').modal('show');
            $('#changepassword').val('');
            $('#confirmchangepassword').val('');
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
                sparrow.post("/accounts/change_password/", {id: $routeParams.id,password:password}, true, function(data) { 
                if (data.code==1){
                    $('#passwordChangeModel').modal('hide');
                    if(data.is_reload){
                        location.reload()
                    }
                }
               })
            }
        });

        $('#app_container').off('click', '#btnClose');
        $('#app_container').on('click', '#btnClose', function(e) {           
            if(sparrow.inIframe()) {
                if(parent.globalIndex.iframeCloseCallback.length > 0) {
                   //parent.sparrow.iframeCloseCallback();
                   var iFrameCloseCallback = parent.globalIndex.iframeCloseCallback.pop();
                   iFrameCloseCallback();
                }
            }
            else {
                $scope.goBack(e,'');
            }            
        });

        setAutoLookup('id_group','/b/lookups/group/','',true, false, false, null, 10); 
        sparrow.setup($scope, $rootScope, $route, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, config, ModalService);
        sparrow.pager($scope, $routeParams, true, 'User','auth','#/accounts/user/');
    });


   

    // $('#app_container').on('click', '#choose_all', function(event) {
    //     event.preventDefault();
    //     var avail_perms = $('#all_permission > option');
    //     $('#all_permission > option').remove();
    //     $('#user_permissions').append(avail_perms);
    // }); 

    // $('#app_container').on('click', '#remove_all', function(event) {
    //     event.preventDefault();
    //     var avail_perms = $('#user_permissions > option');
    //     $('#user_permissions > option').remove();
    //     $('#all_permission').append(avail_perms);
    // }); 

    // $('#app_container').on('click', '#add_permission', function(event) {
    //     event.preventDefault();
    //     var avail_perms = $('#all_permission > option:selected');
    //     $('#all_permission > option:selected').remove();
    //     $('#user_permissions').prepend(avail_perms);
    // });

    // $('#app_container').on('click', '#remove_permission', function(event) {
    //     event.preventDefault();
    //     var avail_perms = $('#user_permissions > option:selected');
    //     $('#user_permissions > option:selected').remove();
    //     $('#all_permission').prepend(avail_perms);
    // });

    // $('#app_container').on('click', '#choose_all_workcenter', function(event) {
    //     event.preventDefault();
    //     var avail_perms = $('#all_work_perm > option');
    //     $('#all_work_perm > option').remove();
    //     $('#user_work_perm').append(avail_perms);
    // }); 

    // $('#app_container').on('click', '#remove_all_workcenter', function(event) {
    //     event.preventDefault();
    //     var avail_perms = $('#user_work_perm > option');
    //     $('#user_work_perm > option').remove();
    //     $('#all_work_perm').append(avail_perms);
    // }); 

    // $('#app_container').on('click', '#add_work_perm', function(event) {
    //     event.preventDefault();
    //     var avail_perms = $('#all_work_perm > option:selected');
    //     $('#all_work_perm > option:selected').remove();
    //     $('#user_work_perm').prepend(avail_perms);
    // });

    // $('#app_container').on('click', '#remove_work_perm', function(event) {
    //     event.preventDefault();
    //     var avail_perms = $('#user_work_perm > option:selected');
    //     $('#user_work_perm > option:selected').remove();
    //     $('#all_work_perm').prepend(avail_perms);
    // });

    // $('#app_container').on('keyup','#filter_permission, #filter_work_perm',function(){
    //     if($(this).attr('id') == 'filter_permission') {
    //         var current_value = $('#filter_permission').val();
    //         $('#all_permission option').show();
    //         if(current_value!=''){
    //             $('#all_permission option').each(function(){
    //                 if($(this).text().toLowerCase().indexOf(current_value.toLowerCase()) < 0)
    //                 $(this).hide();
    //             });
    //         }
    //     }
    //     else {
    //         var current_value = $('#filter_work_perm').val();
    //         $('#all_work_perm option').show();
    //         if(current_value!=''){
    //             $('#all_work_perm option').each(function(){
    //                 if($(this).text().toLowerCase().indexOf(current_value.toLowerCase()) < 0)
    //                 $(this).hide();
    //             });
    //         }
    //     }
    // });
	return user;
}

var user = userInit();