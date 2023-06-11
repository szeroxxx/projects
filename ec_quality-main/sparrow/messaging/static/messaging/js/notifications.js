function notificationsInit() {
    var notifications = {};

    sparrow.registerCtrl('notificationsCtrl', function ($scope, $rootScope, $route, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache) {
        $scope.addViewButtons('');
        $('.view-more-btn').hide();
        $('#panel_body').css('height', (parent.document.body.clientHeight / 2 - 100) + 'px');
        $('#panel_body_general').css('height', (parent.document.body.clientHeight / 2 - 100) + 'px');
        config = {
            pageTitle: "Messages",
            topActionbar: {
               extra: [{
                    id:"btnMarkAsRead",
                    function: markAsRead
               }]
            },
        }

        sparrow.post("/messaging/notifications/", {
            count: 0
        }, false, function (data) {
            for (var i = 0; i < data.user_notifications.length; i++) {
                var userGrid = bindCustomGrid(data.user_notifications[i]);

                $('.user-notificationsTable').append(userGrid);
                $('#id_view_more_user').show();
            }

            for (var j = 0; j < data.notifications.length; j++) {
                var grid = bindCustomGrid(data.notifications[j]);

                $('.general-notificationsTable').append(grid)
                $('#id_view_more_general').show();
            }

            $('#id_view_more_user').attr('count', data.count);
            $('#id_view_more_general').attr('count', data.count);

            if (data.user_notifications.length >= data.user_record) {
                $('#id_view_more_user').hide()
            }

            if (data.notifications.length >= data.general_record) {
                $('#id_view_more_general').hide();
            }

            if (data.user_notifications.length == 0) {
                $('#no-notification-user').show();
                $('#id_view_more_user').hide();
            } else {
                $('#id_user_cnt').append(data.user_record);
            }

            if (data.notifications.length == 0) {
                $('#no-notification-general').show();
                $('#id_view_more_general').hide();
            } else {
                $('#id_general_cnt').append(data.general_record);
            }
        });

        function selectdMarkRead(post_ids) {
            ids = post_ids.join([separator = ','])
            sparrow.post("/messaging/mark_as_read/", {
                ids: ids
            }, false, function (data) {
                if (data.code == 1) {
                    $route.reload();
                }
                if (data.notification_count != 0 || data.user_notification_count != 0) {
                    $('#notification_count').show();
                    if (data.user_notification_count > 0) {
                        $('#notification_count').css('background-color', 'red')
                    }
                    $('#notification_count').text(data.notification_count + data.user_notification_count)
                } else {
                    $('#notification_count').text("");
                }
                for (var i = 0; i < data.notifications.length; i++) {
                    var notification = data.notifications[i]
                    var id = notification.id;
                    var read_by_text = 'Read by ' + notification.read_by + " on " + notification.read_on
                    $('#id_subject_' + id).css('font-weight', 'normal')
                    $('#id_created_on_' + id).css('font-weight', 'normal')
                    $('#mark_as_read_' + id).css('display', 'none')
                    $('#id_read_by_' + id).css('display', 'block')
                    $('#id_read_by_' + id).text(read_by_text)
                }
            });
        }

        $scope.markAsRead = function (is_user_notifications) {
            sparrow.post("/messaging/mark_as_all_read/", {
                is_user_notifications: is_user_notifications
            }, false, function (data) {
                if (data.code == 1) {
                    $('#notification_count').text(data.total_count)
                    if (data.total_count == 0) {
                        $('#notification_count').css('display', 'none')
                    }
                    if (data.notification_count) {
                        $('#notification_count').css('background-color', '');
                        $('#notification_count').addClass('label-primary notification_indicator classCount');
                    }
                    $route.reload();
                }
            });
        }

        $('#app_container').off('click', '.glyphicon-ok');
        $('#app_container').on('click', '.glyphicon-ok', function () {

            var id = $(this).attr('value');

            selectdMarkRead([id]);
        });

        $scope.viewMoreUser = function (event) {
            var count = parseInt($('#id_view_more_user').attr('count')) + 1;
            sparrow.post("/messaging/notifications/", {
                count: count
            }, false, function (data) {
                var user_notifications = data.user_notifications;
                for (var i = 0; i < user_notifications.length; i++) {
                    var grid = bindCustomGrid(user_notifications[i]);

                    $('.user-notificationsTable').append(grid);
                }

                $('#id_view_more_user').attr('count', data.count);
                if (!data.show_more_user) {
                    $('#id_view_more_user').hide();
                }
            });
        };
        $scope.viewMoreGeneral = function (event) {
            var count = parseInt($('#id_view_more_general').attr('count')) + 1;
            sparrow.post("/messaging/notifications/", {
                count: count
            }, false, function (data) {

                for (var i = 0; i < data.notifications.length; i++) {
                    var grid = bindCustomGrid(data.notifications[i]);

                    $('.general-notificationsTable').append(grid);
                }
                $('#id_view_more_general').attr('count', data.count)
                if (!data.show_more_general) {
                    $('#id_view_more_general').hide();
                }
            });
        };

        function bindCustomGrid(notification) {
            var is_read_by = '';
            var is_read_grid = 'font-weight: bold !important;';
            var bold_date = '';
            var read_icon = '';

            if (notification.read_by == '') {
                is_read_by = 'display: none;';
            }
            if (notification.is_read) {
                is_read_grid = 'font-weight: normal;';
                read_icon = 'display: none;';
            } else {
                bold_date = 'font-weight: bold;';
                read_icon = 'color: #1174da;';
            }

            var rowTemplate = '<tr class="notification">\
                                    <td>\
                                        <div class="col-sm-12" style="padding-right:5px">\
                                            <label id="id_subject_' + notification.id + '" class="notification-subject" style="font-weight: normal">' + notification.subject + '</label>\
                                            <label id="id_created_on_' + notification.id + '" class="notification-created-on" style="' + bold_date + '">' + notification.created_on + '<span id="mark_as_read_' + notification.id + '" value="' + notification.id + '" class="glyphicon glyphicon-ok" style="' + read_icon + '"></span></label>\
                                        </div>\
                                    </td>\
                                </tr>';

            return rowTemplate
        }

        sparrow.setup($scope, $rootScope, $route, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, config);
    });

    return notifications;
}

var notifications = notificationsInit();