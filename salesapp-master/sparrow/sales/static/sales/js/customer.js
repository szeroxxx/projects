function customerInit(customer) {
    sparrow.registerCtrl('customerCtrl', function ($scope, $rootScope, $route, $routeParams, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, ModalService) {
        $scope.addViewButtons('');
        sparrow.applyReadOnlyMode('#frmCompany');
        $("#idsaveMasterData").hide();
        $('#idsaveAddress').hide();
        $('#idsaveUser').hide();
        newReportType = "CUST_SURVEY"

        if ($routeParams.edit_customer_from == 'first_deliveries'){
            newReportType = "FIRST_DELIVERY"
        }
        // disabled="disabled"
        $scope.preCmpnyStats = customer.previous_status
        $scope.StatusIdFinal = customer.previous_status
        $scope.isSalesReview = customer.is_sales_review

        var edit_profile = false;
        var finance_role = false;
        var admin_role = false;
        for (var i = 0; i < customer.roles.length; i++) {
            if (customer.roles[i] == 'finance') {
                finance_role = true;
            }
            if (customer.roles[i] == 'admin') {
                admin_role = true;
            }
        }
        var canAddReport = customer.report_permisions['can_add_report'];
        var canUpdateReport = customer.report_permisions['can_update_report'];

        if (
            customer.permissions['can_edit_profile_orders'] ||
            customer.permissions['can_edit_profile_customers'] ||
            customer.permissions['can_edit_new_customers_profile'] ||
            customer.permissions['can_edit_profile_invoice'] ||
            customer.permissions['can_edit_profile_proforma_invoice'] ||
            customer.permissions['can_edit_profile_payment_browser'] ||
            customer.permissions['can_edit_first_deliveries_profile']
        ) {
            edit_profile = true;
            if (finance_role || admin_role) {
                $('.is_edit').removeClass('read-only-mode');
                $('.is_edit').removeAttr('disabled');
            }
            $("#idsaveMasterData").show();
            $('#idsaveAddress').show();
            $('#idsaveUser').show();
            $('.checkbox_two').removeAttr('disabled');
        }
        if ($scope.isSalesReview == 'True') {
            $('.salesReviewEnable').removeClass('read-only-mode');
            $('.salesReviewEnable').removeAttr('disabled');
        }


        $scope.formFields = [];

        $('.chkbx').change(function () {
            if ($(this).prop('checked') == true) {
                $('.chkbx').prop('checked', false);
                $(this).prop('checked', true);
            }
        });

        var title = angular.element('#id_name').val();
        var config = {
            pageTitle: 'Company profile -' + title,
            listing: [
                {
                    url: '/sales/customer_addresses/' + customer.companyId + '/',
                    paging: false,
                    crud: false,
                    columns: [
                        { name: 'ContactName', title: 'Contact name', sort: false },
                        { name: 'AddressName', title: 'Address name', sort: false },
                        { name: 'AddressType', title: 'Address type', sort: false },
                        { name: 'Address', title: 'Address', sort: false },
                        { name: 'IsPrimaryAddress', title: 'Is primary address', sort: false },
                        { name: 'Telephone', title: 'Telephone', sort: false },
                        { name: 'Email', title: 'Email', sort: false },
                    ],
                    inlineCrud: {
                        edit: {
                            callback: onAddresslineEdit,
                        },
                    },
                    index: 1,
                },
                {
                    url: '/sales/customer_users/' + customer.companyId + '/',
                    paging: false,
                    crud: false,
                    columns: [
                        { name: 'UserName', title: 'User name', sort: false },
                        { name: 'FirstName', title: 'First name', sort: false },
                        { name: 'LastName', title: 'Last name', sort: false },
                        { name: 'Status', title: 'Status', sort: false },
                        { name: 'Responsibility', title: 'Responsibility', sort: false },
                    ],
                    inlineCrud: {
                        edit: {
                            callback: onUserEdit,
                        },
                    },
                    index: 2,
                },
                {
                    url: '/sales/get_call_reports/' + customer.companyId + '/',
                    paging: false,
                    crud: false,
                    columns: [
                        {
                            name: 'Report_name',
                            title: 'Report name',
                            sort: false,
                            renderWith: function (data, type, full, meta) {

                                return (
                                    '<a title="View call report" ng-click="onSurveyReport(' +
                                    full.relation_id +
                                    ",'" +
                                    full.Report_name +
                                    "','" +
                                    full.report_type +
                                    "','" +
                                    full.Created_by +
                                    '\')">' +
                                    full.Report_name +
                                    '</a>'
                                );
                            },
                        },
                        { name: 'Created_by', title: 'Created by', sort: false },
                        { name: 'Created_on', title: 'Created on', sort: false },
                        {
                            name: 'relation_id',
                            title: '',
                            sort: false,
                            renderWith: function (data, type, full, meta) {
                                return (
                                    '<a class="icon-pencil-1 list-btn" title="Modify call report" ng-click="onSurveyReport(' +
                                    full.relation_id +
                                    ",'" +
                                    full.Report_name +
                                    "','" +
                                    full.report_type +
                                    "','" +
                                    full.Created_by +
                                    '\')"></a>'
                                );
                            },
                        },
                    ],
                    index: 3,
                },
            ],
        };

        // if(customer.permissions.can_update_address) {
        //     config.listing[0]["inlineCrud"] = {
        //         edit: {
        //             callback: onAddresslineEdit
        //         }
        //     }
        // }
        // if(customer.permissions.can_update_user) {
        //     config.listing[1]["inlineCrud"] = {
        //         edit: {
        //             callback: onUserEdit
        //         }
        //     }
        // }

        $scope.model = {
            name: 'Tabs',
        };

        function getRelativeTime() {
            $scope.all_times = [];
            $scope.all_times.push({ id: 'idLastLogin', value: $('#idLastLogin').val() });
            $scope.all_times.push({ id: 'idLastUploaded', value: $('#idLastUploaded').val() });
            $scope.all_times.push({ id: 'idLastPcbCalculated', value: $('#idLastPcbCalculated').val() });
            $scope.all_times.push({ id: 'idLastBasketSave', value: $('#idLastBasketSave').val() });

            for (i in $scope.all_times) {
                var dateString = $scope.all_times[i].value;
                var idInput = $scope.all_times[i].id;
                if (dateString == null || dateString == '' || dateString == 'None') {
                    relativeTime = '';
                } else {
                    newDateString = dateString.split(' ')[0].split('/');
                    timeString = dateString.split(' ')[1];
                    newTimeString = timeString.split(':');
                    hh = newTimeString[0];
                    mm = newTimeString[1];
                    if (dateString.split(' ')[2] == 'PM') {
                        hh = parseInt(hh) + 12;
                    }
                    date = new Date(newDateString[2], newDateString[1] - 1, newDateString[0], hh, mm);
                    relativeTime = moment(date).fromNow();
                }
                relativeTime = relativeTime.replace('a ','1 ')
                relativeTime = relativeTime.replace('an ','1 ')
                $('#' + idInput).val(relativeTime);
            }
        }

        getRelativeTime();

        $scope.saveCompany = function (event) {
            event.preventDefault();
            var time_zone = $('#time_zone').magicSuggest();
            var selection = time_zone.getSelection()[0];
            var postData = {};
            if (selection) {
                postData['time_zone_now'] = selection.name;
            }
            sparrow.postForm(postData, $('#frmCompany'), $scope, setCompany);
        };

        function setCompany(data) {
            if (data.code == 1) {
                location.reload();
            }
        }

        var addressIdForUpdate = 0;
        function onAddresslineEdit(rowData) {
            sparrow.post(
                '/sales/get_customer_address/',
                { address_id: rowData.id, customer_id: customer.companyId },
                false,
                function (data) {
                    addressIdForUpdate = rowData.id;
                    $('#custAddressform').html(data);
                    var addressTitle = rowData.ContactName != null ? rowData.AddressType + ' - ' + rowData.ContactName : rowData.AddressType;
                    $('#addressModelTitle').text(addressTitle);
                    if (edit_profile != true) {
                        $('#id_add_form').attr('disabled', 'disabled');
                    }

                    $('#customerAddressModel').modal('show');
                },
                'html'
            );
        }

        $scope.saveAddress = function (event) {
            event.preventDefault();
            var postData = {
                CompanyId: customer.companyId,
                AddressId: addressIdForUpdate,
            };

            var address_type = $('#id_addtype').text().toLowerCase();
            if (finance_role && address_type != 'invoice address') {
                sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'User with Finance role can only update Invoice address.', 10);
                return;
            }

            sparrow.postForm(
                postData,
                $('#frmAddress'),
                $scope,
                function (data) {
                    if (data.code == 1) {
                        $('#customerAddressModel').modal('hide');
                        $scope.reloadData(1);
                    }
                },
                'appMsg'
            );
        };

        var userIdForUpdate = 0;
        function onUserEdit(rowData) {
            sparrow.post(
                '/sales/get_cust_user_view/',
                { user_id: rowData.id, customer_id: customer.companyId },
                false,
                function (data) {
                    userIdForUpdate = rowData.id;
                    $('#custUserform').html(data);
                    $('#userModelTitle').text('Edit user - ' + rowData.UserName + '');
                    if (edit_profile != true) {
                        $('#id_useredit_form').attr('disabled', 'disabled');
                    }
                    $('#customerUserModel').modal('show');
                },
                'html'
            );
        }

        // var iFrameID = parent.document.getElementById('iframe_model0');
        // iFrameID.style.paddingLeft = '0px'

        $scope.saveUser = function (event) {
            event.preventDefault();
            var checkboxes = $('input[name="selected"]:checked'),
                values = [];
            Array.prototype.forEach.call(checkboxes, function (el) {
                values.push(el.id);
            });
            var postData = {
                user_responsibilities: values,
                CompanyId: customer.companyId,
                UserId: userIdForUpdate,
            };
            sparrow.postForm(
                postData,
                $('#frmUser'),
                $scope,
                function (data) {
                    if (data.code == 1) {
                        $('#customerUserModel').modal('hide');
                        $scope.reloadData(2);
                    }
                },
                'appMsg'
            );
        };

        $scope.remarkText = ''
        $scope.saveCompanyStatusRemark = function(){
            statusId = $('#idStatus').find(':selected').val()
            $scope.remarkText = $("#remarkCompanyStatus").val()
            if ($scope.remarkText.trim() =="" || $scope.remarkText ==  undefined){
                $("#errorMsg").show()
                return
            }
            $scope.StatusIdFinal = $('#idStatus').find(':selected').val()
            $("#addRemarkOnStatusChangeModal").modal('hide')
            $scope.saveMasterData()
        }

        // To send old data to ecc team so they can manage history
        $scope.OldIsExcludeVat = $('#id_vat_exampt').val();
        $scope.OldAccountManagerId = $('#id_acc_manager').val();
        $scope.OldTransportCompanyCode = $('#id_def_transport').val();
        $scope.OldInvoiceLangId = $('#id_invoice_lang').val();
        $scope.OldInvoiceDelivery = $('#id_invoice_delivery').val();

        $scope.saveMasterData = function (event) {
            var competence = $('input[name="competence"]:checked'),
                competence_values = [];
            Array.prototype.forEach.call(competence, function (el) {
                competence_values.push(el.id);
            });
            var ec_customer_check = $('input[name="ec_customer_check"]:checked'),
                ec_cus_values = [];
            Array.prototype.forEach.call(ec_customer_check, function (el) {
                ec_cus_values.push(el.id);
            });


            statusId = $('#idStatus').find(':selected').val()
            TaxNumberTypeId = $('#idVatNr').find(':selected').val()
            VatNo = $("#idVatNrText").val().replaceAll("'",'"')

            if(String(statusId) != $scope.preCmpnyStats && $scope.remarkText == '' ){
                $("#addRemarkOnStatusChangeModal").modal('show')
                $("#remarkCompanyStatus").val('')
                $("#errorMsg").hide()
                return
            }


           

            $scope.remarkText = $scope.remarkText.replaceAll("'",'"')
            if ($('input[id=idOtherAccount]:checked').val() == undefined) {
                OtherTypeId = 0;
            } else {
                OtherTypeId = $('input[id=idOtherAccount]:checked').val();
            }

            postData = {
                competence: JSON.stringify(competence_values),
                ec_customer_check: JSON.stringify(ec_cus_values),
                CompanyId: customer.companyId,
                user_details: JSON.stringify({
                    IsExcludeVat: $('#id_vat_exampt').prop('checked'),
                    AccountManagerId: $('#id_acc_manager').val(),
                    TransportCompanyCode: $('#id_def_transport').val(),
                    InvoiceLangId: $('#id_invoice_lang').val(),
                    InvoiceDelivery: $('#id_invoice_delivery').val(),
                    OldIsExcludeVat: $scope.OldIsExcludeVat,
                    OldAccountManagerId: $scope.OldAccountManagerId,
                    OldTransportCompanyCode: $scope.OldTransportCompanyCode,
                    OldInvoiceLangId: $scope.OldInvoiceLangId,
                    OldInvoiceDelivery: $scope.OldInvoiceDelivery,
                    OtherTypeId: OtherTypeId,
                    TypeId: $('#idAccType').find(':selected').val(),
                    HandlingCompanyId: $('#idHandlingcompany').find(':selected').val(),
                    CompanyStatusRemark: $scope.remarkText,
                    CompanyStatusId: $scope.StatusIdFinal,
                    TaxNumberTypeId: TaxNumberTypeId,
                    VatNo: VatNo,
                    VATExistsConfirmation: false
                }),
            };

            sparrow.post('/sales/save_customer_data/', postData, false, function (data) {
                if (data.code == 1) {
                    sparrow.showMessage('appMsg', sparrow.MsgType.Success, "Saved", 10);
                    $route.reload()
                }
                if (data.code == '2') {
                    if (data.messageType == "VAT_EXISTS_CONFIRMATION"){
                        sparrow.showConfirmDialog(ModalService, data.message, "Warning", function(confirm) {
                        if(confirm) {
                            postData["user_details"] = JSON.parse(postData["user_details"])
                            postData["user_details"].VATExistsConfirmation = true
                            postData["user_details"] = JSON.stringify(postData["user_details"])
                            sparrow.post('/sales/save_customer_data/', postData, false, function (data) {
                            if (data.code == 1) {
                                sparrow.showMessage('appMsg', sparrow.MsgType.Success, "Saved", 10);
                                $route.reload()
                            }
                            if (data.code == '2') {
                               sparrow.showMessage('appMsg', sparrow.MsgType.Error, data.message, 10);
                              return;
                            }
                        });              
                        }
                      });
                    }else{
                       sparrow.showMessage('appMsg', sparrow.MsgType.Error, data.message, 10);
                      return;
                    }
                }
                if(data.code == 0){
                    sparrow.showMessage('appMsg', sparrow.MsgType.Error, data.message, 10);
                    return
                }
            });
        };

        $('#frmCompany').off('change', '#company_img_change');
        $('#frmCompany').on('change', '#company_img_change', function (e) {
            sparrow.setImagePreview(this, 'company_img');
        });

        function clodeSurveyReportCallback() {
            $scope.reloadData(3);
            parent.document.getElementById('iframe_model0').style.pointerEvents = 'auto'

        }

        window.addEventListener('resize', function () {
            var iFrameID = parent.document.getElementById('iframe_model1');
            if (iFrameID) {
                iFrameID.style.overflowY = 'auto';
            }
        });

        $scope.onSurveyReport = function (relationID, reportName, report_type,createdBy) {
            if (relationID == undefined) {
                relationID = 0;
                if (canAddReport == 'true') {
                    $scope.onEditLink('/b/iframe_index/#/sales/survey_report/' + customer.companyId + '/' + relationID + '/true/'+newReportType+'/', 'Report', clodeSurveyReportCallback, true, 1);
                    resizeDialogue();
                } else {
                    sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'You do not have permission to perform this action', 10);
                    return;
                }
            } else {
                $scope.onEditLink(
                    '/b/iframe_index/#/sales/survey_report/' + customer.companyId + '/' + relationID + '/' + canUpdateReport + '/'+report_type+'/',
                    'Report',
                    clodeSurveyReportCallback,
                    true,
                    1
                );
                resizeDialogue();
            }
        };

        function resizeDialogue() {
            var iFrameID = parent.document.getElementById('iframe_model1');
            iFrameID.style.width = '60%';
            iFrameID.style.left = '20%';
            iFrameID.style.overflowY = 'hidden';
            parent.document.getElementById('iframe_model0').style.pointerEvents = 'none'
        }

        sparrow.setup($scope, $rootScope, $route, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, config, ModalService);
    });
}
