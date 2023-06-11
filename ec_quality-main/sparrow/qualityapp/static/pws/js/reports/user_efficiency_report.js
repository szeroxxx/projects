function user_efficiency_reportInit() {
  sparrow.registerCtrl(
    "user_efficiency_reportCtrl",
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
      $scope.reload_op = null;

      var config = {
        pageTitle: "User efficiency reports",
        listing: [
          {
            index: 1,
            pagging: true,
            scrollBody: true,
            postData: {
              today_date_: "",
            },
            crud: false,
            url: "/qualityapp/search_user_efficiency_reports/",
            columns: [
              {
                name: "operator__user__username",
                title: "Username",
              },
              {
                name: "user_role",
                title: "User role",
              },
              {
                name: "pi",
                title: "PI",
              },
              {
                name: "working_pi",
                title: "Working PI",
              },
              {
                name: "manual_days",
                title: "Worked days",
              },
              {
                name: "total_efficiency",
                title: "Total efficiency",
              },
              {
                name: "minimum_efficiency",
                title: "Minimum efficiency",
                renderWith: function (value, type, full, meta) {
                  if(data.permissions["can_edit"] == true){
                    return (
                      '<input value="'+ value +'" style="border:none; width:50px" id="id_minimum_efficiency_' + full.operator + '" ' +
                      'type="number" min="0" oninput="this.value = Math.abs(this.value)">'
                    );
                  }else{
                    return ('<span>'+ value +'</span>')
                  }
                },
              },
              {
                name: "target_efficiency",
                title: "Target efficiency",
                renderWith: function (value, type, full, meta) {
                  if(data.permissions["can_edit"] == true){
                    return (
                      '<input value="'+ value +'" style="border:none; width:50px" id="id_target_efficiency_' + full.operator + '" ' +
                      'type="number" min="0" oninput="this.value = Math.abs(this.value)">'
                    );
                  }else{
                    return ('<span>'+ value +'</span>')
                  }
                },
              },
              {
                name: "additional_remarks",
                title: "Additional remarks",
                renderWith: viewRemarkLink,
                class: "remarks",
                sort: false,
              },
              {
                name: "rejection",
                title: "Rejection",
              },
              {
                name: "remarks",
                title: "Remarks ",
              },
              {
                name: "date1",
                title: "Date 1",
              },
              {
                name: "date2",
                title: "Date 2",
              },
              {
                name: "date3",
                title: "Date 3",
              },
              {
                name: "date4",
                title: "Date 4",
              },
              {
                name: "date5",
                title: "Date 5",
              },
              {
                name: "date6",
                title: "Date 6",
              },
              {
                name: "date7",
                title: "Date 7",
              },
              {
                name: "date8",
                title: "Date 8",
              },
              {
                name: "date9",
                title: "Date 9",
              },
              {
                name: "date10",
                title: "Date 10",
              },
              {
                name: "date11",
                title: "Date 11",
              },
              {
                name: "date12",
                title: "Date 12",
              },
              {
                name: "date13",
                title: "Date 13",
              },
              {
                name: "date14",
                title: "Date 14",
              },
              {
                name: "date15",
                title: "Date 15",
              },
              {
                name: "date16",
                title: "Date 16",
              },
              {
                name: "date17",
                title: "Date 17",
              },
              {
                name: "date18",
                title: "Date 18",
              },
              {
                name: "date19",
                title: "Date 19",
              },
              {
                name: "date20",
                title: "Date 20",
              },
              {
                name: "date21",
                title: "Date 21",
              },
              {
                name: "date22",
                title: "Date 22",
              },
              {
                name: "date23",
                title: "Date 23",
              },
              {
                name: "date24",
                title: "Date 24",
              },
              {
                name: "date25",
                title: "Date 25",
              },
              {
                name: "date26",
                title: "Date 26",
              },
              {
                name: "date27",
                title: "Date 27",
              },
              {
                name: "date28",
                title: "Date 28",
              },
              {
                name: "date29",
                title: "Date 29",
              },
              {
                name: "date30",
                title: "Date 30",
              },
              {
                name: "date31",
                title: "Date 31",
              },
            ],
          },
          {
            index: 2,
            pagging: true,
            scrollBody: true,
            postData: {
              today_date_: "",
            },
            crud: false,
            url: "/qualityapp/search_user_efficiency_reports/",
            columns: [
              {
                name: "created_on__date",
                title: "Performance date",
              },
              {
                name: "first_shift",
                title: "First shift",
              },
              {
                name: "knowledge_leaders_first",
                title: "Knowledge leaders",
              },
              {
                name: "second_shift",
                title: "Second shift",
              },
              {
                name: "knowledge_leaders_second",
                title: "Knowledge leaders",
              },
              {
                name: "third_shift",
                title: "Third shift",
              },
              {
                name: "knowledge_leaders_third",
                title: "Knowledge leaders",
              },
              {
                name: "total_point",
                title: "Efficiency points",
              },
            ],
          },
          {
            index: 3,
            pagging: true,
            scrollBody: true,
            postData: {
              today_date_: "",
            },
            crud: false,
            url: "/qualityapp/search_user_efficiency_reports/",
            columns: [
              {
                name: "operator__user__username",
                title: "Username",
              },
              {
                name: "user_role",
                title: "User role",
              },
              {
                name: "pi",
                title: "PI",
              },
              {
                name: "working_pi",
                title: "Working PI",
              },
              {
                name: "manual_days",
                title: "Worked days",
              },
              {
                name: "total_efficiency",
                title: "Total efficiency",
              },
              {
                name: "minimum_efficiency",
                title: "Minimum efficiency",
              },
              {
                name: "target_efficiency",
                title: "Target efficiency",
              },
              {
                name: "company__name",
                title: "Company",
              },
              {
                name: "rejection",
                title: "Rejection",
              },
              {
                name: "remarks",
                title: "Remarks ",
              },
              {
                name: "date1",
                title: "Date 1",
              },
              {
                name: "date2",
                title: "Date 2",
              },
              {
                name: "date3",
                title: "Date 3",
              },
              {
                name: "date4",
                title: "Date 4",
              },
              {
                name: "date5",
                title: "Date 5",
              },
              {
                name: "date6",
                title: "Date 6",
              },
              {
                name: "date7",
                title: "Date 7",
              },
              {
                name: "date8",
                title: "Date 8",
              },
              {
                name: "date9",
                title: "Date 9",
              },
              {
                name: "date10",
                title: "Date 10",
              },
              {
                name: "date11",
                title: "Date 11",
              },
              {
                name: "date12",
                title: "Date 12",
              },
              {
                name: "date13",
                title: "Date 13",
              },
              {
                name: "date14",
                title: "Date 14",
              },
              {
                name: "date15",
                title: "Date 15",
              },
              {
                name: "date16",
                title: "Date 16",
              },
              {
                name: "date17",
                title: "Date 17",
              },
              {
                name: "date18",
                title: "Date 18",
              },
              {
                name: "date19",
                title: "Date 19",
              },
              {
                name: "date20",
                title: "Date 20",
              },
              {
                name: "date21",
                title: "Date 21",
              },
              {
                name: "date22",
                title: "Date 22",
              },
              {
                name: "date23",
                title: "Date 23",
              },
              {
                name: "date24",
                title: "Date 24",
              },
              {
                name: "date25",
                title: "Date 25",
              },
              {
                name: "date26",
                title: "Date 26",
              },
              {
                name: "date27",
                title: "Date 27",
              },
              {
                name: "date28",
                title: "Date 28",
              },
              {
                name: "date29",
                title: "Date 29",
              },
              {
                name: "date30",
                title: "Date 30",
              },
              {
                name: "date31",
                title: "Date 31",
              },
            ],
          },
        ],
      };

      $("#saveChanges").on("click", function () {
        if (data.permissions["can_edit"] == false) {
          sparrow.showMessage("appMsg", sparrow.MsgType.Error, "You do not have permission to perform this action", 3);
          return;
        }
        var display_data = $.grep(
          $scope["dtInstance1"].DataTable.data(),
          function (n, i) {
            return n.operator;
          }
        );
        if (display_data.length == 0) {
          return;
        };
        min_and_tar_efficiency_list = [];
        for (let i = 0; i < display_data.length; i++) {
          min_and_tar_efficiency_list.push(
            {
              operator_id : display_data[i]["operator"],
              minimum_efficiency : $("#id_minimum_efficiency_" + display_data[i]["operator"]).val(),
              target_efficiency : $("#id_target_efficiency_" + display_data[i]["operator"]).val()
            }
          )
        };
        sparrow.post(
          "/qualityapp/update_user_efficiency_report/",
          {
            min_and_tar_efficiency_list: JSON.stringify(min_and_tar_efficiency_list),
            select_date: display_data[0]["select_date"],
          },
          false,
          function (data) {
            if (data.code == 1) {
              sparrow.showMessage("appMsg", sparrow.MsgType.Success, data.msg, 3);
            } else {
              sparrow.showMessage("appMsg", sparrow.MsgType.Error, data.msg, 3);
            }
            $scope.reloadData(1);
          }
        );
      });

      $(document).keypress(function (event) {
        if (event.which == "13") {
          event.preventDefault();
        }
      });

      function viewRemarkLink(data, type, full, meta) {
        return '<span><a ng-click="viewOrderDetails(' + full.operator + ",'" + full.select_date + "','" + full.operator__user__username + '\')">' + data + '</a></span>';
      };
      $scope.viewOrderDetails = function (operator_id, select_date, operator_name) {
        $scope.onEditLink('/b/iframe_index/#/qualityapp/user_efficiency_add_remark/' + operator_id + " " + select_date, 'User name - ' + operator_name, closeIframeCallback, '', '', true);
      };
      function closeIframeCallback() {
        $scope.reloadData(1);
        return;
      };
      var select_field = $("#id_select").magicSuggest();
      $(select_field).on("selectionchange", function (e, m) {
        $("#btnExportShiftWise").prop("disabled", true);
        $("#btnExportUserwise").prop("disabled", true);
        $("#btnExportCustomerWise").prop("disabled", true);
        $("#btnAllDataExportShiftWise").prop("disabled", true);
        $("#btnAllDataExportUserwise").prop("disabled", true);
        $("#btnAllDataExportCustomerWise").prop("disabled", true);
        var select_field_id = $("#hid_select").val();
        if (select_field_id) {
          $("#id_select_message").hide();
          $("#id_select").css("border-color", "#ccc");
        }
      });
      $("#btnExportUserwise").show();
      $("#btnExportShiftWise").hide();
      $("#btnExportCustomerWise").hide();
      $("#btnAllDataExportUserwise").show();
      $("#btnAllDataExportShiftWise").hide();
      $("#btnAllDataExportCustomerWise").hide();
      $("#start").on("click", function () {
        $("#start").css("border-color", "#ccc");
        $("#id_start_message").hide();
      });
      $("#generatereport").on("click", function () {
        if ($("#hid_select").val() == undefined) {
          $("#id_select_message").show();
          $("#id_select").css("border-color", "#a94442");
        }
        if ($("#start").val() == "") {
          $("#id_start_message").show();
          $("#start").css("border-color", "#a94442");
        }
        if ($("#hid_select").val() == undefined || $("#start").val() == "") {
          return;
        }
        if ($("#hid_select").val() == "3") {
          $scope.reload_op = 3;
          $("#gridCon_user").hide();
          $("#gridCon_shift").hide();
          $("#gridCon_customer").show();
          $("#btnExportUserwise").hide();
          $("#btnExportShiftWise").hide();
          $("#btnExportCustomerWise").show();
          $("#btnExportCustomerWise").prop("disabled", false);
          $("#btnAllDataExportUserwise").hide();
          $("#btnAllDataExportShiftWise").hide();
          $("#btnAllDataExportCustomerWise").show();
          $("#btnAllDataExportCustomerWise").prop("disabled", false);
          $("#saveChanges").hide();
        }
        if ($("#hid_select").val() == "2") {
          $scope.reload_op = 1;
          $("#gridCon_user").show();
          $("#gridCon_shift").hide();
          $("#gridCon_customer").hide();
          $("#btnExportUserwise").show();
          $("#btnExportShiftWise").hide();
          $("#btnExportCustomerWise").hide();
          $("#btnExportUserwise").prop("disabled", false);
          $("#btnAllDataExportUserwise").show();
          $("#btnAllDataExportShiftWise").hide();
          $("#btnAllDataExportCustomerWise").hide();
          $("#btnAllDataExportUserwise").prop("disabled", false);
          $("#saveChanges").prop("disabled", false);
          $("#saveChanges").show();
        }
        if ($("#hid_select").val() == "1") {
          $scope.reload_op = 2;
          $("#gridCon_user").hide();
          $("#gridCon_shift").show();
          $("#gridCon_customer").hide();
          $("#btnExportUserwise").hide();
          $("#btnExportShiftWise").show();
          $("#btnExportCustomerWise").hide();
          $("#btnExportShiftWise").prop("disabled", false);
          $("#btnAllDataExportUserwise").hide();
          $("#btnAllDataExportShiftWise").show();
          $("#btnAllDataExportCustomerWise").hide();
          $("#btnAllDataExportShiftWise").prop("disabled", false);
          $("#saveChanges").hide();
        }
        sparrow.global.set("SEARCH_EVENT", true);
        dtBindFunction();
        config.listing[$scope.reload_op - 1].postData = $scope.postData;
        $scope.reloadData(
          $scope.reload_op,
          config.listing[$scope.reload_op - 1]
        );
      });

      function dtBindFunction() {
        var select_id = $("#hid_select").val();
        var today_date_ = $("#start").val();
        if (select_id == 1) {
          var postData = {
            select_id: select_id,
            today_date_: today_date_,
            load_data: true,
          };
        }
        else if (select_id == 3) {
          var postData = {
            select_id: select_id,
            today_date_: today_date_,
            load_data: true,
            is_customer_wise: true,
          };
        } else {
          var postData = {
            select_id: select_id,
            today_date_: today_date_,
            load_data: true,
            is_user_wise: true,
          };
        }
        $scope.postData = postData;
      }

      $scope.onExportUserwise = function () {
        if (data.permissions["can_export_user_efficiency_report"] == false) {
          sparrow.showMessage("appMsg", sparrow.MsgType.Error, "You do not have permission to perform this action", 3);
          return;
        }
        dtBindFunction();
        var display_data = $.grep(
          $scope["dtInstance1"].DataTable.data(),
          function (n, i) {
            return n.operator__user__username;
          }
        );
        if (display_data != "") {
          order_by_ = display_data[0].sort_col;
        } else {
          order_by_ = "-id";
          sparrow.showMessage("appMsg", sparrow.MsgType.Error, "No data available for export", 3);
          return
        }
        var postData = $scope.postData;
        sparrow.downloadData("/qualityapp/user_efficiency_user_reports_export/", {
          start: $rootScope.start,
          length: $rootScope.length,
          today_date_: postData["today_date_"],
          order_by: order_by_,
        });
      };

      $scope.onExportShiftWise = function () {
        if (data.permissions["can_export_user_efficiency_report"] == false) {
          sparrow.showMessage("appMsg", sparrow.MsgType.Error, "You do not have permission to perform this action", 3);
          return;
        }
        dtBindFunction();
        var display_data = $.grep(
          $scope["dtInstance2"].DataTable.data(),
          function (n, i) {
            return n.created_on__date;
          }
        );
        if (display_data != "") {
          order_by_ = display_data[0].sort_col;
        } else {
          order_by_ = "-id";
          sparrow.showMessage("appMsg", sparrow.MsgType.Error, "No data available for export", 3);
          return
        }
        var postData = $scope.postData;
        sparrow.downloadData("/qualityapp/user_efficiency_shift_reports_export/", {
          start: $rootScope.start,
          length: $rootScope.length,
          today_date_: postData["today_date_"],
          order_by: order_by_,
        });
      };

      $scope.onExportCustomerWise = function () {
        if (data.permissions["can_export_user_efficiency_report"] == false) {
          sparrow.showMessage(
            "appMsg",
            sparrow.MsgType.Error,
            "You do not have permission to perform this action",
            3
          );
          return;
        }
        dtBindFunction();
        var display_data = $.grep(
          $scope["dtInstance3"].DataTable.data(),
          function (n, i) {
            return n.operator__user__username;
          }
        );
        if (display_data != "") {
          order_by_ = display_data[0].sort_col;
        } else {
          order_by_ = "-id";
          sparrow.showMessage("appMsg", sparrow.MsgType.Error, "No data available for export", 3);
          return
        }
        var postData = $scope.postData;
        sparrow.downloadData("/qualityapp/user_efficiency_customer_reports_export/", {
          start: $rootScope.start,
          length: $rootScope.length,
          today_date_: postData["today_date_"],
          order_by: order_by_,
        });
      };

      $scope.onAllDataExportUserwise = function () {
        if (data.permissions["can_export_user_efficiency_report"] == false) {
          sparrow.showMessage("appMsg", sparrow.MsgType.Error, "You do not have permission to perform this action", 3);
          return;
        }
        dtBindFunction();
        var display_data = $.grep(
          $scope["dtInstance1"].DataTable.data(),
          function (n, i) {
            return n.operator__user__username;
          }
        );
        if (display_data != "") {
          order_by_ = display_data[0].sort_col;
        } else {
          order_by_ = "-id";
          sparrow.showMessage("appMsg", sparrow.MsgType.Error, "No data available for export", 3);
          return
        }
        var postData = $scope.postData;
        sparrow.downloadData("/qualityapp/user_efficiency_user_reports_export/", {
          start: 0,
          length: display_data[0].recordsTotal,
          today_date_: postData["today_date_"],
          order_by: order_by_,
        });
      };

      $scope.onAllDataExportShiftWise = function () {
        if (data.permissions["can_export_user_efficiency_report"] == false) {
          sparrow.showMessage("appMsg", sparrow.MsgType.Error, "You do not have permission to perform this action", 3);
          return;
        }
        dtBindFunction();
        var display_data = $.grep(
          $scope["dtInstance2"].DataTable.data(),
          function (n, i) {
            return n.created_on__date;
          }
        );
        if (display_data != "") {
          order_by_ = display_data[0].sort_col;
        } else {
          order_by_ = "-id";
          sparrow.showMessage("appMsg", sparrow.MsgType.Error, "No data available for export", 3);
          return
        }
        var postData = $scope.postData;
        sparrow.downloadData("/qualityapp/user_efficiency_shift_reports_export/", {
          start: 0,
          length: display_data[0].recordsTotal,
          today_date_: postData["today_date_"],
          order_by: order_by_,
        });
      };

      $scope.onAllDataExportCustomerWise = function () {
        if (data.permissions["can_export_user_efficiency_report"] == false) {
          sparrow.showMessage(
            "appMsg",
            sparrow.MsgType.Error,
            "You do not have permission to perform this action",
            3
          );
          return;
        }
        dtBindFunction();
        var display_data = $.grep(
          $scope["dtInstance3"].DataTable.data(),
          function (n, i) {
            return n.operator__user__username;
          }
        );
        if (display_data != "") {
          order_by_ = display_data[0].sort_col;
        } else {
          order_by_ = "-id";
          sparrow.showMessage("appMsg", sparrow.MsgType.Error, "No data available for export", 3);
          return
        }
        var postData = $scope.postData;
        sparrow.downloadData("/qualityapp/user_efficiency_customer_reports_export/", {
          start: 0,
          length: display_data[0].recordsTotal,
          today_date_: postData["today_date_"],
          order_by: order_by_,
        });
      };

      Mousetrap.reset();
      Mousetrap.bind("shift+o", function () {
        document.getElementById("generatereport").click();
      });
      Mousetrap.bind("shift+x", function () {
        if ($("#hid_select").val() == "2") {
          document.getElementById("btnExportUserwise").click();
        }
        if ($("#hid_select").val() == "1") {
          document.getElementById("btnExportShiftWise").click();
        }
        if ($("#hid_select").val() == "3") {
          document.getElementById("btnExportCustomerWise").click();
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
user_efficiency_reportInit();
