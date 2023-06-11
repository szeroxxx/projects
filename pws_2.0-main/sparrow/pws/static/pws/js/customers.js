function customersInit() {
  sparrow.registerCtrl(
    "customersCtrl",
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
    ) {
      $scope.ScreenChildData = [];
      var customer_set_data = null;
      var config = {
        pageTitle: "Customers",
        topActionbar: {
          add: {
            url: "/#/pws/customer/",
          },
          delete: {
            url: "/pws/delete_customer/",
          },
          edit: {
            url: "/#/pws/customer/",
          },
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
              id: "setOrderScreen",
              multiselect: false,
              function: setOrderScreen,
            },
            {
              id: "btnHistory",
              multiselect: false,
              function: showLog,
            },
            {
              id: "placeOrder",
              multiselect: false,
              function: placeOrder,
            },
          ],
        },
        listing: [
          {
            index: 1,
            search: {
              params: [
                { key: "customer", name: "Customer name" },
                { key: "gen_mail", name: "General email" },
                { key: "ord_rec_mail", name: "Order receive mail" },
                { key: "ord_exc_gen_mail", name: "Exception mail to leader" },
                { key: "ord_exc_rem_mail", name: "Exception mail to customer" },
                { key: "ord_comp_mail", name: "Order completion mail" },
                {
                  key: "is_active",
                  name: "Active",
                  type: "list",
                  options: ["Yes", "No"],
                },
                {
                  key: "is_req_files",
                  name: "File required?",
                  type: "list",
                  options: ["Yes", "No"],
                },
                {
                  key: "is_send_attachment",
                  name: "Send prepared data in attachment",
                  type: "list",
                  options: ["Yes", "No"],
                },
                {
                  key: "is_exp_file_attachment",
                  name: "Send exception file in attachment",
                  type: "list",
                  options: ["Yes", "No"],
                },
              ],
            },
            url: "/pws/search_customer/",
            crud: true,
            scrollBody: true,
            columns: [
              {
                name: "name",
                title: "Customer name",
                renderWith: function (data, type, full, meta) {
                  return (
                    '<span><a ng-click="onEditCustomer(' +
                    full.id +
                    ')">' +
                    data +
                    "</a></span>"
                  );
                },
              },
              {
                name: "gen_mail",
                title: "General email",
              },
              {
                name: "ord_rec_mail",
                title: "Order receive mail",
              },
              {
                name: "ord_exc_gen_mail",
                title: "Exception mail to leader",
              },
              {
                name: "ord_exc_rem_mail",
                title: "Exception mail to customer",
              },
              {
                name: "ord_comp_mail",
                title: "Order completion mail",
              },
              {
                name: "mail_from",
                title: "Mail from",
              },
              {
                name: "int_exc_from",
                title: "Internal exception from",
              },
              {
                name: "int_exc_to",
                title: "Internal exception to",
              },
              {
                name: "int_exc_cc",
                title: "Internal exception cc",
              },
              {
                name: "no_of_jobs",
                title: "Number of jobs",
              },
              {
                name: "is_active",
                title: "Active",
              },
              {
                name: "is_req_files",
                title: "File required",
              },
              {
                name: "is_send_attachment",
                title: "Send prepared data in attachment",
              },
              {
                name: "is_exp_file_attachment",
                title: "Send exception file in attachment",
              },
            ],
          },
        ],
      };
      function placeOrder() {
        if(data.permissions["can_customer_place_order"] == false){
          sparrow.showMessage('appMsg', sparrow.MsgType.Error, "You do not have permission to perform this action", 5)
          return;
        }
        var selectedId = $scope.getSelectedIds(1)[0];
        var rowData = $.grep(
          $scope["dtInstance1"].DataTable.data(),
          function (n, i) {
            return n.id == selectedId;
          }
        );
        $("#order_place").modal("show");
        var company_name = rowData[0]["id"]
        setAutoLookup("id_customer_user", "/lookups/company_user/","", true, true, "", "", "", company_name);
      };

      $scope.orderPlace = function(){
        sparrow.postForm(
          {
              id: "",
          },
          $('#frmPlace'),
          $scope,
          function (data) {
            if(data.id != null){
              var customerUserId = data.id
              var selectedId = $scope.getSelectedIds(1);
              var rowData = $.grep(
                $scope["dtInstance1"].DataTable.data(),
                function (n, i) {
                  return n.id == selectedId;
                }
              );
              window.location.href = "#/pws/place_order/" + rowData[0].id + "/" + customerUserId + "/";
            }
          }
        );
      };

      $scope.closePlaceOrder = function(){
        $route.reload();
        $('.modal-backdrop').remove();
      };

      function showLog(scope) {
        var selectedId = $scope.getSelectedIds(1)[0];
        if(selectedId == undefined ){
          sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please select record', 2);
          return;
        }
        var rowData = $.grep(
          $scope["dtInstance1"].DataTable.data(),
          function (n, i) {
            return n.id == selectedId;
          }
        );
        window.location.hash = "#/auditlog/logs/company/" + selectedId + "?title=" + rowData[0].name;
      };

      function onExport() {
        if (data.permissions["can_export_customers"] == false) {
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
        var display_data = $.grep(
          $scope["dtInstance1"].DataTable.data(),
          function (n, i) {
            return n.id;
          }
        );

        var customer = "";
        var gen_mail = "";
        var ord_rec_mail = "";
        var ord_exc_gen_mail = "";
        var ord_exc_rem_mail = "";
        var ord_comp_mail = "";
        var is_active = "";
        var is_req_files = "";
        var is_send_attachment = "";
        var is_exp_file_attachment = "";

        if (search_parameter) {
          if ("Customer name" in search_parameter) {
            var customer = search_parameter["Customer name"];
          }
          if ("General email" in search_parameter) {
            var gen_mail = search_parameter["General email"];
          }
          if ("Order receive mail" in search_parameter) {
            var ord_rec_mail = search_parameter["Order receive mail"];
          }
          if ("Exception mail to leader" in search_parameter) {
            var ord_exc_gen_mail = search_parameter["Exception mail to leader"];
          }
          if ("Exception mail to customer" in search_parameter) {
            var ord_exc_rem_mail = search_parameter["Exception mail to customer"];
          }
          if ("Order completion mail" in search_parameter) {
            var ord_comp_mail = search_parameter["Order completion mail"];
          }
          if ("Active" in search_parameter) {
            var is_active = search_parameter["Active"];
          }
          if ("File required?" in search_parameter) {
            var is_req_files = search_parameter["File required?"];
          }
          if ("Send prepared data in attachment" in search_parameter) {
            var is_send_attachment = search_parameter["Send prepared data in attachment"];
          }
          if ("Send exception file in attachment" in search_parameter) {
            var is_exp_file_attachment = search_parameter["Send exception file in attachment"];
          }
        }

        if (!selectedIds) {
          selectedIds = "";
        }

        if(display_data != ""){
          order_by_ = display_data[0].sort_col
        }
        else{
          order_by_ = "-id"
          sparrow.showMessage("appMsg", sparrow.MsgType.Error, "No data available for export", 3);
          return
        }

        sparrow.downloadData("/pws/exports_customer/", {
          ids: selectedIds,
          customer: customer,
          gen_mail: gen_mail,
          ord_rec_mail: ord_rec_mail,
          ord_exc_gen_mail: ord_exc_gen_mail,
          ord_exc_rem_mail: ord_exc_rem_mail,
          ord_comp_mail: ord_comp_mail,
          is_active: is_active,
          is_req_files: is_req_files,
          is_send_attachment: is_send_attachment,
          is_exp_file_attachment: is_exp_file_attachment,
          start: $rootScope.start,
          length: $rootScope.length,
          order_by: order_by_,
        });
      };

      function onAllDataExport() {
        if (data.permissions["can_export_customers"] == false) {
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
        var display_data = $.grep(
          $scope["dtInstance1"].DataTable.data(),
          function (n, i) {
            return n.id;
          }
        );

        var customer = "";
        var gen_mail = "";
        var ord_rec_mail = "";
        var ord_exc_gen_mail = "";
        var ord_exc_rem_mail = "";
        var ord_comp_mail = "";
        var is_active = "";
        var is_req_files = "";
        var is_send_attachment = "";
        var is_exp_file_attachment = "";

        if (search_parameter) {
          if ("Customer name" in search_parameter) {
            var customer = search_parameter["Customer name"];
          }
          if ("General email" in search_parameter) {
            var gen_mail = search_parameter["General email"];
          }
          if ("Order receive mail" in search_parameter) {
            var ord_rec_mail = search_parameter["Order receive mail"];
          }
          if ("Exception mail to leader" in search_parameter) {
            var ord_exc_gen_mail = search_parameter["Exception mail to leader"];
          }
          if ("Exception mail to customer" in search_parameter) {
            var ord_exc_rem_mail = search_parameter["Exception mail to customer"];
          }
          if ("Order completion mail" in search_parameter) {
            var ord_comp_mail = search_parameter["Order completion mail"];
          }
          if ("Active" in search_parameter) {
            var is_active = search_parameter["Active"];
          }
          if ("File required?" in search_parameter) {
            var is_req_files = search_parameter["File required?"];
          }
          if ("Send prepared data in attachment" in search_parameter) {
            var is_send_attachment = search_parameter["Send prepared data in attachment"];
          }
          if ("Send exception file in attachment" in search_parameter) {
            var is_exp_file_attachment = search_parameter["Send exception file in attachment"];
          }
        }

        if (!selectedIds) {
          selectedIds = "";
        }

        if(display_data != ""){
          order_by_ = display_data[0].sort_col
        }
        else{
          order_by_ = "-id"
          sparrow.showMessage("appMsg", sparrow.MsgType.Error, "No data available for export", 3);
          return
        }

        sparrow.downloadData("/pws/exports_customer/", {
          ids: selectedIds,
          customer: customer,
          gen_mail: gen_mail,
          ord_rec_mail: ord_rec_mail,
          ord_exc_gen_mail: ord_exc_gen_mail,
          ord_exc_rem_mail: ord_exc_rem_mail,
          ord_comp_mail: ord_comp_mail,
          is_active: is_active,
          is_req_files: is_req_files,
          is_send_attachment: is_send_attachment,
          is_exp_file_attachment: is_exp_file_attachment,
          start: 0,
          length: display_data[0].recordsTotal,
          order_by: order_by_,
        });
      };

      $scope.onEditCustomer = function (id) {
        window.location.href = "#/pws/customer/" + id + "/";
      };

      function setOrderScreen() {
        if(data.permissions["can_set_order_screen"] == false){
          sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'You do not have permission to perform this action', 5)
          return;
        }
        var selectedId = $scope.getSelectedIds(1);
        var rowData = $.grep(
          $scope["dtInstance1"].DataTable.data(),
          function (n, i) {
            return n.id == selectedId;
          }
        );
        $("#setScreenTitle").text(
          "Set order screen ( " + rowData[0].name + " )"
        );
        sparrow.post(
          "/pws/set_order_screen/" + rowData[0].id + "/",
          {},
          false,
          function (data) {
            $("#setScreenBody").html(data);
            $("#setScreenModel").modal("show");
          },
          "html"
        );
      };

      $scope.saveOrderScreenMaster = function () {
        var selectedId = $scope.getSelectedIds(1);
        var select_customer = 0
        var child_data = JSON.stringify($scope.ScreenChildData)
        var rowData = $.grep(
          $scope["dtInstance1"].DataTable.data(),
          function (n, i) {
            return n.id == selectedId;
          }
        );
        var company_id = $("#id_company_set_screen_data").magicSuggest();
        var comp_id = company_id.getSelection();
        if(comp_id.length !=0 && customer_set_data!= null){
          var select_customer = customer_set_data
          var child_data = JSON.stringify([])
        }
        if ($('#id_customer_checkbox').is(":checked") && comp_id.length ==0){
          sparrow.showMessage("appMsg", sparrow.MsgType.Error, "Please select atleast one customer.", 3);
          return;
        }
        if ($('#id_customer_checkbox').is(":unchecked")){
          var select_customer = 0
          var child_data = JSON.stringify($scope.ScreenChildData)
        }
        sparrow.postForm(
          {
            company_id: rowData[0].id,
            child_data: child_data,
            select_customer: select_customer
          },
          $("#idOrderScreenMaster"),
          $scope,
          function (data) {
            if (data.code == 1) {
              $scope.reloadData(1);
              $scope.ScreenChildData = []
              var company_id = $("#id_company_set_screen_data").magicSuggest();
              company_id.clear()
              company_id.disable()
              $('#id_customer_checkbox').prop("checked", false)
              setTimeout(function () {$("#chk_1" + "_" + rowData[0].id).trigger("click").prop("checked", true);}, 10);
              setTimeout(function () {$('#setOrderScreen').click();}, 10);
              window.location.hash = "#/pws/customers/";
            }
          }
        );
      };

      $("#id_customer_checkbox").on("click", function () {
        var company_id = $('#id_company_set_screen_data').magicSuggest()
        if ($('#id_customer_checkbox').is(":checked"))
        {
          company_id.enable()
        }
        if ($('#id_customer_checkbox').is(":unchecked"))
        {
          company_id.disable()
          company_id.clear()
          var selectedId = $scope.getSelectedIds(1);
          var rowData = $.grep(
            $scope["dtInstance1"].DataTable.data(),
            function (n, i) {
              return n.id == selectedId;
            }
          );
          $("#setScreenTitle").text("Set order screen ( " + rowData[0].name + " )");
          sparrow.post(
            "/pws/set_order_screen/" + rowData[0].id + "/",
            {},
            false,
            function (data) {
              $("#setScreenBody").html(data);
              $("#setScreenModel").modal("show");
            },
            "html"
          );
        }
      });

      $scope.applyOrderScreeChild = function () {
        $("td").on("click", function () {$(this).closest("tr").find(".hrchy-dt-checkboxes").attr("checked", true);});
        var form_data = $("#idOrderScreenParamsForm").serializeArray();
        var selected_value = [];
        var parent = null;
        var default_value2 = null;
        var default_value1 = null;
        var default_value3 = null;
        var valueSelect = null;
        for (var i in form_data) {
          if (form_data[i].name == "parent") {
            parent = parseInt(form_data[i].value);
          }
          if (form_data[i].name == "default_value2") {
            default_value2 = form_data[i].value;
          }
          if (form_data[i].name == "default_value3") {
            default_value3 = "Yes";
          }
          if (form_data[i].name == "default_value1") {
            default_value1 = form_data[i].value;
            valueSelect = default_value1.split(",");
            default_value1 = valueSelect[0];
            valueSelect = valueSelect[1];
          }
          if (form_data[i].name == "select") {
            selected_value.push(form_data[i].value);
          }
        }
        if (default_value2) {
          $("#" + parent).html(default_value2);
        } else if (valueSelect) {
          $("#" + parent).html(valueSelect);
        } else if (default_value3 == "Yes") {
          $("#" + parent).html(default_value3);
        } else {
          $("#" + parent).html("");
        }

        $scope.ScreenChildData.push({
          parent_id: parent,
          select: selected_value,
          default_value2: default_value2,
          default_value1: default_value1,
          default_value3: default_value3,
        });
        $("#setScreenChildModel").modal("hide");
      };

      $scope.setScreenData = function () {
        var selectedId = $scope.getSelectedIds(1);
        var rowData = $.grep(
          $scope["dtInstance1"].DataTable.data(),
          function (n, i) {
            return n.id == selectedId;
          }
        );
        var company_id = $("#id_company_set_screen_data").magicSuggest();
        var comp_id = company_id.getSelection();
        if(comp_id.length !=0){
          var company_id = comp_id[0]["id"]
          customer_set_data = company_id
          $scope.reloadData(1);
          setTimeout(function () {$("#chk_1" + "_" + rowData[0].id).trigger("click").prop("checked", true);}, 10);
          $("#setScreenTitle").text("Set order screen ( " + rowData[0].name + " )");
          sparrow.post(
            "/pws/set_order_screen_copy/" + company_id + "/",
            {
              select_customer : rowData[0].id,
            },
            false,
            function (data) {
              $("#setScreenBody").html(data);
              $("#setScreenModel").modal("show");
            },
            "html"
          );
        }
        if($('#id_customer_checkbox').is(":checked") && comp_id.length ==0){
            sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please select customer', 3);
        }
      };

      $scope.closeSetOrderScreen = function(){
        var company_id = $("#id_company_set_screen_data").magicSuggest();
        company_id.clear()
        company_id.disable()
        $('#id_customer_checkbox').prop("checked", false)
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
customersInit();
