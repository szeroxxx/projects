function callReportInit(data) {
  sparrow.registerCtrl(
    "callReportCtrl",
    function (
      $scope,
      $rootScope,
      $route,
      $routeParams,
      $compile,
      DTOptionsBuilder,
      DTColumnBuilder,
      $templateCache,
      ModalService,
      $location
    ) {
      var canAddReport = data.permissions["can_add_customers_report"];
      var canUpdateReport = data.permissions["can_update_customers_report"];
      var config = {
        pageTitle: "Call reports",
        topActionbar: {
          extra: [],
        },
        listing: [
          {
            index: 1,
            search: {
              params: [
                { key: "FirstName", name: "First name" },
                { key: "LastName", name: "Last name" },
                { key: "CreatedBy", name: "Created by" },
                { key: "CustomerName", name: "Customer name" },
                { key: "ReportName", name: "Report name" },
                { key: "Country", name: "Country" },
                { key: "Region", name: "Region" },
                {
                  key: "created_date__date",
                  name: "Report from date till date",
                  type: "datePicker",
                },
                {
                  key: "registered_date__date",
                  name: "Registered from date till date",
                  type: "datePicker",
                },
                {
                  key: "ec_action_needed",
                  name: "Eurocircuits action needed",
                  type: "list",
                  options: ["Yes", "No"],
                },
              ],
            },
            url: "/sales/all_call_reports_search/",
            crud: false,
            paging: true,
            columns: [
              {
                name: "CustomerName",
                title: "Customer name",
                renderWith: function (data, type, full, meta) {
                  return (
                    '<a title="View call report" ng-click="onbtnEditProfile(' +
                    full.customer_id +
                    ",'" +
                    full.CustomerName +
                    "')\">" +
                    full.CustomerName +
                    "</a>"
                  );
                },
              },
              { name: "FirstName", title: "First name" },
              { name: "LastName", title: "Last name" },
              { name: "Email", title: "Email" },
              {
                name: "ec_action_needed",
                title: "Eurocircuits action needed",
              },
              {
                name: "ReportName",
                title: "Report name",
                sort: false,
                renderWith: function (data, type, full, meta) {
                  return (
                    '<a title="View call report" ng-click="onSurveyReport(' +
                    full.relation_id +
                    ",'" +
                    full.ReportName +
                    "','" +
                    full.report_type +
                    "','" +
                    full.customer_id +
                    "')\">" +
                    full.ReportName +
                    "</a>"
                  );
                },
              },
              { name: "Country", title: "Country" },
              { name: "Region", title: "Region" },
              { name: "Registered_on", title: "Registered on" },
              { name: "Created_by", title: "Created by" },
              { name: "Created_on", title: "Created on" },
            ],
          },
        ],
      };

      $scope.onbtnEditProfile = function (customerId, CustomerName) {
        $scope.onEditLink(
          "/b/iframe_index/#/sales/customer/call_reports/" +
            customerId +
            "/" +
            canAddReport +
            "/" +
            canUpdateReport +
            "/",
          "Customer profile - " + CustomerName,
          false,
          false,
          "+1+",
          true
        );
      };

      $scope.onSurveyReport = function (relationID, reportName, reportType ,customer_id) {
        $scope.onEditLink(
          "/b/iframe_index/#/sales/survey_report/" +
            customer_id +
            "/" +
            relationID +
            "/false/"+reportType+'/',
          "Report",
          false,
          true,
          -1
        );
        resizeDialogue();
      };

      window.addEventListener("resize", function () {
        var iFrameID = document.getElementById("iframe_model0");
        if (iFrameID) {
          iFrameID.style.overflowY = "auto";
        }
      });

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
callReportInit();
