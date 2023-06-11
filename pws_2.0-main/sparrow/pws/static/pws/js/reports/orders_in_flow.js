function orders_in_flowInit(data) {
  sparrow.registerCtrl(
    "orders_in_flowCtrl",
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
      $scope.uid = [];
      var config = {
        pageTitle: "Orders in flow",
        topActionbar: {
          extra: [
            {
              id: "btnExport",
              function: onExport,
            },
            {
              id: "btnAllDataExport",
              function: onAllDataExport,
            },
            {
              id: "btnRefresh",
              function: onRefresh,
            },
          ],
        },
        listing: [
          {
            index: 1,
            pagging: true,
            url: "/pws/search_orders_in_flow/",
            crud: false,
            scrollBody: true,
            columns: [
              {
                name: "company__name",
                title: "Customer",
              },
              {
                name: "schematic",
                title: "Schematic",
                renderWith: viewschematic,
              },
              {
                name: "footprint",
                title: "Footprint",
                renderWith: viewfootprint,
              },
              {
                name: "placement",
                title: "Placement",
                renderWith: viewplacement,
              },
              {
                name: "routing",
                title: "Routing",
                renderWith: viewrouting,
              },
              {
                name: "gerber_release",
                title: "Gerber Release",
                renderWith: viewgerber_release,
              },
              {
                name: "analysis",
                title: "Analysis",
                renderWith: viewanalysis,
              },
              {
                name: "incoming",
                title: "Incoming",
                renderWith: viewincoming,
              },
              {
                name: "BOM_incoming",
                title: "BOM incoming",
                renderWith: viewBOM_incoming,
              },
              {
                name: "SI",
                title: "SI",
                renderWith: viewSI,
              },
              {
                name: "SICC",
                title: "SICC",
                renderWith: viewSICC,
              },
              {
                name: "BOM_CC",
                title: "BOM CC",
                renderWith: viewBOM_CC,
              },
              {
                name: "FQC",
                title: "FQC",
                renderWith: viewFQC,
              },
              {
                name: "panel",
                title: "Panel",
                renderWith: viewpanel,
              },
              {
                name: "upload_panel",
                title: "Upload Panel",
                renderWith: viewupload_panel,
              },
              {
                name: "exception",
                title: "Exception",
                renderWith: viewexception,
              },
            ],
          },
        ],
      };


      function onExport() {
        if (data.permissions["can_export_order_in_flow"] == false) {
          sparrow.showMessage(
            "appMsg",
            sparrow.MsgType.Error,
            "You do not have permission to perform this action",
            3
          );
          return;
        }
        var display_data = $.grep(
        $scope["dtInstance1"].DataTable.data(),
        function (n, i) {
          return n.company__id;
        }
        );
        if(display_data != ""){
          order_by_ = display_data[0].sort_col
        }
        else{
          order_by_ = "-id"
          sparrow.showMessage("appMsg", sparrow.MsgType.Error, "No data available for export", 3);
          return
        }
        sparrow.downloadData("/pws/exports_orders_in_flow/", {
          start: $rootScope.start,
          length: $rootScope.length,
          order_by: order_by_,
        });
      };

      function onAllDataExport() {
        if (data.permissions["can_export_order_in_flow"] == false) {
          sparrow.showMessage(
            "appMsg",
            sparrow.MsgType.Error,
            "You do not have permission to perform this action",
            3
          );
          return;
        }
        var display_data = $.grep(
        $scope["dtInstance1"].DataTable.data(),
        function (n, i) {
          return n.company__id;
        }
        );
        if(display_data != ""){
          order_by_ = display_data[0].sort_col
        }
        else{
          order_by_ = "-id"
          sparrow.showMessage("appMsg", sparrow.MsgType.Error, "No data available for export", 3);
          return
        }
        sparrow.downloadData("/pws/exports_orders_in_flow/", {
          start: 0,
          length: display_data[0].recordsTotal,
          order_by: order_by_,
        });
      };

      function onRefresh(){
        $route.reload();
      };

      function viewschematic(data, type, full, meta) {
        if (data == "0") {
          return data;
        }else{
          return (
            '<span><a ng-click="viewdesign(' + "'" + full.company__name + "'," + "'" + "schematic" + "'" + ' )">' + data + '</a></span>'
          );
        }
      };

      function viewfootprint(data, type, full, meta) {
        if (data == "0") {
          return data;
        }else{
          return (
            '<span><a ng-click="viewdesign(' + "'" + full.company__name + "'," + "'" + "footprint" + "'" + ' )">' + data + '</a></span>'
          );
        }
      };

      function viewplacement(data, type, full, meta) {
        if (data == "0") {
          return data;
        }else{
          return (
            '<span><a ng-click="viewdesign(' + "'" + full.company__name + "'," + "'" + "placement" + "'" + ' )">' + data + '</a></span>'
          );
        }
      };

      function viewrouting(data, type, full, meta) {
        if (data == "0") {
          return data;
        }else{
          return (
            '<span><a ng-click="viewdesign(' + "'" + full.company__name + "'," + "'" + "routing" + "'" + ' )">' + data + '</a></span>'
          );
        }
      };

      function viewgerber_release(data, type, full, meta) {
        if (data == "0") {
          return data;
        }else{
          return (
            '<span><a ng-click="viewdesign(' + "'" + full.company__name + "'," + "'" + "gerber_release" + "'" + ' )">' + data + '</a></span>'
          );
        }
      };
      $scope.viewdesign = function (company, status) {
        sparrow.setStorage('company_search', company, 365);
        window.location.href = "/b/#/job_processing/design/?state=" + status;
      };

      function viewanalysis(data, type, full, meta) {
        if (data == "0"){
          return data;
        }else{
          return (
            '<span><a ng-click="viewpreparation(' + "'" + full.company__name + "'," + "'" + "analysis" + "'" + ' )">' + data + '</a></span>'
          );
        }
      };

      function viewincoming(data, type, full, meta) {
        if (data == "0"){
          return data;
        }else{
          return (
            '<span><a ng-click="viewpreparation(' + "'" + full.company__name + "'," + "'" + "incoming" + "'" + ' )">' + data + '</a></span>'
          );
        }
      };

      function viewBOM_incoming(data, type, full, meta) {
        if (data == "0"){
          return data;
        }else{
          return (
            '<span><a ng-click="viewpreparation(' + "'" + full.company__name + "'," + "'" + "BOM_incoming" + "'" + ' )">' + data + '</a></span>'
          );
        }
      };

      function viewSI(data, type, full, meta) {
        if (data == "0"){
          return data;
        }else{
          return (
            '<span><a ng-click="viewpreparation(' + "'" + full.company__name + "'," + "'" + "SI" + "'" + ' )">' + data + '</a></span>'
          );
        }
      };

      function viewSICC(data, type, full, meta) {
        if (data == "0"){
          return data;
        }else{
          return (
            '<span><a ng-click="viewpreparation(' + "'" + full.company__name + "'," + "'" + "SICC" + "'" + ' )">' + data + '</a></span>'
          );
        }
      };

      function viewBOM_CC(data, type, full, meta) {
        if(data == "0"){
          return data;
        }else{
          return (
            '<span><a ng-click="viewpreparation(' + "'" + full.company__name + "'," + "'" + "BOM_CC" + "'" + ' )">' + data + '</a></span>'
          );
        }
      };

      function viewFQC(data, type, full, meta) {
        if(data == "0"){
          return data;
        }else{
          return (
            '<span><a ng-click="viewpreparation(' + "'" + full.company__name + "'," + "'" + "FQC" + "'" + ' )">' + data + '</a></span>'
          );
        }
      };
      $scope.viewpreparation = function (company, status) {
        sparrow.setStorage('company_search', company, 365);
        window.location.href = "/b/#/job_processing/preparation/?state=" + status;
      };

      function viewpanel(data, type, full, meta) {
        if(data == "0"){
          return data;
        }else{
          return (
            '<span><a ng-click="viewpanel_preparation(' + "'" + full.company__name + "'," + "'" + "panel" + "'" + ' )">' + data + '</a></span>'
          );
        }
      };

      function viewupload_panel(data, type, full, meta) {
        if(data == "0"){
          return data;
        }else{
          return (
            '<span><a ng-click="viewpanel_preparation(' + "'" + full.company__name + "'," + "'" + "upload_panel" + "'" + ' )">' + data + '</a></span>'
          );
        }
      };
      $scope.viewpanel_preparation = function (company, status) {
        sparrow.setStorage('company_search', company, 365);
        window.location.href = "/b/#/job_processing/panel_preparation/?state=" + status;
      };

      function viewexception(data, type, full, meta) {
        if(data == "0"){
          return data;
        }else{
          return (
            '<span><a ng-click="viewexception_(' + "'" + full.company__name + "'," + "'" + full.company__name + "'" + ' )">' + data + '</a></span>'
          );
        }
      };
      $scope.viewexception_ = function (company) {
        sparrow.setStorage('company_search', company, 365);
        sparrow.setStorage("process_search", "exception", 365);
        window.location.href = "/b/#/orders/";
      };

      Mousetrap.reset();
      Mousetrap.bind("shift+x", onExport);
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
orders_in_flowInit();
