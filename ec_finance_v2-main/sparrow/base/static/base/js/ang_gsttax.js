(function () {
    angular.module('angular-gsttaxs', []).directive('angGsttaxs', function () {
        return {
            restrict: 'AEC',
            scope: {
                gst_tax_lines: '@',
                gstSameState: '@',
                invoiceId: '@',
                currencySymbol: '@',
                gstshiptaxline: '@',
                appName: '@',
            },
            replace: true,
            controller: function ($scope) {
                if ($scope.invoiceId === '') {
                    $scope.gst_tax_lines = [];
                    $scope.gstshiptaxline = [];
                    return;
                }

                var postData = {
                    invoice_id: $scope.invoiceId,
                    app_name: $scope.appName,
                };
                sparrow.post('/financial/check_gst_tax/', postData, false, function (data) {
                    $scope.gst_tax_lines = data.gst_tax_lines;
                    $scope.gstSameState = data.gsttax_same_state;
                    $scope.currencySymbol = data.currency_symbol;
                    $scope.gstshiptaxline = data.ship_tax_lines;
                });
            },
            link: function (scope, elem, attrs) {},
            templateUrl: function (element, attr) {
                return attr.templateUrl || 'angular-gsttaxs.html';
            },
        };
    });
})();

angular.module('angular-gsttaxs').run([
    '$templateCache',
    function ($templateCache) {
        'use strict';
        $templateCache.put(
            'angular-gsttaxs.html',
            // eslint-disable-next-line no-multi-str
            '<div class="row ang-gsttax">      \
        <div class="gsttax-container">\
            <div ng-if="gstSameState">\
                <div ng-repeat="ship_tax_line in gstshiptaxline">\
                    <div class="col-sm-12 col-md-12 col-lg-12" id="id_ship_sgst" >\
                        <label class="col-sm-7 col-md-7 col-lg-7 text-right">Ship SGST @ {{ship_tax_line.ship_tax_perc}} % on {{ship_tax_line.ship_amount }} :</label>\
                        <label id="id_ship_sgst" class="col-sm-3 col-md-3 col-lg-4 text-right" style="width:31.5%;">\
                        {{ ship_tax_line.ship_cost }}</label>\
                        <label class="col-sm-1 col-md-1 col-lg-1 text-right">{{currencySymbol }}</label>\
                    </div>\
                    <div class="col-sm-12 col-md-12 col-lg-12" id ="id_ship_cgst" >\
                        <label class="col-sm-7 col-md-7 col-lg-7 text-right">Ship CGST @ {{ship_tax_line.ship_tax_perc}} % on {{ship_tax_line.ship_amount }} :</label>\
                        <label id="id_ship_cgst" class="col-sm-3 col-md-3 col-lg-4 text-right" style="width:31.5%;">\
                        {{ ship_tax_line.ship_cost }}</label>\
                        <label class="col-sm-1 col-md-1 col-lg-1 text-right">{{currencySymbol }}</label>\
                    </div>      \
                </div>\
                <div ng-repeat="gst_tax_line in gst_tax_lines">\
                    <div class="col-sm-12 col-md-12 col-lg-12" id="id_sgst">\
                        <label class="col-sm-7 col-md-7 col-lg-7 text-right" >SGST @ {{gst_tax_line.tax_perc}} % on {{gst_tax_line.amount }} :</label>\
                        <label id="id_sgst" class="col-sm-3 col-md-3 col-lg-4 text-right" style="width:31.5%;">\
                        {{ gst_tax_line.price }}</label>\
                        <label class="col-sm-1 col-md-1 col-lg-1 text-right">{{currencySymbol }}</label>\
                    </div>\
                    <div class="col-sm-12 col-md-12 col-lg-12" id ="id_cgst" >\
                        <label class="col-sm-7 col-md-7 col-lg-7 text-right">CGST @ {{gst_tax_line.tax_perc}} % on {{gst_tax_line.amount }} :</label>\
                        <label id="id_cgst" class="col-sm-3 col-md-3 col-lg-4 text-right" style="width:31.5%;">\
                        {{ gst_tax_line.price }}</label>\
                        <label class="col-sm-1 col-md-1 col-lg-1 text-right">{{currencySymbol }}</label>\
                    </div>      \
                </div>\
            </div>\
            <div ng-if="!gstSameState">\
                <div ng-repeat="ship_tax_line in gstshiptaxline">\
                    <div class="col-sm-12 col-md-12 col-lg-12" id ="is_ship_igst" >\
                        <label class="col-sm-7 col-md-7 col-lg-7 text-right">Ship IGST @ {{ship_tax_line.ship_tax_perc}} % on {{ship_tax_line.ship_amount }} :</label>\
                        <label id="is_ship_igst" class="col-sm-3 col-md-3 col-lg-4 text-right" style="width:31.5%;">\
                        {{ ship_tax_line.ship_cost}}</label>\
                        <label class="col-sm-1 col-md-1 col-lg-1 text-right">{{currencySymbol }}</label>\
                    </div> \
                </div>\
                <div ng-repeat="gst_tax_line in gst_tax_lines">\
                    <div class="col-sm-12 col-md-12 col-lg-12" id ="id_igst" >\
                        <label class="col-sm-7 col-md-7 col-lg-7 text-right">IGST @ {{gst_tax_line.tax_perc}} % on {{gst_tax_line.amount }} :</label>\
                        <label id="id_igst" class="col-sm-3 col-md-3 col-lg-4 text-right" style="width:31.5%;"">\
                        {{ gst_tax_line.price}}</label>\
                        <label class="col-sm-1 col-md-1 col-lg-1 text-right">{{currencySymbol }}</label>\
                    </div> \
                </div>\
            </div>           \
        </div>     \
    </div>'
        );
    },
]);
