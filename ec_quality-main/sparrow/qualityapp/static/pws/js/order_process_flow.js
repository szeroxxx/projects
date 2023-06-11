function order_flowsInit() {
  sparrow.registerCtrl(
    "order_process_flowCtrl",
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
      var searchObj = {
        params: [
          { key: "company__name", name: "Customer" },
          { key: "service__name", name: "Services" },
        ],
      };
      var config = {
        pageTitle: "Order Process Flow",
        topActionbar: {
            extra: [
              {
                id: "btnHistory",
                multiselect: false,
                function: showHistory,
              },
            ],

        },
        listing: [
          {
            index: 1,
            search: searchObj,
            url: "/qualityapp/order_flow_search/",
            crud: true,
            paging: 2,
            scrollBody: true,
            columns: [
              {
                name: "company__name",
                title: "Customer name",
                renderWith: function (data, type, full, meta) {
                  let name = full.company__name;
                  return (
                    '<span><a ng-click="onUpdateOrderFlow(' +
                    full.id +
                    ",'" +
                    name +
                    "')\">" +
                    data +
                    "</a></span>"
                  );
                },
              },

              {
                name: "service__name",
                title: "Services",
                sort: false,
              },
            ],
          },
        ],
      };
      $scope.SaveServiceProcess = function () {
          sparrow.postForm(
              {},
              $("#frmSaveServiceProcess"),
              $scope,
              function (data) {
                if (data.code == 1) {
                  $('#serviceProcess').modal('hide');
                  $scope.reloadData(1);
                }
              }
            );
        };

      $scope.onUpdateOrderFlow = function (id, name = null) {
        $("#title").text("Order Process Flow - " + name);
        sparrow.post(
          "/qualityapp/order_flow/" + id + "/",
          {},
          false,
          function (data) {
            $("#editServiceProcess").html(data);
            $("#serviceProcess").modal("show");
            $("#id_company_name").val(name);
            $("#id_company_id").val(id);
          },
          "html"
        );
      };
      function showHistory(scope) {
        var selectedId = $scope.getSelectedIds(1)[0];
        var rowData = $.grep(
          $scope["dtInstance1"].DataTable.data(),
          function (n, i) {
            return n.id == selectedId;
          }
        );
        if(selectedId){
            window.location.hash =
              "#/auditlog/logs/orderflowmapping/" +
              selectedId +
              "?title=" +
              rowData[0].company__name;
        }
        else{
            sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please select record', 2);
        }
      }
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

order_flowsInit();
