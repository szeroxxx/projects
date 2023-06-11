function modifyOrder(data) {
  sparrow.registerCtrl(
    "modifyOrderCtrl",
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
      var config = {
        pageTitle: "Modify Order",
      };
      $("#order_file_modi").on("change", function () {
        var fname = $("#order_file_modi").val()
        var re = /(\.zip|\.kicad|\.brd|\.rar|\.OBD)$/i;
        if (re.exec(fname.replace(/^.*[\\\/]/, ''))) {
          $("#order_file_msg").hide()
        }
      })
      $scope.ModifyOrder = function (event) {
        if (!$("#frmModifyOrder").valid()) {
          return;
        }
        var order_file = $("#order_file_modi").val()
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
        sparrow.showConfirmDialog(
          ModalService,
          "Are you sure you want to modify order?",
          "Modify order",
          function (confirm) {
            if (confirm) {
              sparrow.postForm(
                {
                  id: 0,
                },
                $("#frmModifyOrder"),
                $scope,
                function (data) {
                  if (data.code == 1) {
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
        if(document.getElementById("is_exception") === null){
          window.location.hash = "#/order_tracking/0/"
        }else{
          window.location.hash = "#/exception_tracking/"
        }
      },
      $("#order_file_modify").click(function(){
        $("#order_file_modi").show()
      })
      $("#file_download").click(function(){
        var id = $("#file_down").val()
        if($("#file_down").val() == ""){
          sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'No File uploaded', 5);
        }
        else{
          var model ="order_attachment"
          var app = "pws"
          window.open("/attachment/dwn_attachment/?uid=" +id +"&model=" +model +"&app=" +app,"_blank");
        }
      })

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
modifyOrder();
