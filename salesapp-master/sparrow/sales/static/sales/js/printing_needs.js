function printingNeedsInit(data) {
    sparrow.registerCtrl(
      "printingNeedsCtrl",
      function (
        $scope,
        $rootScope,
        $route,
        $routeParams,
        $compile,
        $uibModal,
        DTOptionsBuilder,
        DTColumnBuilder,
        $templateCache,
        ModalService
      ) {
        var partner_type = $routeParams.type;
        var canAddReport = data.permissions["can_add_report"];
        var canUpdateReport = data.permissions["can_update_report"];
        $scope.modalopened = false;
        $scope.TotalRows = 0
        var config = {
          pageTitle: "Printing needs",
          topActionbar: {
            extra: [
              {
                id: "btnUserHistory",
                multiselect: false,
                function: showLog,
              },
              {
                id: "btnCustomerLogin",
                multiselect: false,
                function: onCustomerLogin,
              },
              {
                id: "btnCustomerProfile",
                multiselect: false,
                function: onCustomerProfile,
              },
              {
                id: "btnExport",
                function: exportCustomersData,
              },
              {
                id: "btnAddNewReport",
                multiselect: false,
                function: onAddNewReport,
              },
              {
                id: "btnIncludedSteam",
                multiselect: false,
                function: onIncludedSteam,
              },
            ],
          },
          listing: [
            {
              index: 1,
              search: {
                params: [
                  { key: "customer_name", name: "Customer name" },
                  { key: "y_orders", name: "Orders more than" },
                  { key: "y_months", name: "Last order in Month(s)" },
                  { key: "country", name: "Country" },
                  { key: "region", name: "Region" },
                  {
                    key: "included_steam",
                    name: "Included in steam",
                    type: "list",
                    options: ["Yes", "No"],
                  },
                ],
              },
              url: "/sales/printing_need_search/",
              crud: true,
              scrollBody: true,
              columns: [
                {
                  name: "data__customer_name",
                  title: "Customer name",
                  sort: false,
                  renderWith: function (data, type, full, meta) {
                    $scope.TotalRows = full.TotalRows
                    $("#total_display").text($scope.TotalRows)
                    return (
                      '<span>\
                                     <a class="link-iframe-item" ng-click="onEditLink(\'/b/iframe_index/#/sales/customer/customers/' +
                      full.customer_id +
                      "/" +
                      canAddReport +
                      "/" +
                      canUpdateReport +
                      "/" +
                      "','" +
                      data +
                      "'," +
                      null +
                      ", " +
                      false +
                      ", " +
                      1 +
                      "," +
                      true +
                      ')">' +
                      data +
                      "</a>\
                                 </span>"
                    );
                  },
                },
                { name: "customer_id", title: "Customer ID", sort: false },
                {
                  name: "data__contact_firstname",
                  title: "First name",
                  sort: false,
                },
                {
                  name: "data__contact_lastname",
                  title: "Last name",
                  sort: false,
                },
                { name: "data__contact_email", title: "Email", sort: false },
                // { name: "data__contact_phone", title: "Phone", sort: false },
                {
                  name: "data__company_phone",
                  title: "Company phone",
                  sort: false,
                },
                { name: "data__company_city", title: "City", sort: false },
                { name: "data__company_country", title: "Country", sort: false },
                {
                  name: "data__registration_date",
                  title: "Registration date",
                  sort: false,
                },
                {
                    name: "number_of_PCB_orders",
                    title: "Number of PCB orders",
                    sort: false,
                  },
                  {
                    name: "number_of_Assembly_orders",
                    title: "Number of Assembly orders",
                    sort: false,
                  },
                {
                  name: "included_steam",
                  title: "Included in Steam",
                  sort: false,
                  renderWith: function (data, type, full, meta) {
                    if (data == true) {
                      return "Yes";
                    } else {
                      return "No";
                    }
                  },
                },
              ],
            },
          ],
        };
  
        $scope.searchCustomers = function (event) {//searchPrintingNeeds
          config.listing[0].postData = {};
          if ($("#dt_register_date").find("span").html() != "") {
            var register_date_ctrl = $("#dt_register_date").data(
              "daterangepicker"
            );
            var register_start_date = moment(register_date_ctrl.startDate).format(
              "DD/MM/YYYY h:mm:ss a"
            );
            var register_end_date = moment(register_date_ctrl.endDate).format(
              "DD/MM/YYYY h:mm:ss a"
            );
            config.listing[0].postData = {
              register_start_date: register_start_date,
              register_end_date: register_end_date,
            };
          }
  
          $scope.reloadData(1, config.listing[0]);
        };
  
        $("#app_container").on("change", ".magic-checkbox", function (e) {
          var val = $(this).is(":checked") ? "checked" : "unchecked";
          if (val == "checked") {
            var selectedId = $scope.getSelectedIds(1)[0];
            var rowData = $.grep(
              $scope["dtInstance" + 1].DataTable.data(),
              function (n, i) {
                return n.id == selectedId;
              }
            );
            if (rowData[0].included_steam) {
              $("#btnIncludedSteam").val("Excluded from steam");
            } else {
              $("#btnIncludedSteam").val("Included in steam");
            }
          } else {
            $("#btnIncludedSteam").val("Included in steam");
          }
        });
  
        function onIncludedSteam() {
          if (getRowData().included_steam == true) {
            included_steam = "0";
          } else {
            included_steam = "1";
          }
          var postData = {
            customer_id: getRowData().customer_id,
            included_steam: included_steam,
          };
          if (getRowData().included_steam) {
            sparrow.showConfirmDialog(
              ModalService,
              "Are you sure you want to exclude selected customer from steam?",
              "Exclude from steam",
              function (confirm) {
                if (confirm) {
                  sparrow.post(
                    "/sales/update_included_steam/",
                    postData,
                    false,
                    function (data) {
                      if (data.code == 1) {
                        $scope.reloadData(1);
                        $("#btnIncludedSteam").val("Included in steam");
                        sparrow.showMessage(
                          "appMsg",
                          sparrow.MsgType.Success,
                          "Customer excluded from steam.",
                          10
                        );
                      }
                    }
                  );
                }
              }
            );
          } else {
            sparrow.post(
              "/sales/update_included_steam/",
              postData,
              false,
              function (data) {
                if (data.code == 1) {
                  $scope.reloadData(1);
                  sparrow.showMessage(
                    "appMsg",
                    sparrow.MsgType.Success,
                    "Customer included in steam.",
                    10
                  );
                }
              }
            );
          }
        }
  
        function showLog(scope) {
          var selectedId = $scope.getSelectedIds(1)[0];
          var rowData = $.grep(
            $scope["dtInstance1"].DataTable.data(),
            function (n, i) {
              return n.id == selectedId;
            }
          );
          window.location.hash =
            "#/auditlog/logs/userprofile/" +
            selectedId +
            "?title=" +
            rowData[0].first_name;
        }
  
        function onCustomerLogin() {
          if (data.permissions["can_do_customer_login"] == false) {
            sparrow.showMessage(
              "appMsg",
              sparrow.MsgType.Error,
              "You do not have permission to perform this action",
              10
            );
            return;
          }
          var selectedId = $scope.getSelectedIds(1)[0];
          var rowData = $.grep(
            $scope["dtInstance1"].DataTable.data(),
            function (n, i) {
              return n.id == selectedId;
            }
          );
          var customer_id = rowData[0].customer_id;
          var ord_nr = "None";
          // window.open("/sales/customer_login/"+customer_id+"/");
          var from = "CUSTOMER";
          sparrow.post(
            "/sales/validate_customer_login/",
            { customer_id: customer_id, from: from },
            false,
            function (data) {
              if (data.code == "1") {
                if (data.msg == "") {
                  var ec_user_id = data.ec_user_id;
  
                  window.open(
                    "/sales/customer_login/" +
                      ord_nr +
                      "/" +
                      from +
                      "/" +
                      ec_user_id +
                      "/" +
                      customer_id +
                      "/"
                  );
                } else {
                  function openmodal() {
                    if ($scope.modalopened) return;
                    var templateUrl = "/sales/validate_customer_login_modal/";
                    var customerLoginValidateModal = $uibModal.open({
                      templateUrl: templateUrl,
                      controller: "customerLoginValidateModalCtrl",
                      scope: $scope,
                      size: "md",
                      backdrop: false,
                      resolve: {
                        dataModal: function () {
                          return {
                            entity_nr: ord_nr,
                            msg: data.msg,
                            customer_id: customer_id,
                            from: from,
                            ec_user_id: data.ec_user_id,
                          };
                        },
                      },
                    });
                    $scope.modalopened = true;
                    $scope.ConfirmMessage = data.msg;
                    customerLoginValidateModal.closed.then(function () {
                      $scope.modalopened = false;
                      $templateCache.remove(templateUrl);
                    });
                  }
                  openmodal();
                }
              }
            }
          );
        }
        function closeSurveyReportCallback() {
          $scope.modalopened = false;
        }
        function onCustomerProfile() {
          if ($scope.modalopened) return;
          var selectedId = $scope.getSelectedIds(1)[0];
          var rowData = $.grep(
            $scope["dtInstance1"].DataTable.data(),
            function (n, i) {
              return n.id == selectedId;
            }
          );
          var customer_id = rowData[0].customer_id;
  
          $scope.onEditLink(
            "/b/iframe_index/#/sales/customer/customers/" +
              customer_id +
              "/" +
              canAddReport +
              "/" +
              canUpdateReport +
              "/",
            "Customer profile",
            dialogCloseCallback,
            false,
            "+1+",
            true
          );
  
          $scope.modalopened = true;
        }
  
        function dialogCloseCallback() {
          $scope.modalopened = false;
        }
  
        function exportCustomersData() {
          var postParam = Object.assign(
            {},
            $scope["searchParams1"],
            config.listing[0].postData
          );
          sparrow.downloadData("/sales/export_customers/", postParam);
          }
        function selectedRowLength() {
          if ($route.current.controller != "customersCtrl") {
            return false;
          }
          if (
            $scope.getSelectedIds(1).length == 0 ||
            $scope.getSelectedIds(1).length > 1
          ) {
            sparrow.showMessage(
              "appMsg",
              sparrow.MsgType.Error,
              "Please select one invoice",
              10
            );
            return false;
          }
  
          return true;
        }
        function getRowData() {
          var selectedId = $scope.getSelectedIds(1)[0];
          var rowData = $.grep(
            $scope["dtInstance1"].DataTable.data(),
            function (n, i) {
              return n.id == selectedId;
            }
          );
          return rowData[0];
        }
        function onAddNewReport() {
          if (data.permissions["can_add_report"]) {
            if ($scope.modalopened) return;
            $scope.onEditLink(
              "/b/iframe_index/#/sales/survey_report/" +
                getRowData().customer_id +
                "/0/true/PRINTING_NEEDS/",
              "Report",
              closeSurveyReportCallback,
              true,
              1
            );
            $scope.modalopened = true;
            resizeDialogue();
          } else {
            sparrow.showMessage(
              "appMsg",
              sparrow.MsgType.Error,
              "You do not have permission to perform this action",
              10
            );
            return;
          }
        }
        function resizeDialogue() {
          var iFrameID = document.getElementById("iframe_model0");
          iFrameID.style.width = "60%";
          iFrameID.style.left = "20%";
          iFrameID.style.overflowY = "hidden";
        }
        $scope.$on('advanced-searchbox:removedSearchParam', function(event, searchParameter, tableIndex, cacheParam) {
          $("#total_display").text(0)
        });
        Mousetrap.bind("e p", function () {
          if (selectedRowLength() == true) {
            onCustomerProfile();
          }
        });
        Mousetrap.bind("l", function () {
          if (selectedRowLength() == true) {
            onCustomerLogin();
          }
        });
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
  
  printingNeedsInit();
  