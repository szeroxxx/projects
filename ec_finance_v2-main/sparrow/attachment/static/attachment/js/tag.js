function tagMasterInit() {
    var tagMaster = {};
    sparrow.registerCtrl('tagCtrl', function ($scope, $rootScope, $route, $routeParams, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, ModalService) {
        $scope.addViewButtons('');
        var config = {
            pageTitle: 'Tag',
        };
        setAutoLookup('id_parent', '/b/lookups/document_tag/', '', false, false, false, null, 1, null, null);
        $scope.saveTag = function () {
            var postData = {
                id: $routeParams.id,
            };
            sparrow.postForm(postData, $('#frmSaveTag'), $scope, switchEditMode);
        };
        var tagCloseCallbackData = {
            id: parseInt($routeParams.id),
            name: $('#id_name').val(),
        };
        console.log('tagCloseCallbackData', tagCloseCallbackData);
        $scope.onClose = function (e) {
            if (sparrow.inIframe()) {
                if (parent.globalIndex.iframeCloseCallback.length > 0) {
                    var iFrameCloseCallback = parent.globalIndex.iframeCloseCallback.pop();
                    iFrameCloseCallback('', tagCloseCallbackData);
                }
            } else {
                $scope.goBack(e, '');
            }
        };

        if ($routeParams.id != 0) {
            sparrow.applyReadOnlyMode('#frmSaveTag');
        }

        $scope.applyEditMode = function (e) {
            detailPageEditMode = true;
            sparrow.applyEditMode('#frmSaveTag', '#id_name');
        };

        function switchEditMode(data) {
            console.log('switchEditMode');
            if (data.id != undefined && data.id != '') {
                console.log('data.id', data.id);
                window.location.hash = '#/attachment/tag/' + data.id + '/';
                $route.reload();
            }
        }
        sparrow.setup($scope, $rootScope, $route, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, config, ModalService);
    });
    return tagMaster;
}

tagMasterInit();
