(function () {
    angular.module('angular-wh-loc-picker', []).directive('angWhLocPicker', function ($rootScope) {
        return {
            restrict: 'AEC',
            scope: {
                edit: '@',
            },
            replace: false,
            controller: function ($scope, $element) {
                $scope.warehouses = [];
                $scope.racks = [];
                $scope.rackLocations = [];
                $scope.selectedWarehouse = null;
                $scope.selectedRackCode = '';
                $scope.usedCells = [];
                $scope.usedRacLoc = null;
                $scope.emptyRacLoc = null;
                $scope.editWarehouseId = 0;
                $scope.rackId = 0;
                $scope.column = 0;
                $scope.locName = '';
                $scope.totalLoc = 0;
                $scope.selectLocId = '';

                var chartOption = {
                    animation: {
                        animateRotate: true,
                        animateScale: true,
                    },
                    cutoutPercentage: 85,
                    legend: false,
                    legendCallback: function (chart) {},
                };

                Chart.pluginService.register({
                    beforeDraw: function (chart) {
                        if (chart.config.options.elements.center) {
                            //Get ctx from string
                            var ctx = chart.chart.ctx;

                            //Get options from the center object in options
                            var centerConfig = chart.config.options.elements.center;
                            var fontStyle = centerConfig.fontStyle || 'Arial';
                            var txt = centerConfig.text;
                            var color = centerConfig.color || '#000';
                            var sidePadding = centerConfig.sidePadding || 20;
                            var sidePaddingCalculated = (sidePadding / 100) * (chart.innerRadius * 2);
                            //Start with a base font of 30px
                            ctx.font = '30px ' + fontStyle;

                            //Get the width of the string and also the width of the element minus 10 to give it 5px side padding
                            var stringWidth = ctx.measureText(txt).width;
                            var elementWidth = chart.innerRadius * 2 - sidePaddingCalculated;

                            // Find out how much the font can grow in width.
                            var widthRatio = elementWidth / stringWidth;
                            var newFontSize = Math.floor(30 * widthRatio);
                            var elementHeight = chart.innerRadius * 2;

                            // Pick a new font size so it will not be larger than the height of label.
                            var fontSizeToUse = Math.min(newFontSize, elementHeight);

                            //Set font settings to draw it correctly.
                            ctx.textAlign = 'center';
                            ctx.textBaseline = 'middle';
                            var centerX = (chart.chartArea.left + chart.chartArea.right) / 2;
                            var centerY = (chart.chartArea.top + chart.chartArea.bottom) / 2;
                            ctx.font = fontSizeToUse + 'px ' + fontStyle;
                            ctx.fillStyle = color;

                            //Draw text in center
                            ctx.fillText(txt, centerX, centerY);
                        }
                    },
                });

                getWarehouses();

                function getWarehouses() {
                    sparrow.post('/inventory/get_warehouses/', null, false, function (data) {
                        $scope.$apply(function () {
                            $scope.warehouses = data.warehouses;
                            if ($scope.warehouses.length > 0) {
                                $scope.viewRacks(data.warehouses[0]);
                            }
                        });
                    });

                    setTimeout(function () {
                        initWarehouseChart();
                    }, 500);
                }

                function initWarehouseChart() {
                    $($element)
                        .find('.wh-chart')
                        .each(function (i, obj) {
                            var usedLoc = $scope.warehouses[i].usedLoc;
                            var totalLoc = $scope.warehouses[i].totalLoc;
                            var chartData = getChartData(usedLoc, totalLoc);
                            var percentageLeft = $scope.getPercentage(usedLoc, totalLoc);
                            chartOption['elements'] = {
                                center: {
                                    text: percentageLeft,
                                    color: '#49B666', //Default black
                                    fontStyle: 'Helvetica', //Default Arial
                                    sidePadding: 15, //Default 20 (as a percentage)
                                },
                            };
                            var chart = new Chart($(this), {
                                type: 'doughnut',
                                data: chartData,
                                options: chartOption,
                            });
                        });
                }

                $scope.getPercentage = function (usedLoc, totalLoc) {
                    var exactPercentage = 0;
                    if (isNaN(parseInt((usedLoc / totalLoc) * 100))) {
                        var exactPercentage = 0;
                    } else {
                        if (parseInt((usedLoc / totalLoc) * 100) > 1) {
                            exactPercentage = parseInt((usedLoc / totalLoc) * 100);
                        } else {
                            exactPercentage = parseFloat((usedLoc / totalLoc) * 100).toFixed(1);
                        }
                    }
                    var percentageLeft = exactPercentage + '%';
                    return percentageLeft;
                };

                function getChartData(usedLoc, totalLoc) {
                    var emptyLoc = totalLoc - usedLoc;
                    var data = {
                        datasets: [
                            {
                                data: [usedLoc, emptyLoc],
                                backgroundColor: ['#49B666', '#c5c5c5'],
                            },
                        ],
                        labels: ['Used', 'Empty'],
                    };
                    return data;
                }

                $scope.viewRacks = function (warehouse) {
                    $scope.selectedWarehouse = warehouse;
                    $scope.selectedRackCode = '';
                    $scope.rackLocations = [];
                    $scope.racks = [];
                    sparrow.post('/inventory/get_warehouse_racks/', { warehouseId: $scope.selectedWarehouse.id }, false, function (data) {
                        $scope.$apply(function () {
                            $scope.racks = data.warehouse_racks;
                            var rack = data.warehouse_racks[0];
                            $scope.viewRackLocation(rack.id, rack.code, rack.totalLoc, rack.usedLoc);
                        });
                    });
                };

                if ($scope.edit == 'true') {
                    $('#basePageTitle').text('Warehouses');
                    $('#top_action_bar').html('');
                    $('#top_action_bar').append(
                        '<div class="focus-inner button-bar">\
                            <input type="button" id="btnAddWarehouse" class="btn btn-primary btn-sm" value="Add new"></input>\
                        </div>'
                    );

                    $(document).on('click', '#btnAddWarehouse', function () {
                        $scope.onEditWahrehouse(0);
                    });
                }

                $scope.viewRackLocation = function (rack_id, code, usedLoc, totalLoc) {
                    $scope.usedRacLoc = usedLoc;
                    $scope.emptyRacLoc = totalLoc - usedLoc;
                    $scope.totalLoc = totalLoc;
                    $scope.rackId = rack_id;
                    $scope.rackLocations = [];
                    sparrow.post('/inventory/get_rack_locations/', { rack_id: rack_id, warehouseId: $scope.selectedWarehouse.id }, false, function (data) {
                        $scope.$apply(function () {
                            $scope.rackLocations = data.rackLocations;
                            $scope.usedCells = data.used_locations;
                            $scope.column = data.rack_cols;
                            if ($scope.column.length > 0) {
                                $scope.column = $scope.column[0].cols;
                            } else {
                                $scope.column = [];
                            }
                            $scope.selectedRackCode = code;
                            if ($scope.edit == 'true') {
                                var height = $(window).height() - 141;
                                $('#table-wrapper').css('height', height + 'px');
                            }
                        });
                    });
                };

                $scope.stockOnWarehouseLoc = function (location_id, name) {
                    $scope.isOccupied = $scope.isCellUsed(name);
                    $('.selectOptions').removeClass('open');
                    if ($scope.isOccupied) {
                        if ($scope.edit == 'false') {
                            $('.l_' + location_id).addClass('open');
                        } else {
                            $scope.showWarehouseLoc(location_id, name);
                        }
                    } else if ($scope.edit == 'false') {
                        $('#l_' + $scope.selectLocId).removeClass('addSelectColor');
                        $scope.selectLocId = location_id;
                        $('#l_' + $scope.selectLocId).addClass('addSelectColor');
                        $scope.assignedLoc(location_id, name);
                    }
                };

                $scope.selectLoc = function (location_id, name) {
                    setTimeout(function () {
                        $('.selectOptions').removeClass('open');
                    }, 500);
                    $scope.assignedLoc(location_id, name);
                    $('#l_' + $scope.selectLocId).removeClass('addSelectColor');
                    $scope.selectLocId = location_id;
                    $('#l_' + $scope.selectLocId).addClass('addSelectColor');
                };

                $scope.showWarehouseLoc = function (location_id, name) {
                    setTimeout(function () {
                        $('.selectOptions').removeClass('open');
                    }, 500);
                    sparrow.post(
                        '/inventory/stock_on_warehouse_location/',
                        { id: location_id },
                        false,
                        function (data) {
                            if ($('#stockOnWarehouseModel').length == 0) {
                                var stockLocationTmpl = getStockLocationTemplate();
                                $('#viewContainer').append(stockLocationTmpl);
                            }

                            $('#sourcingLable').text('Stock location - ' + name);
                            $('#sourcing_model_body').html(data);
                            $('#stockOnWarehouseModel').modal('show');
                            $('#sourcing_model_body').css('height', parent.document.body.clientHeight - 140 + 'px');
                        },
                        'html'
                    );
                };

                function getStockLocationTemplate() {
                    return '<div style="z-index:1051" id="stockOnWarehouseModel" class="modal fade" tabindex="-1" role="dialog">\
                        <div class="modal-dialog modal-lg" role="document" style="width: 500px;">\
                            <div class="modal-content">\
                                <div class="modal-header">\
                                    <button type="button" class="close" data-dismiss="modal" aria-label="Close">\
                                        <span aria-hidden="true">&times;</span>\
                                    </button>\
                                    <h5 class="modal-title" id="sourcingLable" ng-bind="sourcingTitle"></h5>\
                                </div>\
                                <div class="modal-body" id="sourcing_model_body" style="overflow-y: auto;">\
                                </div>\
                            </div>\
                        </div>\
                    </div>';
                }

                $scope.tippyTooltip = function (cellId) {
                    $('#l_' + cellId).tooltip({
                        container: 'body',
                    });
                };

                $scope.getNumber = function (num) {
                    return new Array(num);
                };

                $scope.isCellUsed = function (cell) {
                    $scope.used = false;
                    for (i = 0; i < $scope.usedCells.length; i++) {
                        if (cell == $scope.usedCells[i]) {
                            $scope.used = true;
                            break;
                        } else {
                            $scope.used = false;
                        }
                    }
                    return $scope.used;
                };

                $scope.selectWarehouseLocTooltip = function () {
                    var desc = $('#locSelectInfo').text();
                    $('#warehouseLocSelectInfoId').tooltip({
                        title: desc,
                        placement: 'right',
                    });
                };
            },

            link: function (scope, elem, attrs) {
                scope.onEditWahrehouse = function (warehouseId) {
                    $rootScope.$broadcast('onEditWareHouse', warehouseId);
                };
                scope.assignedLoc = function (location_id, name) {
                    $rootScope.$broadcast('assignedWarehouseLoc', location_id, name);
                };
                scope.onDeleteWahrehouse = function (warehouseId) {
                    $rootScope.$broadcast('onDeleteWarehouse', warehouseId);
                };
            },

            templateUrl: function (element, attr) {
                return attr.templateUrl || 'angular-wh-loc-picker.html';
            },
        };
    });
})();

