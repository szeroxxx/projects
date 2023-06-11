function operatorInit(data) {
  sparrow.registerCtrl(
    "operatorCtrl",
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
      var subgroup_of_operators = data.subgroup_of_operators.replace(/&quot;/g,'"')
      var subgroup_of_operators_list = JSON.parse(subgroup_of_operators)
      $scope.subgroup_of_operators_list = []
      $scope.update_subgroup_of_operators_list = []
      $scope.subgroup_of_operators_list = subgroup_of_operators_list
      $scope.Value = []
      $scope.updateValue = []
      $("#id_first_name").focus()
      $scope.addViewButtons("");
      $('#validate_message').hide();
      var title = "Operator";
      var name = $("#username_id").val();
      var config = {
        pageTitle: $routeParams.id == 0 ? title : title + " " + '(' + name + ')',
      };
      var operator_group = [
        { id:'GROUP_B', name:"Group B" },
        { id:"GROUP_FEE", name:"Group FEE"},
        { id:"CUSTOMER", name:"Customer"},
        { id:"BACKOFFICE_AND_OTH", name:"Backoffice and others"}
      ]
      var operator_type = [
        { id:"PLANET_ENG", name:"Planet engineer" },
        { id:"KNOWLEDGE_LEA", name:"Knowledge leaders" },
        { id:"GROUP_LEA", name:"Group leaders" },
        { id:"CUSTOMER", name:"Customer" },
        { id:"qualityapp_INCH", name:"qualityapp incharge" },
        { id:"NETWORK_ADMI", name:"Network administrator" },
        { id:"GROUP_B", name:"Group B" }
      ]
      var shift = [
        { id:"first_shift", name:"First shift" },
        { id:"second_shift", name:"Second shift"},
        { id:"third_shift", name:"Third shift"},
        { id:"general_shift", name:"General shift"}
      ]
      var permanent_shift = [
        { id:"first_shift", name:"First shift" },
        { id:"second_shift", name:"Second shift"},
        { id:"third_shift", name:"Third shift"},
        { id:"general_shift", name:"General shift"}
      ]
      setAutoLookup("id_user_group", operator_group, "");
      setAutoLookup("id_group", "/lookups/operator_group/", "", true, false, false, null, 1);
      setAutoLookup("id_group_type", operator_type, "");
      setAutoLookup("id_company", "/lookups/companies/", "", false, false, false, null, 100);
      setAutoLookup("id_shift", shift, "");
      setAutoLookup("id_permanent_shift", permanent_shift, "");

      $(document).ready(function(){
        if ($( ".opera-set" ).text()){
          $scope.Value = $( ".opera-set" ).text()
          $('#myInput').removeAttr('placeholder').css("width", "70%");
          $('#id_user_sub_group_data').val($( ".opera-set" ).text());

        }
        else{
          $(".opera-set").hide()
          $("#myInput").val("").css("width", "100%")
          $("#myInput").attr("placeholder", "Search or create new");
        }
      });

      $scope.select = function (value) {
        $scope.Value = value
        $('#id_user_sub_group_data').val(value);
        $("#id_sub_group_lists").removeAttr('style');
        $("#id_sub_group").removeAttr('style');
        $(".opera-set").show()
        $("#myInput").val("").css("width", "70%")
        htmldata = '<span class="ms-close-btn" ng-click="clearselect()"></span>'
        var htmldata = $compile(htmldata)($scope);
        $(".opera-set").text(value).append(htmldata);
        $('#myInput').removeAttr('placeholder');
      };

      $scope.clearselect = function () {
        $scope.Value = []
        $('#id_user_sub_group_data').val("");
        $(".opera-set").hide()
        $(".opera-set").text("")
        $("#myInput").attr("placeholder", "Search or create new");
        $("#myInput").val("").css("width", "100%")
      };

      $("#myInput").keydown(function(e) {
        sub_group = $("#myInput").val()
        if (e.key === "Backspace" && sub_group == ""){
          $scope.$apply(function () {
              $scope.Value = []
          });
          $('#id_user_sub_group_data').val("");
          $(".opera-set").hide()
          $(".opera-set").text("")
          $("#myInput").attr("placeholder", "Search or create new");
          $("#myInput").val("").css("width", "100%")
        }
        if (e.key === "Enter" && sub_group != ""){
          $("#id_sub_group_lists").removeAttr('style');
        $("#id_sub_group").removeAttr('style');
          $('#id_user_sub_group_data').val(sub_group);
          sparrow.post(
            "/qualityapp/create_sub_group_of_operator/",
            {sub_group: sub_group},
            false,
            function (data) {
              if (data.code == 1) {
                $scope.update_subgroup_of_operators_list=data.subgroup_of_operators
                $scope.updateValue = sub_group
                $scope.$apply(function () {
                    $scope.subgroup_of_operators_list = $scope.update_subgroup_of_operators_list
                    $scope.Value = $scope.updateValue
                });
                $(".opera-set").show()
                $("#myInput").val("").css("width", "70%")
                htmldata = '<span class="ms-close-btn" ng-click="clearselect()"></span>'
                var htmldata = $compile(htmldata)($scope);
                $(".opera-set").text(sub_group).append(htmldata);
                $('#myInput').removeAttr('placeholder');
                return;
              }
              else{
                $scope.updateValue = sub_group
                $scope.$apply(function () {
                    $scope.Value = $scope.updateValue
                });
                $(".opera-set").show()
                $("#myInput").val("").css("width", "70%")
                htmldata = '<span class="ms-close-btn" ng-click="clearselect()"></span>'
                var htmldata = $compile(htmldata)($scope);
                $(".opera-set").text(sub_group).append(htmldata);
                $('#myInput').removeAttr('placeholder');
                return;
              }
              })
            }
      })

      $scope.newPassword = function () {
        $('#validate_message').show();
        var password = document.getElementById('op_password');
        var validate_small_letter = document.getElementById('validate_small_letter');
        var validate_capital_letter = document.getElementById('validate_capital_letter');
        var validate_digit = document.getElementById('validate_digit');
        var validate_character_length = document.getElementById('validate_character_length');
        var validate_special_character = document.getElementById('validate_special_character');
        password.onkeyup = function () {
          if (password.value.match(/[a-z]/g)) {
              validate_small_letter.classList.remove('invalid');
              validate_small_letter.classList.add('valid');
          } else {
              validate_small_letter.classList.remove('valid');
              validate_small_letter.classList.add('invalid');
          }
          if (password.value.match(/[A-Z]/g)) {
              validate_capital_letter.classList.remove('invalid');
              validate_capital_letter.classList.add('valid');
          } else {
              validate_capital_letter.classList.remove('valid');
              validate_capital_letter.classList.add('invalid');
          }
          if (password.value.match(/[0-9]/g)) {
              validate_digit.classList.remove('invalid');
              validate_digit.classList.add('valid');
          } else {
              validate_digit.classList.remove('valid');
              validate_digit.classList.add('invalid');
          }
          if (password.value.length >= 8) {
              validate_character_length.classList.remove('invalid');
              validate_character_length.classList.add('valid');
          } else {
              validate_character_length.classList.remove('valid');
              validate_character_length.classList.add('invalid');
          }
          if (password.value.match(/[^a-zA-Z\d]/g)) {
              validate_special_character.classList.remove('invalid');
              validate_special_character.classList.add('valid');
          } else {
              validate_special_character.classList.remove('valid');
              validate_special_character.classList.add('invalid');
          }
        };
      };
      $scope.id_message = function () {
        $("#id_message").hide();
      }
      $scope.saveOperator = function () {
        var password = $('input[id="op_password"]').val();
        var user_id = $routeParams.id;
        if(user_id == 0){
          $('#frmSaveOperator').valid();
          if (
              $('#op_password').val() == $('#confirm_op_password').val()
              ){
              if($("#hid_group").val() == undefined){
                $("#id_message").show();
                return;
              }
              if(password.match(/[a-z]/g) &&
                password.match(/[A-Z]/g) &&
                password.match(/[0-9]/g) &&
                password.match(/[^a-zA-Z\d]/g) &&
                password.length >= 8){
                sparrow.postForm(
                  {
                  operator_id: $routeParams.id,
                  },
                  $("#frmSaveOperator"),
                  $scope,
                  function (data) {
                  if (data.code == 1) {
                      window.location.hash = "#/qualityapp/operators/" ;
                      $route.reload();
                      }
                  }
                );
              }
              else{
                if($("#hid_group").val() == undefined){
                  $("#id_message").show();
                }
                sparrow.showMessage(
                  'appMsg',
                  sparrow.MsgType.Error,
                  'The password must be 8 characters long and should include an UPPERCASE, a lowercase, a numeric, and a special character.',
                  3
                );
              }
              }
          else{
            if($("#hid_group").val() == undefined){
                $("#id_message").show();
            }
            sparrow.showMessage(
              'appMsg',
              sparrow.MsgType.Error,
              'The password must be 8 characters long and should include an UPPERCASE, a lowercase, a numeric, and a special character.',
              3
            );
          }
        }
        else{
          sparrow.postForm(
              {
              operator_id: $routeParams.id,
              },
              $("#frmSaveOperator"),
              $scope,
              function (data) {
              if (data.code == 1) {
                  window.location.hash = "#/qualityapp/operators/" ;
                  $route.reload();
                  }
              }
          );
        }
      };
      $scope.newPaassword = function () {
        $('#validate_change_message').show();
        var changepassword = document.getElementById('changepassword');
        var validate_small_letter = document.getElementById('validatee_small_letter');
        var validate_capital_letter = document.getElementById('validatee_capital_letter');
        var validate_digit = document.getElementById('validatee_digit');
        var validate_character_length = document.getElementById('validatee_character_length');
        var validate_special_character = document.getElementById('validatee_special_character');
        changepassword.onkeyup = function () {
          if (changepassword.value.match(/[a-z]/g)) {
              validate_small_letter.classList.remove('invalid');
              validate_small_letter.classList.add('valid');
          } else {
              validate_small_letter.classList.remove('valid');
              validate_small_letter.classList.add('invalid');
          }
          if (changepassword.value.match(/[A-Z]/g)) {
              validate_capital_letter.classList.remove('invalid');
              validate_capital_letter.classList.add('valid');
          } else {
              validate_capital_letter.classList.remove('valid');
              validate_capital_letter.classList.add('invalid');
          }
          if (changepassword.value.match(/[0-9]/g)) {
              validate_digit.classList.remove('invalid');
              validate_digit.classList.add('valid');
          } else {
              validate_digit.classList.remove('valid');
              validate_digit.classList.add('invalid');
          }
          if (changepassword.value.length >= 8) {
              validate_character_length.classList.remove('invalid');
              validate_character_length.classList.add('valid');
          } else {
              validate_character_length.classList.remove('valid');
              validate_character_length.classList.add('invalid');
          }
          if (changepassword.value.match(/[^a-zA-Z\d]/g)) {
              validate_special_character.classList.remove('invalid');
              validate_special_character.classList.add('valid');
          } else {
              validate_special_character.classList.remove('valid');
              validate_special_character.classList.add('invalid');
          }
        };
      };
      $("#id_change_password").click(function () {
        $('#validate_change_message').hide();
        $("#passwordChangeModel").modal("show");
        $("#changepassword").val("");
        $("#confirmchangepassword").val("");
        $("#changepasswordModalLabel").text("Change password");
        $("#changepassword_form").text("New password");
        $("#confimrchangedpassword_form").text("Confirm password");
        document
          .getElementById("validatee_small_letter")
          .classList.add("invalid");
        document
          .getElementById("validatee_capital_letter")
          .classList.add("invalid");
        document.getElementById("validatee_digit").classList.add("invalid");
        document
          .getElementById("validatee_character_length")
          .classList.add("invalid");
        document
          .getElementById("validatee_special_character")
          .classList.add("invalid");
        $("#validate_message").hide();
      });
      $("#changePass").click(function (event) {
        event.preventDefault();
        var password = $('input[id="changepassword"]').val();
        $("#frmchangedpassword").valid();
        if (
          $("#changepassword").val() == $("#confirmchangepassword").val() &&
          password.match(/[a-z]/g) &&
          password.match(/[A-Z]/g) &&
          password.match(/[0-9]/g) &&
          password.match(/[^a-zA-Z\d]/g) &&
          password.length >= 8
        ) {
          sparrow.post(
            "/qualityapp/operator_change_password/",
            {
              id: $routeParams.id,
              password: password,
            },
            true,
            function (data) {
              if (data.code == 1) {
                $("#passwordChangeModel").modal("hide");
                if (data.is_reload) {
                  location.reload();
                }
              }
            }
          );
          }
        else{
            sparrow.showMessage(
              'appMsg',
              sparrow.MsgType.Error,
              'The password must be 8 characters long and should include an UPPERCASE, a lowercase, a numeric, and a special character.',
              3
            );
          }
      });
        if($routeParams.id == 0){
           $('#password_form_field').show();
           $('#c_password_form_field').show();
           $('#id_change_password_field').hide();
        }
        else{
          $('#op_password').removeAttr("required");
          $('#confirm_op_password').removeAttr("required");
          $('#password_form_field').hide();
          $('#c_password_form_field').hide();
          $('#id_change_password_field').show();
        }
      $scope.goBack = function () {
          window.location.hash = "#/qualityapp/operators/"
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
operatorInit();
