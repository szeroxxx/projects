function firstDeliveriesInit(data) {
    sparrow.registerCtrl('firstDeliveriesCtrl', function (
        $scope,
        $rootScope,
        $route,
        $routeParams,
        $compile,
        $uibModal,
        DTOptionsBuilder,
        DTColumnBuilder,
        $templateCache,
        ModalService
    ) {
        $scope.modalopened = false;
        var config = {
            pageTitle: 'First deliveries',
            topActionbar: {
                extra: [
                    {
                        id: 'btnAddNewReport',
                        multiselect: false,
                        function: onAddNewReport,
                    },
                    {
                        id: 'btnEditProfile',
                        multiselect: false,
                        function: onbtnEditProfile,
                    },
                    {
                        id: 'btnIncludedSteam',
                        multiselect: false,
                        function: onIncludedSteam,
                    },
                ],
            },
            listing: [
                {
                    index: 1,
                    search: {
                        params: [
                            { key: 'Customer_name', name: 'Customer name' },
                            { key: 'delivery_num', name: 'Delivery number' },
                            { key: 'is_assembly_data', name: 'Is assembly', type: 'list', options: ['Yes', 'No'] },
                            { key: 'included_in_steam', name: 'Included in steam', type: 'list', options: ['Yes', 'No'] },
                            { key: 'delivery_date__date', name: 'Delivery from date till date', type: 'datePicker' },
                            { key: 'order_date__date', name: 'Order from date till date', type: 'datePicker' },
                            { key: 'planned_delivery_date__date', name: 'Planned delivery from date till date', type: 'datePicker' },
                            { key: 'country', name: 'Country'},

                        ],
                    },
                    url: '/sales/first_deliveries_search/',
                    crud: true,
                    scrollBody: true,
                    columns: [
                        { name: 'Customer_name', title: 'Customer name', sort: false },
                        {
                            name: 'Delivery_note_number',
                            title: 'Delivery note number',
                            renderWith: function (data, type, full, meta) {
                                return '<a ng-click="getDeliveryNote('+"'"+full.Delivery_note_number+"'"+')">'+full.Delivery_note_number+'</a>'
                            },
                        },
                        { name: 'Order_date', title: 'Order date', sort: false },
                        { name: 'Delivery_note_date', title: 'Delivery note date', sort: false },
                        { name: 'Planned_delivery_date', title: 'Planned delivery date', sort: false },
                        { name: 'Order_type', title: 'Order type', sort: false },
                        { name: 'country', title: 'Country', sort: false },
                        { name: 'Planned_delivery_date_incl_assembly', title: 'Planned delivery date include assembly', sort: false },
                        {
                            name: 'Included_in_steam',
                            title: 'Included in steam',
                            sort: false,
                            renderWith: function (data, type, full, meta) {
                                if (data == true) {
                                    return 'Yes';
                                } else {
                                    return 'No';
                                }
                            },
                        },
                    ],
                },
            ],
        };

        $scope.getDeliveryNote = function (deliveryNoteNumber){
            window.open("/sales/get_delivery_note/" + deliveryNoteNumber+'/',"_blank");
        }

        function getRowData() {
            var selectedId = $scope.getSelectedIds(1)[0];
            var rowData = $.grep($scope['dtInstance1'].DataTable.data(), function (n, i) {
                return n.id == selectedId;
            });
            return rowData[0];
        }

        function onAddNewReport() {
            if (data.permissions['can_add_first_deliveries_report']) {
                if ($scope.modalopened) return;
                $scope.onEditLink('/b/iframe_index/#/sales/survey_report/' + getRowData().id + '/0/true/FIRST_DELIVERY/', 'Report', closeSurveyReportCallback, true, 1);
                $scope.modalopened = true;
                resizeDialogue();
            } else {
                sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'You do not have permission to perform this action', 10);
            }
        }
        function closeSurveyReportCallback() {
            $scope.modalopened = false;
        }

        function onbtnEditProfile(scope) {
            var canAddReport = data.permissions['can_add_first_deliveries_report'];
            var canUpdateReport = data.permissions['can_update_first_deliveries_report'];
            if ($scope.modalopened) return;

            $scope.onEditLink(
                '/b/iframe_index/#/sales/customer/first_deliveries/' + getRowData().id + '/' + canAddReport + '/' + canUpdateReport + '/',
                'Customer profile - ' + getRowData().Customer_name,
                dialogCloseCallback,
                false,
                '+1+',
                true
            );
            $scope.modalopened = true;
        }

        function dialogCloseCallback() {
            $scope.modalopened = false;
        }

        function resizeDialogue() {
            var iFrameID = document.getElementById('iframe_model0');
            iFrameID.style.width = '60%';
            iFrameID.style.left = '20%';
            iFrameID.style.overflowY = 'hidden';
        }

        $('#app_container').on('change', '.magic-checkbox', function (e) {
            var val = $(this).is(':checked') ? 'checked' : 'unchecked';
            if (val == 'checked') {
                var selectedId = $scope.getSelectedIds(1)[0];
                var rowData = $.grep($scope['dtInstance' + 1].DataTable.data(), function (n, i) {
                    return n.id == selectedId;
                });
                if (rowData[0].Included_in_steam) {
                    $('#btnIncludedSteam').val('Excluded from steam');
                } else {
                    $('#btnIncludedSteam').val('Included in steam');
                }
            } else {
                $('#btnIncludedSteam').val('Included in steam');
            }
        });

        function onIncludedSteam() {
            if (getRowData().Included_in_steam == true) {
                included_steam = '0';
            } else {
                included_steam = '1';
            }
            var postData = {
                customer_id: getRowData().id,
                included_steam: included_steam,
            };
            if (getRowData().Included_in_steam) {
                sparrow.showConfirmDialog(ModalService, 'Are you sure you want to exclude selected customer from steam?', 'Exclude from steam', function (confirm) {
                    if (confirm) {
                        sparrow.post('/sales/update_included_steam/', postData, false, function (data) {
                            if (data.code == 1) {
                                $scope.reloadData(1);
                                $('#btnIncludedSteam').val('Included in steam');
                                sparrow.showMessage('appMsg', sparrow.MsgType.Success, 'Customer excluded from steam.', 10);
                            }
                        });
                    }
                });
            } else {
                sparrow.post('/sales/update_included_steam/', postData, false, function (data) {
                    if (data.code == 1) {
                        $scope.reloadData(1);
                        sparrow.showMessage('appMsg', sparrow.MsgType.Success, 'Customer included in steam.', 10);
                    }
                });
            }
        }

        function selectedRowLength() {
            if ($route.current.controller != 'firstDeliveriesCtrl') {
                return false;
            }
            if ($scope.getSelectedIds(1).length == 0 || $scope.getSelectedIds(1).length > 1) {
                sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please select one customer', 10);
                return false;
            }
            return true;
        }
        Mousetrap.bind('e p', function () {
            if (selectedRowLength() == true) {
                onbtnEditProfile();
            }
        });

        Mousetrap.bind('a r', function () {
            if (selectedRowLength() == true) {
                onAddNewReport();
            }
        });

        sparrow.setup($scope, $rootScope, $route, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, config, ModalService);
    });
}

firstDeliveriesInit();
