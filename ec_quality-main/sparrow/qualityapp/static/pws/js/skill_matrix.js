function skill_matrixInit(data) {
  sparrow.registerCtrl(
    "skill_matrixCtrl",
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
        pageTitle: "Skill Matrix - " + data.customer_name,
        topActionbar: {
          extra: [
            {
              id: "btncloseskill",
              function: goBackSkill,
            },
            {
              id: "btndeleteskill",
              function: deleteSkillMatrix,
            },
          ],
        },
      };
      function goBackSkill() {
        window.location.href = "#/qualityapp/skill_matrix/";
      }
      $('.matrix').click(function(e){
          e.stopPropagation();
      });
      function deleteSkillMatrix() {
        sparrow.showConfirmDialog(ModalService, "Are you sure you want to delete skill matrix data?", "Delete skill matrix data",
          function (confirm) {
            if (confirm) {
              sparrow.post(
                "/qualityapp/delete_skill_matrix_company/",
                {
                    company_id : data.customer_name,
                },
                false,
                function (data) {
                  if (data.code == 1) {
                      sparrow.showMessage("appMsg", sparrow.MsgType.Success, data.msg, 3);
                      $route.reload();
                      return;
                  } else {
                      sparrow.showMessage("appMsg", sparrow.MsgType.Error, data.msg, 3);
                      $route.reload();
                      return;
                  }
                }
              );
            }
          }
        )
      };
      $scope.removeSkillMatrixOper = function (customer_id,operator,process) {
        sparrow.showConfirmDialog(ModalService, "Are you sure you want to remove operator?", "Remove operator",
          function (confirm) {
            if (confirm) {
              sparrow.post(
                "/qualityapp/remove_skill_matrix_oper/",
                {
                    customer_id : customer_id,
                    operator : operator,
                    process : process,
                },
                false,
                function (data) {
                  if (data.code == 1) {
                      sparrow.showMessage("appMsg", sparrow.MsgType.Success, data.msg, 3);
                      $route.reload();
                      return;
                  } else {
                      sparrow.showMessage("appMsg", sparrow.MsgType.Error, data.msg, 3);
                      $route.reload();
                      return;
                  }
                }
              );
            }
          }
        )
      };
      $scope.saveSkillMatrix = function (customer_id_, process, process_name) {
      var listoperator = []
      var operatorlist = document.getElementsByName(process);
        for (var checkbox of operatorlist) {
          if (checkbox.checked){
            listoperator.push(checkbox.value)
          }
        }
        sparrow.postForm(
          {
            customer_id_: customer_id_,
            listoperator: listoperator,
            process_name:process_name
          },
          $("#frmSkillMatrix"),
          $scope,
          function (data) {
            $route.reload();
          }
        );
      };
      Mousetrap.reset()
      Mousetrap.bind("shift+d", function(){
       const element = document.getElementById('btndeleteskill');
        if (!element.disabled) {
           deleteSkillMatrix()
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
skill_matrixInit();
