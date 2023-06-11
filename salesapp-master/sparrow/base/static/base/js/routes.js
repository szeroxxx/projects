sparrow.config([
  "$routeProvider",
  "$controllerProvider",
  function ($routeProvider, $controllerProvider) {
    sparrow.registerCtrl = $controllerProvider.register;

    //Attachment controller
    //TODO: Need to add controller in proper file. Can't add in base.js because registerCtrl initializing in route.js and it is loadig after base.js?v=11.7.

    sparrow.registerCtrl(
      "AttachmentController",
      function ($scope, $element, objectId, appName, model, title, close) {
        $scope.title = title;
        $scope.appName = appName;
        $scope.modelName = model + "_attachment";

        var postData = {
          id: 0, //To clear form after upload file.
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

          //Handled an issue when closing model dialog, back area was disable.
          $(".modal-backdrop").remove();

          close({}, 500);
        };
      }
    );
    //Attachment controller ends

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
        resolve: loader(["base/js/app_search.js"]),
      })
      .when("/base/release_note", {
        templateUrl: "/base/release_note/",
        controller: "releaseNoteCtrl",
        resolve: loader(["base/js/release_note.js?v=12.4"]),
      })
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
        resolve: loader(["base/js/report.js?v=13.8"]),
      })
      .when("/base/model_reports/:type", {
        templateUrl: "/base/model_reports/",
        controller: "modelReportsCtrl",
        resolve: loader(["base/js/model_reports.js?v=0.8"]),
      })
      .when("/auditlog/logs/:model/:ids", {
        templateUrl: function (urlattr) {
          return "/auditlog/logs/" + urlattr.model + "/" + urlattr.ids + "/";
        },
        controller: "logsCtrl",
        resolve: loader(["auditlog/js/logs.js?v=12.4"]),
      })
      .when("/accounts/profile", {
        templateUrl: "/accounts/profile/",
        controller: "profileCtrl",
        resolve: loader([
          "accounts/js/profile.js?v=13.0",
          "base/js/jqColorPicker.min.js?v=12.0",
          "base/js/colors.js?v=12.0",
        ]),
      })
      .when("/accounts/users/:type", {
        templateUrl: "/accounts/users/",
        controller: "usersCtrl",
        resolve: loader(["accounts/js/users.js?v=1.8"]),
      })
      .when("/accounts/user/:id", {
        name: "user",
        templateUrl: function (urlattr) {
          return "/accounts/user/" + urlattr.id + "/";
        },
        controller: "userCtrl",
        resolve: loader(["accounts/js/user.js?v=13.6"]),
      })
      .when("/messaging/notifications", {
        templateUrl: "/messaging/notifications/",
        controller: "notificationsCtrl",
        resolve: loader(["messaging/js/notifications.js?v=2.7"]),
      })
      .when("/messaging/messages", {
        templateUrl: "/messaging/messages/",
        controller: "messagesCtrl",
        resolve: loader(["messaging/js/messages.js?v=11.8"]),
      })
      .when("/messaging/message", {
        templateUrl: "/messaging/message/",
        controller: "messageCtrl",
        resolve: loader(["messaging/js/message.js?v=11.8"]),
      })
      .when("/task/tasks/", {
        templateUrl: "/task/tasks/",
      })
      .when("/task/crm/", {
        templateUrl: "/task/crm/",
      })
      .when("/accounts/company", {
        name: "company",
        templateUrl: "/accounts/company/",
        controller: "companyCtrl",
        resolve: loader(["accounts/js/company.js?v=13.6"]),
      })
      .when("/sysparameters", {
        templateUrl: "/b/sysparameters/",
        controller: "sysparametersCtrl",
        resolve: loader(["base/js/sysparameters.js?v=12.3"]),
      })
      .when("/sysparameter/:id", {
        name: "systemparameter",
        templateUrl: function (urlattr) {
          return "/b/sysparameter/" + urlattr.id + "/";
        },
        controller: "sysparameterseditCtrl",
        resolve: loader(["base/js/sysparameter.js?v=12.0"]),
      })
      .when("/b/sysparameter/:id", {
        name: "systemparameter",
        templateUrl: function (urlattr) {
          return "/b/sysparameter/" + urlattr.id + "/";
        },
        controller: "sysparameterseditCtrl",
        resolve: loader(["base/js/sysparameter.js?v=12.0"]),
      })
      .when("/accounts/roles", {
        templateUrl: "/accounts/roles/",
        controller: "rolesCtrl",
        resolve: loader(["accounts/js/roles.js?v=12.4"]),
      })
      .when("/accounts/role/:id", {
        name: "role",
        templateUrl: function (urlattr) {
          return "/accounts/role/" + urlattr.id + "/";
        },
        controller: "roleCtrl",
        resolve: loader(["accounts/js/role.js?v=12.7"]),
      })
      .when("/mails/test_mail/", {
        templateUrl: "/mails/test_mail/",
      })
      .when("/sales/customers", {
        templateUrl: "/sales/customers/",
        controller: "customersCtrl",
        resolve: loader([
          "sales/js/customers.js?v=1.9",
          "sales/js/customer_login_validation.js?v=0.1",
        ]),
      })
      .when("/sales/customer/:edit_customer_from/:id/:can_add/:can_update/", {
        templateUrl: function (urlattr) {
          return (
            "/sales/customer/" +
            urlattr.edit_customer_from +
            "/" +
            urlattr.id +
            "/" +
            urlattr.can_add +
            "/" +
            urlattr.can_update +
            "/"
          );
        },
        controller: "customerCtrl",
        resolve: loader(["sales/js/customer.js?v=3.7"]),
      })
      .when("/sales/orders", {
        templateUrl: "/sales/orders/",
        controller: "ordersCtrl",
        resolve: loader([
          "sales/js/orders.js?v=1.6",
          "sales/js/customer_login_validation.js?v=0.2",
        ]),
      })
      .when("/sales/inquiries", {
        templateUrl: "/sales/inquiries/",
        controller: "inquiriesCtrl",
        resolve: loader(["sales/js/inquiries.js?v=1.3"]),
      })
      .when("/finance/invoices", {
        templateUrl: "/finance/invoices/",
        controller: "invoicesCtrl",
        resolve: loader([
          "finance/js/invoices.js?v=3.0",
          "finance/js/credit_limit.js?v=0.6",
          "finance/js/invoice_history.js?v=0.1",
          "finance/js/credit_report.js?v=0.1",
          "sales/js/customer_login_validation.js?v=0.1",
        ]),
      })
      .when("/finance/invoices/:customer_name", {
        name: "invoices",
        templateUrl: function (urlattr) {
          return "/finance/invoices/" + urlattr.customer_name + "/";
        },
        controller: "invoicesCtrl",
        resolve: loader(["finance/js/invoices.js?v=3.0"]),
      })
      .when("/finance/proforma_invoices", {
        templateUrl: "/finance/proforma_invoices/",
        controller: "proformaInvoicesCtrl",
        resolve: loader([
          "finance/js/proforma_invoices.js?v=1.9",
          "finance/js/credit_limit.js?v=0.6",
          "finance/js/invoice_history.js?v=0.1",
          "finance/js/credit_report.js?v=0.1",
        ]),
      })
      .when("/finance/proforma_invoices/:customer_name", {
        name: "proforma_invoices",
        templateUrl: function (urlattr) {
          return "/finance/proforma_invoices/" + urlattr.customer_name + "/";
        },
        controller: "proformaInvoicesCtrl",
        resolve: loader(["finance/js/proforma_invoices.js?v=1.9"]),
      })
      .when("/finance/payment_browser", {
        templateUrl: "/finance/payment_browser/",
        controller: "paymentBrowserCtrl",
        resolve: loader([
          "finance/js/payment_browser.js?v=1.5",
          "finance/js/invoice_history.js?v=0.1",
          "sales/js/customer_login_validation.js?v=0.1",
        ]),
      })
      .when("/finance/payment_unmatched", {
        templateUrl: "/finance/payment_browser_unmatched/",
        controller: "paymentBrowserUnmatchedCtrl",
        resolve: loader(["finance/js/payment_browser_unmatched.js?v=1.3"]),
      })
      .when("/sales/new_customers", {
        templateUrl: "/sales/new_customers/",
        controller: "newCustomersCtrl",
        resolve: loader([
          "sales/js/new_customers.js?v=1.4",
          "finance/js/credit_limit.js?v=0.6",
        ]),
      })
      .when(
        "/sales/survey_report/:id/:relation_id/:readonly_mode/:reportType",
        {
          templateUrl: function (urlattr) {
            return (
              "/sales/survey_report/" +
              urlattr.id +
              "/" +
              urlattr.relation_id +
              "/" +
              urlattr.readonly_mode +
              "/" +
              urlattr.reportType +
              "/"
            );
          },
          controller: "surveryReportCtrl",
          resolve: loader(["sales/js/survey_report.js?v=1.0"]),
        }
      )
      .when("/sales/call_reports/", {
        templateUrl: "/sales/all_call_reports/",
        controller: "callReportCtrl",
        resolve: loader(["sales/js/call_reports.js?v=0.7"]),
      })
      .when(
        "/sales/survey_report/:id/:relation_id/:readonly_mode/:token/:ec_user_id/:reportType/",
        {
          templateUrl: function (urlattr) {
            return (
              "/sales/public_survey_report/" +
              urlattr.id +
              "/" +
              urlattr.relation_id +
              "/" +
              urlattr.readonly_mode +
              "/" +
              urlattr.token +
              "/" +
              urlattr.ec_user_id +
              "/" +
              urlattr.reportType +
              "/"
            );
          },
          controller: "surveryReportCtrl",
          resolve: loader(["sales/js/survey_report.js?v=1.0"]),
        }
      )
      .when("/sales/first_deliveries/", {
        templateUrl: "/sales/first_deliveries/",
        controller: "firstDeliveriesCtrl",
        resolve: loader(["sales/js/first_deliveries.js?v=0.4"]),
      })
      .when("/sales/printing_needs", {
        templateUrl: "/sales/printing_needs",
        controller: "printingNeedsCtrl",
        resolve: loader([
          "sales/js/printing_needs.js?v=0.4",
          "sales/js/customer_login_validation.js?v=0.3",
        ]),
      });
  },
]);
