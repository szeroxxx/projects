function holidaysInit(data) {
    var holidays = {};

    sparrow.registerCtrl('holidaysCtrl', function ($scope, $rootScope, $route, $routeParams, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, ModalService) {
        var title = 'Holidays';
        config = {
            pageTitle: title,
            topActionbar: {
                delete: {
                    url: '/hrm/holidays_del/',
                },
                extra: [
                    {
                        id: 'btnImport',
                        function: importHolidays,
                        noselect: true,
                    },
                    {
                        id: 'btnExport',
                        function: onExport,
                        noselect: true,
                    },
                    {
                        id: 'btnAddHoliday',
                        function: addHoliday,
                    },
                    {
                        id: 'btnEditLeaveType',
                        function: function () {
                            var selectedId = $scope.getSelectedIds(1).join([(separator = ',')]);
                            $scope.oneditLeaveType(selectedId);
                        },
                    },
                ],
            },
            listing: [
                {
                    index: 1,
                    search: {
                        params: [
                            {
                                key: 'name__icontains',
                                name: 'Name',
                            },
                        ],
                    },
                    url: '/hrm/holidays_search/',
                    crud: true,
                    scrollBody: true,
                    columns: [
                        {
                            name: 'name',
                            title: 'Name',
                            renderWith: function (data, type, full) {
                                return '<span class="a-link" ng-click="oneditLeaveType(' + full.id + ')">' + data + '</span>';
                            },
                        },

                        {
                            name: 'holiday_on',
                            title: 'Holiday on',
                            sort: false,
                        },
                    ],
                },
            ],
        };
        var selectedHolidayId = 0;

        function addHoliday() {
            selectedHolidayId = 0;
            $('#myModalLabel').text('Add holiday');
            $('#id_name').val('');
            $('#id_holiday_date').val('');
            $('#id_reoccurring').prop('checked', false);
            $('#holidayModel').modal('show');
        }

        $scope.oneditLeaveType = function (leaveTypeId) {
            selectedHolidayId = leaveTypeId;
            $('#myModalLabel').text('Edit holiday');
            sparrow.post(
                '/hrm/get_holiday/',
                {
                    id: leaveTypeId,
                },
                false,
                function (data) {
                    $('#id_name').val(data.holiday_type_data.name);
                    $('#id_holiday_date').val(data.holiday_on);
                    if (data.reoccurring == true) {
                        $('#id_reoccurring').prop('checked', true);
                    } else {
                        $('#id_reoccurring').prop('checked', false);
                    }
                    $('#holidayModel').modal('show');
                }
            );
        };

        $scope.saveHolidayForm = function (event) {
            event.preventDefault();
            var name = $('#id_name').val();
            var holiday = $('#id_holiday_date').val().split('/');
            var day = holiday[0];
            var month = holiday[1];
            var year = holiday[2];
            var current_year = new Date().getFullYear();
            if ($('#id_reoccurring').is(':checked')) {
                year = '';
            }
            var postData = {
                id: selectedHolidayId,
                name: name,
                holiday_day: day,
                holiday_month: month,
                holiday_year: year,
            };

            if ((year == '' || parseInt(year) == current_year) && day != '' && month != '' && name != '') {
                var holiday_date = current_year + '-' + month + '-' + day;
                sparrow.post(
                    '/hrm/check_working_day/',
                    {
                        holiday_date: holiday_date,
                    },
                    false,
                    function (data) {
                        if (data.code == 1) {
                            sparrow.showConfirmDialog(
                                ModalService,
                                holiday_date + ' day is working day, Are you sure you want to add Holiday for this date?',
                                'Working holiday',
                                function (confirm) {
                                    if (confirm) {
                                        postData['holiday_date'] = holiday_date;
                                        holidaySave(postData);
                                    }
                                }
                            );
                        } else if (data.code == 2) {
                            holidaySave(postData);
                        }
                    }
                );
            } else {
                holidaySave(postData);
            }
        };

        function holidaySave(postData) {
            sparrow.postForm(postData, $('#holidayForm'), $scope, function (data) {
                if (data.code == 1) {
                    $('#holidayModel').modal('hide');
                    $scope.reloadData(1);
                }
            });
        }

        function importHolidays(rootScope) {
            if (data.permissions['can_import_holidays'] == true) {
                var staticUrl = sparrow.getStaticUrl();
                sparrow.showImportDialog(
                    ModalService,
                    'holiday',
                    'Import holiday',
                    '/hrm/import_holiday/',
                    "(Please select csv, xls or xlsx only.Sample template is available <a href='" + staticUrl + "base/sampletemplates/Holidays.xls'>here</a>)",
                    null,
                    refreshHolidayList
                );
            } else {
                sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'You do not have permission to perform this action', 10);
                return;
            }
        }

        function onExport(rootScope) {
            if (data.permissions['can_export_holidays'] == true) {
                var selectedIds = $scope.getSelectedIds(1).join([(separator = ',')]);
                if (!selectedIds) {
                    selectedIds = 0;
                }
                if (selectedIds == 0) {
                    sparrow.showConfirmDialog(ModalService, 'All records will be exported, are you sure?', 'Export Holidays', function (confirm) {
                        if (confirm) {
                            $('#btnExport').closest('div').removeClass('open');
                            sparrow.downloadData('/hrm/export_holiday/', {
                                ids: selectedIds,
                            });
                        } else {
                            return true;
                        }
                    });
                } else {
                    $('#btnExport').closest('div').removeClass('open');
                    sparrow.downloadData('/hrm/export_holiday/', {
                        ids: selectedIds,
                    });
                }
            } else {
                sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'You do not have permission to perform this action', 10);
                return;
            }
        }

        function refreshHolidayList() {
            $scope.reloadData(1);
        }

        sparrow.setup($scope, $rootScope, $route, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, config, ModalService);
    });

    return holidays;
}

holidays = holidaysInit();
