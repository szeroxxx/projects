sparrow.config([
  "$routeProvider",
  "$controllerProvider",
  function ($routeProvider, $controllerProvider) {
    sparrow.registerCtrl = $controllerProvider.register;

    // Attachment controller
    // TODO: Need to add controller  proper file. Can't add in base.js because registerCtrl initializing in route.js and it is loadig after base.js?v=11.7.

    sparrow.registerCtrl(
      "AttachmentController",
      function ($scope, $element, objectId, appName, model, title, close) {
        $scope.title = title;
        $scope.appName = appName;
        $scope.modelName = model + "_attachment";

        var postData = {
          id: 0, // To clear form after upload file.
          object_id: objectId,
          app: appName,
          model: $scope.modelName,
        };

        sparrow.post(
          "/attachment/get_attachments/",
          postData,
          false,
          function (result) {
            $scope.$applyAsync(function () {
              if (result.data.length == 0) {
                $scope.noData = "No attachment available.";
              }
              $scope.attachments = result.data;
            });
          }
        );

        $scope.uploadfile = function () {
          sparrow.postForm(
            postData,
            $("#frmAttachment"),
            $scope,
            function (result) {
              $scope.$applyAsync(function () {
                var attachment = result.data[0];
                if (attachment) {
                  $("#noData").hide();
                }
                $("#id_file_type").val($("#id_file_type option:first").val());
                $scope.attachments.push(attachment);
              });
            }
          );
        };

        $scope.delete = function (element) {
          var id = element.attachment.id;
          postData["id"] = id;

          sparrow.post(
            "/attachment/del_attachment/",
            postData,
            true,
            function (data) {
              if (data.code == 1) {
                $.each($scope.attachments, function (i) {
                  if (this.id == id) {
                    $scope.$applyAsync(function () {
                      $scope.attachments.splice(i, 1);
                      if ($scope.attachments.length == 0) {
                        $("#noData").show();
                      }
                    });
                    return false;
                  }
                });
              }
            },
            "json",
            "msg"
          );
        };

        $scope.cancel = function () {
          $element.modal("hide");

          // Handled an issue when closing model dialog, back area was disable.
          $(".modal-backdrop").remove();

          close({}, 500);
        };
      }
    );
    // Attachment controller ends

    function loadScript(path) {
      var result = $.Deferred(),
        script = document.createElement("script");
      script.async = "async";
      script.type = "text/javascript";
      script.src = sparrow.getStaticUrl() + path;
      script.onload = script.onreadystatechange = function (_, isAbort) {
        if (!script.readyState || /loaded|complete/.test(script.readyState)) {
          if (isAbort) result.reject();
          else result.resolve();
        }
      };
      script.onerror = function () {
        result.reject();
      };
      var scriptContainer =
        $("#viewContainer").length != 0
          ? document.getElementById("viewContainer")
          : document.querySelector("body");
      scriptContainer.appendChild(script);
      var google_analytics_code = sparrow.global.get(
        sparrow.global.keys.GOOGLE_ANALYTICS_CODE
      );
      if (google_analytics_code && google_analytics_code != "") {
        gtag("config", google_analytics_code, {
          page_path: location.pathname + location.hash,
        });
      }
      return result.promise();
    }

    function loader(arrayName) {
      return {
        load: function ($q) {
          var deferred = $q.defer(),
            map = arrayName.map(function (name) {
              return loadScript(name);
            });
          $q.all(map).then(function (r) {
            deferred.resolve();
          });
          return deferred.promise;
        },
      };
    }

    $routeProvider
      .when("/search", {
        templateUrl: "/base/search/",
        controller: "appSearchCtrl",
        resolve: loader(["base/js/app_search.js?v=0.1"]),
      })
      .when("/testpage", {
        templateUrl: "/spw_test/testpage/",
        controller: "testCtrl",
      })
      .when("/partners/createpartner", {
        templateUrl: "/partners/createpartner/",
        controller: "createPartnerController",
        resolve: loader(["partners/js/partners_edit.js?v=12.2"]),
      })
      .when("/base/release_note/:id/", {
        templateUrl: function (urlattr) {
          return "/base/release_note/" + urlattr.id + "/";
        },
        controller: "releaseNoteCtrl",
        resolve: loader(["base/js/release_note.js?v=12.1"]),
      })
      // .when('/admin/release_notes', {
      //     templateUrl: '/admin/release_notes/',
      //     controller: 'releaseNotesCtrl',
      //     resolve: loader(['base/js/release_notes.js?v=1.1']),
      // })
      .when("/dashboard", {
        templateUrl: "/base/dashboard/",
      })
      .when("/", {
        templateUrl: "/base/dashboard/",
      })
      .when("/base/reports/:id", {
        name: "reports",
        templateUrl: function (urlattr) {
          $("#loading-image").show();
          return "/base/reports/" + urlattr.id + "/";
        },
        controller: "reportsCtrl",
        resolve: loader(["base/js/report.js?v=14.2"]),
      })
      .when("/base/model_reports/:type", {
        templateUrl: "/base/model_reports/",
        controller: "modelReportsCtrl",
        resolve: loader(["base/js/model_reports.js?v=1.3"]),
      })
      .when("/base/mo_cost_report", {
        templateUrl: "/base/mo_cost_report/",
        controller: "moCostReportCtrl",
        resolve: loader(["base/js/mo_cost_report.js?v=1.4"]),
      })
      .when("/base/components_usage", {
        templateUrl: "/base/components_usage/",
        controller: "componentsUsageCtrl",
        resolve: loader(["base/js/components_usage.js?v=1.23"]),
      })
      .when("/base/waiting_components/", {
        templateUrl: "/base/waiting_components/",
        controller: "waitingComponentsInit",
        resolve: loader(["base/js/waiting_for_components.js?v=1.3"]),
      })
      .when("/base/components_usage_by_supplier", {
        templateUrl: "/base/components_usage_by_supplier/",
        controller: "componentsUsageBySupplierCtrl",
        resolve: loader(["base/js/components_usage_by_supplier.js?v=0.3"]),
      })
      .when("/auditlog/logs/:model/:ids", {
        templateUrl: function (urlattr) {
          return "/auditlog/logs/" + urlattr.model + "/" + urlattr.ids + "/";
        },
        controller: "logsCtrl",
        resolve: loader(["auditlog/js/logs.js?v=12.7"]),
      })
      .when("/customer/users", {
        templateUrl: "/customer/users/",
        controller: "usersCtrl",
        resolve: loader(["accounts/js/users.js?v=13.9"]),
      })
      .when("/accounts/profile", {
        templateUrl: "/accounts/profile/",
        controller: "profileCtrl",
        resolve: loader([
          "accounts/js/profile.js?v=12.15",
          "base/js/jqColorPicker.min.js?v=12.1",
          "base/js/colors.js?v=12.5",
        ]),
      })
      .when("/accounts/users/", {
        templateUrl: "/accounts/users/",
        controller: "usersCtrl",
        resolve: loader(["accounts/js/users.js?v=13.9"]),
      })
      .when("/accounts/user/:id/", {
        name: "user",
        templateUrl: function (urlattr) {
          return "/accounts/user/" + urlattr.id + "/";
        },
        controller: "userCtrl",
        resolve: loader(["accounts/js/user.js?v=0.1"]),
      })
      .when("/messaging/notifications/", {
        templateUrl: "/messaging/notifications/",
        controller: "notificationsCtrl",
        resolve: loader(["messaging/js/notifications.js?v=2.9"]),
      })
      .when("/messaging/messages", {
        templateUrl: "/messaging/messages/",
        controller: "messagesCtrl",
        resolve: loader(["messaging/js/messages.js?v=12.2"]),
      })
      .when("/document/:type/:id", {
        name: "document",
        templateUrl: function (urlattr) {
          return (
            "/attachment/document/" + urlattr.type + "/" + urlattr.id + "/"
          );
        },
        controller: "documentditCtrl",
        resolve: loader(["attachment/js/document.js?v=0.3"]),
      })
      .when("/task/tasks/", {
        templateUrl: "/task/tasks/",
      })

      .when("/sysparameters", {
        templateUrl: "/b/sysparameters/",
        controller: "sysparametersCtrl",
        resolve: loader(["base/js/sysparameters.js?v=13.2"]),
      })
      .when("/sysparameter/:id/", {
        name: "systemparameter",
        templateUrl: function (urlattr) {
          return "/b/sysparameter/" + urlattr.id + "/";
        },
        controller: "sysparameterseditCtrl",
        resolve: loader(["base/js/sysparameter.js?v=12.7"]),
      })
      .when("/b/sysparameter/:id/", {
        name: "systemparameter",
        templateUrl: function (urlattr) {
          return "/b/sysparameter/" + urlattr.id + "/";
        },
        controller: "sysparameterseditCtrl",
        resolve: loader(["base/js/sysparameter.js?v=12.7"]),
      })
      .when("/accounts/roles", {
        templateUrl: "/accounts/roles/",
        controller: "rolesCtrl",
        resolve: loader(["accounts/js/roles.js?v=13.2"]),
      })

      .when("/accounts/role/:id/", {
        name: "role",
        templateUrl: function (urlattr) {
          return "/accounts/role/" + urlattr.id + "/";
        },
        controller: "roleCtrl",
        resolve: loader(["accounts/js/role.js?v=12.15"]),
      })
      .when("/settings", {
        templateUrl: "/base/settings/",
        controller: "settingsCtrl",
      })

      .when("/exception_log/dashboard/", {
        templateUrl: "/exception_log/dashboard/",
      })
      .when("/exception_log/logs/:type/", {
        templateUrl: function (urlattr) {
          return "/exception_log/logs/" + urlattr.type + "/";
        },
        controller: "exception_logsCtrl",
        resolve: loader(["exception_log/js/exception_logs.js?v=0.2"]),
      })

      .when("/attachment/tags/", {
        templateUrl: "/attachment/tags/",
        controller: "tagsCtrl",
        resolve: loader(["attachment/js/tags.js?v=0.1"]),
      })
      .when("/attachment/tag/:id/", {
        name: "tag",
        templateUrl: function (urlattr) {
          return "/attachment/tag/" + urlattr.id + "/";
        },
        controller: "tagCtrl",
        resolve: loader(["attachment/js/tag.js?v=0.2"]),
      })
      .when("/accounts/customer_masters/", {
        templateUrl: "/accounts/customer_masters/",
        controller: "customer_mastersCtrl",
        resolve: loader(["accounts/js/customer_masters.js?v=0.1"]),
      })
      .when("/accounts/customer_master/:id/", {
        name: "customer_masters",
        templateUrl: function (urlattr) {
          return "/accounts/customer_masters/" + urlattr.id + "/";
        },
        controller: "userCtrl",
        resolve: loader(["accounts/js/customer_master.js?v=0.1"]),
      })
      .when("/qualityapp/customers/", {
        templateUrl: "/qualityapp/customers/",
        controller: "customersCtrl",
        resolve: loader(["qualityapp/js/customers.js?v=0.2","base/js/shortcuts.js?v=0.1"]),
      })
      .when("/qualityapp/customer/:id/", {
        templateUrl: function (urlattr) {
          return "/qualityapp/customer/" + urlattr.id + "/";
        },
        controller: "customerCtrl",
        resolve: loader(["qualityapp/js/customer.js?v=0.2"]),
      })
      .when("/qualityapp/detail_master", {
        templateUrl: "/base/detail_master/",
        controller: "detail_masterCtrl",
        resolve: loader(["base/js/detail_master.js"]),
      })
      .when("/exceptions/incoming/", {
        templateUrl: function (urlattr) {
          for (var key in urlattr) {
            if (Object.prototype.hasOwnProperty.call(urlattr, key)) {
              urlattr.type = key;
            }
          }
          return "/qualityapp/incomings/" + urlattr.state + "/";
        },
        reloadOnSearch: false,
        controller: "incomingsCtrl",
        resolve: loader([
          "qualityapp/js/incomings.js?v=0.6",
          "attachment/js/files.js?v=0.1",
          "base/js/shortcuts.js?v=0.1",
        ]),
      })
        .when("/compare_orders/", {
        templateUrl: function (urlattr) {
          for (var key in urlattr) {
            if (Object.prototype.hasOwnProperty.call(urlattr, key)) {
              urlattr.type = key;
            }
          }
          return "/qualityapp/compare_orders/" + urlattr.state + "/";
        },
        reloadOnSearch: false,
        controller: "compare_ordersCtrl",
        resolve: loader(["qualityapp/js/reports/compare_orders.js?v=3","base/js/shortcuts.js?v=0.1"]),
      })
      .when("/qualityapp/customer_users/", {
        templateUrl: "/qualityapp/customer_users_view/",
        controller: "customer_usersCtrl",
        resolve: loader(["qualityapp/js/customer_users.js?v=0.2","base/js/shortcuts.js?v=0.1"]),
      })
      .when("/qualityapp/customer_user/:id/", {
        templateUrl: function (urlattr) {
          return "/qualityapp/customer_user/" + urlattr.id + "/";
        },
        controller: "customer_userCtrl",
        resolve: loader(["qualityapp/js/customer_user.js?v=0.1"]),
      })
      .when("/qualityapp/import_orders/", {
        templateUrl: "/qualityapp/import_order/",
        controller: "import_orderCtrl",
        resolve: loader(["qualityapp/js/import_order.js"]),
      })
      .when("/qualityapp/batch_code/", {
        templateUrl: "/qualityapp/batch_code/",
        controller: "batch_codeCtrl",
        resolve: loader(["qualityapp/js/batch_code.js"]),
      })
      .when("/job_processing/design/", {
        templateUrl: function (urlattr) {
          for (var key in urlattr) {
            if (Object.prototype.hasOwnProperty.call(urlattr, key)) {
              urlattr.type = key;
            }
          }
          return "/qualityapp/designs/" + urlattr.state + "/";
        },
        reloadOnSearch: false,
        controller: "designsCtrl",
        resolve: loader([
          "qualityapp/js/designs.js?v=0.13",
          "attachment/js/files.js?v=0.1",
          "base/js/shortcuts.js?v=0.1",
        ]),
      })
      .when("/job_processing/preparation/", {
        templateUrl: function (urlattr) {
          for (var key in urlattr) {
            if (Object.prototype.hasOwnProperty.call(urlattr, key)) {
              urlattr.type = key;
            }
          }
          return "/qualityapp/preparations/" + urlattr.state + "/";
        },
        reloadOnSearch: false,
        controller: "preparationsCtrl",
        resolve: loader([
          "qualityapp/js/preparations.js?v=0.13",
          "attachment/js/files.js?v=0.1",
          "base/js/shortcuts.js?v=0.1",
        ]),
      })
      .when("/job_processing/panel_preparation/", {
        templateUrl: function (urlattr) {
          for (var key in urlattr) {
            if (Object.prototype.hasOwnProperty.call(urlattr, key)) {
              urlattr.type = key;
            }
          }
          return "/qualityapp/productions/" + urlattr.state + "/";
        },
        reloadOnSearch: false,
        controller: "productionsCtrl",
        resolve: loader([
          "qualityapp/js/productions.js?v=0.13",
          "attachment/js/files.js?v=0.1",
          "base/js/shortcuts.js?v=0.1",
        ]),
      })
      .when("/qualityapp/order/:id/", {
        templateUrl: function (urlattr) {
          return "/qualityapp/order/" + urlattr.id + "/";
        },
        controller: "orderCtrl",
        resolve: loader(["qualityapp/js/order.js?v=0.1"]),
      })
      .when("/qualityapp/place_order/", {
        templateUrl: "/qualityapp/place_order/",
        controller: "place_orderCtrl",
        resolve: loader(["qualityapp/js/place_order.js?v=13.9"]),
      })
      .when("/qualityapp/order_allocations", {
        templateUrl: "/qualityapp/order_allocations/",
        controller: "order_allocationsCtrl",
        resolve: loader([
          "qualityapp/js/order_allocations.js?v=14.5",
          "base/js/shortcuts.js?v=0.1"
        ]),
      })
      .when("/qualityapp/user_efficiencies", {
        templateUrl: "/qualityapp/user_efficiencies/",
        controller: "userEfficienciesCtrl",
        resolve: loader(["qualityapp/js/user_efficiencies.js?v=0.4", "base/js/shortcuts.js?v=0.1"]),
      })
      .when("/orders/", {
        templateUrl: "/qualityapp/orders/",
        reloadOnSearch: false,
        controller: "ordersCtrl",
        resolve: loader([
          "qualityapp/js/reports/orders.js?v=0.12",
          "attachment/js/files.js?v=0.1",
          "base/js/shortcuts.js?v=0.1",
        ]),
      })
      .when("/reports/work_details/", {
        templateUrl: "/qualityapp/work_details_reports/",
        controller: "work_details_reportsCtrl",
        resolve: loader([
          "qualityapp/js/reports/work_details_reports.js?v=0.6",
          "base/js/shortcuts.js?v=0.1"
        ]),
      })
      .when("/reports/work_summary/", {
        templateUrl: "/qualityapp/work_summary_reports/",
        controller: "work_summary_reportsCtrl",
        resolve: loader([
          "qualityapp/js/reports/work_summary_reports.js?v=0.6",
          "base/js/shortcuts.js?v=0.1"
        ]),
      })
      .when("/qualityapp/operators/", {
        templateUrl: "/qualityapp/operators/",
        controller: "operatorsCtrl",
        resolve: loader(["qualityapp/js/operators.js?v=0.4","base/js/shortcuts.js?v=0.1"]),
      })
      .when("/qualityapp/order_process_flow/", {
        templateUrl: "/qualityapp/order_process_flow/",
        controller: "order_process_flowCtrl",
        resolve: loader(["qualityapp/js/order_process_flow.js?v=0.2", "base/js/shortcuts.js?v=0.1"]),
      })
      .when("/qualityapp/operator/:id/", {
        templateUrl: function (urlattr) {
          return "/qualityapp/operator/" + urlattr.id + "/";
        },
        controller: "operatorCtrl",
        resolve: loader(["qualityapp/js/operator.js?v=0.1"]),
      })
      // .when("/portal/place_order/", {
      //   templateUrl: "/portal/place_order/",
      //   controller: "placeOrderCtrl",
      //   resolve: loader(["portal/js/place_order.js?v=0.1"]),
      // })
      // .when("/portal/placed_order", {
      //   templateUrl: "/portal/placed_order/",
      // })
      // .when("/report_agent", {
      //   templateUrl: "/portal/report_agent/",
      //   controller: "reportagentCtrl",
      //   resolve: loader(["portal/js/report_agent.js?v=0.1"]),
      // })
      // .when("/order_tracking/:id/", {
      //    templateUrl: function (urlattr) {
      //     return "/portal/order_tracking/" + urlattr.id ;
      //   },
      //   reloadOnSearch: false,
      //   controller: "ordertrackingCtrl",
      //   resolve: loader([
      //     "portal/js/order_tracking.js?v=0.4",
      //     "attachment/js/files.js?v=0.1",
      //     "base/js/shortcuts.js?v=0.1",
      //   ]),
      // })
      .when("/engineers_work_report/", {
        templateUrl: "/qualityapp/engineers_work_report/",
        controller: "engineers_work_reportCtrl",
        resolve: loader(["qualityapp/js/reports/engineers_work_report.js?v=0.4"]),
      })

      // .when("/exception_tracking/", {
      //   templateUrl: "/portal/exception_tracking/",
      //   reloadOnSearch: false,
      //   controller: "exception_trackingCtrl",
      //   resolve: loader([
      //     "portal/js/exception_tracking.js?v=0.2",
      //     "attachment/js/files.js?v=0.1",
      //      "base/js/shortcuts.js?v=0.1",
      //   ]),
      // })
      .when("/qualityapp/nc_details", {
        templateUrl: "/qualityapp/nc_details/",
        controller: "nc_detailsCtrl",
        resolve: loader(["qualityapp/js/nc_details.js?v=0.2"]),
      })
      // .when("/portal/dashboard/", {
      //   templateUrl: "/portal/dashboard/",
      //   controller: "customerDashBoardCtrl",
      //   resolve: loader(["portal/js/customer_dashboard.js"]),
      // })
      // .when("/portal/modify_order/:id/:is_exc/", {
      //   templateUrl: function (urlattr) {
      //     return "/portal/modify_order/" + urlattr.id + "/" + urlattr.is_exc + "/";
      //   },
      //   controller: "modifyOrderCtrl",
      //   resolve: loader(["portal/js/modify_order.js?v=0.1"]),
      // })
      .when("/nc_reports/", {
        templateUrl: "/qualityapp/nc_reports/",
        controller: "nc_reportsCtrl",
        resolve: loader(["qualityapp/js/reports/nc_reports.js?v=0.2","base/js/shortcuts.js?v=0.1"]),
      })
      .when("/admin_utilities", {
        templateUrl: "/base/admin_utilities/",
        controller: "adminUtilitiesCtrl",
      })
      .when("/qualityapp/place_order/:model/:ids/", {
        templateUrl: function (urlattr) {
          return "/qualityapp/utility_place_order/" + urlattr.model + "/" + urlattr.ids + "/";
        },
        controller: "utilityPlaceOrderCtrl",
        resolve: loader(["qualityapp/js/utility_place_order.js?v=0.1"]),
      })
      .when("/work_detail_customer/", {
        templateUrl: "/qualityapp/work_detail_customer/",
        controller: "workDetailCustomerCtrl",
        resolve: loader(["qualityapp/js/reports/work_detail_customer.js?v=0.4","base/js/shortcuts.js?v=0.1"]),
      })
      .when("/summary_report_customer/", {
        templateUrl: "/qualityapp/summary_report_customer/",
        controller: "summaryReportCustomerCtrl",
        resolve: loader(["qualityapp/js/reports/summary_report_customer.js?v=0.4","base/js/shortcuts.js?v=0.1"]),
      })
      // .when("/portal/modify_and_place_order/:id/", {
      //   templateUrl: function (urlattr) {
      //     return "/portal/modify_and_place_order/" + urlattr.id + "/";
      //   },
      // })
      .when("/admin_dashboard/", {
        templateUrl: "/qualityapp/admin_dashboard/",
        controller: "adminDashboardCtrl",
        resolve: loader(["qualityapp/js/dashboard.js?v=0.1"]),
      })
      .when("/logged_in_opertaors/", {
        templateUrl: "/qualityapp/logged_in_user/",
        controller: "loggedInUserInitCtrl",
        resolve: loader(["qualityapp/js/logged_in_user.js?v=0.5"]),
      })
      .when("/qualityapp/skill_matrix", {
        templateUrl: "/qualityapp/skill_matrixs/",
        controller: "skill_matrixsCtrl",
        resolve: loader(["qualityapp/js/skill_matrixs.js"]),
      })
      .when("/qualityapp/skill_matrix/:id/", {
        templateUrl: function (urlattr) {
          return "/qualityapp/skill_matrix/" + urlattr.id + "/";
        },
        controller: "skill_matrixCtrl",
        resolve: loader(["qualityapp/js/skill_matrix.js?v=0.1"]),
      })
      .when("/task/messages/", {
        templateUrl: "/task/messages/",
        controller: "messagesCtrl",
        resolve: loader(["task/js/messages.js?v=2.9"]),
      })
      .when("/documents", {
        templateUrl: "/attachment/documents",
        controller: "documentsCtrl",
        resolve: loader(["attachment/js/documents.js?v=1.7"]),
      })
      .when("/orders_in_flow/", {
        templateUrl: "/qualityapp/orders_in_flow/",
        controller: "orders_in_flowCtrl",
        resolve: loader(["qualityapp/js/reports/orders_in_flow.js?v=0.3"]),
      })
      .when("/reports/live_prep_tracking_report/", {
        templateUrl: "/qualityapp/live_prep_tracking_report/",
        controller: "live_prep_tracking_reportCtrl",
        resolve: loader(["qualityapp/js/reports/live_prep_tracking_report.js?v=0.3","base/js/shortcuts.js?v=0.1"]),
      })
      .when("/reports/user_efficiency_report/", {
        templateUrl: "/qualityapp/user_efficiency_report/",
        controller: "user_efficiency_reportCtrl",
        resolve: loader(["qualityapp/js/reports/user_efficiency_report.js?v=0.3"]),
      })
      .when("/accounts/allowed_ip/", {
        templateUrl: "/accounts/whitelist_ips/",
        controller: "allowedipCtrl",
        resolve: loader(["accounts/js/whitelisting_ip.js?v=0.1"]),
      })
      .when("/qualityapp/performance_index", {
        templateUrl: "/qualityapp/performance_indexes/",
        controller: "performanceIndexesCtrl",
        resolve: loader(["qualityapp/js/performance_indexes.js?v=0.1", "base/js/shortcuts.js?v=0.1"]),
      })
      .when("/reports/orders_with_qta/", {
        templateUrl: "/qualityapp/orders_with_qta/",
        controller: "orders_with_qta_reportsCtrl",
        resolve: loader([
          "qualityapp/js/reports/orders_with_qta_reports.js?v=0.1",
          "base/js/shortcuts.js?v=0.1"
        ]),
      })
      .when("/reports/remarks_report/", {
        templateUrl: "/qualityapp/remark_report/",
        controller: "remark_reportCtrl",
        resolve: loader(["qualityapp/js/reports/remark_report.js?v=0.4",
        "base/js/shortcuts.js?v=0.1"]),
      })
      .when("/qualityapp/user_efficiency_add_remark/:id/", {
        templateUrl: function (urlattr) {
          return "/qualityapp/user_efficiency_add_remark/" + urlattr.id + "/";
        },
        controller: "user_efficiency_add_remarkCtrl",
        resolve: loader(["qualityapp/js/reports/user_efficiency_add_remark.js?v=0.1"]),
      })
      .when("/reports/exceptions_report/", {
        templateUrl: "/qualityapp/exceptions_report/",
        controller: "exceptions_reportCtrl",
        resolve: loader([
          "qualityapp/js/reports/exceptions_report.js?v=0.3",
          "base/js/shortcuts.js?v=0.1",
        ]),
      });
  },
]);
