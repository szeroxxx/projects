function supportInit() {
    var support = {};

    sparrow.registerCtrl('supportCtrl', function($scope, $rootScope, $route, $routeParams, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, ModalService, Upload) {
        var title = 'Sparrow Support';
        $scope.success_msg = false;
        $scope.suppost_form = true;
        var config = {
            pageTitle: title
        }


        $scope.selectedReqType = 'bug';
        $scope.onRequestTypeSelect = function(reqType) {
            $scope.selectedReqType = reqType;
        }
        $('#id_title').focus();

        $scope.uploadDailouge = function(files) {
            $scope.files = files;            
        };

        $scope.upload = function(event) {
            event.preventDefault();

            if (!$('#frmSubmitIssue').valid()) {
                return;
            }

            var postData = {
              title: $('#id_title').val(),
              details: $('#id_details').val(),
              from_email: $('#from_email').val(),
              request_type: $scope.selectedReqType
            }

            var files = $scope.files;
            var allowedExtensions = /(\.jpg|\.jpeg|\.png|\.gif|\.txt|\.doc|\.docx|\.csv|\.pdf|\.xls|\.xlsx|\.txt|\.jpg)$/i;
            
            if (files && files.length) {
                for (var i = 0; i < files.length; i++) {                                        
                    if (files[i].size > 3000000) {
                        sparrow.showMessage("appMsg", sparrow.MsgType.Error, 'File more than 2MB size is not allowed.', 10);
                        return false;
                    }


                    if(!allowedExtensions.exec(files[i].name)){                        
                        sparrow.showMessage("appMsg", sparrow.MsgType.Error, 'Please upload file having extensions .jpg, .gif, .png, .txt, .doc, .pdf, .txt only.', 10);                        
                        return false;
                    }
                }

                postData['file'] = $scope.files[0]
            }            
            
            $('#loading-image').show();                    
            Upload.upload({
                url: '/accounts/submit_sparrow_issue/',
                data: postData
            }).then(function(resp) {
                $('#loading-image').hide();                
                if (resp.data.code == 1) {
                  $scope.success_msg = true; 
                  $scope.suppost_form = false;
                } else {
                    sparrow.showMessage("appMsg", sparrow.MsgType.Error, resp.data.msg, 10);
                }   
            }, function(resp) {
                $('#loading-image').hide();
                sparrow.showMessage("appMsg", sparrow.MsgType.Error, resp.status, 10);
            });
        };

        $scope.updateCount = function(count) {
            if ($("#" + $scope.countId) != undefined) {
                $("#" + $scope.countId).hide();
                if (count > 0) {
                    $("#" + $scope.countId).text("(" + count + ")");
                    $("#" + $scope.countId).show();
                }
            }
        }
        sparrow.setup($scope, $rootScope, $route, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, config, ModalService);
    });
    return support
}

var support = supportInit();