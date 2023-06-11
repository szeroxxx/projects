function surveryReportInit(data) {
    var surveyReportModal = {};
    sparrow.registerCtrl('surveryReportCtrl', function (
        $scope,
        $rootScope,
        $route,
        $routeParams,
        $compile,
        DTOptionsBuilder,
        DTColumnBuilder,
        $templateCache,
        ModalService,
        $location
    ) {
        if (data != undefined) {
            $scope.reportId = data.report_id;
            $scope.formData = data.questions;
            $scope.customer_id = data.customer_id;
            $scope.canUpdateReport = data.can_update_report;
            $scope.ecActionNeeded = data.ec_action_needed;
            $scope.ecUserId = data.ec_userid;
            $scope.openFromEc = data.open_from_ec;
            $scope.reportType = data.report_type
        }

        postdata = {
            customer_id: $scope.customer_id,
            report_id: $scope.reportId,
            user_id: 0,
            submitted_by_admin_id: 0,
            submitted_by_customer_id: 0,
            answers: [],
        };

        if ($scope.ecUserId != 0 && $scope.ecUserId != undefined){
            postdata['ec_user_id'] = $scope.ecUserId;
        }
        if ($routeParams.relation_id != 0) {
            postdata['relation_id'] = $routeParams.relation_id;
        }

        if ($scope.canUpdateReport == 'false') {
            $('#btnSave').hide();
            $('#btnSaveClose').hide();
            $scope.inputDisabled = true;
        } else {
            $scope.inputDisabled = false;
        }

        // $scope.totalCheckedOtherBoxes = []

        // if ($routeParams.relation_id == 0){
        //     $scope.inputDisabled = false
        //     $("#btnEdit").hide()
        //     $("#btnCancel").hide()
        // }
        // else {
        //     postdata["relation_id"] = $routeParams.relation_id
        //     $scope.inputDisabled = true
        //     $("#btnSaveClose").hide()
        //     $("#btnSave").hide()
        //     $("#btnCancel").hide()
        // }
        // $("#btnEdit").click(function(){
        //     $scope.$apply(function(){
        //         $scope.inputDisabled = false
        //     })
        //     $("#btnSaveClose").show()
        //     $("#btnCancel").show()

        //     $("#btnSave").show()
        //     $("#btnEdit").hide()
        // })
        // $("#btnCancel").click(function(){
        //     $route.reload()
        //     // $scope.$apply(function(){
        //     //     $scope.inputDisabled = true
        //     // })
        //     // $("#btnSaveClose").show()
        //     // $("#btnSave").show()
        //     // $("#btnEdit").show()
        // })

        $scope.submitFormData = function (isClose) {
            postdata['answers'] = [];
            for (var i = 0; i < $scope.formData.length; i++) {
                temporary = { question_id: $scope.formData[i].question_id, answer: [] };
                if ($scope.formData[i].field == 'MCQ_SINGLE') {
                    name = $scope.formData[i].question_id + '_answer';
                    radioValue = $('input[name=' + name + ']:checked').val();
                    if (radioValue != undefined) {
                        otherCheckBoxId = 'question_' + name + '_true';
                        otherCheckBoxIdLength = $('input[id=' + otherCheckBoxId + ']:checked').length;
                        if (otherCheckBoxIdLength == 1) {
                            temporary['answer_text'] = $('#' + otherCheckBoxId + '_input').val();
                        }
                        temporary['answer'].push(radioValue);
                    }
                }

                if ($scope.formData[i].field == 'TEXT') {
                    id = 'question_' + $scope.formData[i].question_id + '_answer';
                    if ($('#' + id).val() != '') {
                        temporary['answer'].push($('#' + id).val());
                    }
                }
                if ($scope.formData[i].field == 'MCQ_MULTI') {
                    name = 'question_' + $scope.formData[i].question_id + '_answer';
                    var checkBoxes = document.getElementsByName(name);
                    for (var checkBox = 0; checkBox < checkBoxes.length; checkBox++) {
                        if (checkBoxes[checkBox].checked == true) {
                            isCheckboxOtherText = checkBoxes[checkBox].id.split('_');
                            isCheckboxOtherText = isCheckboxOtherText[isCheckboxOtherText.length - 1];
                            if (isCheckboxOtherText == 'true') {
                                temporary['answer_text'] = $('#' + checkBoxes[checkBox].id + '_input').val();
                            }
                            temporary['answer'].push(checkBoxes[checkBox].value.split('_')[1]);
                        }
                    }
                }
                if (temporary['answer'].length > 0) {
                    postdata['answers'].push(temporary);
                }
            }
            postdata['ec_action_needed'] = $('#ecActionNeed').prop('checked');
            sparrow.post(
                '/sales/save_survey_report/'+$scope.openFromEc+'/',
                {
                    data: JSON.stringify(postdata),
                },
                true,
                function (data) {
                    if (data.code == 1) {
                        if ($scope.openFromEc=='false'){
                            $routeParams.relation_id = data.relation_id;
                            window.location.hash = '#/sales/survey_report/' + $scope.customer_id + '/' + data.relation_id + '/' + $scope.canUpdateReport + '/'+$scope.reportType+'/';
                            $location.replace();
                            $route.reload();
                        }
                        sparrow.showMessage('appMsg', sparrow.MsgType.Success, data.msg, 10);
                        if (isClose == true) {
                            if ($scope.openFromEc == 'false'){
                                if (parent.globalIndex.iframeCloseCallback.length > 0) {
                                    var iFrameCloseCallback = parent.globalIndex.iframeCloseCallback.pop();
                                    setTimeout(function () {
                                        iFrameCloseCallback();
                                    }, 300);
                                }
                            }
                            else{
                            location.href = 'http://be.eurocircuits.com/shop/orders/eccOrderModified.aspx?successmsgtitle=close';
                            }
                        }
                    } else {
                        sparrow.showMessage('appMsg', sparrow.MsgType.Error, data.msg, 10);
                        return;
                    }
                }
            );
        };

        function showHideTextBox(id) {
            radioValue = $('input[id=' + id + ']:checked').length;
            if (radioValue == 1) {
                $('#' + id + '_input').removeClass('ng-hide');
            } else {
                $('#' + id + '_input').addClass('ng-hide');
            }
        }

        $scope.showOtherTextBox = function (questionId, obj, fieldType, fullQuestionObj) {
            if (obj.is_text == 'true' && fieldType == 'MCQ_MULTI') {
                id = 'question_' + questionId + '_answer_' + obj.is_text;
                showHideTextBox(id);
            }
            if (fieldType == 'MCQ_SINGLE') {
                for (var i = 0; i < fullQuestionObj.options.length; i++) {
                    id = 'question_' + questionId + '_answer_true';
                    showHideTextBox(id);
                }
            }
        };
        sparrow.setup($scope, $rootScope, $route, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, {}, ModalService);
    });
    return surveyReportModal;
}
surveryReportInit();
