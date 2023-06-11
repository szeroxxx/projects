function placeOrder(data) {

  sparrow.registerCtrl(
    "placeOrderCtrl",
    function (
      $scope,
      $rootScope,
      Upload,
      $route,
      $routeParams,
      $compile,
      DTOptionsBuilder,
      DTColumnBuilder,
      $templateCache,
      ModalService
    ) {
      $scope.addViewButtons("");
      config = {
        pageTitle: "Place order",
      };
      $("#order_file").on("change", function () {
        var fname = $("#order_file").val()
        var re = /(\.zip|\.kicad|\.brd|\.rar|\.OBD)$/i;
        if (re.exec(fname.replace(/^.*[\\\/]/, ''))) {
          $("#order_file_msg").hide()
        }
      })
      $scope.OrderPlace = function () {
        var order_file = $("#order_file").val()
        if(order_file){
          var files_ = order_file.split("\\")
          var extension = /(\.zip|\.kicad|\.brd|\.rar|\.OBD)$/i;
          if (!extension.exec(order_file.replace(/^.*[\\\/]/, ''))) {
            $("#order_file_msg").show()
            return;
          }
          if(files_.slice(-1)[0].length > 170){
              sparrow.showMessage( "appMsg", sparrow.MsgType.Error, "File name is too long.", 3);
              return;
          }
        }
        if (!$("#frmPlaceOrder").valid()) {
          return;
        }
        sparrow.showConfirmDialog(
          ModalService,
          "Are you sure you want to place order?",
          "Place order",
          function (confirm) {
            if (confirm) {
              sparrow.postForm(
                {
                  id: 0,
                },
                $("#frmPlaceOrder"),
                $scope,
                function (data) {
                  if (data.code == 1) {
                    sparrow.showMessage(
                      "appMsg",
                      sparrow.MsgType.Success,
                      data.msg,
                      5
                    );
                    window.location.href = "#/order_tracking/0/";
                    location.reload();
                  }
                },
                "appMsg"
              );
            }
          }
        );
      };
      $scope.goBack = function () {
          window.location.hash = "#/order_tracking/0/"
          location.reload();
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
placeOrder();
