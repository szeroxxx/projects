function iprestrictionInit(data) {
    sparrow.registerCtrl('allowedipCtrl', function ($scope, $rootScope, $route, $routeParams, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, ModalService) {
        $scope.addViewButtons("");
        $scope.ipdata = [];
        $scope.ips_name = [];
        $scope.addMode = false;
        $scope.addNewLine = true;
        $scope.editingIP = null;
        $scope.update_ip = null;

        var allowed_ips = data['allowed_ips'];
        var config = {
            pageTitle: 'Manage IP Address Restrictions',
        };

        function getCurrentDate() {
            var today = new Date();
            var dd = today.getDate();
            var mm = today.getMonth() + 1; // January is 0!

            var yyyy = today.getFullYear();
            if (dd < 10) {
                dd = '0' + dd;
            }
            if (mm < 10) {
                mm = '0' + mm;
            }
            return dd + '/' + mm + '/' + yyyy;
        }
        var current_date = getCurrentDate();

        var user_data = data['user_data'];
        var login_user = data['login_user_data'];
        $scope.user_data = user_data;

        for (var i = 0; i < allowed_ips.length; i++) {
            $scope.ipdata.push({
                user_id: allowed_ips[i].user_id,
                desc: allowed_ips[i].desc,
                ip_name: allowed_ips[i].ip_name,
                date: allowed_ips[i].date,
            });
            $scope.ips_name.push(allowed_ips[i].ip_name);
        }

        $scope.addIp = function () {
            if (data.permissions['can_add_ip'] == false) {
                sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'You do not have permission to perform this action', 10);
                return;
            }
            $scope.addNewLine = false;
            $scope.addMode = true;
            var ip = {
                user_id: login_user['id'],
                ip_name: '',
                desc: '',
                date: current_date,
            };
            $scope.ipdata.push(ip);
            $scope.editingIP = ip;
        };

        $scope.cancelIP = function (row) {
            $scope.editingIP = null;
            for (var i = 0; i < $scope.ipdata.length; i++) {
                if ($scope.addMode && $scope.ipdata[i].ip_name == row.ip_name) {
                    $scope.ipdata.splice(i, 1);
                    break;
                }
            }
            $scope.addNewLine = true;
        };

        $scope.editIP = function (row) {
            if (data.permissions['can_update_ip'] == false) {
                sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'You do not have permission to perform this action', 10);
                return;
            }
            $scope.editingIP = row;
            $scope.update_ip = row.ip_name;
            $scope.addMode = false;
            $scope.addNewLine = true;
        };

        $scope.saveIP = function (row) {
            var ip_name = row['ip_name'];
            if (ip_name == '' || ip_name == undefined) {
                sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please add IP.', 5);
                return false;
            }

            if ($scope.update_ip != ip_name) {
                if (jQuery.inArray(ip_name, $scope.ips_name) != -1) {
                    sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'IP already exists.', 5);
                    return false;
                }
            }

            var Ipv4_pattern = new RegExp('(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]).){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$');

            var Ipv6_pattern = new RegExp(
                '((?:[0-9A-Fa-f]{1,4}))((?::[0-9A-Fa-f]{1,4}))*::((?:[0-9A-Fa-f]{1,4}))((?::[0-9A-Fa-f]{1,4}))*|((?:[0-9A-Fa-f]{1,4}))((?::[0-9A-Fa-f]{1,4})){7}$'
            );

            if (!(Ipv4_pattern.test(ip_name) || Ipv6_pattern.test(ip_name))) {
                sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please enter valid IP', 5);
                return false;
            }

            for (var i = 0; i < $scope.ipdata.length; i++) {
                if ($scope.ipdata[i].ip_name == ip_name) {
                    $scope.ipdata[i].date = current_date;
                    $scope.ipdata[i].user_id = login_user['id'];
                    break;
                }
            }

            $scope.editingIP = '';
            $scope.addNewLine = true;
            sparrow.post(
                '/accounts/save_whitelist_ip/',
                {
                    ip_data: JSON.stringify($scope.ipdata),
                    type: 'save',
                },
                true
            );
        };

        $scope.deleteIP = function (row) {
            if (data.permissions['can_delete_ip'] == false) {
                sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'You do not have permission to perform this action', 10);
                return;
            }
            sparrow.showConfirmDialog(ModalService, 'Are you sure you want to delete record?', 'Delete record', function (confirmAction) {
                if (confirmAction) {
                    for (var i = 0; i < $scope.ipdata.length; i++) {
                        if ($scope.ipdata[i].ip_name == row.ip_name) {
                            $scope.ipdata.splice(i, 1);
                            break;
                        }
                    }
                    sparrow.post(
                        '/accounts/save_whitelist_ip/',
                        {
                            ip_data: JSON.stringify($scope.ipdata),
                            type: 'delete',
                        },
                        true
                    );
                }
            });
        };
        sparrow.setup($scope, $rootScope, $route, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, config, ModalService);
    });
}

iprestrictionInit();
