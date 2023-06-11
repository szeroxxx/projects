function newCustomersInit(data) {
  sparrow.registerCtrl(
    "newCustomersCtrl",
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
      $scope.modalopened = false;

      var config = {
        pageTitle: "New customers",
        topActionbar: {
          extra: [
            {
              id: "btnEditProfile",
              multiselect: false,
              function: onbtnEditProfile,
            },
            {
              id: "btnCreditLimit",
              multiselect: false,
              function: onCreditLimit,
            },
            {
              id: "btnIncludedSteam",
              multiselect: false,
              function: onIncludedSteam,
            },
            {
              id: "btnAddNewReport",
              multiselect: false,
              function: onAddNewReport,
            },
          ],
        },
        listing: [
          {
            index: 1,
            search: {
              params: [
                {
                  key: "company_craeted_date",
                  name: "Company created date",
                  type: "datePicker",
                },
                { key: "company_name", name: "Customer name" },
                { key: "handling_com", name: "Handling company name" },
                { key: "root_company", name: "Root company" },
                { key: "email", name: "Email" },
                { key: "country", name: "Country" },
                { key: "acc_manager", name: "Account manager" },
                {
                  key: "included_steam",
                  name: "Included in steam",
                  type: "list",
                  options: ["Yes", "No"],
                },
                {
                  key: "company_dup",
                  name: "Company duplicate",
                  type: "list",
                  options: ["Yes", "No"],
                },
              ],
            },
            url: "/sales/new_customers_search/",
            crud: true,
            paging: true,
            scrollBody: true,
            columns: [
              { name: "company_name", title: "Customer name" },
              { name: "vat_number", title: "VAT nr" },
              { name: "handling_com", title: "Handling company" },
              { name: "root_company", title: "Root company" },
              { name: "code", title: "Code" },
              { name: "email", title: "Email" },
              { name: "country", title: "Country" },
              { name: "acc_manager", title: "Account manager" },
              { name: "created_date", title: "Created date" },
              {
                name: "included_steam",
                title: "Included in Steam",
                renderWith: function (data, type, full, meta) {
                  if (data == true) {
                    return "Yes";
                  } else {
                    return "No";
                  }
                },
              },
              // Put the column (company_dup) at last of listing.if you want to add new column add before this
              {
                name: "company_dup",
                title: "Company duplicate",
                renderWith: function (data, type, full, meta) {
                  var rows = document
                    .getElementById("newCustomerTable")
                    .getElementsByTagName("tbody")[0]
                    .getElementsByTagName("tr");
                  setTimeout(function () {
                    for (i = 0; i < rows.length; i++) {
                      cells = rows[i].getElementsByTagName("td");
                      if (cells[cells.length - 1].innerHTML == "Yes") {
                        rows[i].style.background = "#ffcccb";
                      }
                    }
                  }, 100);
                  return full.company_dup;
                },
              },
            ],
          },
        ],
      };

      config.listing[0].columns.forEach(columnSort);
      function columnSort(obj) {
        obj.sort = false;
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
          customer_id: getRowData().id,
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

      function onCreditLimit() {
        if (data.permissions["can_update_new_customer_credit_limit"]) {
          var templateUrl = "/finance/credit_limit/" + getRowData().id + "/";
          function openmodal() {
            if ($scope.modalopened) return;
            var creditLimitModal = $uibModal.open({
              templateUrl: templateUrl,
              controller: "creditLimitModalCtrl",
              scope: $scope,
              size: "md",
              backdrop: false,
            });
            $scope.modalopened = true;
            $scope.creditLimitModalTitle =
              "Credit limit - " + getRowData().company_name;
            creditLimitModal.closed.then(function () {
              $scope.modalopened = false;
              $templateCache.remove(templateUrl);
            });
          }
          openmodal();
        } else {
          sparrow.showMessage(
            "appMsg",
            sparrow.MsgType.Error,
            "You do not have permission to perform this action",
            10
          );
        }
      }

      function onbtnEditProfile(scope) {
        var canAddReport = data.permissions["can_add_new_customers_report"];
        var canUpdateReport =
          data.permissions["can_update_new_customers_report"];
        if ($scope.modalopened) return;
        $scope.onEditLink(
          "/b/iframe_index/#/sales/customer/new_customers/" +
            getRowData().id +
            "/" +
            canAddReport +
            "/" +
            canUpdateReport +
            "/",
          "Customer profile - " + getRowData().company_name,
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

      function selectedRowLength() {
        if ($route.current.controller != "newCustomersCtrl") {
          return false;
        }
        if (
          $scope.getSelectedIds(1).length == 0 ||
          $scope.getSelectedIds(1).length > 1
        ) {
          sparrow.showMessage(
            "appMsg",
            sparrow.MsgType.Error,
            "Please select one customer",
            10
          );
          return false;
        }
        return true;
      }
      Mousetrap.bind("e p", function () {
        if (selectedRowLength() == true) {
          onbtnEditProfile();
        }
      });
      Mousetrap.bind("c l", function () {
        if (selectedRowLength() == true) {
          onCreditLimit();
        }
      });
      Mousetrap.bind("a r", function () {
        if (selectedRowLength() == true) {
          onAddNewReport();
        }
      });

      function closeSurveyReportCallback() {
        $scope.modalopened = false;
      }

      window.addEventListener("resize", function () {
        var iFrameID = document.getElementById("iframe_model0");
        if (iFrameID) {
          iFrameID.style.overflowY = "auto";
        }
      });

      function onAddNewReport() {
        if (data.permissions["can_add_new_customers_report"]) {
          if ($scope.modalopened) return;
          $scope.onEditLink(
            "/b/iframe_index/#/sales/survey_report/" +
              getRowData().id +
              "/0/true/CUST_SURVEY/",
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
        }
      }

      function resizeDialogue() {
        var iFrameID = document.getElementById("iframe_model0");
        iFrameID.style.width = "60%";
        iFrameID.style.left = "20%";
        iFrameID.style.overflowY = "hidden";
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

newCustomersInit();
