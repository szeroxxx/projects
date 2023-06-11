function orders_with_qta_reportsInit() {
  sparrow.registerCtrl(
    "orders_with_qta_reportsCtrl",
    function (
      $scope,
      $rootScope,
      $route,
      $routeParams,
      $compile,
      DTOptionsBuilder,
      DTColumnBuilder,
      $templateCache,
      ModalService
    ) {
      $scope.addViewButtons("");
      var config = {
        pageTitle: "Orders with QTA / No QTA",
        topActionbar: {
          extra: [
            {
              id: "btnExport",
              function: onExport,
            },
          ],
        },
        listing: [
          {
            index: 1,
            url: "/qualityapp/search_orders_with_qta/",
            paging: true,
            scrollBody: true,
            columns: [
              {
                name: "order_date",
                title: "Order date",
              },
              {
                name: "order_number",
                title: "qualityapp ID",
              },
              {
                name: "customer_order_nr",
                title: "Order number",
              },
              {
                name: "qta",
                title: "QTA",
              },
            ],
          },
        ],
      };

      function onExport() {
        if (data.permissions["can_export_orders_with_qta"] == false) {
          sparrow.showMessage("appMsg", sparrow.MsgType.Error, "You do not have permission to perform this action", 3);
          return;
        }
        var display_data = $.grep(
          $scope["dtInstance1"].DataTable.data(),
          function (n, i) {
            return n.id;
          }
        );
        if(display_data != ""){
          order_by_ = display_data[0].sort_col
        }
        else{
          order_by_ = "-id"
        }
        sparrow.downloadData("/qualityapp/exports_orders_with_qta/", {
          start: $rootScope.start,
          length: $rootScope.length,
          order_by: order_by_,
        });
      };

      sparrow.setup(
        $scope,
        $rootScope,
        $route,
        $compile,
        DTOptionsBuilder,
        DTColumnBuilder,
        $templateCache,
        config,
        ModalService
      );
    }
  );
}
orders_with_qta_reportsInit();