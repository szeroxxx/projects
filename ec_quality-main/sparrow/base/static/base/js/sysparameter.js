function sysparameterInit() {
    var sysparameters = {};
    sparrow.registerCtrl('sysparameterseditCtrl', function ($scope, $rootScope, $route, $routeParams, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, ModalService) {
        $('#id_para_code').focus()
        $scope.addViewButtons('');
        var title = 'System parameter';
        var paraCode = $('#id_para_code').val();
        config = {
            pageTitle: $routeParams.id == 0 ? title : title + ' - ' + paraCode,
        };

        $scope.SaveSysParameter = function () {
            var para_code = $('#id_para_code').val();
            var para_value = $('#id_para_value').val();
            if (para_code == 'quotation_approval') {
                $('.sidebarChilemenu').each(function () {
                    var childMenuName = $(this).attr('refrence');
                    if (childMenuName == 'To be approved') {
                        if (para_value == 'True') {
                            $(this).show();
                        }
                        if (para_value == 'False') {
                            $(this).hide();
                        }
                    }
                });
            }
            sparrow.postForm(
                {
                    id: $routeParams.id,
                },
                $('#frmSysParameter'),
                $scope,
                switchEditMode
            );
        };

        function switchEditMode(data) {
            if (data.id != undefined && data.id != '') {
                window.location.hash = '#/b/sysparameter/' + data.id + '/';
            }
        }
        $scope.goBack = function () {
            window.location.hash = "#/sysparameters"
          }

        sparrow.setup($scope, $rootScope, $route, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, config, ModalService);
    });

    return sysparameters;
}

sysparameterInit();
