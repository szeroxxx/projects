function loggedInUserInit() {
  sparrow.registerCtrl(
    "loggedInUserInitCtrl",
    function (
      $scope,
      $rootScope,
      $route,
      $routeParams,
      $uibModal,
      $compile,
      DTOptionsBuilder,
      DTColumnBuilder,
      $templateCache,
      ModalService
    )
    {
       var config = {
         pageTitle: "Logged in Operators",
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
           ],
         },
         listing: [
           {
             index: 1,
             search: {
               params: [
                 {
                   key: "reserved_order_id__customer_order_nr",
                   name: "Order number",
                 },
                 { key: "user_name", name: "Operator name" },
                 { key: "first_name", name: "First name" },
                 { key: "last_name", name: "Last name" },
                 { key: "reserved_order_id__company__name", name: "Customer" },
                 { key: "reserved_order_id__order_number", name: "PWS ID" },
               ],
             },
             url: "/pws/logged_in_user_data/",
             crud: true,
             scrollBody: true,
             paging: true,
             columns: [
               {
                 name: "operator_id__user__first_name",
                 title: "First name",
               },
               {
                 name: "operator_id__user__last_name",
                 title: "Last name",
               },
               {
                 name: "operator_id__user__username",
                 title: "Operator name",
               },
               {
                 name: "logged_in_time",
                 title: "Login time",
               },
               {
                 name: "reserved_order_id__order_number",
                 title: "PWS ID",
               },
               {
                 name: "reserved_order_id__customer_order_nr",
                 title: "Order number",
               },
               {
                 name: "reserved_order_id__company__name",
                 title: "Customer",
               },
               {
                 name: "reserved_order_id__service__name",
                 title: "Service",
               },
               {
                 name: "reserved_order_id__order_status",
                 title: "Process",
               },
               {
                 name: "reserved_on",
                 title: "Reserved on",
                 sort: false,
               },
             ],
           },
         ],
       };

      function onExport() {
        if (data.permissions["can_export_logged_in_users"] == false) {
          sparrow.showMessage(
            "appMsg",
            sparrow.MsgType.Error,
            "You do not have permission to perform this action",
            3
          );
          return;
        }
         var selectedIds = $scope.getSelectedIds(1).join([(separator = ",")]);
         var search_parameter = $rootScope.searchParts;
         const myArray = selectedIds.split(",");
         var numberArray = myArray.map(Number);
         selectedIds_ = []
         var rowData = $.grep(
            $scope["dtInstance1"].DataTable.data(),
            function (n, i) {
               for (let i = 0; i < numberArray.length; i++) {
                if(n.id == numberArray[i]){
                    selectedIds_.push(n.login_id)
                }
              }
              return selectedIds_;
            }
          );
         var display_data = $.grep(
          $scope["dtInstance1"].DataTable.data(),
          function (n, i) {
            return n.id;
          }
        );

        var first_name = "";
        var last_name = "";
        var user_name = "";
        var reserved_order_id__company__name = "";
        var reserved_order_id__order_number = "";
        var reserved_order_id__customer_order_nr = "";

        if (search_parameter) {
          if ("First name" in search_parameter) {
            var first_name = search_parameter["First name"];
          }
          if ("Last name" in search_parameter) {
            var last_name = search_parameter["Last name"];
          }
          if ("Operator name" in search_parameter) {
            var user_name = search_parameter["Operator name"];
          }
          if ("Customer" in search_parameter) {
            var reserved_order_id__company__name = search_parameter["Customer"];
          }
          if ("PWS ID" in search_parameter) {
            var reserved_order_id__order_number = search_parameter["PWS ID"];
          }
          if ("Order number" in search_parameter) {
            var reserved_order_id__customer_order_nr = search_parameter["Order number"];
          }
        }

        if (!selectedIds) {
          selectedIds = "";
        }

         if(display_data != ""){
          order_by_ = display_data[0].sort_col
          }
          else{
            order_by_ = "-logged_in_time";
            sparrow.showMessage("appMsg", sparrow.MsgType.Error, "No data available for export", 3);
            return
          }

         sparrow.downloadData("/pws/exports_logged_in_operator/", {
            ids: selectedIds_,
            first_name: first_name,
            last_name: last_name,
            user_name: user_name,
            reserved_order_id__company__name: reserved_order_id__company__name,
            reserved_order_id__order_number: reserved_order_id__order_number,
            reserved_order_id__customer_order_nr: reserved_order_id__customer_order_nr,
            start: $rootScope.start,
            length: $rootScope.length,
            order_by: order_by_,
         });
      };

      function onAllDataExport() {
        if (data.permissions["can_export_logged_in_users"] == false) {
          sparrow.showMessage(
            "appMsg",
            sparrow.MsgType.Error,
            "You do not have permission to perform this action",
            3
          );
          return;
        }
         var selectedIds = $scope.getSelectedIds(1).join([(separator = ",")]);
         var search_parameter = $rootScope.searchParts;
         const myArray = selectedIds.split(",");
         var numberArray = myArray.map(Number);
         selectedIds_ = []
         var rowData = $.grep(
            $scope["dtInstance1"].DataTable.data(),
            function (n, i) {
               for (let i = 0; i < numberArray.length; i++) {
                if(n.id == numberArray[i]){
                    selectedIds_.push(n.login_id)
                }
              }
              return selectedIds_;
            }
          );
         var display_data = $.grep(
          $scope["dtInstance1"].DataTable.data(),
          function (n, i) {
            return n.login_id;
          }
        );

        var first_name = "";
        var last_name = "";
        var user_name = "";
        var reserved_order_id__company__name = "";
        var reserved_order_id__order_number = "";
        var reserved_order_id__customer_order_nr = "";

        if (search_parameter) {
          if ("First name" in search_parameter) {
            var first_name = search_parameter["First name"];
          }
          if ("Last name" in search_parameter) {
            var last_name = search_parameter["Last name"];
          }
          if ("Operator name" in search_parameter) {
            var user_name = search_parameter["Operator name"];
          }
          if ("Customer" in search_parameter) {
            var reserved_order_id__company__name = search_parameter["Customer"];
          }
          if ("PWS ID" in search_parameter) {
            var reserved_order_id__order_number = search_parameter["PWS ID"];
          }
          if ("Order number" in search_parameter) {
            var reserved_order_id__customer_order_nr = search_parameter["Order number"];
          }
        }

         if (!selectedIds) {
           selectedIds = "";
         }

         if(display_data != ""){
          order_by_ = display_data[0].sort_col
          }
          else{
            order_by_ = "-logged_in_time";
            sparrow.showMessage("appMsg", sparrow.MsgType.Error, "No data available for export", 3);
            return
          }

         sparrow.downloadData("/pws/exports_logged_in_operator/", {
            ids: selectedIds_,
            first_name: first_name,
            last_name: last_name,
            user_name: user_name,
            reserved_order_id__company__name: reserved_order_id__company__name,
            reserved_order_id__order_number: reserved_order_id__order_number,
            reserved_order_id__customer_order_nr: reserved_order_id__customer_order_nr,
            start: 0,
            length: display_data[0].recordsTotal,
            order_by: order_by_,
         });
      };

      Mousetrap.reset()
      Mousetrap.bind('shift+x',onExport)
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
loggedInUserInit();
