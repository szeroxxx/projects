function roleInit() {
    var role = {};
    $('#loading-image').show();
    sparrow.registerCtrl('roleCtrl', function ($scope, $rootScope, $route, $routeParams, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, ModalService) {
        $scope.addViewButtons('');
        var detailPageEditMode = false;
        $('#loading-image').hide();
        var title = 'Role permission';
        var roleName = $('#id_name').val();
        var config = {
            pageTitle: $routeParams.id == 0 ? title : title + ' - ' + roleName,
        };

        $scope.SaveRole = function (event) {
            event.preventDefault();
            var selected = [];
            $('.perm input:checked').each(function () {
                selected.push($(this).val());
            });
            var postData = {
                id: $routeParams.id,
                role_assi_perm: selected.join([(separator = ',')]),
            };
            sparrow.postForm(postData, $('#frmRole'), $scope, switchEditMode);
        };

        function switchEditMode(data) {
            if ($routeParams.id != undefined && $routeParams.id != '0') {
                $route.reload();
            }
            if (data.id != undefined && data.id != '') {
                window.location.hash = '#/accounts/role/' + data.id;
            }
        }

        $(document).ready(function () {
            $('.perm_section').find('li').first().addClass('active');
            $('.perm_section').find('ul').first().addClass('onActive');
            $('.perm_section').find('a').first().addClass('onActive');
            var data = $('.perm_section').find('ul').first().attr('id');
            var name = $('.perm_section').find('ul').first().text();
            var parent_name = $('.perm_section').find('a').first().text();
            var dataId = data.split('_')[1];
            display_msg = 'Select all permissions for ' + parent_name.trim() + ' module';
            $('#display_msg_id').text(display_msg);
            $('.head').addClass('permissionItem');
            $('.check-all').show();
            $('#menu_name').text(parent_name + ' / ' + name);
            $('.select-all').attr('id', dataId);
            $('div[data-id="' + dataId + '"]').show();
            var $li = $('.perm_section').find('li').first();
            var list = $li.find('ul');
            list.css('display', 'block');
            var dropDown = $('.perm_section').find('span').first();
            dropDown.addClass('icon-arrow-1-up');
            var checked = $('input[data-id="' + dataId + '"]:checked').length;
            var totalcheck = $('input[data-id="' + dataId + '"]').length;
            if (checked == totalcheck) {
                $('.select-all').prop('checked', true);
            }

            $('.perm_section')
                .find('a')
                .on('click', function (ev) {
                    var $li = $(this).parent();
                    $('.sub-menu').removeClass('onActive');
                    $(this).addClass('onActive');

                    if ($li.is('.active')) {
                        $li.removeClass('active');
                        $('ul', $li).slideUp();
                        $('.sub-menu').removeClass('onActive');
                        if (!$li.parent().is('.child_menu')) {
                            $('.icon-arrow-1-up').removeClass('icon-arrow-1-up').addClass('icon-arrow-1-down');
                        }
                    } else {
                        // prevent closing menu if we are on child menu
                        if (!$li.parent().is('.child_menu')) {
                            $('.perm_section').find('li').removeClass('active');
                            $('.permCheckbox ch').prop('disabled', true);
                            $('.perm_section').find('li ul').slideUp();
                            $('.icon-arrow-1-up').removeClass('icon-arrow-1-up').addClass('icon-arrow-1-down');
                        } else {
                            $li.parent().find('li').removeClass('active').removeClass('current-page');
                        }

                        $li.addClass('active');
                        $(this).find('.icon-arrow-1-down').removeClass('icon-arrow-1-down').addClass('icon-arrow-1-up');
                        $('ul', $li).slideDown();
                    }
                });
        });

        $scope.permclick = function (id, name, parent_name) {
            display_msg = 'Select all permissions for ' + parent_name + ' module';
            $('#display_msg_id').text(display_msg);
            $('ul').removeClass('onActive');
            $('.single_menu').removeClass('onActive');
            $('#menu_' + id).addClass('onActive');
            $('.perm').hide();
            $('.head').addClass('permissionItem');
            $('.check-all').show();
            $('div[data-id="' + id + '"]').show();
            $('.select-all').attr('id', id);
            if (name == parent_name) {
                $('.perm_section').find('li').removeClass('active');
                $('.perm_section').find('li ul').slideUp();
                $('.icon-arrow-1-up').removeClass('icon-arrow-1-up').addClass('icon-arrow-1-down');
                $('.sub-menu').removeClass('onActive');
                $('#menu_' + id).addClass('onActive');
                $('#menu_name').text(parent_name);
            } else {
                $('#menu_name').text(parent_name + ' / ' + name);
            }

            mainCheckBoxSelection(id);
        };

        function mainCheckBoxSelection(id) {
            if ($('input[data-id="' + id + '"]:checked').length == $('div[data-id="' + id + '"]').length) {
                $('input[id="' + id + '"]')[0].checked = true;
            } else {
                $('input[id="' + id + '"]')[0].checked = false;
                $('input[data-id="selectAll"]').prop('checked', false);
            }
            if ($('input[data-id="' + id + '"][data-type="view"]').length == 0) {
                $('input[data-id="' + id + '"]').removeAttr('disabled');
            } else {
                if ($('input[data-id="' + id + '"][data-type="view"]:checked').length == 0) {
                    $('input[data-id="' + id + '"]')
                        .not('input[data-id="' + id + '"][data-type="view"]')
                        .attr('checked', false);
                    $('input[data-id="' + id + '"]')
                        .not('input[data-id="' + id + '"][data-type="view"]')
                        .attr('disabled', 'disabled');
                } else {
                    // $('input[data-id="' + id + '"]').removeAttr('disabled');
                    if (detailPageEditMode) {
                        $('input[data-id="' + id + '"]').prop('disabled', false);
                    } else {
                        $('input[data-id="' + id + '"]').prop('disabled', true);
                    }
                }
            }
        }

        $('.select-all').click(function () {
            var id = $(this).attr('id');
            $('input[data-id="' + id + '"]').prop('checked', this.checked);

            if (this.checked) {
                $('input[data-id="' + id + '"]').removeAttr('disabled');
            } else {
                $('input[data-id="' + id + '"]')
                    .not('input[data-id="' + id + '"][data-type="view"]')
                    .attr('disabled', 'disabled');
            }
        });

        $('.permCheckbox.ch').click(function () {
            mainCheckBoxSelection($(this).attr('data-id'));
        });

        $('#selectAllId').click(function () {
            var menu_all_permission = $('#display_msg_id').text();
            var parent_name = menu_all_permission.split(' ').slice(4, 5)[0];

            var menuIds = [];
            $('.' + parent_name).each(function () {
                menuIds.push(parseInt($(this).attr('id').replace('menu_', '')));
            });

            for (var i = 0; i < menuIds.length; i++) {
                if ($('input[data-id="selectAll"]:checked').length == 1) {
                    $('#' + menuIds[i]).prop('checked', true);
                    $('input[data-id="' + menuIds[i] + '"]').prop('checked', this.checked);
                    $('input[data-id="' + menuIds[i] + '"]').removeAttr('disabled');
                } else {
                    $('#' + menuIds[i]).prop('checked', false);
                    $('input[data-id="' + menuIds[i] + '"]').prop('checked', false);
                }
            }
        });

        // $('#app_container').on('click', '#id_change_password', function(event) {
        // event.preventDefault();
        // $('#id_change_password_field').hide()
        // $('#id_password_field').show()
        // $('#id_confirm_password_field').show()
        // });

        // $('#app_container').on('click', '#choose_all', function(event) {
        //     event.preventDefault();
        //     var avail_perms = $('#all_permission > option');
        //     $('#all_permission > option').remove();
        //     $('#role_permissions').append(avail_perms);
        // });

        // $('#app_container').on('click', '#remove_all', function(event) {
        //     event.preventDefault();
        //     var avail_perms = $('#role_permissions > option');
        //     $('#role_permissions > option').remove();
        //     $('#all_permission').append(avail_perms);
        // });

        // $('#app_container').on('click', '#add_permission', function(event) {
        //     event.preventDefault();
        //     var avail_perms = $('#all_permission > option:selected');
        //     $('#all_permission > option:selected').remove();
        //     $('#role_permissions').prepend(avail_perms);
        // });

        // $('#app_container').on('click', '#remove_permission', function(event) {
        //     event.preventDefault();
        //     var avail_perms = $('#role_permissions > option:selected');
        //     $('#role_permissions > option:selected').remove();
        //     $('#all_permission').prepend(avail_perms);
        // });

        // $('#app_container').on('click', '#choose_all_workcenter', function(event) {
        //     event.preventDefault();
        //     var avail_perms = $('#all_work_perm > option');
        //     $('#all_work_perm > option').remove();
        //     $('#role_work_perm').append(avail_perms);
        // });

        // $('#app_container').on('click', '#remove_all_workcenter', function(event) {
        //     event.preventDefault();
        //     var avail_perms = $('#role_work_perm > option');
        //     $('#role_work_perm > option').remove();
        //     $('#all_work_perm').append(avail_perms);
        // });

        // $('#app_container').on('click', '#add_work_perm', function(event) {
        //     event.preventDefault();
        //     var avail_perms = $('#all_work_perm > option:selected');
        //     $('#all_work_perm > option:selected').remove();
        //     $('#role_work_perm').prepend(avail_perms);
        // });

        // $('#app_container').on('click', '#remove_work_perm', function(event) {
        //     event.preventDefault();
        //     var avail_perms = $('#role_work_perm > option:selected');
        //     $('#role_work_perm > option:selected').remove();
        //     $('#all_work_perm').prepend(avail_perms);
        // });

        // $('#app_container').on('click', '#choose_all_perm', function(event) {
        //     event.preventDefault();
        //     var avail_perms = $('#all_perm > option');
        //     $('#all_perm > option').remove();
        //     $('#perm').append(avail_perms);
        // });

        // $('#app_container').on('click', '#remove_all_perm', function(event) {
        //     event.preventDefault();
        //     var avail_perms = $('#perm > option');
        //     $('#perm > option').remove();
        //     $('#all_perm').append(avail_perms);
        // });

        // $('#app_container').on('click', '#add_perm', function(event) {
        //     event.preventDefault();
        //     var avail_perms = $('#all_perm > option:selected');
        //     $('#all_perm > option:selected').remove();
        //     $('#perm').prepend(avail_perms);
        // });

        // $('#app_container').on('click', '#remove_perm', function(event) {
        //     event.preventDefault();
        //     var avail_perms = $('#perm > option:selected');
        //     $('#perm > option:selected').remove();
        //     $('#all_perm').prepend(avail_perms);
        // });

        // $('#app_container').on('keyup','#filter_permission',function(){
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
        // else if($(this).attr('id') == 'filter_work_perm'){
        //     var current_value = $('#filter_work_perm').val();
        //     $('#all_work_perm option').show();
        //     if(current_value!=''){
        //         $('#all_work_perm option').each(function(){
        //             if($(this).text().toLowerCase().indexOf(current_value.toLowerCase()) < 0)
        //             $(this).hide();
        //         });
        //     }
        // }
        // else if($(this).attr('id') == 'filter_perm'){
        //     var current_value = $('#filter_perm').val();
        //     $('#all_perm option').show();
        //     if(current_value!=''){
        //         $('#all_perm option').each(function(){
        //             if($(this).text().toLowerCase().indexOf(current_value.toLowerCase()) < 0)
        //             $(this).hide();
        //         });
        //     }
        // }
        // else if($(this).attr('id') == 'filter_assi_permission'){
        //     var current_value = $('#filter_assi_permission').val();
        //     $('#role_permissions option').show();
        //     if(current_value!=''){
        //         $('#role_permissions option').each(function(){
        //             if($(this).text().toLowerCase().indexOf(current_value.toLowerCase()) < 0)
        //             $(this).hide();
        //         });
        //     }
        // }
        // else if($(this).attr('id') == 'filter_assi_work_perm'){
        //     var current_value = $('#filter_assi_work_perm').val();
        //     $('#role_work_perm option').show();k
        //     if(current_value!=''){
        //         $('#role_work_perm option').each(function(){
        //             if($(this).text().toLowerCase().indexOf(current_value.toLowerCase()) < 0)
        //             $(this).hide();
        //         });
        //     }
        // }
        // else{
        //     var current_value = $('#filter_assi_perm').val();
        //     $('#perm option').show();
        //     if(current_value!=''){
        //         $('#perm option').each(function(){
        //             if($(this).text().toLowerCase().indexOf(current_value.toLowerCase()) < 0)
        //             $(this).hide();
        //         });
        //     }
        // }
        // });
        if ($routeParams.id != 0) {
            $('.permCheckbox').prop('disabled', true);
            sparrow.applyReadOnlyMode('#frmRole');
        }

        $scope.applyEditMode = function (e) {
            detailPageEditMode = true;
            $('.permCheckbox').prop('disabled', false);
            sparrow.applyEditMode('#frmRole', '#id_name');
        };

        sparrow.setup($scope, $rootScope, $route, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, config, ModalService);
    });

    // console.log($('#permi').text());

    return role;
}

roleInit();
