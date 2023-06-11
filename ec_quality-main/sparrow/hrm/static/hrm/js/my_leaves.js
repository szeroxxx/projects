function myLeavesInit() {
    var myleaves = {};
    sparrow.registerCtrl('myLeavesCtrl', function ($scope, $rootScope, $route, $routeParams, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, ModalService) {
        $scope.leaves = [];
        var isList = true;
        var config = {
            pageTitle: 'My leaves',
            topActionbar: {
                extra: [
                    {
                        id: 'btnAddMyLeaves',
                        function: showAddMyLeave,
                    },
                    {
                        id: 'cancelLeave',
                        function: leaveCancel,
                        multiselect: true,
                    },
                    {
                        id: 'btnMyLeaveListView',
                        function: showMyLeavesListView,
                    },
                    {
                        id: 'btnMyLeaveCalendarView',
                        function: showMyLeavesCalendar,
                    },
                    {
                        id: 'btnLeavesHistory',
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
                    url: '/hrm/leaves_search/my_leaves/',
                    crud: true,
                    columns: [
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
                        },
                        {
                            name: 'created_on',
                            title: 'Applied on',
                        },
                    ],
                },
            ],
        };

        if ($('#id_leave_type').length) {
            setAutoLookup('id_leave_type', '/b/lookups/my_allocated_leave/', '', true);
        }

        function showAddMyLeave(my_leave_from, my_leave_to) {
            selectedLevelId = 0;
            $('#myModalLabel').text('Add leave');
            $('#myLeaveModel').modal('show');
            clearAllocationForm();
            if (my_leave_from == my_leave_to) {
                $('#id_leave_from').val(my_leave_from);
                $('#id_leave_to').val(my_leave_to);
                $scope.leavesFragments();
            }
        }

        var leave_type_ms = $('#id_leave_type').magicSuggest();
        $(leave_type_ms).on('selectionchange', function (e, m) {
            var leave_allocation_id = $('#hid_leave_type').val() ? $('#hid_leave_type').val() : undefined;
            if (leave_allocation_id != undefined) {
                leave_allocation_id = $('#hid_leave_type').val();
                sparrow.post(
                    '/hrm/get_leave_allocation/',
                    {
                        leave_allocation_id: leave_allocation_id,
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

        function leaveCancel(rootScope) {
            sparrow.showConfirmDialog(ModalService, 'Are you sure you want to cancel leave?', 'Cancel leave', function (confirmAction) {
                if (confirmAction) {
                    var selectedIds = $scope.getSelectedIds(1).join([(separator = ',')]);
                    sparrow.post(
                        '/hrm/leave_cancel/',
                        {
                            ids: selectedIds,
                        },
                        true,
                        function (data) {
                            $route.reload();
                        }
                    );
                }
            });
        }

        function showMyLeavesCalendar() {
            isList = false;
            isCal = true;
            $('#idMyLeaves').hide();
            $('#btnMyLeaveCalendarView').css('font-weight', '700');
            $('#my_leaves_calendar').css('display', 'block');
            $('#btnMyLeaveListView').css('font-weight', 'normal');
            $scope.loadMyLeaveCalendarData();
        }

        function showMyLeavesListView() {
            isList = true;
            isCal = false;
            $('#idMyLeaves').show();
            $('#my_leaves_calendar').css('display', 'none');
            $('#btnMyLeaveCalendarView').css('font-weight', 'normal');
            $('#btnMyLeaveListView').css('font-weight', '700');
        }
        $scope.loadMyLeaveCalendarData = function () {
            $('#my_leaves_calendar').fullCalendar({
                header: {
                    left: 'prev,next today ',
                    right: '',
                    center: 'title',
                },
                editable: true,
                events: function (start, end, timzone, callback) {
                    var currenDate = $('#my_leaves_calendar').fullCalendar('getDate');
                    currentYear = currenDate.format('Y');
                    currentMonth = currenDate.format('M');
                    sparrow.post(
                        '/hrm/get_all_leaves_calendar/',
                        {
                            currentMonth: currentMonth,
                            currentYear: currentYear,
                            my_leave_id: 1,
                        },
                        false,
                        function (data) {
                            events = data.data;
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
                    my_leave_from = date.format('DD/MM/YYYY H:mm');
                    my_leave_to = date.format('DD/MM/YYYY H:mm');
                    showAddMyLeave(my_leave_from, my_leave_to);
                },
                eventRender: function (event, eventElement) {
                    if (event.weekends) {
                        $('td[data-date="' + event.common_date + '"]').css('background-color', '#69696952');
                        $("td.fc-day-top[data-date='" + event.common_date + "']").css('background-color', 'rgba(105, 105, 105, -0.68)');
                    }
                    var status = '';
                    if (event.status == 'pending') {
                        var status = 'Pending';
                        eventElement.find('div.fc-content').addClass('cal-skyblue');
                        eventElement.find('span.fc-title').prepend("<i class='icon-clock my-pending-leaves-icon'>");
                        eventElement.find('span.fc-title').addClass('my-pending-leaves-title');
                    } else if (event.status == 'approved') {
                        var status = 'Approved';
                        eventElement.find('div.fc-content').addClass('cal-green');
                        eventElement.find('span.fc-title').prepend("<i class='icon-check-circle my-approved-leaves-icon'>");
                        eventElement.find('span.fc-title').addClass('my-approved-leaves-title');
                    } else if (event.status == 'rejected') {
                        var status = 'Rejected';
                        eventElement.find('div.fc-content').addClass('cal-red');
                        eventElement.find('span.fc-title').prepend("<i class='icon-ban my-rejected-leaves-icon'>");
                        eventElement.find('span.fc-title').addClass('my-rejected-leaves-title');
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
                        eventElement.find('div.fc-content').prepend("<img class ='my-leaves-img-profile' src='" + event.imageurl + "' width='22' height='22'>");
                    } else if (!event.imageurl) {
                        eventElement.find('div.fc-content').addClass('public-holiday');
                    }
                },
            });
        };

        $scope.saveLeaves = function (event) {
            event.preventDefault();
            var user_days = 0;
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
                    user_days = user_days + leave_val;
                    if (with_one.length > 0) {
                        leaveFrags.push(with_one[0]);
                        with_one = [];
                    }
                } else {
                    user_days = user_days + leave_val;

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
            var leave_allocation_id = $('#hid_leave_type').val();
            var description = $('#id_description').val();

            var postData = {
                leave_allocation: leave_allocation_id,
                description: description,
                leaveFrags: JSON.stringify(leaveFrags),
            };

            if ($('#leaveform').valid() && leave_allocation_id != undefined) {
                sparrow.post('/hrm/my_leaves_save/', postData, true, function (data) {
                    if (data.code == 1) {
                        $('#myLeaveModel').modal('hide');
                        $scope.reloadData(1);
                        $('#id_allocated_day').text(data.allocated_day);
                        $('#id_total_leave').text(data.total_leave);
                        $('#id_remaining_leave').text(data.remaining_leave);
                        $('#my_leaves_calendar').fullCalendar('destroy');
                        if (isList) {
                            $('#my_leaves_calendar').hide();
                        }
                        $scope.loadMyLeaveCalendarData();
                    }
                });
            }
        };

        function clearAllocationForm() {
            var worker_ms = $('#id_leave_type').magicSuggest();
            worker_ms.clear();
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
                // date = moment(d).format("DD/MM/YYYY")
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
    return myleaves;
}
myleaves = myLeavesInit();
