function messagesInit() {
  var message = {};
  sparrow.registerCtrl(
    "messagesCtrl",
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
      $scope.uid = [];
      $scope.addViewButtons("");
      var config = {
        pageTitle: "Messages",
        // listing: [
        //   {
        //     index: 1,
        //     url: "",
        //     paging: true,
        //     scrollBody: true,
        //   },
        // ],
      };

      var dec = [];
      $scope.decre = [];
      $scope.viewTask = function (messageId, title, priority) {
        if (priority == "Warning") {
          $("#id_priority_view").css("background", "#fff");
          $("#id_priority_view").css("color", "#feb739");
          $("#id_priority_view").css("padding", "2px 2px");
          $("#id_priority_view").css("border-radius", "20px");
          $("#id_priority_view").css("border", "1px solid #feb739");
          $("#id_priority_view").css("font-size", "12px");

        }
        if (priority == "Urgent") {
          $("#id_priority_view").css("background", "#EF7878");
          $("#id_priority_view").css("color", "#fff");
          $("#id_priority_view").css("padding", "2px 5px");
          $("#id_priority_view").css("border-radius", "20px");
          $("#id_priority_view").css("border", "1px solid #EF7878");
          $("#id_priority_view").css("font-size", "12px");
        }
        if (priority == "Normal") {
          $("#id_priority_view").css("background", "#fff");
          $("#id_priority_view").css("color", "#fff");
          $("#id_priority_view").css("padding", "2px 5px");
          $("#id_priority_view").css("border-radius", "20px");
          $("#id_priority_view").css("border", "1px solid #fff");
          $("#id_priority_view").css("font-size", "12px");
        }
        if (priority == "Critical") {
          $("#id_priority_view").css("background", "#fff");
          $("#id_priority_view").css("color", "#EF7878");
          $("#id_priority_view").css("padding", "2px 5px");
          $("#id_priority_view").css("border-radius", "20px");
          $("#id_priority_view").css("border", "1px solid #EF7878");
          $("#id_priority_view").css("font-size", "12px");
        }
        sparrow.post(
          "/task/task_detail/",
          {
            id: messageId,
          },
          false,
          function (data) {
            $("#title").text(title);
            $("#id_priority_view").text(priority);
            $("#message_detail").html(data);
            $("#view_message").modal("show");
          },
          "html"
        );
      };

      $("#view_message").on("hidden.bs.modal", function (e) {
        $(".navbar-nav").load(window.location.href + " .navbar-nav");
        $route.reload();
      });
      $scope.onClose = function () {
        $(".navbar-nav").load(window.location.href + " .navbar-nav");
        $route.reload();
        $(".modal-backdrop").remove();
      };

      $scope.markAsRead = function (data) {
        sparrow.post(
          "/task/message_read/",
          {
            id: data,
          },
          false,
          location.reload()
        );
      };

      $scope.deleteTask = function (id) {
        sparrow.showConfirmDialog(
          ModalService,
          "Are you sure, want to remove message?",
          "Remove message",
          function (confirm) {
            if (confirm) {
              sparrow.post(
                "/task/delete_message/",
                {
                  id: id,
                },
                false,
                function (data) {
                  if (data.code == 1) {
                    $route.reload();
                    sparrow.showMessage(
                      "appMsg",
                      sparrow.MsgType.Success,
                      data.msg,
                      10
                    );
                    location.reload();
                  }
                }
              );
            }
          }
        );
      };

      $scope.onUnread = function () {
        var id = $("#id_unread_task").val();
        sparrow.post(
          "/task/message_unread/",
          {
            id: id,
          },
          false,
          function (data) {
            if (data.code == 1) {
              sparrow.showMessage(
                "appMsg",
                sparrow.MsgType.Success,
                data.msg,
                3
              );
              // location.reload();
              $(".navbar-nav").load(window.location.href + " .navbar-nav");
              $route.reload();
              $(".modal-backdrop").remove();
            }
          }
        );
      };
      $scope.onUnread_ = function (id, is_read) {
        sparrow.post(
          "/task/unread_message/",
          {
            id: id,
            is_read: is_read,
          },
          false,
          function (data) {
            if (data.code == 1) {
              sparrow.showMessage(
                "appMsg",
                sparrow.MsgType.Success,
                data.msg,
                3
              );
              location.reload();
            }
          }
        );
      };
      $("table.paginated").each(function () {
        var $table = $(this);
        var itemsPerPage = 5;
        var currentPage = 0;
        var pages = Math.ceil(
          $table.find("tr:not(:has(th))").length / itemsPerPage
        );
        $table.bind("repaginate", function () {
          if (pages > 1) {
            var pager;
            if ($table.next().hasClass("pager")) pager = $table.next().empty();
            else
              pager = $(
                '<div class="pager" style="direction:ltr;text-align: right;margin-top: 10px;" align="right"></div>'
              );

            $(
              '<a class="icon-arrow-2-left" style="color: black;">&nbsp;&nbsp;</a>'
            )
              .bind("click", function () {
                if (currentPage > 0) currentPage--;
                $table.trigger("repaginate");
              })
              .appendTo(pager);

            var startPager = currentPage > 2 ? currentPage - 2 : 0;
            var endPager = startPager > 0 ? currentPage + 3 : 5;
            if (endPager > pages) {
              endPager = pages;
              startPager = pages - 5;
              if (startPager < 0) startPager = 0;
            }

            for (var page = startPager; page < endPager; page++) {
              $(
                '<a id="pg' +
                  page +
                  '" class="' +
                  (page == currentPage
                    ? "pg-selected message_page"
                    : "pg-normal message_page") +
                  '"></a>&nbsp;&nbsp;'
              )
                .text(page + 1)
                .bind(
                  "click",
                  {
                    newPage: page,
                  },
                  function (event) {
                    currentPage = event.data["newPage"];
                    $table.trigger("repaginate");
                  }
                )
                .appendTo(pager);
            }

            $(
              '<a class="icon-arrow-2-right" style="color: black;">&nbsp;&nbsp;&nbsp;</a>'
            )
              .bind("click", function () {
                if (currentPage < pages - 1) currentPage++;
                $table.trigger("repaginate");
              })
              .appendTo(pager);

            if (!$table.next().hasClass("pager")) pager.insertAfter($table);
          }

          $table
            .find("tbody tr:not(:has(th))")
            .hide()
            .slice(currentPage * itemsPerPage, (currentPage + 1) * itemsPerPage)
            .show();
        });

        $table.trigger("repaginate");
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
  return message;
}
message = messagesInit();
