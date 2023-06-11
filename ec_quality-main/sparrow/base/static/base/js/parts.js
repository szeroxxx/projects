function partsInit() {
    var parts = {};
    sparrow.registerCtrl('partsCtrl', function ($scope, $rootScope, $route, $routeParams, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, ModalService) {
        config = {
            pageTitle: 'Generic/EC-Stock parts',
            listing: [
                {
                    index: 1,
                    url: '/base/parts_search/' + $routeParams.type + '/',
                    paging: true,
                    scrollBody: true,
                    search: {
                        params: [
                            { key: 'name', name: 'Product' },
                            { key: 'cat_id__name', name: 'Category' },
                            { key: 'description_purchase', name: 'Description' },
                            { key: 'stock_status', name: 'Stock type' },
                        ],
                    },
                    onBindCallback: function (data) {
                        loadChart(data);
                    },
                    columns: [
                        {
                            name: 'name',
                            title: 'Product',
                            renderWith: function (data, type, full, meta) {
                                return (
                                    '<span title="' +
                                    sparrow.stripHtml(full.description) +
                                    '">' +
                                    '<a class="link-iframe-item" ng-click="onEditLink(\'/b/iframe_index/#/products/product/' +
                                    undefined +
                                    '/' +
                                    full.id +
                                    "','Product - " +
                                    data +
                                    "'," +
                                    null +
                                    ', ' +
                                    false +
                                    ', ' +
                                    1 +
                                    ',' +
                                    true +
                                    ')">' +
                                    data +
                                    '</a>' +
                                    '</span>'
                                );
                            },
                        },
                        { name: 'manufacturer__name', title: 'Manufacturer' },
                        { name: 'stock_status', title: 'Stock Type' },
                        { name: 'product_group__name', title: 'Group' },
                        { name: 'stock', title: 'Stock', sort: false },
                        { name: 'stock_value', title: 'Stock Value', sort: false },
                        { name: 'cost_price', title: 'Unit Price' },
                        { name: 'cat_id__name', title: 'Category' },
                        { name: 'description_purchase', title: 'Description' },
                    ],
                },
            ],
        };

        function loadChart(data) {
            $('.chart-container').html('&nbsp;');
            $('.chart-container').html('<canvas id="myChart"></canvas>');
            var ctx = document.getElementById('myChart').getContext('2d');
            var label_values = [];
            var data_values_stock_value = [];
            var data_values_stock = [];
            // var data_values_cost_price = [];
            data.data.forEach(loopdata);
            function loopdata(item) {
                label_values.push(item.name);
                data_values_stock_value.push(item.stock_value);
                data_values_stock.push(item.stock);
                // data_values_cost_price.push(item.cost_price);
            }
            // eslint-disable-next-line no-unused-vars
            var chart = new Chart(ctx, {
                // The type of chart we want to create
                type: 'horizontalBar',

                // The data for our dataset
                data: {
                    labels: label_values,
                    datasets: [
                        {
                            label: 'Stock',
                            backgroundColor: '#28a745',
                            borderColor: '#28a745',
                            data: data_values_stock,
                            fill: false,
                        },
                        {
                            label: 'Stock value',
                            backgroundColor: '#007bff',
                            borderColor: '#007bff',
                            data: data_values_stock_value,
                            fill: false,
                        },
                        // {
                        //     label: 'Unit price',
                        //     backgroundColor: 'orange',
                        //     borderColor: 'orange',
                        //     data: data_values_cost_price,
                        //     fill: false,
                        // },
                    ],
                },
                options: {
                    scales: {
                        yAxes: [
                            {
                                barPercentage: 1.0,
                            },
                        ],
                    },
                    tooltips: {
                        mode: 'nearest',
                        callbacks: {
                            label: function (tooltipItem, data) {
                                return data.datasets[tooltipItem.datasetIndex].label + ': ' + data.datasets[tooltipItem.datasetIndex].data[tooltipItem.index].toLocaleString();
                            },
                        },
                    },
                },
            });
        }

        $scope.onExportPart = function (scope) {
            window.open('/base/parts_export/', '_blank');
        };
        sparrow.setup($scope, $rootScope, $route, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, config, ModalService);
    });

    return parts;
}

partsInit();
