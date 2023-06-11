function qualificationInit() {
    var qualification = {};
    sparrow.registerCtrl('qualificationtypesCtrl', function ($scope, $rootScope, $route, $routeParams, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, ModalService) {
        var selectedqualificationId = 0;
        $scope.saveQualificationType = function (event) {
            var selectedId = $('#qualificationId').text();
            if (selectedId) {
                selectedqualificationId = selectedId;
            }
            event.preventDefault();
            sparrow.postForm(
                {
                    id: selectedqualificationId,
                },
                $('#qualificationTypeForm'),
                $scope,
                function (data) {
                    $scope.$dismiss(data.data);
                    if ($routeParams.id != undefined) {
                        var msOperation = $('#id_qualification_type').magicSuggest();
                        msOperation.setSelection([{ id: data.id, name: data.name }]);
                    } else {
                        $route.reload();
                    }
                }
            );
        };
    });
    return qualification;
}

qualification = qualificationInit();
