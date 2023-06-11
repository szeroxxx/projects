function creditLimitModalInit(customer_id) {
    if (customer_id != undefined){
        customerId = customer_id
    }
    var creditLimitModal = {};
    sparrow.registerCtrl('creditLimitModalCtrl', function (
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
        $scope.saveCreditLimit = function (){
            radioValue = $('input[name=invoiceDays]:checked').val()
            if ($("#id_base_system").val().trim()=='' && $("#id_base_graydon_cl").val().trim()==''){
                $("#baseSystem").show()
                $("#baseGraydon").show()
                return
            }
            if ($("#id_base_system").val().trim()==''){
                $("#baseSystem").show()
                $("#baseGraydon").hide()
                return
            }
            if ($("#id_base_graydon_cl").val().trim()==''){
                $("#baseSystem").hide()
                $("#baseGraydon").show()
                return
            }
            $("#baseGraydon").hide()
            $("#baseSystem").hide()

            if($("#id_base_system").val().trim().length >18 && $("#id_base_graydon_cl").val().trim().length > 18){
                $("#baseSystemLength").show()
                $("#baseGraydonLength").show()
                return
            }
            if($("#id_base_system").val().trim().length >18){
                $("#baseSystemLength").show()
                $("#baseGraydonLength").hide()
                return
            }
            if($("#id_base_graydon_cl").val().trim().length > 18){
                $("#baseSystemLength").hide()
                $("#baseGraydonLength").show()
                return
            }
            sparrow.post(
                    '/finance/save_credit_limit/',
                    {
                        daysStart: $('#id_days_starting').val(),
                        systemLimit: $('#id_base_system').val(),
                        insurance: $("#id_base_graydon_cl").val(),
                        flag: radioValue,
                        customer_id: customerId
                    },
                    true,
                    function (data) {
                        if (data.code == 1) {
                            sparrow.showMessage('appMsg', sparrow.MsgType.Success, data.message, 10);
                            $scope.$dismiss(data.data);
                            $scope.reloadData(1)
                        }
                        else{
                            sparrow.showMessage('appMsg', sparrow.MsgType.Error, data.message, 10);
                            return;
                        }
                    },
                );            
        }
        sparrow.setup($scope, $rootScope, $route, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, {}, ModalService);
    });
    return creditLimitModal;
}
creditLimitModalInit();
