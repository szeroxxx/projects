/* eslint-disable no-multi-str */
/* eslint-disable max-len */
(function () {
    angular
        .module('angular-comments', [])
        .filter('trusted', function ($sce) {
            return function (html) {
                return $sce.trustAsHtml(html);
            };
        })
        .directive('angComments', function () {
            return {
                restrict: 'AEC',
                scope: {
                    appName: '@',
                    modelName: '@',
                    entityId: '@',
                    mentionedIn: '@',
                    comments: '@',
                    modelRemarkField: '@',
                    countId: '@',
                    deleteButton: '@',
                    user: '@',
                    existUsers: '@',
                    cmtButtonText: '@',
                    displayScopeField: '@',
                    remarkType: '@',
                    remarkName: '@',
                    remarkId: '@',
                    createDate: '@',
                },
                replace: true,
                controller: function ($scope, Upload, ModalService) {
                    $scope.isPreDefineComment = false;
                    $scope.existUsers = [];
                    $scope.fileMaxCount = 0;
                    $scope.files = [];
                    $scope.cmtButtonText = 'Add remark';
                    $scope.cmtButtonDisable = false;
                    $scope.scopeShow = false;
                    if ($scope.displayScopeField == undefined) {
                        $scope.displayScopeField = 'false';
                    }
                    if ($scope.appName != 'production') {
                        $('.production_remark_dialogue').css('display', 'none');
                    }
                    if ($scope.appName == 'production' && $scope.modelName == 'PreDefineComment') {
                        $scope.scopeShow = true;
                        $('.production_remark_dialogue').hide();
                    }

                    if ($scope.modelName != 'PreDefineComment') {
                        $('.production_remark_dialogue').css('display', 'none');
                        $('#id_source_of_info').css('display', 'none');
                        $('#id_scope').css('display', 'none');
                        $('#label_source_of_info').css('display', 'none');
                        $('#label_scope').css('display', 'none');
                    }

                    // function stripScripts(s) {
                    //     var div = document.createElement('div');
                    //     div.innerHTML = s;
                    //     var scripts = div.getElementsByTagName('script');
                    //     var styles = div.getElementsByTagName('style');
                    //     var i = scripts.length;
                    //     var j = styles.length;
                    //     while (i--) {
                    //         scripts[i].parentNode.removeChild(scripts[i]);
                    //     }
                    //     while (j--) {
                    //         styles[j].parentNode.removeChild(styles[j]);
                    //     }
                    //     return div.innerHTML;
                    // }
                    if ($scope.appName == 'products') {
                        $('.production_remark_dialogue').css('display', 'none');
                        $('#label_id_remark_type').css('display', 'none');
                        $('#id_source_of_info').css('display', 'none');
                        $('#id_scope').css('display', 'none');
                        $('#label_source_of_info').css('display', 'none');
                        $('#label_scope').css('display', 'none');
                        $('#id_remark_type').css('display', 'none');
                    }

                    $scope.uploadDailouge = function (files) {
                        if (files.length != 0) {
                            for (var i = 0; i < files.length; i++) {
                                $scope.files.push(files[i]);
                                var currentValue = files[i].name;
                                $scope.fileMaxCount = $scope.fileMaxCount + 1;
                                $('#attachmentList' + $scope.entityId).prepend(
                                    '<div class="mail-attachment"><span data-attachment-name="attachment' +
                                        $scope.fileMaxCount +
                                        '" title="'+ currentValue +'"">' +
                                        currentValue +
                                        '</span><i class="icon-close"></i></div>'
                                );
                            }
                        }
                    };

                    setTimeout(function () {
                        $('#txtComment' + $scope.entityId).summernote({
                            height: 50,
                            toolbar: [
                                ['font', ['bold', 'italic', 'underline', 'clear']],
                                ['fontname', ['fontname']],
                                ['color', ['color']],
                                ['para', ['ul', 'ol', 'paragraph']],
                                ['table', ['table']],
                                ['insert', ['link']],
                            ],
                            callbacks: {
                                onInit: function () {
                                    $('#txtComment' + $scope.entityId)
                                        .next()
                                        .find('.note-toolbar')
                                        .hide();
                                },
                                onFocus: function () {
                                    $('#txtComment' + $scope.entityId)
                                        .next()
                                        .find('.note-toolbar')
                                        .hide();
                                },
                                onBlur: function () {
                                    $('#txtComment' + $scope.entityId)
                                        .next()
                                        .find('.note-popover')
                                        .css('display', 'none');
                                    $scope.existUsers = [];
                                },
                                onImageUpload: function (image, editor, welEditable) {
                                    console.log('-------------');
                                    // if (!$scope.image_paste) {
                                    //     sparrow.uploadImage(image[0], '#txtComment' + $scope.entityId);
                                    // }
                                },
                                onPaste: function (e) {
                                    $('.note-editable').css('font-size', '15px');
                                    var clipboardData = e.originalEvent.clipboardData;
                                    var image_text = e.originalEvent.clipboardData.getData('text/html');
                                    var files = false;
                                    if (clipboardData && clipboardData.files && clipboardData.files.length) {
                                        var files = true;
                                        if(files == true){
                                            e.preventDefault();
                                        }
                                        // sparrow.uploadDailouge(clipboardData.files[0], '#txtComment' + $scope.entityId);
                                    }

                                    if (clipboardData && clipboardData.items && clipboardData.items.length) {
                                        // var item = clipboardData.items[0];
                                        var item = clipboardData.items[1];
                                        if (item && item.kind === 'file' && item.type.indexOf('image/') !== -1) {
                                            e.preventDefault();
                                        }
                                        var item1 = clipboardData.items[0];
                                        if (item1 && item1.kind === 'file' && item1.type.indexOf('image/') !== -1) {
                                            e.preventDefault();
                                        }
                                    }
                                    setTimeout(function () {
                                        if (image_text.includes('img') && files == false) {
                                            if (image_text.includes('src')) {
                                                // var remark = stripScripts($('#txtComment' + $scope.entityId).summernote('code'));
                                                $('#txtComment' + $scope.entityId).summernote('code', '');
                                            }
                                        }
                                        // } else {
                                        //     var remark = stripScripts($('#txtComment' + $scope.entityId).summernote('code'));
                                        //     console.log('remark', remark);
                                        //     $('#txtComment' + $scope.entityId).summernote('code', remark);
                                        // }
                                    }, 100);
                                },
                                onMediaDelete: function (target) {
                                    sparrow.deleteImage('<p>' + target[0].outerHTML + '</p>');
                                },
                                onKeydown: function (e) {
                                    $('.note-editable').css('font-size', '15px');
                                    if (e.which == 8) {
                                        var oldRemark = $('#txtComment' + $scope.entityId)
                                            .summernote('code')
                                            .trim();
                                        setTimeout(function () {
                                            var newRemark = $('#txtComment' + $scope.entityId)
                                                .summernote('code')
                                                .trim();
                                            tagExists = oldRemark.indexOf('<p>');
                                            if (tagExists > -1) {
                                                sparrow.getImageTag(oldRemark, newRemark);
                                            }
                                        }, 100);
                                    }
                                    if (event.ctrlKey && event.key === 'z') {
                                        if (sparrow.deletedImagesStr.length > 0) {
                                            removeImageFromNote(sparrow.deletedImagesStr.length, 0);
                                        }
                                    }
                                },
                            },
                            hint: {
                                match: /\B@(\w*)$/,
                                search: function (keyword, callback) {
                                    sparrow.post(
                                        '/base/get_all_user_list/',
                                        { keyword: keyword, existUsers: JSON.stringify($scope.existUsers) },
                                        false,
                                        function (data) {
                                            callback(data);
                                        },
                                        'json',
                                        'appMsg',
                                        undefined,
                                        undefined,
                                        undefined,
                                        { hideLoading: true }
                                    );
                                },
                                content: function (item) {
                                    var userSpan = $(item)[0];
                                    var userSpanContent = '<b style="color:#337ab7;">@' + $(userSpan).text() + '&nbsp;</b><span>&nbsp;</span>';
                                    $(userSpan).html(userSpanContent);
                                    $scope.existUsers.push(parseInt($(item).attr('ref')));
                                    return $(userSpan)[0];
                                },
                            },
                        });
                        if ($scope.appName == 'production' && $scope.modelName == 'PreDefineComment') {
                            $('div.note-editable').height(290);
                        }

                        $('body').on('click', 'div.mail-attachment i', function () {
                            for (var j = 0; j < $scope.files.length; j++) {
                                if ($(this).parent().text() == $scope.files[j].name) {
                                    var index = $scope.files.indexOf($scope.files[j]);
                                    $scope.files.splice(index, 1);
                                }
                            }
                            $('[name="' + $(this).parent().find('span').attr('data-attachment-name') + '"]').remove();
                            $(this).parent().remove();
                        });
                    }, 0);

                    if ($scope.entityId === '') {
                        $scope.comments = [];
                        return;
                    }

                    if ($scope.modelName == 'operator'){
                        var postData = {
                          app_name: $scope.appName,
                          model_name: $scope.modelName,
                          entity_id: $scope.entityId,
                          create_date: $scope.createDate,
                        };
                    }
                    else if ($scope.modelName == 'order'){
                        var postData = {
                          app_name: $scope.appName,
                          model_name: $scope.modelName,
                          entity_id: $scope.entityId,
                        };
                    }
                    else{
                        var postData = {
                            app_name: $scope.appName,
                            model_name: $scope.modelName,
                            entity_id: $scope.entityId,
                        };
                    }
                    sparrow.post('/base/get_remarks/', postData, false, function (data) {
                        $scope.updateCount(data.count);
                        $scope.comments = data.data;
                        $scope.allCommentData = $scope.comments;
                        $scope.user = data.user;
                        $scope.$digest();
                        if ($scope.appName == 'production' && $scope.modelName == 'PreDefineComment') {
                            $('.cmtButton').hide();
                            $('.addAttachmentButton').hide();
                        }
                        var ms = $('#id_remark_type').val();
                        var cs = $('#id_comment_type').magicSuggest();
                        if ($scope.remarkName != 'None' && $scope.remarkType != 'None' && ms) {
                            ms.setSelection([{ name: $scope.remarkName, id: $scope.remarkType }]);
                            cs.setSelection([{ name: $scope.remarkName, id: $scope.remarkType }]);
                        }
                        comment_type();
                        $('#id_remark_type').removeClass('read-only-mode');
                        $('#id_comment_type').removeClass('read-only-mode');
                        $('#id_remark_type .ms-trigger').show();
                        $('#id_comment_type .ms-trigger').show();
                        if ($scope.remarkName != 'None' && $scope.remarkType != 'None' && ms) {
                            ms.enable();
                            cs.enable();
                        }

                        var ms = $('#id_source_of_info').magicSuggest();
                        $('#id_source_of_info').removeClass('read-only-mode');
                        $('#id_source_of_info .ms-trigger').show();
                        ms.enable();

                        var ms = $('#id_scope').magicSuggest();
                        $('#id_scope').removeClass('read-only-mode');
                        $('#id_scope .ms-trigger').show();
                        ms.enable();
                    });

                    removeImageFromNote = function (imagesStrLength, counter) {
                        if (counter < imagesStrLength) {
                            setTimeout(function () {
                                var remark = $('#txtComment' + $scope.entityId)
                                    .summernote('code')
                                    .trim();
                                $('#txtComment' + $scope.entityId).summernote('code', remark.replace(sparrow.deletedImagesStr[counter], ''));
                                counter++;
                                removeImageFromNote(imagesStrLength, counter);
                            }, 100);
                        }
                    };
                    setAutoLookup('id_comment_type', '/b/lookups/remark_type/', '', false, false, false, null, 10, null, null, null, 'Remark type');
                    setAutoLookup('id_remark_type', '/b/lookups/remark_type/', '', false, false, false, null, 1, null, null, null, 'Remark type');
                    setAutoLookup('id_source_of_info', '/b/lookups/remark_source/', '', false, false, false, null, 1, null, null, null, 'Source of Information');
                    setAutoLookup('id_scope', '/b/lookups/remark_scope/', '', false, false, false, null, 10, null, null, null, 'Scope');
                    function comment_type() {
                        $scope.remarkTypeList = [];
                        var filteredData = [];
                        if ($('input[name = remark_type]').val() == undefined) {
                            $scope.remarkTypeList = [];
                        }
                        $('input[name = remark_type]').each(function (i, obj) {
                            if ($scope.remarkTypeList.includes(parseInt($(obj).val()))) {
                            } else {
                                $scope.remarkTypeList.push(parseInt($(obj).val()));
                            }
                        });
                        for (i = 0; i < $scope.allCommentData.length; i++) {
                            for (j = 0; j < $scope.remarkTypeList.length; j++) {
                                if ($scope.allCommentData[i]['remark_type_id'] == $scope.remarkTypeList[j]) {
                                    filteredData.push($scope.allCommentData[i]);
                                }
                            }
                        }
                        if ($scope.remarkTypeList.length == 0) {
                            $scope.comments = $scope.allCommentData;
                        } else {
                            $scope.comments = filteredData;
                        }
                        $scope.$apply(function () {
                            $scope.comments = $scope.remarkTypeList.length != 0 ? filteredData : $scope.allCommentData;
                        });
                    }

                    $('#id_comment_type').click(function () {
                        comment_type();
                    });

                    // By default $scope.displayScopeField will be "false" and this condition is used for hiding dropdowns in comments tab.
                    if ($scope.displayScopeField == 'false') {
                        $('.displayScopeField').hide();
                    }
                    $scope.$on('trigger-save-comment', function (event, args) {
                        var remark = $('#txtComment' + $scope.entityId)
                            .summernote('code')
                            .trim();
                        $scope.entityId = args['id'];
                        $scope.isPreDefineComment = true;
                        $scope.saveComment(remark);
                    });

                    $scope.saveComment = function (remark) {
                        if ($scope.isPreDefineComment == true) {
                            remark = remark;
                        } else {
                            remark = $('#txtComment' + $scope.entityId)
                                .summernote('code')
                                .trim();
                        }
                        var files = $scope.files;
                        if ((remark == '' || remark == '<p><br></p>') && files == '') {
                            sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please enter a required Remark.', 3);
                            return false;
                        }
                        if (files.length > 1) {
                            sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'You can upload only 1 documents at a time.', 3);
                            return false;
                        }
                        if (remark == '' || remark == "<p><br></p>" && files.length != 0 ) {
                            sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please enter a required Remark.', 3);
                            return false;
                        }
                        var mentionedUsers = [];
                        var mentionedUsersEles = $($.parseHTML(remark)).find('.usr-ref');
                        for (var i = 0; i < mentionedUsersEles.length; i++) {
                            mentionedUsers.push($(mentionedUsersEles[i]).attr('ref'));
                        }
                        var msRemarkType = $('#id_remark_type').magicSuggest();
                        var msSourceInfo = $('#id_source_of_info').magicSuggest();
                        var msScope = $('#id_scope').magicSuggest();
                        sourceInfoSelection = '';
                        remarkTypeSelection = '';
                        scopeSelection = [];
                        if (msRemarkType.getSelection().length > 0) {
                            remarkTypeSelection = msRemarkType.getSelection()[0]['id'];
                        }
                        if (msSourceInfo.getSelection().length > 0) {
                            sourceInfoSelection = msSourceInfo.getSelection()[0]['id'];
                        }
                        if (msScope.getSelection().length > 0) {
                            for (var i = 0; i < msScope.getSelection().length; i++) {
                                scopeSelection.push(msScope.getSelection()[i]['id']);
                            }
                        }
                        scopeSelection = scopeSelection.toString();

                        if (remarkTypeSelection == '' && $scope.appName == 'production') {
                            sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please select remark type.', 3);
                            return;
                        }
                        if (remarkTypeSelection == "") {
                            sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please select remark type.', 3);
                            return;
                        }
                        if(files != ""){
                            if(files[0].name.length > 150){
                                sparrow.showMessage( "appMsg", sparrow.MsgType.Error, "File name is too long.", 3);
                                return;
                            }
                        }

                        if ($scope.modelName == 'operator'){
                            var postData = {
                                app_name: $scope.appName,
                                model_name: $scope.modelName,
                                entity_id: $scope.entityId,
                                remark: remark,
                                remarkType: remarkTypeSelection,
                                sourceOfInfo: sourceInfoSelection,
                                scope: scopeSelection,
                                model_remark_field: $scope.modelRemarkField,
                                mentioned_in: $scope.mentionedIn,
                                mentionedUsers: mentionedUsers.join([(separator = ',')]),
                                fileCount: files.length,
                                prep_on: $scope.createDate + "-02",
                                create_date: $scope.createDate,
                            };
                        }
                        else if ($scope.modelName == 'order'){
                            var postData = {
                                app_name: $scope.appName,
                                model_name: $scope.modelName,
                                entity_id: $scope.entityId,
                                remark: remark,
                                remarkType: remarkTypeSelection,
                                sourceOfInfo: sourceInfoSelection,
                                scope: scopeSelection,
                                model_remark_field: $scope.modelRemarkField,
                                mentioned_in: $scope.mentionedIn,
                                mentionedUsers: mentionedUsers.join([(separator = ',')]),
                                fileCount: files.length,
                            };
                        }
                        else{
                            var postData = {
                                app_name: $scope.appName,
                                model_name: $scope.modelName,
                                entity_id: $scope.entityId,
                                remark: remark,
                                remarkType: remarkTypeSelection,
                                sourceOfInfo: sourceInfoSelection,
                                scope: scopeSelection,
                                model_remark_field: $scope.modelRemarkField,
                                mentioned_in: $scope.mentionedIn,
                                mentionedUsers: mentionedUsers.join([(separator = ',')]),
                                fileCount: files.length,
                            };
                        }
                        if (files && files.length != 0) {
                            for (var i = 0; i < files.length; i++) {
                                if (files[i].size > 5020000) {
                                    sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'File more than 5MB size is not allowed.', 3);
                                    return false;
                                }
                                postData['file' + i] = files[i];
                            }
                        }

                        $scope.cmtButtonText = 'Adding...';
                        $scope.cmtButtonDisable = true;

                        Upload.upload({
                            url: '/base/create_remark/',
                            data: postData,
                        }).then(
                            function (resp) {
                                $scope.cmtButtonText = 'Add remark';
                                $scope.cmtButtonDisable = false;
                                if (resp.data.code == 1) {
                                    $('#txtComment' + $scope.entityId).summernote('code', '');
                                    $scope.fileMaxCount = 0;
                                    $('.mail-attachment').remove();
                                    // var cs = $('#id_comment_type').magicSuggest();
                                    // cs.clear();
                                    $scope.allCommentData = resp.data.data;
                                    $scope.comments = resp.data.data;

                                    $scope.updateCount($scope.comments.length);
                                    $scope.files = [];

                                    $scope.existUsers = [];
                                    var ms = $('#id_remark_type').val();
                                    var cs = $('#id_comment_type').magicSuggest();
                                    if ($scope.remarkName != 'None' && $scope.remarkType != 'None' && ms) {
                                        ms.setSelection([{ name: $scope.remarkName, id: $scope.remarkType }]);
                                        cs.setSelection([{ name: $scope.remarkName, id: $scope.remarkType }]);
                                    }
                                    // comment_type();
                                    if ($scope.modelName == 'operator'){
                                        remark_id = $scope.remarkId;
                                        remark_name = $scope.remarkName;
                                        var remark_type = $("#id_remark_type").magicSuggest();
                                        remark_type.disable();
                                        remark_type.setSelection([ { name: remark_name, id: remark_id }, ])
                                    }
                                } else {
                                    sparrow.showMessage('appMsg', sparrow.MsgType.Error, resp.data.msg, 3);
                                }
                            },
                            function (resp) {
                                $scope.cmtButtonText = 'Add remark';
                                $scope.cmtButtonDisable = false;

                                $('#loading-image').hide();
                                sparrow.showMessage('appMsg', sparrow.MsgType.Error, resp.status, 3);
                            }
                        );
                        msRemarkType.clear();
                        msSourceInfo.clear();
                        msScope.clear();
                    };
                    $scope.deleteComment = function (commentId, entityId, modelName) {
                        sparrow.showConfirmDialog(ModalService, 'Are you sure you want to delete remark?', 'Delete remark', function (confirmAction) {
                            if (confirmAction) {
                                var postData = {
                                    app_name: $scope.appName,
                                    model_name: modelName,
                                    entity_id: entityId,
                                    model_remark_field: $scope.modelRemarkField,
                                    remark_id: commentId,
                                    mentioned_in: $scope.mentionedIn,
                                };
                                sparrow.post('/base/delete_remark/', postData, false, function () {
                                    for (var i = $scope.comments.length - 1; i >= 0; i--) {
                                        if ($scope.comments[i].id == commentId) {
                                            remark = $scope.comments[i]['remark'];
                                            $scope.comments.splice(i, 1);
                                            sparrow.deleteImage(remark);
                                            break;
                                        }
                                    }
                                    $scope.updateCount($scope.comments.length);
                                    $scope.$digest();
                                });
                            }
                        });
                    };
                    $scope.scopeShow = true;
                    $scope.editComment = function (id, remark, remark_type_id, remark_type, source, source_id, remark_scope, remark_scope_id, entity_id, content_model) {
                        perm_postData = {
                            id: id,
                        };
                        sparrow.post('/base/check_edit_remark_perm/', perm_postData, false, function (response) {
                            if (response['code'] == 1) {
                                $scope.content_model = content_model;
                                $scope.base_entity_id = entity_id;
                                $scope.remark_id = id;
                                $scope.update_remark = remark;
                                $('.icon-trash').hide();
                                $('.cmtButton').hide();
                                $('#close_remark' + $scope.remark_id).show();
                                $('#label_dynamic_remark_type' + $scope.remark_id).show();
                                $('#dynamic_remark_type' + $scope.remark_id).show();
                                $('#update_remark' + $scope.remark_id).show();
                                $('.dynamic_displayScopeField' + $scope.remark_id).show();
                                $('.comment_edit').hide();
                                $('#editRemark' + $scope.remark_id).summernote('code', remark);
                                $('.note-toolbar').css('display', 'none');
                                $('#remark_id_' + $scope.remark_id).hide();
                                $('#txtComment' + $scope.entityId).summernote('destroy');
                                $('#id_remark_type').hide();
                                $('#label_source_of_info').hide();
                                $('#id_source_of_info').hide();
                                $('#id_scope').hide();
                                $('#label_id_remark_type').hide();
                                $('#label_scope').hide();
                                $('.addAttachmentButton').hide();
                                setAutoLookup(
                                    'dynamic_remark_type' + $scope.remark_id,
                                    '/b/lookups/remark_type/',
                                    '',
                                    false,
                                    false,
                                    false,
                                    null,
                                    1,
                                    null,
                                    null,
                                    null,
                                    'Remark type'
                                );
                                setAutoLookup(
                                    'dynamic_source' + $scope.remark_id,
                                    '/b/lookups/remark_source/',
                                    '',
                                    false,
                                    false,
                                    false,
                                    null,
                                    1,
                                    null,
                                    null,
                                    null,
                                    'Source of Information'
                                );
                                setAutoLookup('dynamic_scope' + $scope.remark_id, '/b/lookups/remark_scope/', '', false, false, false, null, 1, null, null, null, 'Scope');
                                var scope_magic_suggest = $('#dynamic_scope' + $scope.remark_id).magicSuggest();
                                if (remark_scope_id != '') {
                                    scope_magic_suggest.setSelection([{ name: remark_scope, id: remark_scope_id }]);
                                }
                                var label_magic_suggest = $('#dynamic_source' + $scope.remark_id).magicSuggest();
                                if (source_id != '') {
                                    label_magic_suggest.setSelection([{ name: source, id: source_id }]);
                                }
                                var ms = $('#dynamic_remark_type' + $scope.remark_id).magicSuggest();
                                if ($scope.modelName == "operator") {
                                  ms.disable();
                                }
                                if (remark_type_id != '') {
                                    ms.setSelection([{ name: remark_type, id: remark_type_id }]);
                                }
                            } else {
                                sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'You do not have permission to perform this action.', 3);
                                return;
                            }
                        });
                    };

                    if ($scope.modelName == 'operator'){
                        remark_id = $scope.remarkId;
                        remark_name = $scope.remarkName;
                        var remark_type = $("#id_remark_type").magicSuggest();
                        remark_type.disable();
                        remark_type.setSelection([ { name: remark_name, id: remark_id }, ])
                    }

                    $scope.updateComment = function () {
                        var new_remark = $('#editRemark' + $scope.remark_id)
                            .summernote('code')
                            .trim();
                        sourceInfoSelection = '';
                        scopeInfoSelection = '';
                        remarkTypeSelection = '';
                        var msRemarkType = $('#dynamic_remark_type' + $scope.remark_id).magicSuggest();
                        if (new_remark == '' || new_remark == '<p><br></p>') {
                            sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please enter a required Remark.', 3);
                            return false;
                        }
                        if (msRemarkType.getSelection().length > 0) {
                            remarkTypeSelection = msRemarkType.getSelection()[0]['id'];
                        }
                        if (remarkTypeSelection == '' && $scope.appName == 'production') {
                            sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please select remark type.', 3);
                            return;
                        }
                        if (remarkTypeSelection == "") {
                            sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please select remark type.', 3);
                            return;
                        }
                        var label_magic_suggest = $('#dynamic_source' + $scope.remark_id).magicSuggest();
                        if (label_magic_suggest.getSelection().length > 0) {
                            sourceInfoSelection = label_magic_suggest.getSelection()[0]['id'];
                        }
                        var scope_magic_suggest = $('#dynamic_scope' + $scope.remark_id).magicSuggest();
                        if (scope_magic_suggest.getSelection().length > 0) {
                            scopeInfoSelection = scope_magic_suggest.getSelection()[0]['id'];
                        }
                        var postData = {
                            app_name: $scope.appName,
                            model_name: $scope.modelName,
                            id: $scope.remark_id,
                            remark: new_remark,
                            sourceInfoSelection: sourceInfoSelection,
                            scopeInfoSelection: scopeInfoSelection,
                            base_entity_id: $scope.base_entity_id,
                            content_model: $scope.content_model,
                            edit_remark_type_id: remarkTypeSelection,
                            create_date: $scope.createDate,
                        };
                        sparrow.post('/base/edit_remark/', postData, false, function (response) {
                            if (response['code'] == 1) {
                                sparrow.showMessage('appMsg', sparrow.MsgType.Success, 'Remark updated', 3);
                                $scope.$apply(function () {
                                    $scope.comments = response['data'];
                                    $('.cmtButton').show();
                                    $('#close_remark' + $scope.remark_id).hide();
                                    $('#update_remark' + $scope.remark_id).hide();
                                    var ms = $('#id_remark_type').val();
                                    // ms.setSelection([{ name: $scope.remarkName, id: $scope.remarkType }]);
                                    var label_magic_suggest = $('#id_source_of_info').magicSuggest();
                                    label_magic_suggest.clear();
                                    var scope_magic_suggest = $('#id_scope').magicSuggest();
                                    scope_magic_suggest.clear();
                                    $('#editRemark' + $scope.remark_id).summernote('code', '');
                                });
                            } else {
                                sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Something went wrong.', 3);
                            }
                        });
                        $('#remark_id_' + $scope.remark_id).show();
                        $('#txtComment' + $scope.entityId).summernote('code', '');
                        $('#label_dynamic_remark_type' + $scope.remark_id).hide();
                        $('#label_dynamic_source' + $scope.remark_id).hide();
                        $('#label_dynamic_scope' + $scope.remark_id).hide();
                        $('#dynamic_scope' + $scope.remark_id).hide();
                        $('#dynamic_remark_type' + $scope.remark_id).hide();
                        $('#dynamic_source' + $scope.remark_id).hide();
                        $('#id_remark_type').show();
                        $('#label_id_remark_type').show();
                        $('.addAttachmentButton').show();
                        $('.dynamic_displayScopeField' + $scope.remark_id).hide();
                        $('#txtComment' + $scope.entityId)
                            .next()
                            .find('.note-toolbar')
                            .hide();
                    };

                    $scope.closeRemark = function () {
                        $('.icon-trash').show();
                        $('#editRemark' + $scope.remark_id).summernote('code', '');
                        $('#editRemark' + $scope.remark_id).summernote('destroy');
                        $('.cmtButton').show();
                        $('#id_remark_type').show();
                        $('#close_remark' + $scope.remark_id).hide();
                        $('#update_remark' + $scope.remark_id).hide();
                        $('.comment_edit').show();

                        var ms = $('#id_remark_type').val();
                        // ms.setSelection([{ name: $scope.remarkName, id: $scope.remarkType }]);
                        var label_magic_suggest = $('#id_source_of_info').magicSuggest();
                        label_magic_suggest.clear();
                        var scope_magic_suggest = $('#id_scope').magicSuggest();
                        scope_magic_suggest.clear();
                        $('#remark_id_' + $scope.remark_id).show();
                        $('#txtComment' + $scope.entityId).summernote('code', '');
                        $('#label_dynamic_remark_type' + $scope.remark_id).hide();
                        // $('#label_dynamic_source' + $scope.remark_id).hide();
                        // $('#label_dynamic_scope' + $scope.remark_id).hide();
                        // $('#dynamic_scope' + $scope.remark_id).hide();
                        $('#dynamic_remark_type' + $scope.remark_id).hide();
                        // $('#dynamic_source' + $scope.remark_id).hide();
                        // $('#label_source_of_info').show();
                        // $('#id_source_of_info').show();
                        // $('#id_scope').show();
                        $('#label_id_remark_type').show();
                        // $('#label_scope').show();
                        $('.addAttachmentButton').show();
                        $('.dynamic_displayScopeField' + $scope.remark_id).hide();
                        $('#txtComment' + $scope.entityId)
                            .next()
                            .find('.note-toolbar')
                            .hide();
                    };
                },
                link: function (scope, elem, attrs, Upload) {
                    // scope.saveComment = function () {
                    //     if(scope.entityId === "") {
                    //         sparrow.showMessage("appMsg", sparrow.MsgType.Error, "Please create record before adding remark.", 10);
                    //         return
                    //     }

                    //     var remark = $('#txtComment'+scope.entityId).summernote('code');
                    //     var mentionedUsers = [];
                    //     var mentionedUsersEles = $(remark).find(".usr-ref");
                    //     for (var i=0; i < mentionedUsersEles.length; i++) {
                    //         mentionedUsers.push($(mentionedUsersEles[i]).attr('ref'));
                    //     }

                    //     var postData = {
                    //         app_name: scope.appName,
                    //         model_name: scope.modelName,
                    //         entity_id: scope.entityId,
                    //         model_remark_field: scope.modelRemarkField,
                    //         remark: remark,
                    //         mentioned_in : scope.mentionedIn,
                    //         mentionedUsers: mentionedUsers.join([separator = ','])
                    //     }

                    //     sparrow.post("/base/create_remark/", postData, false, function(data){
                    //         if(data.code == 0) {
                    //             sparrow.showMessage("appMsg", sparrow.MsgType.Error, data.msg, 10);
                    //             return;
                    //         }
                    //         $('#txtComment'+scope.entityId).summernote('code', '');
                    //         scope.fileMaxCount = 0;
                    //         $('.mail-attachment').remove();
                    //         scope.comments.push(data.data[0]);
                    //         scope.updateCount(scope.comments.length);
                    //         scope.existUsers = [];
                    //         scope.$digest();
                    //     });
                    // };

                    scope.updateCount = function (count) {
                        if ($('#' + scope.countId) != undefined) {
                            $('#' + scope.countId).hide();
                            if (count > 0) {
                                $('#' + scope.countId).text('(' + count + ')');
                                $('#' + scope.countId).show();
                            }
                        }
                    };
                },
                templateUrl: function (element, attr) {
                    return attr.templateUrl || 'angular-comments.html';
                },
            };
        });
})();

