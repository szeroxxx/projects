function componentsUsageInit() {
    var componentsUsage = {};
    sparrow.registerCtrl('componentsUsageCtrl', function ($scope, $rootScope, $route, $routeParams, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, ModalService) {
        config = {
            pageTitle: 'Component usage',
            topActionbar: {
                extra: [
                    {
                        id: 'btnClose',
                        multiselect: false,
                        function: back,
                    },
                    {
                        id: 'btndetailExport',
                        multiselect: false,
                        function: onExportDetails,
                    },
                ],
            },
            listing: [
                {
                    url: '/base/component_usage_search/',
                    paging: true,
                    scrollBody: true,
                    postData: {
                        from_date: '',
                        to_date: '',
                        id_cat: '',
                        id_product: '',
                        id_product_group: '',
                        grid_show: false,
                        id_Stock_status: '',
                    },
                    onBindCallback: function (data) {
                        loadChart(data);
                    },
                    columns: [
                        {
                            name: 'part__name',
                            title: 'Product',
                            renderWith: function (data, type, full, meta) {
                                return (
                                    // eslint-disable-next-line no-multi-str
                                    '<span>\
                                     <a class="link-iframe-item" ng-click="onEditLink(\'/b/iframe_index/#/products/product/' +
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
                                    // eslint-disable-next-line no-multi-str
                                    '</a>\
                                </span></br>\
                              <span style="float:left;line-height:1;margin-left:0px;" class="replace-part">\
                                <a  style="color:#6D7279; font-size: 12px; white-space: pre;">Total used qty in order: ' +
                                    full.total_qty +
                                    // eslint-disable-next-line no-multi-str
                                    '</a>\
                              </span>'
                                );
                            },
                        },
                        { name: 'part__manufacturer__name', title: 'Manufacturer' },
                        { name: 'part__internal_cat__name', title: 'Category' },
                        { name: 'part__product_group__name', title: 'Group' },
                        { name: 'stock', title: 'Stock', sort: false },
                        { name: 'stock_value', title: 'Stock value', class: 'text-right', sort: false },
                        { name: 'total_purch_qty', title: 'Total purchased qty', class: 'text-right', sort: false },
                        { name: 'total_prod_qty', title: 'Total used qty', class: 'text-right' },
                        { name: 'total_orders', title: 'Total used in order', class: 'text-right' },
                        { name: 'part__cost_price', title: 'Unit price', class: 'text-right' },
                        { name: 'total_customer', title: 'Total customer', class: 'text-right' },
                        { name: 'part__description_purchase', title: 'Description' },
                        { name: 'mo', title: '', class: 'text-right', renderWith: mosButton, sort: false },
                    ],
                    index: 1,
                },
                {
                    url: '/base/products_usage_search/',
                    paging: true,
                    scrollBody: true,
                    postData: {
                        product_id: '',
                        grid_show: true,
                        id_Stock_status: '',
                        from_date: '',
                        to_date: '',
                    },
                    columns: [
                        { name: 'mfg_order__mfg_order_num', title: 'Mfg order', link: { route: 'mfg_order', params: { id: 'id' } } },
                        { name: 'mfg_order__product__name', title: 'Product', link: { route: 'product', params: { id: 'mfg_order__product__id' } } },
                        { name: 'prod_qty', title: 'Total used qty', class: 'text-right' },
                        { name: 'price', title: 'Unit price', class: 'text-right', sort: false },
                        { name: 'sum_price', title: 'Total cost price', class: 'text-right', sort: false },
                    ],
                    index: 2,
                },
            ],
        };
        setAutoLookup('id_cat', '/b/lookups/internal_cat/', '', false, true);
        setAutoLookup('id_product', '/b/lookups/product/', '', false, true);
        setAutoLookup('id_product_group', '/b/lookups/product_type/', '', false, true);

        function loadChart(data) {
            $('.chart-container').html('&nbsp;');
            $('.chart-container').html('<canvas id="myChart"></canvas>');
            var ctx = document.getElementById('myChart').getContext('2d');
            var label_values = [];
            var data_values_usage = [];
            var data_values_stock = [];
            data.data.forEach(loopdata);
            function loopdata(item) {
                label_values.push(item.part__name);
                data_values_usage.push(item.total_prod_qty);
                data_values_stock.push(item.stock);
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
                        },
                        {
                            label: 'Usage',
                            backgroundColor: '#007bff',
                            borderColor: '#007bff',
                            data: data_values_usage,
                        },
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

        function mosButton(data, type, full, meta) {
            return `<span><a href='' ng-click="onChildMo('${full.part__name}','${full.id}')">View orders</a></span>`;
        }

        function back(scope) {
            $('.onButton').hide();
            $('.onLoad').show();
            $('#btnClose').hide();
            $('#selection_option').show();
            $('#btnExport').show();
            $('#btndetailExport').hide();
            $('#basePageTitle').text('Component usage');
        }

        $scope.onChildMo = function (product_name, product_id) {
            $scope.productId = product_id;
            config.listing[1].postData = {
                product_id: product_id,
                grid_show: false,
                from_date: $scope.from_date,
                to_date: $scope.to_date,
            };
            $('#selection_option').hide();
            var title = 'Product' + ' - ' + product_name;
            $('#basePageTitle').text(title);
            $scope.reloadData(2, config.listing[1]);
            $('.onLoad').hide();
            $('#btnClose').show();
            $('.onButton').show();
            $('#btnExport').hide();
            $('#btndetailExport').show();
        };

        $('#load_btn').on('click', function (event) {
            sparrow.global.set('SEARCH_EVENT', true);
            dtBindFunction();
            config.listing[0].postData = $scope.postData;
            $scope.reloadData(1, config.listing[0]);
            $('#btnExport').show();
        });

        function dtBindFunction() {
            categoryId = $('#hid_cat').val();
            productId = $('#hid_product').val();
            from_date = $('#from_date').val();
            to_date = $('#to_date').val();
            stock_status = $('#id_Stock_status').val();
            id_product_group = $('#hid_product_group').val();

            if (categoryId == undefined) {
                categoryId = '';
            }
            if (productId == undefined) {
                productId = '';
            }
            if (id_product_group == undefined) {
                id_product_group = '';
            }
            if (from_date == undefined) {
                from_date = '';
            }
            if (to_date == undefined) {
                to_date = '';
            }
            var Dates = $('#dates').text();
            var from_date = '';
            var to_date = '';
            if (Dates != '') {
                var newDates = Dates.split('-');
                from_date = newDates[0].trim();
                to_date = newDates[1].trim();
                var newToDate = to_date.split('/');

                if (parseInt(newToDate[0]) + 1 < 31) {
                    newToDate[0] = (parseInt(newToDate[0]) + 1).toString();
                    to_date = newToDate.join('/').trim();
                }
            }
            $scope.from_date = from_date;
            $scope.to_date = to_date;
            var postData = {
                from_date: from_date,
                to_date: to_date,
                id_cat: categoryId,
                id_product: productId,
                id_product_group: id_product_group,
                grid_show: true,
                stock_status: stock_status,
            };
            $scope.postData = postData;
        }

        $scope.onExport = function (event) {
            event.preventDefault();
            dtBindFunction();
            var postData = $scope.postData;
            var url =
                '/base/component_usage_export?cat=' +
                postData['id_cat'] +
                '&product=' +
                postData['id_product'] +
                '&group=' +
                postData['id_product_group'] +
                '&from=' +
                postData['from_date'] +
                '&to=' +
                postData['to_date'] +
                '&stockstatus=' +
                postData['stock_status'];
            window.open(url, '_blank');
        };

        function onExportDetails(scope) {
            window.open('/base/product_usage_export/' + $scope.productId + '/', '_blank');
        }

        sparrow.setup($scope, $rootScope, $route, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, config, ModalService);
    });

    return componentsUsage;
}

componentsUsageInit();
