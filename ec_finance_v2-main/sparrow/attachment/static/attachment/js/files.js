function filesInit(data) {
  sparrow.registerCtrl(
    "filesCtrl",
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
      // if($scope.permission.permissions["can_add_new_file"] == false || $scope.is_incomings_section == true){
      //     $scope.addNew = false;
      // }
      // else{
      //     $scope.addNew = true;
      // }
      // if($scope.permission.permissions["view_file_history"] == false){
      //     $scope.btnHistory = false;
      // }
      // else{
      //     $scope.btnHistory = true;
      // }
      $scope.showall = false
      $scope.hidedelete = true
      $scope.showAll = function(){
        sparrow.global.set("SEARCH_EVENT", true);
        config.listing[0].postData.show_all = true;
        $scope.reloadData(20, config.listing[0]);
        $scope.showall = true
        $scope.hidedelete = false
      }
      $scope.hideDeleted = function(){
        sparrow.global.set("SEARCH_EVENT", true);
        config.listing[0].postData.show_all = false;
        $scope.reloadData(20, config.listing[0]);
          $scope.showall = false
        $scope.hidedelete = true
      }
      $scope.fileView = true;
      $scope.fileUpload = false;
      var config = {
        listing: [
          {
            index: 20,
            paging: false,
            crud: false,
            url: "/attachment/files_search/",
            postData: {
              object_id: $scope.object_id,
              model_name: $scope.model_name,
              app_name: $scope.app_name,
              show_all: false,
            },
            columns: [
              {
                name: "claim_file_name",
                title: "File name",
              },
              {
                name: "size",
                title: "Size",
              },
              {
                name: "claim_created_date",
                title: "Created on",
              },
              {
                name: "id",
                title: "",
                sort: false,
                renderWith: function (data, type, full, meta) {
                  return (
                    '<div style = "text-align:center;"> <a ng-click="fileDownload(\'' +
                    full.id +
                    '\')"> <i class="icon-arrow-2-circle-down" title="File download" style="cursor:pointer; color:#2a9f00; font-size: 18px;"></a></i></div>'
                  );
                },
              },
            ],
          },
        ],
      };
      $scope.fileDownload = function (id = id) {
        window.open(
          "/attachment/dwn_attachment/?uid=" +
            id +
            "&model=" +
            $scope.model_name +
            "&app=" +
            $scope.app_name,
          "_parent"
        );
      };

      $scope.addNewFile = function (id) {
        if($scope.is_reserve == false){
          sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please first reserve the operator.', 2);
          return;
        }
        else{
          $scope.showall = true;
          $scope.addNew = false;
          $scope.fileView = false;
          $scope.fileUpload = true;
        }
      };

      $scope.Filetype = function (e) {
        var file_type = $('#id_file_type').magicSuggest()
        $(file_type).on("selectionchange", function (e, m) {
          var file_type_id = $("#hid_file_type").val()
          if (file_type_id) {
            $("#id_message_file_type").hide();
            $('#id_file_type').css('border-color', '#ccc');
          }
        });
      };

      $scope.File = function (e) {
        $("#id_message_file").hide();
        $('#id_file').css('border-color', '#ccc');
      };

      $scope.uploadFile = function (e) {
        var id_file = $("#id_file").val();
        var file_type = $("#hid_file_type").val();
        if (id_file.trim() == "" && file_type == undefined ) {
          $("#id_message_file_type").show();
          $('#id_file_type').css('border-color', '#a94442');
          $("#id_message_file").show();
          $('#id_file').css('border-color', '#a94442');
          return;
        }
        if (id_file.trim() == "") {
          $("#id_message_file").show();
          $('#id_file').css('border-color', '#a94442');
          return;
        }
        if (file_type == undefined ) {
          $("#id_message_file_type").show();
          $('#id_file_type').css('border-color', '#a94442');
          return;
        }
        var file_extension = id_file.toLowerCase().endsWith(".zip")
        var files_ = id_file.split("\\")
        if (file_extension == false){
          sparrow.showMessage("appMsg", sparrow.MsgType.Error, "Please upload .zip file only." ,3)
          return;
        }
        if(files_.slice(-1)[0].length > 170){
          sparrow.showMessage( "appMsg", sparrow.MsgType.Error, "File name is too long.", 3);
          return;
        }
        var postData = {
          file: id_file,
          object_id: $scope.object_id,
          model: $scope.model_name,
          app: $scope.app_name,
          order_number: $scope.order_number
        };

        sparrow.postForm(postData, $("#uploadFrm"), $scope, function (data) {
          if (data.code != 1) {
            sparrow.showMessage("appMsg", sparrow.MsgType.Error, "Please select required field.", 3);
            return;
          }
          $scope.reloadData(20);
          $scope.btnHistory = true;
          $scope.addNew = true;
          $scope.showall = false;
          $scope.fileView = true;
          $scope.fileUpload = false;
          $("#id_file").val("");
          var file_ty = $("#id_file_type").magicSuggest();
          file_ty.clear();
        });
      };

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

filesInit();