angular.module('angular-comments').run([
    '$templateCache',
    function ($templateCache) {
        'use strict';
        $templateCache.put(
          "angular-comments.html",
          '<div class="ang-comment">\
      <style>\
        .mail-attachment{\
          width: 450px;\
          padding-top:2px;\
          height: 24px;\
          background: #f5f5f5;\
          margin-bottom: 10px;\
          }\
        .mail-attachment span{\
          width: 400px;\
          vertical-align: sub;\
          display: inline-block;\
          padding-left: 5px;\
          color: #0000ff;\
          overflow: hidden;\
          white-space: nowrap;\
          text-overflow: ellipsis;\
          }\
        .mail-attachment i{\
          float: right;\
          margin-top: 7px;\
          margin-right: 5px;\
          cursor: pointer;\
        }\
        .cmtButton {\
            width:100px;\
        }\
        .comments-list{\
            margin-top:0px;\
        }\
        .comment-content{\
            white-space: pre-wrap !important; \
        }\
        .comment-dropdown{\
            width::240px;\
            max-width:247px;\
            float:left;\
            padding-left:5px\
        }\
        @media  screen and (max-width: 1920px) {\
            .pencil{\
                position:absolute;\
                margin-top: -3%;\
                right:0;\
            }\
             .note-editable{\
                   width:600px;\
               }\
        }\
       @media only screen and (min-device-width: 1500px) and (max-device-width: 1600px) {\
            .pencil{\
                position:absolute;\
                top:-6px;\
                right:0;\
            }\
              .note-editable{\
                   width:690px;\
               }\
        }\
      @media only screen and (min-device-width: 720px) and (max-device-width: 1366px) {\
            .note-editable{\
                   width:600px;\
               }\
            .pencil{\
                position:absolute;\
                top:-6px;\
                right:0;\
            }\
        }\
        @media only screen and (min-device-width: 2000px) and (max-device-width: 2560px) {\
            .note-editable{\
                   width:600px;\
               }\
            .pencil{\
                position:absolute;\
                top:13px ;\
                right:0;\
            }\
        }\
        @media only screen and (min-device-width: 3400px) and (max-device-width: 3840px) {\
            .pencil{\
                position:absolute;\
                top:-31px !important ;\
                right:0;\
            }\
        }\
      </style>\
      <div class="production_remark_dialogue" style="display: flex; justify-content: flex-end; align-items: center; grid-gap: 15px" hidden>\
        <label>Remark type:</label>\
        <div style="width:20%">\
                <input value="" id="id_comment_type" type="text" name="remark_type" style="height: auto;">\
            </div>\
        </div>\
        <div class="comments-container" style="">\
            <ul id="comments-list" class="comments-list" ng-style="comments.length == 0 && {\'display\':\'none\'}  || comments.length > 0 && {\'display\':\'block\'}">\
                <li ng-repeat="comment in comments">\
                    <div class="comment-main-level">\
                        <div class="comment-avatar"><img ng-if="comment.display_img" src="{{comment.display_img}}" onerror="this.src=\'/static/base/images/man.png\'" alt="{{comment.display_name}}">\
                            </div>\
                        <div class="comment-box">\
                            <div class="comment-head">\
                                <div class="col-md-12">\
                                    <div class="col-md-8">\
                                    <p hidden>{{comment.id}}</p>\
                                        <h6 class="comment-name semi-bold">{{comment.display_name}}</h6>\
                                        <h6 class="comment-name semi-bold" style="color:#283035;" ng-if = "comment.remark_type" >Type:</h6><span style="font-size:14px;color:black;padding-right:10px;margin-left:0px;margin-top:-1px;" ng-if = "comment.remark_type">{{ comment.remark_type }} </span>\
                                        <h6 class="comment-name semi-bold" style="color:#283035;" ng-if = "comment.remark_source"> Source:</h6><span style="font-size:14px;color:black;padding-right:10px;margin-left:0px;margin-top:-1px;" ng-if = "comment.remark_source">{{ comment.remark_source }} </span>\
                                        <h6 class="comment-name semi-bold" style="color:#283035;" ng-if = "comment.remark_scope && scopeShow">Scope:</h6><span style="font-size:14px;color:black;padding-right:10px;margin-left:0px;margin-top:-1px;" ng-if = "comment.remark_scope && scopeShow">{{ comment.remark_scope }}</span>\
                                        <h6 class="comment-name semi-bold" style="color:#283035;" ng-if = "comment.op_name" >Operation name:</h6><span style="font-size:14px;color:black;padding-right:10px;margin-left:0px;margin-top:-1px;" ng-if = "comment.op_name">{{ comment.op_name }} </span>\
                                    </div>\
                                    <div class="col-md-4" style="display:flex; align-items:center; justify-content:flex-end;padding-right:35px;margin-bottom:1rem">\
                                        <h6 class="comment-name" style="color:#a6a6a6;font-weight: 100;" ng-if = comment.content_model=="order">{{ comment.date }}</h6>\
                                        <h6 class="comment-name" style="color:#a6a6a6;font-weight: 100;" ng-if = comment.content_model=="operator">{{ comment.prep_on }}</h6>\
                                        <i ng-if = "user == comment.user_id" ng-click="deleteComment(comment.id,comment.entity_id,comment.content_model);" class="icon-trash" title="Delete remark" style="top:0;margin-left:5px !important;"></i>\
                                    </div>\
                                     <div class="col-md-12">\
                                        <i ng-click="editComment(comment.id, comment.remark, comment.remark_type_id, comment.remark_type, comment.remark_source, comment.remark_source_id, comment.remark_scope, comment.remark_scope_id, comment.entity_id, comment.content_model);" id="editRemark{{comment.id}}" class="icon-pencil-1 list-btn comment_edit pencil" title="Edit remark"></i>\
                                    </div>\
                                </div>\
                            </div>\
                            <div class="comment-content" id="remark_id_{{comment.id}}"  ng-bind-html="comment.remark | trusted">\
                            </div>\
                            <div>\
                                <div ng-repeat="attachment in comment.attachments" style="margin-top:7px;">\
                                    <span><i class="icon-paper-clip"></i></span>\
                                    <span style="margin-left:5px;">\
                                        <a href="/attachment/dwn_attachment/?uid={[{attachment.uid}]}&a=base&m=remark_attachment" target="_blank">{{attachment.name}}</a>                                        \
                                    </span>\
                                </div>\
                            </div>\
                        </div>\
                    </div>      \
                    <input style="display:none; margin-left:6rem;" type="button" class="btn btn-primary" id="update_remark{{comment.id}}" ng-click="updateComment();" value="Save" />\
                    <input style="display:none;" type="button" class="btn btn-secondary" id="close_remark{{comment.id}}" ng-click="closeRemark();" value="Close"/>\
                    </br>\
                    <div class="dynamic_displayScopeField{{comment.id}}" style="display:none;padding-bottom:15px; margin-left: 5.5rem;margin-top: 1rem;">\
                        <div class="container comment-dropdown" >\
                            <label style="display:none;" id="label_dynamic_remark_type{{comment.id}}" style="color:#c66c6c; margin-bottom:4px" >Remark type:</label>\
                            <input style="display:none;" class="form-control" id="dynamic_remark_type{{comment.id}}" name="remark" type="text" value="" style="height: auto;" />\
                        </div>\
                        <div class="container comment-dropdown">\
                        <label style="display:none;" for="id_country" id="label_dynamic_source{{comment.id}}" >Source of Information:</label>\
                            <input style="display:none;" class="form-control" id="dynamic_source{{comment.id}}" name="source" type="text" value="" style="height: auto;" />\
                        </div>\
                        <div class="container comment-dropdown">\
                            <label style="display:none;" for="id_country" id="label_dynamic_scope{{comment.id}}">Scope:</label>\
                        <input style="display:none;" class="form-control" id="dynamic_scope{{comment.id}}" name="scope" type="text" value="" style="height: auto;" />\
                        </div>\
                    </div>\
                </li>\
            </ul>\
        </div>\
        <p hidden cols="40" rows="5" class="form-control" id="txtComment{{entityId}}"></p>\
        <div id="attachmentList{{entityId}}"></div>\
        <div class="col-md-12 displayScopeField" style="padding-bottom:15px;width:250px">\
            <div class="container comment-dropdown" >\
                <label for="id_country" id="label_id_remark_type" style="color:#c66c6c; margin-bottom:4px" >Remark type:</label>\
                <input class="form-control" id="id_remark_type" name="remark" type="text" value="" style="height: auto;"/>\
            </div>\
            <div class="container comment-dropdown">\
            <label for="id_country" id="label_source_of_info" >Source of Information:</label>\
                <input class="form-control" id="id_source_of_info" name="source" type="text" value="" style="height: auto;" />\
            </div>\
            <div class="container comment-dropdown">\
                <label for="id_country" id="label_scope">Scope:</label>\
                <input class="form-control" id="id_scope" name="scope" type="text" value="" style="height: auto;" />\
            </div>\
        </div>\
        <div class="addAttachmentButton" >\
            <div  ngf-multiple="true" id="cmt-spnattach{{entityId}}" >\
                <span ngf-select="uploadDailouge($files)" style="cursor:pointer;color:#337ab7;">\
                    <i class="icon-paper-clip" style="font-size: 15px;"></i><span style="margin-left:5px;">Attach file</span>\
                </span>    \
            </div>   \
        </div>\
        <div style="margin-top: 5px;">\
            <input type="button" class="btn btn-primary cmtButton" ng-click="saveComment();" ng-disabled="cmtButtonDisable" value="{{cmtButtonText}}" />\
        </div>    \
    </div>'
        );
    },
]);
