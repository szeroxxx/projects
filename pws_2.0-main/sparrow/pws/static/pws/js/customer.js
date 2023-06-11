function customerInit(data) {
  sparrow.registerCtrl(
    "customerCtrl",
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
        pageTitle: "Customer",
      };
      $(".id_mes_gen_mail").on("click", function () {
        $("#id_mes_gen_mail").hide();
        $('#id_gen_mail').css('border-color', '#ccc')
        $("#id_label_gen_mail").css('color', 'black');
      });
      $(".id_mes_ord_rec_mail").on("click", function () {
        $("#id_mes_ord_rec_mail").hide();
        $('#id_ord_rec_mail').css('border-color', '#ccc')
        $("#id_label_ord_rec_mail").css('color', 'black');
      });
      $(".id_mes_ord_exc_gen_mail").on("click", function () {
        $("#id_mes_ord_exc_gen_mail").hide();
        $('#id_ord_exc_gen_mail').css('border-color', '#ccc')
        $("#id_label_ord_exc_gen_mail").css('color', 'black');
      });
      $(".id_mes_ord_exc_rem_mail").on("click", function () {
        $("#id_mes_ord_exc_rem_mail").hide();
        $('#id_ord_exc_rem_mail').css('border-color', '#ccc')
        $("#id_label_ord_exc_rem_mail").css('color', 'black');
      });
      $(".id_mes_ord_comp_mail").on("click", function () {
        $("#id_mes_ord_comp_mail").hide();
        $('#id_ord_comp_mail').css('border-color', '#ccc')
        $("#id_label_ord_comp_mail").css('color', 'black');
      });
      $(".id_mes_mail_from").on("click", function () {
        $("#id_mes_mail_from").hide();
        $('#id_mail_from').css('border-color', '#ccc')
        $("#id_label_mail_from").css('color', 'black');
      });
      $(".mes_int_exc_from").on("click", function () {
        $("#mes_int_exc_from").hide();
        $('#id_int_exc_from').css('border-color', '#ccc')
        $("#label_int_exc_from").css('color', 'black');
      });
      $(".mes_int_exc_to").on("click", function () {
        $("#mes_int_exc_to").hide();
        $('#id_int_exc_to').css('border-color', '#ccc')
        $("#label_int_exc_to").css('color', 'black');
      });
      $(".mes_int_exc_cc").on("click", function () {
        $("#mes_int_exc_cc").hide();
        $('#id_int_exc_cc').css('border-color', '#ccc')
        $("#label_int_exc_cc").css('color', 'black');
      });
      var arr = new Array();
      $scope.saveCustomer = function () {

        var gen_mail_ = $("#id_gen_mail").val().replace(/ /g, "").replaceAll(",", ", ");
        var ord_rec_mail_ = $("#id_ord_rec_mail").val().replace(/ /g, '').replaceAll(",", ", ");
        var ord_exc_gen_mail_ = $("#id_ord_exc_gen_mail").val().replace(/ /g, '').replaceAll(",", ", ");
        var ord_exc_rem_mail_ = $("#id_ord_exc_rem_mail").val().replace(/ /g, '').replaceAll(",", ", ");
        var ord_comp_mail_ = $("#id_ord_comp_mail").val().replace(/ /g, '').replaceAll(",", ", ");
        var mail_from_ = $("#id_mail_from").val().replace(/ /g, '').replaceAll(",", ", ");
        var int_exc_from_= $("#id_int_exc_from").val().replace(/ /g, '').replaceAll(",", ", ");
        var int_exc_to_= $("#id_int_exc_to").val().replace(/ /g, '').replaceAll(",", ", ");
        var int_exc_cc_ = $("#id_int_exc_cc").val().replace(/ /g, '').replaceAll(",", ", ");

        var regex = /^([a-zA-Z0-9_.+-])+\@(([a-zA-Z0-9-])+\.)+([a-zA-Z0-9]{2,4})+$/;
        
        var gen_mail = $("#id_gen_mail").val().replace(/ /g, "");
        if (gen_mail != ""){
          var gen_mail = gen_mail.split(",")
          for (let x in gen_mail) {
            var rem_mail = regex.test(gen_mail[x])
            if (rem_mail == false){
               arr.push(rem_mail);
              $('#id_mes_gen_mail').show()
              $('#id_gen_mail').css('border-color', '#a94442');
              $('#id_label_gen_mail').css('color', '#a94442');
             }
          }
        };
        var ord_rec_mail = $("#id_ord_rec_mail").val().replace(/ /g, "");
        if (ord_rec_mail != ""){
          var ord_rec_mail = ord_rec_mail.split(",")
          for (let x in ord_rec_mail) {
            var rem_mail = regex.test(ord_rec_mail[x])
             if (rem_mail == false){
               arr.push(rem_mail);
              $('#id_mes_ord_rec_mail').show()
              $('#id_ord_rec_mail').css('border-color', '#a94442');
              $('#id_label_ord_rec_mail').css('color', '#a94442');
             }
          }
        };
        var ord_exc_gen_mail = $("#id_ord_exc_gen_mail").val().replace(/ /g, '');
        if (ord_exc_gen_mail != ""){
          var ord_exc_gen_mail = ord_exc_gen_mail.split(",")
          for (let x in ord_exc_gen_mail) {
            var rem_mail = regex.test(ord_exc_gen_mail[x])
             if (rem_mail == false){
               arr.push(rem_mail);
              $('#id_mes_ord_exc_gen_mail').show()
              $('#id_ord_exc_gen_mail').css('border-color', '#a94442');
              $('#id_label_ord_exc_gen_mail').css('color', '#a94442');
             }
          }
        };
        var ord_exc_rem_mail = $("#id_ord_exc_rem_mail").val().replace(/ /g, '');
        if (ord_exc_rem_mail != ""){
          var ord_exc_rem_mail = ord_exc_rem_mail.split(",")
          for (let x in ord_exc_rem_mail) {
            var rem_mail = regex.test(ord_exc_rem_mail[x])
             if (rem_mail == false){
               arr.push(rem_mail);
              $('#id_mes_ord_exc_rem_mail').show()
              $('#id_ord_exc_rem_mail').css('border-color', '#a94442');
              $('#id_label_ord_exc_rem_mail').css('color', '#a94442');
             }
          }
        };
        var ord_comp_mail = $("#id_ord_comp_mail").val().replace(/ /g, "");
        if (ord_comp_mail != ""){
          var ord_comp_mail = ord_comp_mail.split(",")
          for (let x in ord_comp_mail) {
            var rem_mail = regex.test(ord_comp_mail[x])
             if (rem_mail == false){
               arr.push(rem_mail);
              $('#id_mes_ord_comp_mail').show()
              $('#id_ord_comp_mail').css('border-color', '#a94442');
              $('#id_label_ord_comp_mail').css('color', '#a94442');
             }
          }
        };
        var mail_from = $("#id_mail_from").val().replace(/ /g, "");
        if (mail_from != ""){
          var mail_from = mail_from.split(",")
          for (let x in mail_from) {
            var rem_mail = regex.test(mail_from[x])
            if (rem_mail == false){
               arr.push(rem_mail);
              $('#id_mes_mail_from').show()
              $('#id_mail_from').css('border-color', '#a94442');
              $('#id_label_mail_from').css('color', '#a94442');
            }
          }
        };
        var int_exc_from = $("#id_int_exc_from").val().replace(/ /g, '');
        if(int_exc_from != ""){
          var int_exc_from = int_exc_from.split(",")
          for(let x in int_exc_from){
            var int_exc_from_1 = regex.test(int_exc_from[x])
            if(int_exc_from_1 == false){
              arr.push(int_exc_from_1);
              $('#mes_int_exc_from').show();
              $('#id_int_exc_from').css('border-color', '#a94442');
              $('#label_int_exc_from').css('color', '#a94442');
            }
          }
        };
        var int_exc_to = $("#id_int_exc_to").val().replace(/ /g, '');
        if(int_exc_to != ""){
          var int_exc_to = int_exc_to.split(",")
          for(let x in int_exc_to){
            var int_exc_to_1 = regex.test(int_exc_to[x])
            if(int_exc_to_1 == false){
              arr.push(int_exc_to_1);
              $('#mes_int_exc_to').show();
              $('#id_int_exc_to').css('border-color', '#a94442');
              $('#label_int_exc_to').css('color', '#a94442');
            }
          }
        };
        var int_exc_cc = $("#id_int_exc_cc").val().replace(/ /g, '');
        if(int_exc_cc != ""){
          var int_exc_cc = int_exc_cc.split(",")
          for(let x in int_exc_cc){
            var int_exc_cc_1 = regex.test(int_exc_cc[x])
            if(int_exc_cc_1 == false){
              arr.push(int_exc_cc_1);
              $('#mes_int_exc_cc').show();
              $('#id_int_exc_cc').css('border-color', '#a94442');
              $('#label_int_exc_cc').css('color', '#a94442');
            }
          }
        };
        if(($.inArray(false, arr) >= 0)){
            arr = []
          return;
        };
        var file_size = $("#company_img_change")[0].files[0];
        if (file_size != undefined) {
          const size = Math.round(file_size.size / 1024);
          if (size < 1) {
            sparrow.showMessage("appMsg", sparrow.MsgType.Error, "The file size should be more than 2KB", 10);
            return;
          }
        }
        sparrow.postForm(
          {
            company_id: $routeParams.id,
            gen_mail_: gen_mail_,
            ord_rec_mail_: ord_rec_mail_,
            ord_exc_gen_mail_: ord_exc_gen_mail_,
            ord_exc_rem_mail_: ord_exc_rem_mail_,
            ord_comp_mail_: ord_comp_mail_,
            mail_from_: mail_from_,
            int_exc_from_: int_exc_from_,
            int_exc_to_: int_exc_to_,
            int_exc_cc_: int_exc_cc_
          },
          $("#frmSaveCustomer"),
          $scope,
          function (data) {
            if (data.code == 1) {
              window.location.hash = "#/pws/customers/";
              $route.reload();
            }
          }
        );
      };
      $scope.goBack = function () {
        window.location.href = "#/pws/customers/";
      };
      if($routeParams.id == 0){
           $('#id_is_active').prop("checked", true);
           $('#note_efficiency').show();
      };
      $("#company_img_change").bind("change", function () {
        const file = Math.round(this.files[0].size / 1024);
        $("#file_size_value").text(file + "KB");
        if (parseInt(file) < 1) {
          $("#company_img_change").attr("required", "required");
          $("#company_img_change_msg").text(
            "The file size should be more than 2KB"
          );
        } else {
          $("#company_img_change").prop("required", true);
        }
      });
      $("#frmSaveCustomer").off("change", "#company_img_change");
      $("#frmSaveCustomer").on("change", "#company_img_change", function (e) {
        sparrow.setImagePreview(this, "company_img");
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
customerInit();
