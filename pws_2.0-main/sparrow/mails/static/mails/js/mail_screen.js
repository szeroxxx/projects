/* eslint-disable no-multi-str */
sparrow.config([
    '$routeProvider',
    '$controllerProvider',
    function ($routeProvider, $controllerProvider) {
        sparrow.registerCtrl = $controllerProvider.register;

        var fileMaxCount = 0;

        sparrow.registerCtrl('MailScreenController', function (
            $scope,
            $route,
            $element,
            title,
            appName,
            model,
            attachments,
            entityId,
            mailSendURL,
            toEmails,
            cc_mails,
            emailTeplate,
            skipMailURL,
            orderType,
            callback,
        ) {
            $scope.title = title;
            $scope.appName = appName;
            $scope.model = model;
            $scope.entityId = entityId;
            $scope.attachments = attachments;
            $scope.mailSendURL = mailSendURL;
            $scope.toEmails = toEmails;
            $scope.cc_mails = cc_mails;
            $scope.emailTeplate = emailTeplate;
            $scope.skipMailURL = skipMailURL;
            $scope.btnText = 'Send';


            $scope.$applyAsync(function () {
                $("#id_label_attachment").hide();
                for (var i = 0; i < attachments.length; i++) {
                    if (attachments[i].upload_image) {
                     $("#id_label_attachment").show();
                     var imageicon =' <div class="attachments" style="width=100">\
                     <p>Exception file&emsp;&emsp;</p>\
                     <img src="/static/images/image.svg" alt="" width="60" height="60">\
                     <div class="form-group" id="upload_image">\
                     <div class="col-sm-4">\
                            <a onclick="downloadFile(\''+attachments[i].upload_image_uid+'\')">Download</a>\
                        </div>\
                        </div>\
                      </div>';
                     $('.mail-link-imageicon').append(imageicon);
                    }
                    if (attachments[i].si_file) {
                      $("#id_label_attachment").show();
                     var zip2icon ='<div class="attachments"  style="width=100">\
                      <p>SI file&emsp;&emsp;</p>\
                      <img src="/static/images/zip.svg" alt="" width="60" height="60">\
                      <div class="form-group" id="upload_image">\
                      <div class="col-sm-4">\
                            <a onclick="downloadFile(\''+attachments[i].si_file_uid+'\')" >Download</a>\
                        </div>\
                        </div>\
                      </div>';
                     $('.mail-link-zip2icon').append(zip2icon);
                    }
                    if (attachments[i].upload_image) {
                        $("#id_label_attachment").show();
                    }
                    if (attachments[i].si_file) {
                      $("#id_label_attachment").show();
                    }
                }
                // if (!($route.current.params['state'] == 'rfq' || $route.current.params['state'] == 'rfqpending')) {
                //     $('.mail-footer').append(
                //         '<a id="continue_without_mail" class="continue-without-mail" style="float: left;cursor:pointer;font-size:13px;margin-top: 10px;">Continue without mail</a>'
                //     );
                // }

                $('.mail-footer').off('click', '.continue-without-mail');
                $('.mail-footer').on('click', '.continue-without-mail', function () {
                    sparrow.post(
                        skipMailURL,
                        {
                            order_id: $scope.entityId,
                        },
                        false,
                        function (data) {
                            if (data.code == 1) {
                                $element.modal('hide');
                                $('.modal-backdrop').remove();

                                callback({
                                    sentMail: false,
                                });
                                // $route.reload();
                            } else {
                                sparrow.showMessage('appMsg', sparrow.MsgType.Error, data.msg, 10);
                            }
                        }
                    );
                });
            });


            $scope.cancel = function () {
                $element.modal('hide');
                $('.modal-backdrop').remove();
                fileMaxCount = 0;

                if (callback) {
                    callback();
                }
            };

            $scope.send = function () {
                var emails = $scope.toEmails
                var emails_cc = $scope.cc_mails

                if (emails != "" && emails != undefined){
                    var emails = emails.replace(/ /g, '')
                    var emails = emails.split(",")
                    var regex = /^([a-zA-Z0-9_.+-])+\@(([a-zA-Z0-9-])+\.)+([a-zA-Z0-9]{2,4})+$/;
                    for (let x in emails) {
                        var emails_ = regex.test(emails[x])
                        if (emails_ == false){
                        $('#id_message').show()
                        $('#toUser').css('border-color', '#a94442');
                        return;
                        }
                    }
                }
                if (emails_cc != "" && emails_cc != undefined){
                    var emails_cc_ = emails_cc.replace(/ /g, '')
                    var emails_cc_1 = emails_cc_.split(",")
                    var regex = /^([a-zA-Z0-9_.+-])+\@(([a-zA-Z0-9-])+\.)+([a-zA-Z0-9]{2,4})+$/;
                    for (let x in emails_cc_1) {
                        var emails_cc_2 = regex.test(emails_cc_1[x])
                        if (emails_cc_2 == false){
                        $('#id_message_cc').show()
                        $('#ccUser').css('border-color', '#a94442');
                        return;
                        }
                    }
                }
                if (
                    /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+/.test($scope.cc_mails) ||
                    $scope.cc_mails == '' || $scope.cc_mails == null ||
                    /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test($scope.cc_mails)
                ) {
                    sparrow.postForm(
                        {
                            counter: fileMaxCount,
                            order_id: entityId,
                            toUser: $scope.toEmails,
                            ccUser: $scope.cc_mails,
                        },
                        $('#frmSendMail'),
                        $scope,
                        function (data) {
                            if (data.code == 1) {
                                $element.modal('hide');
                                $('.modal-backdrop').remove();
                                sparrow.showMessage('appMsg', sparrow.MsgType.Success, data.msg, 10);
                                fileMaxCount = 0;
                                $route.reload();
                                callback({
                                    sentMail: true,
                                });
                            } else {
                                sparrow.showMessage('appMsg', sparrow.MsgType.Error, data.msg, 10);
                            }
                        },
                        'appMsg'
                    );
                } else {
                    sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please Enter a valid Email Address ', 10);
                }
            };
            // $('body').on('change','[name="attachment"]',function(event){
            //     if($('[name="attachment"]').val()!=''){
            //         var currentValue = $('[name="attachment"]')[0].files[0].name;
            //         // var ext = currentValue.split('.').pop();
            //         // var extensionList = ['xls','txt','xlsx','zip','rar','pdf','jpg','jpeg','png',]
            //         // if(ext == '' || extensionList.indexOf() == -1)
            //         fileMaxCount = parseInt(fileMaxCount) + 1;
            //         $('#attachmentList').prepend('<div class="mail-attachment"><span data-attachment-name=
            // "attachment'+fileMaxCount+'"">'+currentValue+'</span><i class="icon-close"></i></div>');
            //         $('[name="attachment"]').css('display','none').attr('name','attachment'+fileMaxCount);
            //         $('#fileUploadParent').append('<input class="form-control" name="attachment" type="file">');
            //     }
            // });

            $('body').off('change', '[name="attachment"]');
            $('body').on('change', '[name="attachment"]', function (event) {
                if ($('[name="attachment"]').val() != '') {
                    var currentValue = $('[name="attachment"]')[0].files[0].name;
                    // var ext = currentValue.split('.').pop();
                    // var extensionList = ['xls','txt','xlsx','zip','rar','pdf','jpg','jpeg','png',]
                    // if(ext == '' || extensionList.indexOf() == -1)
                    fileMaxCount = parseInt(fileMaxCount) + 1;
                    $('#attachmentList').prepend(
                        '<div class="mail-attachment"><span data-attachment-name="attachment' + fileMaxCount + '"">' + currentValue + '</span><i class="icon-close"></i></div>'
                    );
                    $('[name="attachment"]')
                        .css('display', 'none')
                        .attr('name', 'attachment' + fileMaxCount);
                    $('#fileUploadParent').append('<input class="form-control" name="attachment" type="file">');
                }
            });

            $('body').off('click', 'div.mail-attachment i');
            $('body').on('click', 'div.mail-attachment i', function () {
                $('[name="' + $(this).parent().find('span').attr('data-attachment-name') + '"]').remove();
                $(this).parent().remove();
            });

            if (orderType == 'order') {
                $scope.btnText = 'Send confirmation';
            }
        });
    },
]);
