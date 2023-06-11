sparrow.config([
  "$routeProvider",
  "$controllerProvider",
  function ($routeProvider, $controllerProvider) {
    sparrow.registerCtrl = $controllerProvider.register;

    sparrow.registerCtrl(
      "ImportController",
      function (
        $scope,
        $element,
        model,
        title,
        postUrl,
        descr,
        id,
        callback,
        extraData,
        close,
        ModalService,
        Upload
      ) {
        $scope.importModel = model;
        $scope.title = title;
        $scope.postUrl = postUrl;
        $scope.descr = descr;
        $scope.importId = id;
        $scope.excelData = [];
        $scope.mappingColumns = [];
        $scope.selectedMapColumn = [];
        $scope.columnLength = [];
        $scope.showInput = false;
        $scope.mappedCols = [];
        $scope.newRow = [];
        $scope.mappingFieldsData = [];
        $scope.headerWarning = [];
        $scope.mappingFields = {};
        $scope.required_fields = [];
        $scope.hideTable = true;
        $scope.startIndex = 0;
        $scope.maxData = 100;
        var sendData = 0;
        $scope.disable = false;
        $scope.completePercentage = "0%";
        $scope.fields = null;
        var first_row = [];
        $scope.lowerCaseFieldNames = [];
        $scope.uploadSection = true;
        $scope.excelSection = false;
        $scope.btnUpldDisabled = false;
        $scope.imageUploadBtn = false;
        $scope.imageImportBtn = false;
        $scope.waitForExcelScreen = false;
        $scope.line_text = "Find existing records based on*";
        $scope.showDialog = false;
        $scope.errorMsg = "";
        $scope.errorData = [];
        $scope.serverErrorMsg = "";
        $scope.totalExcelData = 0;
        $scope.uploadedDataCount = 0;
        $scope.keys = [];
        $scope.isFieldMapped = {};
        $scope.fullDataKeys = [];
        $scope.exceldata_length = 0;
        $scope.row_wise_selected_cross = {};
        $scope.onMapDropdownBindFinish = function (colIndex, mappingColumns) {
          var dataHeader = $scope.excelData[0][colIndex].toLowerCase();
          var matchFound = false;
          for (var i = 0; i < mappingColumns.length; i++) {
            var keywords = mappingColumns[i].keywords.split(",");
            for (var j = 0; j < keywords.length; j++) {
              if (
                dataHeader != "" &&
                keywords[j].trim().toLowerCase() == dataHeader &&
                $scope.selectedMapColumn.indexOf(mappingColumns[i].col_name) ==
                -1
              ) {
                matchFound = true;
                break;
              }
            }

            if (matchFound) {
              $scope.selectedMapColumn.push(mappingColumns[i].col_name);
              $scope.mappedCols.push(true);
              $scope.isFieldMapped[mappingColumns[i].col_name] = true;
              if (mappingColumns[i].is_required == "true") {
                $scope.mappingFieldsData.push({
                  is_required: true,
                  data_type: mappingColumns[i].data_type,
                  col_label: mappingColumns[i].col_label,
                  col_name: mappingColumns[i].col_name,
                  msg: "",
                });
              } else if (mappingColumns[i].is_required == "false") {
                $scope.mappingFieldsData.push({
                  is_required: false,
                  data_type: mappingColumns[i].data_type,
                  col_label: mappingColumns[i].col_label,
                  col_name: mappingColumns[i].col_name,
                  msg: "",
                });
              }
              break;
            } else if (dataHeader == "") {
              $scope.selectedMapColumn.push("");
              $scope.mappedCols.push(false);
              $scope.mappingFieldsData.push({
                is_required: false,
                data_type: "",
                col_label: "",
                col_name: "",
                msg: "",
              });
              break;
            }
          }
          if (!matchFound && dataHeader != "") {
            $scope.selectedMapColumn.push("");
            $scope.mappedCols.push(false);
            if ($scope.lowerCaseFieldNames.indexOf(dataHeader) != -1) {
              $scope.mappingFieldsData.push({
                is_required: false,
                data_type: "",
                col_label: "",
                col_name: dataHeader,
                msg: "",
              });
            } else {
              $scope.mappingFieldsData.push({
                is_required: false,
                data_type: "",
                col_label: "",
                col_name: "",
                msg: "",
              });
            }
          }
        };

        $(document).on(
          "focusout",
          "#id-table-data tbody tr td input",
          function (e) {
            $(this).css("border", "none");
            $(this).css("outline", "none");
          }
        );

        $(document).on(
          "focus",
          "#id-table-data tbody tr td input",
          function (e) {
            $(this).css("border", "solid 1.5px rgb(59, 59, 59)");
            $(this).css("width", "98%");
          }
        );

        $scope.checkRequired = function (bool) {
          var symbol = "";
          if (bool == "true") {
            symbol = "*";
          }
          return symbol;
        };

        $scope.addNewRow = function () {
          $scope.newRow.length = [];
          for (var i = 0; i < $scope.columnLength.length; i++) {
            $scope.newRow.push("");
          }
          $scope.excelData.push($scope.newRow);
        };

        $scope.changeValueInExcelData = function (
          show,
          rowIndex,
          colIndex,
          data
        ) {
          if (!show) {
            $scope.excelData[rowIndex][colIndex] = data;
          }
        };

        $scope.changeDropdownData = function (index, col_name) {
          for (i = 0; i <= $scope.excelData.length - 1; i++) {
            $scope.colIndex = i;
            for (j = 0; j <= $scope.excelData[i].length - 1; j++) {
              $scope.rowIndex = j;

              $(
                "#td_cell_" + $scope.colIndex + "_" + $scope.rowIndex + ""
              ).removeClass("invalid-data");
              $(
                "#td_warning_icon_" + $scope.colIndex + "_" + $scope.rowIndex
              ).css("display", "none");
            }
          }
          var mapKeys = Object.keys($scope.isFieldMapped);
          for (var i = 0; i < mapKeys.length; i++) {
            if ($scope.selectedMapColumn.indexOf(mapKeys[i]) > -1) {
              $scope.isFieldMapped[mapKeys[i]] = true;
            } else {
              $scope.isFieldMapped[mapKeys[i]] = false;
            }
          }
          var colNameIndex = $scope.selectedMapColumn.indexOf(col_name);
          for (var i = 0; i < $scope.selectedMapColumn.length; i++) {
            if (
              colNameIndex > -1 &&
              i != index &&
              $scope.selectedMapColumn[i] == col_name
            ) {
              $scope.selectedMapColumn[i] = "";
            }
            if ($scope.selectedMapColumn[i] == "") {
              $scope.updateMappingFieldsData(i, false, "", "", "");
              $scope.mappedCols[i] = false;
            } else {
              $scope.mappedCols[i] = true;
            }
          }

          var is_required = false;
          var data_type = "";
          var col_label = "";

          if (col_name == "") {
            is_required = false;
          } else {
            is_required = $scope.mappingFields[col_name].is_required;
            data_type = $scope.mappingFields[col_name].data_type;
            col_label = $scope.mappingFields[col_name].col_label;
            if (is_required == "true") {
              is_required = true;
            } else {
              is_required = false;
            }
          }
          $scope.updateMappingFieldsData(
            index,
            is_required,
            data_type,
            col_label,
            col_name
          );
        };

        $scope.updateMappingFieldsData = function (
          index,
          is_required,
          data_type,
          col_label,
          col_name
        ) {
          $scope.mappingFieldsData[index].is_required = is_required;
          $scope.mappingFieldsData[index].data_type = data_type;
          $scope.mappingFieldsData[index].col_label = col_label;
          $scope.mappingFieldsData[index].col_name = col_name;
          $scope.headerWarning[index] = false;
        };

        $scope.deleteRow = function (index) {
          var index = $scope.excelData.indexOf($scope.excelData[index]);
          $scope.excelData.splice(index, 1);

          for (var i = 0; i < $scope.columnLength.length; i++) {
            $scope.headerWarning[i] = false;
          }
        };
        $scope.inputValueCheck = function (colIndex, data, rowIndex, show) {
          if ($scope.isValidData(colIndex, data, rowIndex, show)) {
            $("#td_cell_" + rowIndex + "_" + colIndex + "").addClass(
              "invalid-data"
            );
            $("#td_warning_icon_" + rowIndex + "_" + colIndex + "").css(
              "display",
              "block"
            );
          } else {
            $scope.isValidData(colIndex, data, rowIndex, true);
            $("#td_cell_" + rowIndex + "_" + colIndex + "").removeClass(
              "invalid-data"
            );
            $("#td_warning_icon_" + rowIndex + "_" + colIndex + "").css(
              "display",
              "none"
            );
          }
        };
        $scope.isValidData = function (colIndex, data, rowIndex, show) {
          var isFirstRow = $("#is-first-row").prop("checked");
          if (!isFirstRow) {
            rowIndex = -1;
          }
          var fromRequired = 0;
          data = data.toString();

          if (
            rowIndex != 0 &&
            $scope.mappingFieldsData[colIndex].is_required &&
            $scope.mappingFieldsData[colIndex].data_type == "float" &&
            data == ""
          ) {
            $scope.excelData[rowIndex][colIndex] = 0;
            return false;
          }
          if (
            rowIndex != 0 &&
            $scope.mappingFieldsData[colIndex].is_required &&
            data == ""
          ) {
            $scope.mappingFieldsData[colIndex].msg =
              "Required data cannot be blank.";
            $scope.headerWarning[colIndex] = true;
            fromRequired = 1;
          } else if (
            $scope.mappingFieldsData[colIndex].is_required &&
            data != ""
          ) {
            if (show) {
              $scope.headerWarning[colIndex] = false;
            }
          } else if (
            !$scope.mappingFieldsData[colIndex].is_required &&
            data == ""
          ) {
            if (show) {
              $scope.headerWarning[colIndex] = false;
            }
          }
          if (rowIndex != 0 && data != "") {
            switch ($scope.mappingFieldsData[colIndex].data_type) {
              case "int":
                if (
                  !(Math.floor(data) == +data && $.isNumeric(data)) ||
                  +data < 0
                ) {
                  $scope.mappingFieldsData[colIndex].msg =
                    "Numeric data is required.";
                  $scope.headerWarning[colIndex] = true;
                  return true;
                } else {
                  if (show) {
                    $scope.headerWarning[colIndex] = false;
                  }
                }
                break;

              case "float":
                if (!$.isNumeric(data) || +data < 0) {
                  $scope.mappingFieldsData[colIndex].msg =
                    "Numeric data is required.";
                  $scope.headerWarning[colIndex] = true;
                  return true;
                } else {
                  if (show) {
                    $scope.headerWarning[colIndex] = false;
                  }
                }
                break;
              case "date":
                if (!isValidDate(data)) {
                  $scope.mappingFieldsData[colIndex].msg =
                    "Please add date in yyyy-mm-dd format.";
                  $scope.headerWarning[colIndex] = true;
                  return true;
                } else {
                  if (show) {
                    $scope.headerWarning[colIndex] = false;
                  }
                }
                break;
              case "bool":
                if (
                  !(
                    $.trim(data).toLowerCase() == "true" ||
                    $.trim(data).toLowerCase() == "false" ||
                    $.trim(data).toLowerCase() == "0" ||
                    $.trim(data).toLowerCase() == "1" ||
                    $.trim(data).toLowerCase() == "yes" ||
                    $.trim(data).toLowerCase() == "no"
                  )
                ) {
                  $scope.mappingFieldsData[colIndex].msg =
                    "Boolean data is required.(Example: yes, no or true, false.)";
                  $scope.headerWarning[colIndex] = true;
                  return true;
                } else {
                  if (show) {
                    $scope.headerWarning[colIndex] = false;
                  }
                }
                break;
              default:
                return false;
            }
          }
          if (fromRequired == 1) {
            return true;
          }
          return false;
        };

        $scope.sample = function () {
          $("#idProductImport").attr("style", "display: block !important");
          $("#idProductImport").modal("show");
          setAutoLookup(
            "id_type_id",
            "/b/lookups/product_type/",
            "",
            "",
            false,
            true
          );
        };

        $scope.sampleProduct = function (event) {
          var groupId =
            $("#hid_type_id").val() != undefined ? $("#hid_type_id").val() : 0;
          $("#idProductImport").modal("hide");
          var group_id = $("#id_type_id").magicSuggest();
          group_id.clear();
          window.open(
            "/baseimport/export_sample_product/" + groupId + "/",
            "_blank"
          );
        };

        function isValidDate(s) {
          var bits = s.split("-");
          var d = new Date(bits[0] + "-" + bits[1] + "-" + bits[2]);
          return !!(
            d &&
            d.getMonth() + 1 == bits[1] &&
            d.getDate() == Number(bits[2])
          );
        }

        var postData = {
          model: $scope.importModel,
        };

        if ($scope.importModel == "contact" && $scope.importId != null) {
          postData["is_subscriber_import"] = true;
        }

        var dropdown_data = "";
        var model_name = "";

        $scope.cancel = function () {
          $element.modal("hide");
          $(".modal-backdrop").remove();
          close({}, 500);
        };

        $scope.onCategoryChange = function (val) {
          if (val == "new_record") {
            $scope.line_text = "Skip existing records based on*";
          } else {
            $scope.line_text = "Find existing records based on*";
          }
        };

        $scope.uploadfile = function () {
          var supplier = $("input[name = supplier_lookup]").val();
          $(".check").css("display", "block");
          $("#data_file-error").remove();
          $("div.form-group").removeClass("has-error");
          if (
            $("#data_file").val() != "" &&
            !(
              $("#data_file").val().split(".").pop() == "csv" ||
              $("#data_file").val().split(".").pop() == "xls" ||
              $("#data_file").val().split(".").pop() == "xlsx"
            )
          ) {
            if ($("#data_file-error").length > 0) {
              $("#data_file-error").text("Please uplaod csv, xls, xlsx only.");
            } else {
              $("#data_file").after(
                '<span id="data_file-error" class="help-block" style="display: block;">Please uplaod csv, xls only.</span>'
              );
            }
            $("div.form-group").addClass("has-error");
            $("#loading-image").hide();
            return false;
          }
          if ($("#data_file").val()) {
            $scope.btnUpldDisabled = true;
            $scope.waitForExcelScreen = true;
          }

          sparrow.postForm(
            postData,
            $("#frmImport"),
            $scope,
            function (result) {
              $scope.$applyAsync(function () {
                $scope.btnUpldDisabled = false;
                $scope.hideTable = false;
                $scope.uploadSection = false;
                $scope.excelSection = true;
                $scope.waitForExcelScreen = false;
                $scope.cross_references = [];
                $("#delimiter-body").show();
                $("#delimiter-body").empty();
                model_name = result["model_name"];
                $scope.model_name = result["model_name"];
                dropdown_data = result["dropdown_fields"];
                if (dropdown_data != undefined && dropdown_data != null) {
                  for (i = dropdown_data.length - 1; i >= 0; i--) {
                    $(".selectList").append(
                      new Option(
                        dropdown_data[i].col_label,
                        dropdown_data[i].col_name
                      )
                    );
                  }
                }
                if (dropdown_data == null) {
                  $("#after-upload").css("display", "none");
                }
                var data = result["data"];
                if (data != undefined && data != null) {
                  $scope.excelData = data;
                  if (model_name == "alternatives") {
                    $("#delimiter-body").hide();
                    $scope.cross_references =
                      result["available_cross_ref_fields"];
                    for (i = 0; i < $scope.excelData.length; i++) {
                      if (i == 0) {
                        $scope.excelData[i].push("Cross reference");
                      } else {
                        $scope.excelData[i].push("");
                      }
                    }
                  }
                  $scope.totalExcelData = $scope.excelData.length - 1;
                  $scope.fields = result["fields"];
                  $scope.lowerCaseFieldNames = [];
                  for (var i = 0; i < $scope.fields.length; i++) {
                    $scope.lowerCaseFieldNames.push(
                      $scope.fields[i].toLowerCase()
                    );
                  }

                  $scope.mappingColumns = result["mapping_columns"];
                  $("#is-first-row").parent().parent().remove();

                  if (
                    result.file_type != "csv" &&
                    $("#delimiter-parent").length == 1
                  ) {
                    $("#delimiter-body").empty();
                  }

                  if (
                    result.file_type == "csv" &&
                    $("#delimiter-parent").length == 0
                  ) {
                    $("#delimiter-body").append(
                      '<h4 style="margin: 0;">Choose delimiters your data contains:</h4><div id="delimiter-parent" class="row" style="margin-bottom:10px;">' +
                      '<div class="col-sm-12" style="margin-left:10px;"><label class="radio-inline">' +
                      '<input type="radio" name="delimiter" value=",">Comma</label>' +
                      '<label class="radio-inline"><input type="radio" name="delimiter" value=";">Semicolon</label><label class="radio-inline">' +
                      '<input type="radio" name="delimiter" value="|">Pipe</label><label class="radio-inline">' +
                      '<input type="radio" name="delimiter" value="\t">Tab</label></div></div>'
                    );
                  }

                  if (
                    result.file_type == "csv" &&
                    $("#delimiter-parent").length == 1
                  ) {
                    $(
                      "input[name=delimiter][value='" +
                      result["delimiter"] +
                      "']"
                    ).attr("checked", "checked");
                  }

                  $scope.columnLength = new Array($scope.excelData[0].length);

                  for (var i = 0; i < $scope.columnLength.length; i++) {
                    $scope.headerWarning.push(false);
                  }

                  for (var i = 0; i < $scope.mappingColumns.length; i++) {
                    $scope.isFieldMapped[
                      $scope.mappingColumns[i].col_name
                    ] = false;
                    if ($scope.mappingColumns[i].is_required == "true") {
                      $scope.required_fields.push(
                        $scope.mappingColumns[i].col_name
                      );
                    }
                    $scope.mappingFields[$scope.mappingColumns[i].col_name] = {
                      is_required: $scope.mappingColumns[i].is_required,
                      data_type: $scope.mappingColumns[i].data_type,
                      col_label: $scope.mappingColumns[i].col_label,
                    };
                  }

                  var marginClass = "";
                  if (model_name == "bom_line") {
                    $("#delimiter-body").append(
                      '<div style="margin-top:-10px;margin-bottom:5px;"><label><label style="margin-right:10px; font-size: 16px;">BOM Name</label>' +
                      '<input type="text" style="width: 200px;" autofocus id="id_bom_name" name="bom_name" value="' +
                      extraData["product_name"] +
                      '"></label></div>'
                    );
                    marginClass = 'style="margin-left: 91px;"';
                  }
                  $("#delimiter-body").append(
                    '<div style="margin-top:0px;margin-bottom:5px;"><label ' +
                    marginClass +
                    '><input type="checkbox" id="is-first-row" onclick="checkVal()" checked="checked">' +
                    '<label style="position:relative;top:-2px;left:5px;">First row contains column header</label>' +
                    "</label></div>"
                  );
                  if (
                    model_name == "purchase_order_line" ||
                    model_name == "sale_order_line" ||
                    model_name == "mfg_bom_line" ||
                    model_name == "bom_line"
                  ) {
                    $("#delimiter-body").append(
                      '<div style="margin-top:-10px;margin-bottom:5px;"><label ' +
                      marginClass +
                      '><input type="checkbox" id="is-create-product" checked="checked">' +
                      '<label style="position:relative;top:-2px;left:5px;">Automatically create product if not exist</label>' +
                      "</label></div>"
                    );
                  }
                  if (model_name == "contact") {
                    $("#delimiter-body").append(
                      '<div style="margin-top:0px;margin-bottom:5px;"><label ' +
                      marginClass +
                      '><input type="checkbox" id="is-duplicate-email" >' +
                      '<label style="position:relative;top:-2px;left:5px;">Allow duplicate contact (Checked by email)</label>' +
                      "</label></div>"
                    );
                  }
                  var height = $(window).height() - 370;
                  $("div.table-parent").css({
                    height: height + "px",
                    overflow: "auto",
                  });
                }
              });
            }
          );
          $("#loading-image").hide();
        };

        $scope.onBackSelection = function () {
          $scope.excelData = [];
          $scope.mappingColumns = [];
          $scope.columnLength = [];
          $scope.selectedMapColumn = [];
          $scope.headerWarning = [];
          $scope.mappingFields = {};
          $scope.mappingFieldsData = [];
          $scope.required_fields = [];
          $scope.mappedCols = [];
          $scope.isFieldMapped = {};
          if (dropdown_data != null) {
            $(".selectList option").each(function () {
              for (i = 0; i < dropdown_data.length; i++) {
                if ($(this).val() == dropdown_data[i].col_name) {
                  $(this).remove();
                }
              }
            });
          }

          $scope.uploadSection = true;
          $scope.excelSection = false;
        };

        $scope.backFromImageUpload = function () {
          $scope.imageUpload = false;
          $scope.imageUploadBtn = false;
          $scope.fileInfo = false;
          $scope.excelSection = true;
        };

        $scope.uploadImageDailouge = function (files) {
          $scope.files = files;
          $scope.fileInfo = true;
          for (var i = 0; i < files.length; i++) {
            var file_name = files[i].name
              .replace(/[^a-z0-9\s]/gi, "")
              .replace(/[_\s]/g, "-");
            $scope.files[i]["objectName"] = file_name;
          }
          if (files.length > 0) {
            $scope.imageUploadBtn = true;
            $("#btnUploadImageFolder").show();
            var fileStatus = /(progress|succeess|failed)$/i.test(
              $scope.files[0]["status"]
            );
            if (fileStatus == true) {
              importProductImages = false;
              $("#btnUploadImageFolder").val("Reupload");
              $("#btnNext").show();
            }
          }
        };

        $scope.uploadImageFolder = function (event) {
          event.preventDefault();
          var files = $scope.files;
          if (files.length == 0) {
            sparrow.showMessage(
              "appMsg",
              sparrow.MsgType.Error,
              "Please drag and drop image folders to upload.",
              10
            );
            return;
          }
          if (files.length > 500) {
            sparrow.showMessage(
              "appMsg",
              sparrow.MsgType.Error,
              "You can upload maximum 500 documents at a time.",
              10
            );
            return;
          }

          $("#btnUploadImageFolder").text("Uploading");
          $("#btnUploadImageFolder").attr("disabled", true);
          $scope.disable = true;

          var counter = 0;

          $.each(files, function (i) {
            files[i]["status"] = "progress";
          });

          $scope.startUploadImageFolder = function (file, totalFiles) {
            Upload.upload({
              url: "/products/upload_image_folder/",
              data: {
                file: file,
                path: file["webkitRelativePath"],
                fileIndex: counter,
              },
            }).then(function (resp) {
              var file_name = resp.data.file_name
                .replace(/[^a-z0-9\s]/gi, "")
                .replace(/[_\s]/g, "-");
              var file_path = resp.data.file_path;
              $scope.path = file_path;

              if (file["objectName"] == file_name) {
                file["status"] = resp.data.code == 1 ? "succeess" : "failed";
                file["msg"] = resp.data.msg;
              }

              counter = counter + 1;
              if (counter == totalFiles) {
                $("#btnUploadImageFolder").hide();
                $("#btnUploadImageFolder").attr("disabled", false);
                $scope.disable = false;
                $(".mapped-column").remove();
                importProductImages = false;
                sparrow.showMessage("appMsg", null, "Images are uploaded.", 10);
                $scope.imageUploadBtn = false;
                $scope.imageImportBtn = true;
              } else {
                $scope.startUploadImageFolder(files[counter], files.length);
              }
            });
          };

          if (files && files.length) {
            $scope.startUploadImageFolder(files[0], files.length);
          }
        };

        $scope.excel_data_batch = function () {
          var allData = [];
          count = 0;
          for (var i = 0; i < $scope.excelData.length; i++) {
            var rowData = {};
            if (count == 100 && model_name != "bom_line") {
              break;
            } else {
              count++;
            }
            for (var j = 0; j < $scope.excelData[i].length; j++) {
              var data_type = $scope.mappingFieldsData[j].data_type;
              if (data_type == "bool" && $scope.excelData[i][j] != "") {
                if ($.trim($scope.excelData[i][j]).toLowerCase() == "yes") {
                  $scope.excelData[i][j] = "1";
                } else if (
                  $.trim($scope.excelData[i][j]).toLowerCase() == "no"
                ) {
                  $scope.excelData[i][j] = "0";
                }
              }

              if ($scope.mappingFieldsData[j].col_name != "") {
                rowData[$scope.mappingFieldsData[j].col_name] =
                  $scope.excelData[i][j].toString();
              } else {
                if (
                  fullDataKeys[j].startsWith("attribute_") |
                  ($scope.importModel == "part_specs")
                ) {
                  rowData[fullDataKeys[j]] = $scope.excelData[i][j].toString();
                }
              }
            }
            rowData["product_images"] = $scope.path;
            if (Object.keys(rowData).length != 0) {
              allData.push(rowData);
              sendData++;
            }
          }
          return allData;
        };

        $scope.send_data_to_server = function (
          url,
          radio_value,
          dropdown_Value,
          createProduct,
          bom_name
        ) {
          if (url.includes("import_part_offers") === true) {
            var supplier = $("input[name = supplier_lookup]").val();
            if (supplier == undefined) {
              supplier = 0
            }
            url = url + supplier + "/";
          }

          allData = $scope.excel_data_batch();
          var post_Data = {};
          $scope.mpn = title.split(" ")[1];
          if ($scope.model_name == "alternatives") {
            post_Data = {
              data: JSON.stringify(allData),
              mpn: $scope.mpn,
            };
          } else {
            post_Data = {
              id: id,
              radio_value: radio_value,
              dropdown_Value: dropdown_Value,
              createProduct: createProduct,
              data: JSON.stringify(allData),
              bom_name: bom_name,
              allow_duplicate_email: $("#is-duplicate-email").prop("checked"),
            };
          }
          sparrow.post(
            url,
            post_Data,
            false,
            function (data) {
              if (data.code == 1) {
                if (sendData < exceldata_length) {
                  $scope.$apply(function () {
                    if (model_name != "bom_line") {
                      $scope.excelData.splice(0, 100);
                    }
                    $scope.send_data_to_server(
                      url,
                      radio_value,
                      dropdown_Value,
                      createProduct
                    );
                    var dataSend = Math.floor(
                      (100 * sendData) / $scope.excelData.length
                    );
                    if (dataSend <= 100) {
                      $scope.completePercentage = dataSend + "%";
                    }
                    $scope.uploadedDataCount += sendData;
                    $("#appMsg").hide();
                  });
                } else {
                  sparrow.showMessage(
                    "appMsg",
                    sparrow.MsgType.Success,
                    data.msg,
                    10
                  );
                  $element.modal("hide");
                  $(".modal-backdrop").remove();
                  close({}, 500);
                  $("#appMsg").show();
                  if (callback) {
                    callback(data);
                  }
                }
              } else {
                if (data.invalidData) {
                  $scope.keys = Object.keys(data.invalidData);
                  $scope.errorMsg = "";
                  $scope.errorData = [];
                  for (var i = 0; i < $scope.keys.length; i++) {
                    var key_data = data.invalidData[$scope.keys[i]];
                    if (key_data.length > 0) {
                      for (var j = 0; j < key_data.length; j++) {
                        if (!$scope.errorData[key_data[j].index]) {
                          $scope.errorData[key_data[j].index] = [];
                          $scope.errorData[key_data[j].index].push({
                            value: key_data[j].value,
                            type: $scope.keys[i],
                          });
                        } else {
                          $scope.errorData[key_data[j].index].push({
                            value: key_data[j].value,
                            type: $scope.keys[i],
                          });
                        }
                      }
                    }
                  }
                }
                $(".after-import-show").css("display", "none");
                $scope.$apply(function () {
                  var isFirstRow = $("#is-first-row").prop("checked");
                  if (isFirstRow) {
                    $scope.excelData.splice(0, 0, first_row);
                  }
                  $scope.errorMsg =
                    $scope.uploadedDataCount +
                    " data uploaded out of " +
                    $scope.totalExcelData;
                  $scope.serverErrorMsg = data.msg;
                  $scope.startIndex = 0;
                  sendData = 0;
                  $scope.completePercentage = "0%";
                  $scope.imageUpload = false;
                  $scope.imageUploadBtn = false;
                  $scope.fileInfo = false;
                  $scope.excelSection = true;
                  $scope.disable = false;
                  $scope.showDialog = true;
                  $scope.imageUploadBtn = false;
                  $scope.imageImportBtn = false;
                  var height = $(window).height() - 210;
                  $("#errorBody").css("max-height", height + "px");
                  $("#errorDialog").modal("show");
                  $scope.errorData = $scope.errorData;
                });
              }
            },
            "json",
            "appMsg",
            undefined,
            undefined,
            undefined,
            {
              hideLoading: true,
            }
          );
        };

        $scope.importItems = function (check_product) {
          for (i = 0; i <= $scope.excelData.length - 1; i++) {
            $scope.colIndex = i;
            for (j = 0; j <= $scope.excelData[i].length - 1; j++) {
              $scope.rowIndex = j;
              $scope.rowData = $scope.excelData[i][j];
              if ($scope.mappingFieldsData[$scope.rowIndex] == undefined) {
                sparrow.showMessage(
                  "appMsg",
                  sparrow.MsgType.Error,
                  "First row columns are not matching with other row columns.",
                  10
                );
                return false;
              }
              if (
                $scope.isValidData(
                  $scope.rowIndex,
                  $scope.rowData,
                  $scope.colIndex,
                  false
                )
              ) {
                $(
                  "#td_cell_" + $scope.colIndex + "_" + $scope.rowIndex + ""
                ).addClass("invalid-data");
                $(
                  "#td_warning_icon_" + $scope.colIndex + "_" + $scope.rowIndex
                ).css("display", "block");
              } else {
                $(
                  "#td_cell_" + $scope.colIndex + "_" + $scope.rowIndex + ""
                ).removeClass("invalid-data");
                $(
                  "#td_warning_icon_" + $scope.colIndex + "_" + $scope.rowIndex
                ).css("display", "none");
              }
            }
          }
          var columns = "";
          var count = 0;
          var bom_name;
          var dropdown_Value = $(".selectList").val();
          if (model_name == "bom_line") {
            bom_name = $("#id_bom_name").val() || "";
            if (bom_name == "") {
              sparrow.showMessage(
                "appMsg",
                sparrow.MsgType.Error,
                "Please enter bom name.",
                10
              );
              return false;
            }
          }
          if (check_product) {
            if ($scope.selectedMapColumn.indexOf("product_images") != -1) {
              $scope.excelSection = false;
              $scope.imageUpload = true;
              return false;
            }
          }

          for (var i = 0; i < $scope.required_fields.length; i++) {
            if (
              $scope.selectedMapColumn.indexOf($scope.required_fields[i]) == -1
            ) {
              sparrow.showMessage(
                "appMsg",
                sparrow.MsgType.Error,
                "Please map all required fields.",
                10
              );
              return false;
            }
          }
          for (var i = 0; i < $scope.headerWarning.length; i++) {
            if ($scope.headerWarning[i]) {
              if (count > 0) {
                columns += ", " + $scope.mappingFieldsData[i].col_label;
              } else {
                columns += $scope.mappingFieldsData[i].col_label + " ";
              }
              count++;
            }
          }
          if (columns != "") {
            sparrow.showMessage(
              "appMsg",
              sparrow.MsgType.Error,
              "Column(s) " + columns + " contains invalid data.",
              10
            );
            return false;
          } else if (dropdown_Value != null && dropdown_Value != "none") {
            if ($scope.selectedMapColumn.indexOf(dropdown_Value) == -1) {
              selectedOption = $(
                '.selectList option[value="' + $(".selectList").val() + '"]'
              ).text();
              sparrow.showMessage(
                "appMsg",
                sparrow.MsgType.Error,
                selectedOption + " is not mapped.",
                10
              );
              return false;
            }
          }

          $scope.disable = true;
          $scope.excelSection = false;
          $scope.imageUpload = false;
          $scope.fileInfo = false;
          $(".after-import-show").css("display", "block");
          var url = $scope.postUrl;
          var isFirstRow = $("#is-first-row").prop("checked");
          var createProduct = "";
          var radio_value = $("input[name=operation_category]:checked").val();
          if (
            model_name == "purchase_order_line" ||
            model_name == "sale_order_line" ||
            model_name == "mfg_bom_line" ||
            model_name == "bom_line"
          ) {
            createProduct = $("#is-create-product").prop("checked");
          }

          fullDataKeys = $scope.excelData[0];
          exceldata_length = $scope.excelData.length - 1;
          if (isFirstRow) {
            first_row = $scope.excelData.shift();
          }
          $scope.send_data_to_server(
            url,
            radio_value,
            dropdown_Value,
            createProduct,
            bom_name,
            fullDataKeys
          );
        };
      }
    );
  },
]);
