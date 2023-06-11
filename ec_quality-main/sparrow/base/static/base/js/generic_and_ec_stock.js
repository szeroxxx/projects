function gcecstockInit() {
    var gcecstock = {};

    sparrow.registerCtrl('GcEcStockCtrl', function ($scope, $rootScope, $route, $routeParams, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, ModalService) {
        config = {
            pageTitle: 'Generic and  EC Stock',

            topActionbar: {
                extra: [
                    {
                        id: 'btnExport',
                        function: onExport,
                    },
                ],
            },
            listing: [
                {
                    index: 1,
                    url: '/base/generic_and_ec_stock_search/',
                    postData: {
                        product_id: '',
                    },

                    paging: true,
                    scrollBody: true,
                    search: {
                        params: [
                            {
                                key: 'name__icontains',
                                name: 'MPN',
                            },
                            {
                                key: 'created_on__date',
                                name: 'Created on',
                                type: 'datePicker',
                            },
                        ],
                    },
                    columns: [
                        {
                            name: 'name',
                            title: 'MPN',
                            renderWith: function (data, type, full, meta) {
                                return (
                                    '<span>' +
                                    '<a class="link-iframe-item" ng-click="onEditLink(\'/b/iframe_index/#/products/product/buy/' +
                                    full.product_id +
                                    "?is_purchasable=True','Product - " +
                                    full.name +
                                    "'," +
                                    null +
                                    ', ' +
                                    false +
                                    ', ' +
                                    1 +
                                    ',' +
                                    true +
                                    ')">' +
                                    full.name +
                                    '</a>' +
                                    '</span>'
                                );
                            },
                        },
                        { name: 'stock', title: 'Stock', sort: false },
                        { name: 'qty', title: 'Quantity', sort: false },
                        { name: 'supplier', title: 'supplier', sort: false },
                        { name: 'discount_price', title: 'Unit price', sort: false },
                        { name: 'total', title: 'Total price', sort: false },
                    ],
                    index: 1,
                },
            ],
        };
        if (data.company_code == 1) {
            config.listing[0].columns.splice(1, 0, {
                name: 'generic_part',
                title: 'GC/EC',
                class: 'generic-part',
                renderWith: onGenericPart,
            });
        }
        function onGenericPart(data, type, full, meta) {
            if (data) {
                return '<img src="/static/base/images/generic.png?v=1" title="Generic part" />';
            } else if (full.ec_stock) {
                return '<img src="/static/base/images/ec_stock.png?v=1" title="EC stock part" />';
            }
        }
        setAutoLookup('id_product', '/b/lookups/product/', '', true, true, false, null, 1);

        function dtBindFunction() {
            var ms = $('#id_product').magicSuggest();
            var product_ids = [];
            if (ms.getSelection().length > 0) {
                for (var i = 0; i < ms.getSelection().length; i++) {
                    product_ids.push(ms.getSelection()[i]['id']);
                }
            }
            var postData = {
                id_product: product_ids,
            };
            $scope.postData = postData;
        }
        $('#load_btn').on('click', function (event) {
            sparrow.global.set('SEARCH_EVENT', true);
            dtBindFunction();
            event.preventDefault();
            config.listing[0].postData = $scope.postData;
            $scope.reloadData(1, config.listing[0]);
        });
        function onExport(scope) {
            dtBindFunction();
            var postData = $scope.postData;
            var id = postData['id_product'];
            if (id == undefined || id == '') {
                id = 0;
            }

            event.preventDefault();
            window.open('/base/generic_and_ec_stock_export/?ids=' + id);
        }
        sparrow.setup($scope, $rootScope, $route, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, config, ModalService);
    });
    return gcecstock;
}
gcecstockInit();
