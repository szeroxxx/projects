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
        resolve: loader(["auditlog/js/logs.js?v=12.8"]),
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
        resolve: loader(["exception_log/js/exception_logs.js?v=0.3"]),
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
      .when("/admin_utilities", {
        templateUrl: "/base/admin_utilities/",
        controller: "adminUtilitiesCtrl",
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

      .when("/accounts/allowed_ip/", {
        templateUrl: "/accounts/whitelist_ips/",
        controller: "allowedipCtrl",
        resolve: loader(["accounts/js/whitelisting_ip.js?v=0.1"]),
      })
      .when("/collection/dashboard/", {
        templateUrl: "/collection/dashboard/",
      });;
  },
]);
