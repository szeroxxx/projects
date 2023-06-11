function releaseNoteInit() {
    var releaseNote = {};

    sparrow.registerCtrl('releaseNoteCtrl', function ($scope, $rootScope, $route, $routeParams, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, ModalService) {
        $scope.addViewButtons('');
        var config = {
            pageTitle: 'Release note',
        };
        $('#id_release_note_count').find('span').remove();
        sparrow.setup($scope, $rootScope, $route, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, config, ModalService);
        sparrow.setParent('');
    });

    return releaseNote;
}

releaseNoteInit();
