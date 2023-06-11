// function import_orderInit(data) {
//   sparrow.registerCtrl(
//     "import_orderCtrl",
//     function (
//       $scope,
//       $rootScope,
//       $route,
//       $routeParams,
//       $compile,
//       DTOptionsBuilder,
//       DTColumnBuilder,
//       $templateCache,
//       ModalService
//     ) {
//       var config = {
//         pageTitle: "Import Order(for testing purpose)",
//       };
//       setAutoLookup("select_type_id", "/lookups/select_type/", "", false, true);
//       setAutoLookup(
//         "order_number_id",
//         "/lookups/order_number/",
//         "select_type_id",
//         false,
//         true
//       );
//       $scope.importOrder = function () {
//         var order = $("input[name='order']:checked").val();
//         var postData = {
//           order_type: order,
//         };
//         sparrow.post(
//           "/qualityapp/import_order_from_ecc_and_ppm/",
//           postData,
//           false,
//           function (data) {
//             if (data.code == 1) {
//               sparrow.showMessage(
//                 "appMsg",
//                 sparrow.MsgType.Success,
//                 "Record(s) imported",
//                 10
//               );
//             }
//           }
//         );
//       };
//       sparrow.setup(
//         $scope,
//         $rootScope,
//         $route,
//         $compile,
//         DTOptionsBuilder,
//         DTColumnBuilder,
//         $templateCache,
//         config,
//         ModalService
//       );
//     }
//   );
// }
// import_orderInit();
