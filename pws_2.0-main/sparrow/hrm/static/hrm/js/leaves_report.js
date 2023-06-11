function leavesReportInit() {
    var leavesReport = {};
    sparrow.registerCtrl('leavesReportCtrl', function ($scope, $rootScope, $route, $routeParams, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, ModalService) {
        var config = {
            pageTitle: 'Leaves report',

            listing: [
                {
                    url: '/hrm/leaves_search/leaves_report/',
                    paging: true,
                    scrollBody: true,
                    postData: {
                        start_date__date: '',
                        end_date__date: '',
                        worker_id: '',
                    },
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
                        },
                        {
                            name: 'created_on',
                            title: 'Applied on',
                        },
                    ],
                    index: 1,
                },
            ],
        };
        setAutoLookup('id_worker', '/b/lookups/labour/', 'worker', true);
        $('#load_btn').on('click', function (event) {
            sparrow.global.set('SEARCH_EVENT', true);
            dtBindFunction();
            config.listing[0].postData = $scope.postData;
            $scope.reloadData(1, config.listing[0]);
            $('#btnExport').show();
        });

        function dtBindFunction() {
            var worker_id = $('#hid_worker').val();
            if (worker_id == undefined) {
                worker_id = '';
            }
            var Dates = $('#dates').text();
            var from_date = '';
            var to_date = '';
            if (Dates != '') {
                var newDates = Dates.split('-');
                from_date = newDates[0].trim();
                to_date = newDates[1].trim();
            }
            var postData = {
                start_date__date: from_date,
                end_date__date: to_date,
                worker_id: worker_id,
            };
            console.log(postData);
            $scope.postData = postData;
            $('.date_range').text('From ' + $scope.postData.start_date__date + ' to ' + $scope.postData.end_date__date);
        }

        $scope.onExport = function (event) {
            event.preventDefault();
            dtBindFunction();
            var postData = $scope.postData;
            var url = '/hrm/leaves_export?worker_id=' + postData['worker_id'] + '&from=' + postData['start_date__date'] + '&to=' + postData['end_date__date'];
            window.open(url, '_blank');
        };

        sparrow.setup($scope, $rootScope, $route, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, config, ModalService);
    });

    return leavesReport;
}

leavesReport = leavesReportInit();
