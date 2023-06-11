function userInit() {
  var user = {};

  sparrow.registerCtrl(
    "userCtrl",
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
      var title = "Operator";
      var name = $("#id_first_name").val();
      var config = {
        pageTitle: $routeParams.id == 0 ? title : title + " - " + name,
      };
      $scope.saveUser = function (event) {
        event.preventDefault();
        var email = $("#id_email").val();
        if (email.includes(".")) {
          var email_valid = email.split(".");
          if (!(email_valid[1].length != 0)) {
            sparrow.showMessage(
              "appMsg",
              sparrow.MsgType.Error,
              "Please enter valid email",
              5
            );
            return;
          }
        } else {
          sparrow.showMessage(
            "appMsg",
            sparrow.MsgType.Error,
            "Please enter valid email",
            5
          );
          return;
        }
        // var user_current_perm = $('#user_permissions option').map(function() { return this.value; }).get().join(',');
        // var user_work_current_perm = $('#user_work_perm option').map(function() { return this.value; }).get().join(',');
        var user_role_ids = [];
        var user_type = $("#id_customer_type option:selected").val();
        var is_customer = $("#id_is_customer").val();
        if (user_type == undefined && is_customer == "True") {
          user_type = 2;
        }
        $("input[name=group]").each(function (i, obj) {
          user_role_ids.push(parseInt($(obj).val()));
        });
        remark_id = $("input[name=remark_type]").val();
        if (remark_id == undefined) {
          remark_id = "None";
        }
        var postData = {
          id: $routeParams.id,
          user_role_ids: user_role_ids,
          remark_id: remark_id,
          user_type: user_type,
          // user_current_perm: user_current_perm,
          // user_work_current_perm: user_work_current_perm
        };
        sparrow.postForm(
          postData,
          $("#frmUser"),
          $scope,
          function (data) {
            if (data.code == 1) {
              window.location.hash = "#/accounts/user/" + data.id + "/";
              $route.reload();
              if (data.is_reload) {
                location.reload();
              }
            }
          },
          "appMsg"
        );
      };

      if ($routeParams.id == 0) {
        $("#id_change_password_field").hide();
      }
      $scope.newPassword = function () {
        $("#validate_message").show();
        var password = document.getElementById("changepassword");
        var validate_small_letter = document.getElementById(
          "validate_small_letter"
        );
        var validate_capital_letter = document.getElementById(
          "validate_capital_letter"
        );
        var validate_digit = document.getElementById("validate_digit");
        var validate_character_length = document.getElementById(
          "validate_character_length"
        );
        var validate_special_character = document.getElementById(
          "validate_special_character"
        );

        password.onkeyup = function () {
          if (password.value.match(/[a-z]/g)) {
            validate_small_letter.classList.remove("invalid");
            validate_small_letter.classList.add("valid");
          } else {
            validate_small_letter.classList.remove("valid");
            validate_small_letter.classList.add("invalid");
          }

          if (password.value.match(/[A-Z]/g)) {
            validate_capital_letter.classList.remove("invalid");
            validate_capital_letter.classList.add("valid");
          } else {
            validate_capital_letter.classList.remove("valid");
            validate_capital_letter.classList.add("invalid");
          }

          if (password.value.match(/[0-9]/g)) {
            validate_digit.classList.remove("invalid");
            validate_digit.classList.add("valid");
          } else {
            validate_digit.classList.remove("valid");
            validate_digit.classList.add("invalid");
          }

          if (password.value.length >= 8) {
            validate_character_length.classList.remove("invalid");
            validate_character_length.classList.add("valid");
          } else {
            validate_character_length.classList.remove("valid");
            validate_character_length.classList.add("invalid");
          }

          if (password.value.match(/[^a-zA-Z\d]/g)) {
            validate_special_character.classList.remove("invalid");
            validate_special_character.classList.add("valid");
          } else {
            validate_special_character.classList.remove("valid");
            validate_special_character.classList.add("invalid");
          }
        };
      };
      $("#id_change_password").click(function () {
        $("#passwordChangeModel").modal("show");
        $("#changepassword").val("");
        $("#confirmchangepassword").val("");
        $("#changepasswordModalLabel").text("Change password");
        $("#changepassword_form").text("New password");
        $("#confimrchangedpassword_form").text("Confirm password");
        $("#passwordSave").hide();
        document
          .getElementById("validate_small_letter")
          .classList.add("invalid");
        document
          .getElementById("validate_capital_letter")
          .classList.add("invalid");
        document.getElementById("validate_digit").classList.add("invalid");
        document
          .getElementById("validate_character_length")
          .classList.add("invalid");
        document
          .getElementById("validate_special_character")
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
            "/accounts/change_password/",
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
      });

      $("#app_container").off("click", "#btnClose");
      $("#app_container").on("click", "#btnClose", function (e) {
        if (sparrow.inIframe()) {
          if (parent.globalIndex.iframeCloseCallback.length > 0) {
            // parent.sparrow.iframeCloseCallback();
            var iFrameCloseCallback =
              parent.globalIndex.iframeCloseCallback.pop();
            iFrameCloseCallback();
          }
        } else {
          $scope.goBack();
        }
      });

      setAutoLookup(
        "id_group",
        "/b/lookups/group/",
        "",
        true,
        false,
        false,
        null,
        10
      );
      setAutoLookup(
        "id_default_remark",
        "/b/lookups/remark_type/",
        "",
        false,
        false,
        false,
        null,
        1
      );
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

  // $('#app_container').on('click', '#choose_all', function(event) {
  //     event.preventDefault();
  //     var avail_perms = $('#all_permission > option');
  //     $('#all_permission > option').remove();
  //     $('#user_permissions').append(avail_perms);
  // });

  // $('#app_container').on('click', '#remove_all', function(event) {
  //     event.preventDefault();
  //     var avail_perms = $('#user_permissions > option');
  //     $('#user_permissions > option').remove();
  //     $('#all_permission').append(avail_perms);
  // });

  // $('#app_container').on('click', '#add_permission', function(event) {
  //     event.preventDefault();
  //     var avail_perms = $('#all_permission > option:selected');
  //     $('#all_permission > option:selected').remove();
  //     $('#user_permissions').prepend(avail_perms);
  // });

  // $('#app_container').on('click', '#remove_permission', function(event) {
  //     event.preventDefault();
  //     var avail_perms = $('#user_permissions > option:selected');
  //     $('#user_permissions > option:selected').remove();
  //     $('#all_permission').prepend(avail_perms);
  // });

  // $('#app_container').on('click', '#choose_all_workcenter', function(event) {
  //     event.preventDefault();
  //     var avail_perms = $('#all_work_perm > option');
  //     $('#all_work_perm > option').remove();
  //     $('#user_work_perm').append(avail_perms);
  // });

  // $('#app_container').on('click', '#remove_all_workcenter', function(event) {
  //     event.preventDefault();
  //     var avail_perms = $('#user_work_perm > option');
  //     $('#user_work_perm > option').remove();
  //     $('#all_work_perm').append(avail_perms);
  // });

  // $('#app_container').on('click', '#add_work_perm', function(event) {
  //     event.preventDefault();
  //     var avail_perms = $('#all_work_perm > option:selected');
  //     $('#all_work_perm > option:selected').remove();
  //     $('#user_work_perm').prepend(avail_perms);
  // });

  // $('#app_container').on('click', '#remove_work_perm', function(event) {
  //     event.preventDefault();
  //     var avail_perms = $('#user_work_perm > option:selected');
  //     $('#user_work_perm > option:selected').remove();
  //     $('#all_work_perm').prepend(avail_perms);
  // });

  // $('#app_container').on('keyup','#filter_permission, #filter_work_perm',function(){
  //     if($(this).attr('id') == 'filter_permission') {
  //         var current_value = $('#filter_permission').val();
  //         $('#all_permission option').show();
  //         if(current_value!=''){
  //             $('#all_permission option').each(function(){
  //                 if($(this).text().toLowerCase().indexOf(current_value.toLowerCase()) < 0)
  //                 $(this).hide();
  //             });
  //         }
  //     }
  //     else {
  //         var current_value = $('#filter_work_perm').val();
  //         $('#all_work_perm option').show();
  //         if(current_value!=''){
  //             $('#all_work_perm option').each(function(){
  //                 if($(this).text().toLowerCase().indexOf(current_value.toLowerCase()) < 0)
  //                 $(this).hide();
  //             });
  //         }
  //     }
  // });
  return user;
}

userInit();
