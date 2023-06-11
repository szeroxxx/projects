function orderInit(data) {
  sparrow.registerCtrl(
    "orderCtrl",
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
        if(data.permissions["can_add_new_file"] == false){
           $("#id_file_add").hide()
        }
        if(data.permissions["can_edit_order"] == false){
           $("#btnEditOrderDetails").hide()
           $("#btnSaveOrderDetails").hide()
        }
        order_number=data.order_number
        customer_order_nr =data.customer_order_nr
        id=data.id
        remarks_status = data.remarks_status
        $scope.requestTabName = {
            basic_details: false,
            technical_parameter: false,
            customer_specific_parameter: false,
            comment: false,
            file: false,
        };
        var config = {
            pageTitle: "Order" + " - " + order_number ,
            listing: [
              {
                index: 1,
                url: "/attachment/files_search/",
                postData: {
                  object_id: id,
                  model_name: "order_attachment",
                  app_name: "pws",
                },
                scrollBody: true,
                columns: [
                  {
                    name: "name",
                    title: "File name",
                  },
                  {
                    name: "file_type",
                    title: "Type",
                  },
                  {
                    name: "size",
                    title: "Size",
                  },
                  {
                    name: "create_date",
                    title: "Created on",
                  },
                  {
                    name: "uid",
                    title: "",
                    sort: false,
                    renderWith: function (data, type, full, meta) {
                      $("#records_total_id").text("(" + full.recordsTotal + ")")
                      return (
                        '<div style = "text-align:center;" > <a ng-click="onefileDownload(\'' +
                        full.uid +
                        '\')" target="_blank" > <i class="icon-arrow-2-circle-down" title="File download" style="cursor:pointer; color:#2a9f00; font-size: 18px;"></a></i></div>'
                      );
                    },
                  },
                ],
              }
            ]
        };
        $scope.onTabChange = function (tab_name, index) {
          if ($scope.requestTabName[tab_name] == false) {
            $scope.requestTabName[tab_name] = true;
            $scope.tabIndex = index;
          }
          if (tab_name == "comment" || tab_name == "file"){
              $scope.hideSaveEdit = true;
          }
          else{
              $scope.hideSaveEdit = false;
          }
        }
        if (remarks_status == "true" ){
              $scope.hideSaveEdit = true;
          }

        $scope.EditHide = false;
        $scope.SaveHide = true;
        $scope.EditOrderDetails = function() {
            document.getElementById("company_id").focus();
            $scope.SaveHide = false;
            $scope.EditHide = true;
            $(".orderform :input").prop('disabled', false);
        };

        $scope.SaveOrderDetails =function(){
          sparrow.postForm(
            {
              order_id: id,
            },
            $('#frmSaveOrderDetails'),
            $scope,
            function (data) {
              if (data.code == 1) {
                      $(".orderform :input").prop('disabled', true);
                      $scope.EditHide = false;
                      $scope.SaveHide = true;
                    }
                    $scope.reloadData(1);
                    $('#order_deli_date_id').val(data.delivery_date);
                }
            );
        };

        $scope.onefileDownload = function (uid = uid) {
          window.open("/attachment/dwn_attachment/?uid=" + uid + "&model=" + "order_attachment" + "&app=" + "pws", "_blank" );
        };
        $scope.addNewFile = function() {
          if (data.is_reserve == "False"){
            sparrow.showMessage('appMsg', sparrow.MsgType.Error, 'Please first reserve the operator.', 2);
            return;
          }
          else{
            $("#addNewFileTitle").text("File" + " - " + customer_order_nr );
            $("#viewaddFileModel").modal("show");
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

        $scope.closeAddFile = function(){
          $("#id_message_file_type").hide();
          $('#id_file_type').css('border-color', '#ccc');
          $("#id_message_file").hide();
          $('#id_file').css('border-color', '#ccc');
          $('.modal-backdrop').remove();
        }

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
          var file_type = $("#hid_file_type").val();
          if (id_file.trim() == "" || file_type == "Select file") {
            sparrow.showMessage(
              "appMsg",
              sparrow.MsgType.Error,
              "Please select required field.",
              10
            );
            return;
          }
          var postData = {
            file: id_file,
            object_id: id,
            model: "order_attachment",
            app: "pws",
            order_number: customer_order_nr
          };
          sparrow.postForm(postData, $("#uploadFrm"), $scope, function (data) {
            if (data.code != 1) {
              sparrow.showMessage("appMsg", sparrow.MsgType.Error, "Please select required field.", 3);
              return;
            }
            var file_ty = $("#id_file_type").magicSuggest();
            file_ty.clear();
            $("#id_file").val("");
            $("#viewaddFileModel").modal("hide");
            $scope.reloadData(1);
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
orderInit();