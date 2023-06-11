function messageInit() {
    var message = {};
    sparrow.registerCtrl('messageCtrl',function($scope, $rootScope, $routeParams, $compile, $templateCache){        
        $rootScope.pageTitle = "Compose Message";  
        setAutoLookup('id_to_user','/b/lookups/users/', '');
        $('.richtext').summernote();  
        $scope.sendMail = function (event) {
            sparrow.postForm({id:0}, $('#frmUser'), $scope);
        };
    }); 
    return message;
}

var message = messageInit();