angular.module('angular-wh-loc-picker').run([
    '$templateCache',
    function ($templateCache) {
        'use strict';
        $templateCache.put(
            'angular-wh-loc-picker.html',
            '<div>\
    <style>\
    .progress {\
        width:85%;\
        height:16px;\
        border:1px solid #ccc;\
        position:relative;\
        display:inline-block;\
        cursor:pointer;\
        float:left;\
    }\
    .progress:after {\
        position:absolute;\
        content:"\\A";\
        background:#28BD50;\
        color:#28BD50;\
        top:0; bottom:0;\
        left:0;\
        -webkit-animation: prog-filler 0.5s ease-in-out;\
        -moz-animation: prog-filler 0.5s ease-in-out;\
        animation: prog-filler 0.5s ease-in-out;\
    }\
    .progress span {\
        position: absolute;\
        top: 0;\
        z-index: 2;\
        color: black; /* Change according to needs */\
        text-align: center;\
        width: 100%;\
    }\
    .card {\
        min-width: 210px;\
        position: relative;\
        display: -webkit-box;\
        display: -ms-flexbox;\
        display: flex;\
        -webkit-box-orient: vertical;\
        -webkit-box-direction: normal;\
        -ms-flex-direction: column;\
        flex-direction: column;\
        word-wrap: break-word;\
        background-color: #fbfbfb;\
        background-clip: border-box;\
        border: 0 solid rgba(0,0,0,.125);\
        margin-bottom: 29px;\
        -webkit-box-shadow: 0 1px 0 rgba(0,0,0,.05);\
        box-shadow: 0 1px 0 rgba(0,0,0,.05);\
        border-radius: 1px;\
    }\
    .active-card{\
        box-shadow: inset 1px 0 0 #dadce0, inset -1px 0 0 #dadce0, 0 1px 2px 0 rgba(60,64,67,.3), 0 1px 3px 1px rgba(60,64,67,.15);\
        z-index: 1;\
    }\
    .card-header {\
        font-size: 1.385rem;\
        font-weight: 400;\
        color: #3d3d3d;\
        padding: 10px 0;\
        margin: 0 20px;\
        background-color: transparent;\
        border-bottom: 0 solid rgba(0,0,0,.125);\
    }\
    .card-header .tools .icon {\
        display: inline-block;\
        vertical-align: middle;\
        cursor: pointer;\
        color: #3d3d3d;\
        text-align: center;\
        float: right;\
        margin-left:5px;\
    }\
    .card-body {\
        -webkit-box-flex: 1;\
        -ms-flex: 1 1 auto;\
        flex: 1 1 auto;\
        padding: 1rem;\
    }\
    .card-subtitle {\
        display: block;\
        font-size: 1rem;\
        margin-top: 0;\
        line-height: 1;\
        margin-bottom: 4px;\
        color: #878787;\
    }\
    .chart-legend {\
        position:absolute;\
        width:100%;\
        bottom:10%;\
    }\
    .chart-legend li {\
        cursor:pointer;\
        margin: 10px 4px;\
    }\
    .chart-legend li span {\
        position: relative;\
        padding: 4px 6px;\
        border-radius: 4px;\
        color: white;\
        z-index: 2;\
        font-size:13px;\
    }\
    .noselect {\
        -webkit-touch-callout: none;\
        -webkit-user-select: none;\
        -khtml-user-select: none;\
        -moz-user-select: none;\
        -ms-user-select: none;\
        user-select: none;\
    }\
    .chart-legend ol,.chart-legend ul {\
        list-style: none;\
        margin:0;\
        padding:0;\
        text-align:center;\
    }\
    .chart-legend li {\
        display: inline-table;\
    }\
    .edit-warehouse-btn{\
        background: none;\
        color: black;\
        font-size: 16px;\
        padding-left: 5px;\
        padding-right: 2px;\
        vertical-align: bottom;\
        margin-left: -25px;\
        cursor: pointer;\
    }\
    .usedLoc{\
        cursor: pointer;\
        background-color: #28BD50;\
    }\
    .usedSymb{\
        background-color: #28BD50;\
    }\
    .cellSymb{\
        display:inline-block;\
        height: 16px;\
        width: 16px;\
        margin-right:5px;\
        vertical-align: middle;\
    }\
    .lc-table {\
        width: 100%;\
        overflow:auto;\
    }\
    .td-loc{\
        border: 1px solid #ccc;\
        padding: 10px;\
        margin-top:10px;\
        min-width: 70px;\
        width: 70px;\
        height: 35px !important;\
        border-radius: 5px;\
    }\
    .icon-server{\
        cursor: pointer;\
        font-size: 16px;\
    }\
    .row-label, .col-label{\
        font-size: 11px;\
    }\
    .row-label {\
        width: 2px;\
        padding-right: 3px;\
    }\
    .col-height{\
        padding-top: 2px;\
        height: 5px;\
    }\
    #table-wrapper {\
      position:relative;\
      overflow:auto;\
    }\
    @-webkit-keyframes prog-filler {\
        0% {\
            width:0;\
        }\
    }\
    @-moz-keyframes prog-filler {\
        0% {\
            width:0;\
        }\
    }\
    @keyframes prog-filler {\
        0% {\
            width:0;\
        }\
    }\
    .active-card .title {\
        font-weight: bold;\
    }\
    .active-card .card-header .icon-server {\
        visibility: hidden;\
    }\
    .rec-title{\
        font-size: 17px;\
        font-weight:bold;\
        padding-left:24px;\
    }\
    .sourcingClose{\
        -webkit-appearance: none;\
        padding: 0;\
        cursor: pointer;\
        background: 0 0;\
        border: 0;\
        float: right;\
        font-size: 21px;\
        font-weight: 700;\
        line-height: 1;\
        color: #000;\
        text-shadow: 0 1px 0 #fff;\
        opacity: .2;\
    }\
    .selectOptions li a{\
        padding: 4px 16px;\
    }\
    .selectMenu{\
        left: -63px !important;\
        top: 16px;\
    }\
    .addSelectColor{\
        background: #FFFFCC;\
    }\
    .loc-table{\
        border-spacing: 5px;\
        border-collapse: separate;\
    }\
    .loc-table .usedLoc{\
        border: 0;\
    }\
    .usedLocSelection{\
        padding: 12px 20px !important;\
    }\
    .sdw-bottom {\
        box-shadow: 0 4px 6px -5px #333;\
    }\
    </style>\
    <div style="margin-top:15px;">\
        <div class="col-md-3 col-lg-2">\
            <div ng-repeat="warehouse in warehouses">\
                <div class="card" ng-class="{\'active-card\': selectedWarehouse == warehouse}">\
                    <div class="card-header">\
                      <span class="title col-sm-6">{{warehouse.code}} / {{warehouse.name}}</span>\
                      <span class="tools">\
                        <span style="margin-left: 25px;" ng-if="edit == \'true\'" class="icon" title="Edit Warehouse" ng-click="onEditWahrehouse(warehouse.id)"><i class="icon-pencil-1 list-btn edit-warehouse-btn" ng-click="onOrderlineEdit(5925)"></i></span>\
                        <span  ng-if="edit == \'true\'" class="icon" title="Delete Warehouse" ng-click="onDeleteWahrehouse(warehouse.id)"><i class="icon-trash list-btn delte-warehouse-btn" ng-click="onOrderlineEdit(5925)"></i></span>\
                        <span class="icon" title="View racks" ng-if="warehouse.totalLoc != 0" ng-click="viewRacks(warehouse)"><i class="icon-server cursorPointer" style="font-size: 16px;"></i></span>\
                      </span>\
                    </div>\
                    <div class="card-body" style="margin-top: -10px;">\
                        <div style="padding: 10px 0;">\
                            <canvas class="wh-chart" style="cursor: pointer;" ng-click="viewRacks(warehouse)" width="100%"></canvas>\
                        </div>\
                        <div ng-if="warehouse == selectedWarehouse && racks.length > 0">\
                            <div ng-repeat="rack in racks" style="clear:both;">\
                                <div class="title">{{rack.code}}</div>\
                                    <style>.progress-r{{rack.id}}:after { width:{{getPercentage(rack.usedLoc, rack.totalLoc)}};}</style>\
                                    <div class="progress progress-r{{rack.id}}" ng-click="viewRackLocation(rack.id, rack.code, rack.usedLoc, rack.totalLoc)">\
                                        <span>{{getPercentage(rack.usedLoc, rack.totalLoc)}}</span>\
                                    </div>\
                                    <div class="tools" style="display:inline-block;margin-left:5px;">\
                                        <span ng-if="selectedRackCode != rack.code" class="icon" title="View rack locations" ng-click="viewRackLocation(rack.id, rack.code, rack.usedLoc, rack.totalLoc)">\
                                            <i class="icon-server"></i>\
                                        </span>\
                                    </div>\
                                </div>\
                            </div>\
                        </div>\
                    </div>\
                </div>\
            </div>\
        <div class="col-md-9 col-lg-10" style="padding-left: 13px;">\
            <div ng-show="rackLocations.length > 0">\
                <div style="margin-bottom: 5px; display: inline-block; width: 100%;">\
                    <div style="float:left"><span class="rec-title">{{selectedWarehouse.code}}/{{selectedRackCode}}</span>\
                        <span ng-if="edit==\'false\'" class="icon-info" id="warehouseLocSelectInfoId" style="font-size:16px;color: #1174da;cursor: pointer;"></span>\
                        <span ng-if="edit==\'false\'" id="locSelectInfo" style="font-size:12px;display:none"><div class="left-align"><p style="padding-top:5px;">Click on cell to select warehouse location.</p></div></span>\
                        {{selectWarehouseLocTooltip()}}\
                    </div>\
                  <div style="float:right">\
                    <span ng-if="(selectedRackCode == \'Locations(Without Rack)\') && (totalLoc > 1000)">Top 1000 locations are shown</span>\
                    <span class="usedSymb cellSymb" style="margin-left:10px"></span><span>{{usedRacLoc}} in use</span>\
                    <span class="cellSymb" style="border:solid 1px #000;margin-left:10px"></span><span>{{emptyRacLoc}} empty locations</span>\
                  </div>\
                </div>\
                <div id="table-wrapper">\
                    <table class="loc-table">\
                        <tr ng-repeat="row in rackLocations track by $index">\
                            <td class="row-label" ng-style="rackId == \'0\' && {\'padding-right\':\'23px\'}"><span ng-if="rackId != 0">R{{$index+1}}</span></td>\
                            <td id="l_{{col[0].id}}" title="{{col[0].name}}" ng-style="edit==\'false\' && {\'cursor\':\'pointer\'}" ng-repeat="col in row track by $index" ng-click="stockOnWarehouseLoc(col[0].id, col[0].name)" ng-class="{ \'usedLoc\' : isCellUsed(col[0].name)}" class="td-loc sdw-bottom">\
                                {{tippyTooltip(col[0].id)}}\
                                <ul class="nav navbar-nav navbar-right">\
                                <li class="selectOptions l_{{col[0].id}}">\
                                <ul class="selectMenu dropdown-menu dropdown-usermenu pull-right" style="width:180px;border-bottom-left-radius: 0;border-bottom-right-radius: 0;">\
                                    <li>\
                                      <a class="usedLocSelection" ng-click="selectLoc(col[0].id, col[0].name)"> Select location </a>\
                                      <a class="usedLocSelection" ng-click="showWarehouseLoc(col[0].id, col[0].name)"> Show stock on this location</a>\
                                    </li>\
                                </ul>\
                            </ul>\
                            </td>\
                        </tr>\
                        <tr ng-if="rackId != 0">\
                            <td></td>\
                            <td class="col-height" ng-repeat="i in getNumber(column) track by $index"><span>C{{$index+1}}<span></td>\
                        </tr>\
                    </table>\
                </div>\
            </div>\
        </div>\
    </div>'
        );
    },
]);
