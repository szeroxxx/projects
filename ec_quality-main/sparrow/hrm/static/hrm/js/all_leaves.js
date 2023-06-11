function allLeavesInit() {
    var all_leaves = {};
    sparrow.registerCtrl('allLeavesCtrl', function ($scope, $rootScope, $route, $routeParams, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, ModalService) {
        $scope.leaves = [];
        var isList = true;
        var config = {
            pageTitle: 'All leaves',
            topActionbar: {
                extra: [
                    {
                        id: 'leaveapprove',
                        function: approveLeave,
                        multiselect: true,
                    },
                    {
                        id: 'deleteleave',
                        function: deleteLeave,
                        multiselect: true,
                    },
                    {
                        id: 'rejectleave',
                        function: rejectLeave,
                        multiselect: true,
                    },
                    {
                        id: 'leaveadd',
                        function: addLeave,
                    },
                    {
                        id: 'btnAllLeaveListView',
                        function: showAllLeavesListView,
                    },
                    {
                        id: 'btnAllLeaveCalendarView',
                        function: showAllLeavesCalendar,
                    },
                    {
                        id: 'btnAllLeavesHistory',
                        multiselect: false,
                        function: showLog,
                    },
                ],
            },
            listing: [
                {
                    index: 1,
                    search: {
                        params: [
                            {
                                key: 'worker__name__icontains',
                                name: 'Employee',
                            },
                            {
                                key: 'start_date__date',
                                name: 'Leave from',
                                type: 'datePicker',
                            },
                            {
                                key: 'end_date__date',
                                name: 'Leave to',
                                type: 'datePicker',
                            },
                            {
                                key: 'status__icontains',
                                name: 'Status',
                            },
                            {
                                key: 'created_on__date',
                                name: 'Applied on',
                                type: 'datePicker',
                            },
                            {
                                key: 'leave_type__name__icontains',
                                name: 'Leave type',
                            },
                        ],
                    },
                    url: '/hrm/leaves_search/all_leaves/',
                    crud: true,
                    columns: [
                        {
                            name: 'worker',
                            title: 'Employee',
                        },
                        {
                            name: 'start_date',
                            title: 'Leave from',
                        },
                        {
                            name: 'end_date',
                            title: 'Leave to',
                        },
                        {
                            name: 'days',
                            title: 'Days',
                        },
                        {
                            name: 'leave_allocation__leave_type__name',
                            title: 'Leave type',
                        },
                        {
                            name: 'description',
                            title: 'Reason',
                        },
                        {
                            name: 'status',
                            title: 'Status',
                            renderWith: function (data) {
                                if (data == 'Pending') {
                                    return '<span style="color: red">' + data + '</span>';
                                } else {
                                    return '<span>' + data + '</span>';
                                }
                            },
                        },
                        {
                            name: 'created_on',
                            title: 'Applied on',
                        },
                    ],
                },
            ],
        };

        setAutoLookup('id_worker', '/b/lookups/labour/', 'worker', true);

        setAutoLookup('id_leave_type', '/b/lookups/employee_allocated_leave/', 'id_worker', true);

        function addLeave(leave_start_date, leave_end_date) {
            selectedLevelId = 0;
            $('#myModalLabel').text('Add leave');
            $('#allLeaveModel').modal('show');
            clearLeaveForm();
            if (leave_start_date == leave_end_date) {
                $('#id_leave_from').val(leave_start_date);
                $('#id_leave_to').val(leave_end_date);
                $scope.leavesFragments();
            }
        }
        var leave_type_ms = $('#id_leave_type').magicSuggest();
        $(leave_type_ms).on('selectionchange', function (e, m) {
            var leave_type_id = $('#hid_leave_type').val() ? $('#hid_leave_type').val() : undefined;
            var worker_id = $('#hid_worker').val();
            if (leave_type_id != undefined) {
                leave_type_id = $('#hid_leave_type').val();
                sparrow.post(
                    '/hrm/get_leave_allocation/',
                    {
                        leave_type_id: leave_type_id,
                        worker_id: worker_id,
                    },
                    false,
                    function (data) {
                        if (data.code == 1 && data.allocated_day != 0) {
                            var calculated_days = data.remaining_leave + ' remaining out of ' + data.allocated_day;
                            $('#totalOfDays').show();
                            $('#calculatedDays').text(calculated_days);
                        } else {
                            $('#totalOfDays').hide();
                        }
                    }
                );
            } else {
                $('#totalOfDays').hide();
            }
        });

        function showAllLeavesCalendar() {
            isList = false;
            isCal = true;
            $('#idAllLeaves').hide();
            $('#btnAllLeaveCalendarView').css('font-weight', '700');
            $('#all_leaves_calendar').css('display', 'block');
            $('#btnAllLeaveListView').css('font-weight', 'normal');
            $scope.loadCalendarData();
        }

        function showAllLeavesListView() {
            isList = true;
            isCal = false;
            $('#idAllLeaves').show();
            $('#all_leaves_calendar').css('display', 'none');
            $('#btnAllLeaveCalendarView').css('font-weight', 'normal');
            $('#btnAllLeaveListView').css('font-weight', '700');
        }

        $scope.loadCalendarData = function () {
            $('#all_leaves_calendar').fullCalendar({
                header: {
                    left: 'prev,next today ',
                    right: '',
                    center: 'title',
                },
                editable: true,
                events: function (start, end, timzone, callback) {
                    var currenDate = $('#all_leaves_calendar').fullCalendar('getDate');
                    currentYear = currenDate.format('Y');
                    currentMonth = currenDate.format('M');
                    sparrow.post(
                        '/hrm/get_all_leaves_calendar/',
                        {
                            currentMonth: currentMonth,
                            currentYear: currentYear,
                        },
                        false,
                        function (data) {
                            var events = data.data;
                            callback(events);
                        }
                    );
                },
                dayRender: function (date, cell) {
                    var startdate = moment();
                    startdate = startdate.subtract(1, 'days');
                    if (date < startdate) {
                        cell.css('background-color', '#c0c0c040');
                    }
                },
                eventColor: '#ddd0',
                dayClick: function (date, jsEvent, view) {
                    leave_start_date = date.format('DD/MM/YYYY H:mm');
                    leave_end_date = date.format('DD/MM/YYYY H:mm');
                    addLeave(leave_start_date, leave_end_date);
                },
                eventRender: function (event, eventElement, view) {
                    if (event.weekends == 1) {
                        $('td[data-date="' + event.common_date + '"]').css('background-color', '#69696952');
                        $("td.fc-day-top[data-date='" + event.common_date + "']").css('background-color', 'rgba(105, 105, 105, -0.68)');
                    }
                    var status = '';
                    if (event.status == 'pending') {
                        var status = 'Pending';
                        eventElement.find('div.fc-content').addClass('cal-skyblue');
                        eventElement.find('span.fc-title').prepend("<i class='icon-clock all-pending-leaves-icon'>");
                        eventElement.find('span.fc-title').addClass('all-pending-leaves-title');
                    } else if (event.status == 'approved') {
                        var status = 'Approved';
                        eventElement.find('div.fc-content').addClass('cal-green');
                        eventElement.find('span.fc-title').prepend("<i class='icon-check-circle all-approved-leaves-icon'>");
                        eventElement.find('span.fc-title').addClass('all-approved-leaves-title');
                    } else if (event.status == 'rejected') {
                        var status = 'Rejected';
                        eventElement.find('div.fc-content').addClass('cal-red');
                        eventElement.find('span.fc-title').prepend("<i class='icon-ban all-rejected-leaves-icon'>");
                        eventElement.find('span.fc-title').addClass('all-rejected-leaves-title');
                    }
                    if (event.status != null) {
                        $(eventElement).tooltip({
                            title: status + ' - ' + event.description,
                            placement: 'bottom',
                        });
                    }
                    if (event.imageurl == 'holiday') {
                        eventElement.find('div.fc-content').addClass('public-holiday cal-orange');
                    } else if (event.imageurl) {
                        eventElement.find('div.fc-content').prepend("<img class='img-profile' src='" + event.imageurl + "' width='23' height='23'>");
                    } else if (!event.imageurl) {
                        if (event.status == 'pending') {
                            eventElement.find('div.fc-content').prepend("<span class='icon-user-circle all-pending-leaves-user-avatar'></span>");
                        }
                        if (event.status == 'approved') {
                            eventElement.find('div.fc-content').prepend("<span class='icon-user-circle all-approved-leaves-user-avatar'></span>");
                        }
                        if (event.status == 'rejected') {
                            eventElement.find('div.fc-content').prepend("<span class='icon-user-circle all-rejected-leaves-user-avatar'></span>");
                        }
                    }
                },
            });
        };

        function approveLeave(rootScope) {
            sparrow.showConfirmDialog(ModalService, 'Are you sure you want to approve leave?', 'Approve leave', function (confirmAction) {
                if (confirmAction) {
                    var selectedIds = $scope.getSelectedIds(1).join([(separator = ',')]);
                    sparrow.post(
                        '/hrm/leave_approve/',
                        {
                            ids: selectedIds,
                        },
                        true,
                        function (data) {
                            $scope.reloadData(1);
                        }
                    );
                }
            });
        }

        function rejectLeave(rootScope) {
            sparrow.showConfirmDialog(ModalService, 'Are you sure you want to reject leave?', 'Reject leave', function (confirmAction) {
                if (confirmAction) {
                    var selectedIds = $scope.getSelectedIds(1).join([(separator = ',')]);
                    sparrow.post(
                        '/hrm/leave_reject/',
                        {
                            ids: selectedIds,
                        },
                        true,
                        function (data) {
                            $scope.reloadData(1);
                        }
                    );
                }
            });
        }

        function deleteLeave(rootScope) {
            sparrow.showConfirmDialog(ModalService, 'Are you sure you want to delete leave?', 'Delete leave', function (confirmAction) {
                if (confirmAction) {
                    var selectedIds = $scope.getSelectedIds(1).join([(separator = ',')]);
                    sparrow.post(
                        '/hrm/all_leaves_delete/',
                        {
                            ids: selectedIds,
                        },
                        true,
                        function (data) {
                            $scope.reloadData(1);
                        }
                    );
                }
            });
        }

        $scope.saveLeaves = function (event) {
            event.preventDefault();
            var leaveFrags = [];
            var with_one = [];
            for (i = 0; i < $scope.leaves.length; i++) {
                var leave_val = parseFloat($scope.leaves[i].leave_val);
                var date = moment($scope.leaves[i].date, 'dddd, MMMM DD, YYYY').format('DD/MM/YYYY');
                if (leave_val < 1) {
                    leaveFrags.push({
                        start_date: date,
                        end_date: date,
                        days: leave_val,
                    });
                    if (with_one.length > 0) {
                        leaveFrags.push(with_one[0]);
                        with_one = [];
                    }
                } else {
                    if (with_one.length > 0) {
                        with_one[0]['days'] = with_one[0]['days'] + leave_val;
                        with_one[0]['end_date'] = date;
                    } else {
                        with_one.push({
                            start_date: date,
                            end_date: date,
                            days: leave_val,
                        });
                    }
                }
            }

            if (with_one.length > 0) {
                leaveFrags.push(with_one[0]);
            }

            if (leaveFrags.length == 0) {
                sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please enter valid leave duration.', 5);
                return false;
            }

            var leave_allocation_id = $('#hid_leave_type').val();
            var description = $('#id_description').val();
            var worker_id = $('#hid_worker').val();

            var postData = {
                leave_allocation: leave_allocation_id,
                description: description,
                leaveFrags: JSON.stringify(leaveFrags),
                worker: worker_id,
            };

            if ($('#allLeaveForm').valid() && leave_allocation_id != undefined) {
                sparrow.post('/hrm/my_leaves_save/', postData, true, function (data) {
                    if (data.code == 1) {
                        $('#allLeaveModel').modal('hide');
                        $scope.reloadData(1);
                        $('#all_leaves_calendar').fullCalendar('destroy');
                        if (isList) {
                            $('#all_leaves_calendar').hide();
                        }
                        $scope.loadCalendarData();
                    }
                });
            }
        };

        function clearLeaveForm() {
            var worker = $('#id_worker').magicSuggest();
            var leave_type = $('#id_leave_type').magicSuggest();
            worker.clear();
            leave_type.clear();
            $('#id_description').val('');
            $('#hid_leave_type').val('');
            $('#id_leave_from').val('');
            $('#id_leave_to').val('');
            $scope.leaves = [];
            $scope.$apply(function () {
                $scope.leaves;
            });
        }

        $('input[name="end_date"],input[name="start_date"]').on('apply.daterangepicker', function (ev, picker) {
            $(this).val(picker.startDate.format('DD/MM/YYYY H:mm'));
            $scope.leavesFragments();
        });

        $scope.leavesFragments = function () {
            var startDate = $('#id_leave_from').val();
            var endDate = $('#id_leave_to').val();
            if (startDate == '' || endDate == '') {
                return;
            }
            var mDate = '';
            mDate = moment(startDate, 'DD/MM/YYYY H:mm');
            startDate = new Date(moment(mDate).format('MM/DD/YYYY'));

            mDate = moment(endDate, 'DD/MM/YYYY H:mm');
            endDate = new Date(moment(mDate).format('MM/DD/YYYY'));
            var temp_leaves = [];
            for (d = startDate; d <= endDate; d.setDate(d.getDate() + 1)) {
                date = moment(d).format('dddd, MMMM DD, YYYY');
                if ($scope.leaves.length > 0) {
                    var is_preserved = false;
                    for (i = 0; i < $scope.leaves.length; i++) {
                        if (date == $scope.leaves[i].date) {
                            is_preserved = true;
                            temp_leaves.push({
                                date: date,
                                leave_val: $scope.leaves[i].leave_val,
                            });
                        }
                    }
                    if (is_preserved != true) {
                        temp_leaves.push({
                            date: date,
                            leave_val: '1',
                        });
                    }
                } else {
                    temp_leaves.push({
                        date: date,
                        leave_val: '1',
                    });
                }
            }
            $scope.leaves = temp_leaves;
            $scope.$apply(function () {
                $scope.leaves;
            });
        };

        function showLog(scope) {
            var selectedId = $scope.getSelectedIds(1);
            var rowData = $.grep($scope['dtInstance1'].DataTable.data(), function (n, i) {
                return n.id == selectedId;
            });
            window.location.hash = '#/auditlog/logs/labourholiday/' + selectedId + '?title=' + rowData[0].worker;
        }

        sparrow.setup($scope, $rootScope, $route, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, config, ModalService);
    });
    return all_leaves;
}
all_leaves = allLeavesInit();
