function customer_userInit(data) {
  sparrow.registerCtrl(
    "customer_userCtrl",
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
      $("#id_first_name").focus()
      $scope.addViewButtons("");
      $('#validate_message').hide();
      var title = "Customer-User";
      var name = $("#username_id").val();
      var config = {
        pageTitle: $routeParams.id == 0 ? title : title + " " + '(' + name + ')',
      };
      setAutoLookup("id_group", "/lookups/user_group/", "", true, false, false, null, 1);
      setAutoLookup("id_company", "/b/lookups/companies/", "", false, true);
      $scope.newPassword = function () {
        $('#validate_message').show();
        var password = document.getElementById('password');
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
      $scope.saveCustomerUser = function () {
        var password = $('input[id="password"]').val();
        var validate_email = $('input[id="id_email"]').val();
        if (/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test(validate_email) == false)
        {
          sparrow.showMessage('appMsg',sparrow.MsgType.Error,'Email is invalid.',3);
          return;
        }
        var user_id = $routeParams.id;
        if(user_id == 0){
          $('#frmSaveCustomerUser').valid();
          if (
              $('#password').val() == $('#confirmpassword').val()
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
                      user_id: $routeParams.id,
                      },
                      $("#frmSaveCustomerUser"),
                      $scope,
                      function (data) {
                      if (data.code == 1) {
                          window.location.hash = "#/pws/customer_users/" ;
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
              user_id: $routeParams.id,
              },
              $("#frmSaveCustomerUser"),
              $scope,
              function (data) {
              if (data.code == 1) {
                  window.location.hash = "#/pws/customer_users/" ;
                  $route.reload();
                  }
              }
          );
        }
      };
      $scope.newPaassword = function () {
        $('#validatee_message').show();
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
        $('#validatee_message').hide();
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
            "/pws/customer_user_change_password/",
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
      var user_id = $routeParams.id;
        if(user_id == 0){
           $('#password_form_field').show();
           $('#c_password_form_field').show();
           $('#id_change_password_field').hide();
        }
        else{
          $('#password').removeAttr("required");
          $('#confirmpassword').removeAttr("required");
          $('#password_form_field').hide();
          $('#c_password_form_field').hide();
          $('#id_change_password_field').show();
        }
      $scope.goBack = function () {
          window.location.hash = "#/pws/customer_users/"
      },
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
customer_userInit();