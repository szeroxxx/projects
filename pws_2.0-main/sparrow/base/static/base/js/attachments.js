/* eslint-disable no-unused-vars */
/* eslint-disable no-multi-str */
/* eslint-disable max-len */
/* eslint-disable indent */
/* eslint-disable prettier/prettier */
(function () {
  angular
    .module("angular-attachments", [])
    .directive("angAttachments", function () {
      return {
        restrict: "AEC",
        scope: {
          appName: "@",
          modelName: "@",
          entityId: "@",
          countId: "@",
          files: "@",
          file_types: "@",
          sourceDoc: "@",
        },
        replace: true,
        controller: function ($scope, Upload, $route, ModalService) {
          $scope.showWorkcenter = false;
          $scope.currentIndex = 0;
          $scope.attachments = [];
          $scope.com_id = [];
          $scope.documentsdata = [];
          $scope.attachment_total = "";
          $scope.tags = ""

          if ($scope.entityId === "") {
            $scope.comments = [];
            return;
          }
          $scope.currentPage = 1;
          $scope.pageNumber = 1;
          $scope.searchFilters = {
            search_filter: "",
          };

          getAttachments($scope.searchFilters, "doc");

          $scope.closeDailouge = function (event) {
            event.preventDefault();
            $("#id_message").hide();
            $("#id_customer").css("border-color", "#ccc");
            $("#onAttachmentDailougeModel").attr("class", "modal fade");
            $("#onAttachmentDailougeModel").hide();
            $scope.files = [];
            // $route.reload();
          };
          $scope.delete = function (attachment_data) {
            permission = $scope.permissions;
            if (attachment_data.is_url == null) {
              if (permission["can_delete_attachment"] == false) {
                sparrow.showMessage(
                  "appMsg",
                  sparrow.MsgType.Error,
                  "You do not have permission to perform this action",
                  10
                );
                return;
              }
              sparrow.showConfirmDialog(
                ModalService,
                "Are you sure, want to remove document?",
                "Remove Document",
                function (confirm) {
                  if (confirm) {
                    var id = attachment_data.id;
                    sparrow.post(
                      "/attachment/del_attachment/",
                      {
                        id: id,
                        app: attachment_data.app_name,
                        model: attachment_data.model_name,
                        is_url: false
                      },
                      false,
                      function (data) {
                        if (data.code == 1) {
                          getAttachments("", "doc");
                          sparrow.showMessage(
                            "appMsg",
                            sparrow.MsgType.Success,
                            data.msg,
                            3
                          );
                        }
                        for (
                          var i = $scope.attachments.length - 1;
                          i >= 0;
                          i--
                        ) {
                          if ($scope.attachments[i].id == id) {
                            $scope.attachments.splice(i, 1);
                            break;
                          }
                        }

                        if ($scope.attachments.length >= 1) {
                          var index = $scope.currentIndex - 1;
                          $scope.propertyDetails(
                            $scope.attachments[0].name,
                            $scope.attachments[0].title,
                            $scope.attachments[0].subject,
                            $scope.attachments[0].description,
                            $scope.attachments[0].id,
                            $scope.attachments,
                            0,
                            $scope.attachments[0].is_public,
                            $scope.attachments[0].uid,
                            $scope.attachments[0].app_name,
                            $scope.attachments[0].model_name,
                            $scope.attachments[0].model_exist,
                            $scope.attachments[0].selected_tags
                          );
                          $scope.attachments[0].isSelected = false;
                          if (index == -1) {
                            $scope.attachments[0].isSelected = true;
                          } else {
                            $scope.propertyDetails(
                              $scope.attachments[index].name,
                              $scope.attachments[index].title,
                              $scope.attachments[index].subject,
                              $scope.attachments[index].description,
                              $scope.attachments[index].id,
                              $scope.attachments,
                              index,
                              $scope.attachments[index].is_public,
                              $scope.attachments[index].uid,
                              $scope.attachments[index].app_name,
                              $scope.attachments[index].model_name,
                              $scope.attachments[index].model_exist,
                              $scope.attachments[index].selected_tags
                            );
                            $scope.attachments[index].isSelected = true;
                          }
                        }

                        if ($scope.attachments.length == 0) {
                          $scope.IsVisible = false;
                        }
                        var index = $scope.currentIndex;
                        $scope.attachment_data = $scope.attachments[index];
                        $scope.updateCount($scope.attachments.length);
                        $scope.$digest();
                      }
                    );
                  }
                }
              );
            } else {
              if (permission["can_delete_link"] == false) {
                sparrow.showMessage(
                  "appMsg",
                  sparrow.MsgType.Error,
                  "You do not have permission to perform this action",
                  10
                );
                return;
              }
              sparrow.showConfirmDialog(
                ModalService,
                "Are you sure, want to remove link?",
                "Remove Link",
                function (confirm) {
                  if (confirm) {
                    var id = attachment_data.id;
                    sparrow.post(
                      "/attachment/del_attachment/",
                      {
                        id: id,
                        app: attachment_data.app_name,
                        model: attachment_data.model_name,
                        is_url: true,
                      },
                      false,
                      function (data) {
                        if (data.code == 1) {
                          getAttachments("", "doc");
                          sparrow.showMessage(
                            "appMsg",
                            sparrow.MsgType.Success,
                            data.msg,
                            3
                          );
                        }
                        for (
                          var i = $scope.attachments.length - 1;
                          i >= 0;
                          i--
                        ) {
                          if ($scope.attachments[i].id == id) {
                            $scope.attachments.splice(i, 1);
                            break;
                          }
                        }

                        if ($scope.attachments.length >= 1) {
                          var index = $scope.currentIndex - 1;
                          $scope.propertyDetails(
                            $scope.attachments[0].name,
                            $scope.attachments[0].title,
                            $scope.attachments[0].subject,
                            $scope.attachments[0].description,
                            $scope.attachments[0].id,
                            $scope.attachments,
                            0,
                            $scope.attachments[0].is_public,
                            $scope.attachments[0].uid,
                            $scope.attachments[0].app_name,
                            $scope.attachments[0].model_name,
                            $scope.attachments[0].model_exist,
                            $scope.attachments[0].selected_tags
                          );
                          $scope.attachments[0].isSelected = false;
                          if (index == -1) {
                            $scope.attachments[0].isSelected = true;
                          } else {
                            $scope.propertyDetails(
                              $scope.attachments[index].name,
                              $scope.attachments[index].title,
                              $scope.attachments[index].subject,
                              $scope.attachments[index].description,
                              $scope.attachments[index].id,
                              $scope.attachments,
                              index,
                              $scope.attachments[index].is_public,
                              $scope.attachments[index].uid,
                              $scope.attachments[index].app_name,
                              $scope.attachments[index].model_name,
                              $scope.attachments[index].model_exist,
                              $scope.attachments[index].selected_tags
                            );
                            $scope.attachments[index].isSelected = true;
                          }
                        }
                        if ($scope.attachments.length == 0) {
                          $scope.IsVisible = false;
                        }
                        var index = $scope.currentIndex;
                        $scope.attachment_data = $scope.attachments[index];
                        $scope.updateCount($scope.attachments.length);
                        $scope.$digest();
                      }
                    );
                  }
                }
              );
            }
          };

          $scope.uploadDailouge = function (files) {
            if (data.permissions["can_upload_document"] == false) {
              sparrow.showMessage(
                "appMsg",
                sparrow.MsgType.Error,
                "You do not have permission to perform this action",
                3
              );
              return;
            }

            $scope.files = [];
            for (var i = 0; i < files.length; i++) {
              var fileName = sparrow.removeInvaidUTF8Char(files[i]["name"]);
              $scope.files.push(
                new File([files[i]], fileName, { type: files[i].type })
              );
              $scope.onAttachmentDailougeTitle = "Upload file(s)";
              $("#onAttachmentDailougeModel").show();
              $("#onAttachmentDailougeModel").attr("class", "modal fade in");
            }
          };

          $scope.getPageIndex = function (event, index, pageNumber) {
            var total_page = parseInt($scope.attachment_total) / 25;
            if (total_page <= pageNumber) {
              return;
            }
            event.preventDefault();
            // if (index <= 0 || index > $scope.totalAttachments) {
            //   return;
            // }
            $scope.currentPage = index;
            $scope.pageNumber = (index + 24) / 25;
            $scope.searchFilters.page_index = index;
            if ($scope.pageNumber > 199) {
              sparrow.showMessage(
                "appMsg",
                sparrow.MsgType.Error,
                "You cannot access records beyond page number 199",
                10
              );
              return;
            }
            getAttachments($scope.searchFilters, "doc");
          };

          $scope.sourceDocEdit = function (
            app_name,
            model_name,
            source_doc,
            entity_id
          ) {
            var type = "partner";
            var lastIndex = model_name.lastIndexOf("_");
            model_name = model_name.substring(0, lastIndex);

            sparrow.onEditLink(
              sparrow.getEntityIframeURL(
                app_name,
                model_name,
                entity_id,
                source_doc,
                type
              ),
              source_doc
            );
          };

          $scope.$on(
            "onAttachmentChange",
            function (event, attachment_data, is_delete) {
              if (!is_delete) {
                var attachment = attachment_data;
                attachment.date = $scope.getReadableDateRight(
                  attachment.create_date
                );
                attachment.id = attachment.attachment_id;
                attachment.object_id = attachment.entity_id;
                attachment.app_name = $scope.appName;
                attachment.model_name = $scope.modelName;
                attachment.permissions = $scope.permissions;
                $scope.attachments.push(attachment);
                $scope.attachment_data = $scope.attachments.at(-1);
                $scope.updateCount($scope.attachments.length);
              } else {
                var id = attachment_data;
                for (var i = $scope.attachments.length - 1; i >= 0; i--) {
                  if ($scope.attachments[i].id == id) {
                    $scope.attachments.splice(i, 1);
                    break;
                  }
                  $scope.updateCount($scope.attachments.length);
                }
              }
            }
          );
          setAutoLookup("id_customer","/b/lookups/companies/","",true,"","","",1);
          setAutoLookup("id_doc_tag","/b/lookups/document_tag/","",true,"","","",1);
          if (data.permissions["can_upload_document"] == false) {
            $("#id_staff_file").hide();
          } else {
            $("#id_staff_file").show();
          }
          // if (data.permissions["can_delete_attachment"] == false) {
          //   $("#id_staff_file_dlt").hide();
          // } else {
          //   $("#id_staff_file_dlt").show();
          // }
          // if (data.permissions["can_make_attachment_public"] == false) {
          //   $("#id_staff_file_lock").hide();
          // } else {
          //   $("#id_staff_file_lock").show();
          // }
          $scope.permissions = "";
          var cussearchParam = [];
          function getAttachments(searchFilters, search_type, tag = null) {
            var searchParam = {};
            if (searchFilters != undefined) {
              if ($scope.isSearchPerformed) {
                $scope.isSearchPerformed = false;
              } else {
                // if (search_type == "doc") {
                //   searchParam["search_filter"] = searchFilters.search_filter;
                // }
                // if (search_type == "tag") {
                //   searchParam["search_filter"] = JSON.stringify(
                //     searchFilters.search_filter
                //   );
                // }

                searchParam["page_index"] = $scope.currentPage;
                if ($scope.entityId != 0) {
                  searchParam["object_id"] = $scope.entityId;
                }
                searchParam["search_type"] = search_type;
                searchParam["tag"] = tag;
                searchParam["app"] = $scope.appName;
                searchParam["model"] = $scope.modelName;
                searchParam["customer"] = $scope.com_id[0];
                searchParam["documentdata"] = $scope.documentsdata;
              }
            }
            sparrow.post(
              "/attachment/get_attachments/",
              searchParam,
              false,
              function (data) {
                $scope.$apply(function () {
                  $scope.tags = data.tags[0];
                  // treeViewTags(data.tags[0]);
                  $scope.attachment_total = data.base_Attachment_count;
                  $scope.file_types = data.file_types;
                  $scope.updateCount(data.count);
                  $scope.attachments = data.data;
                  if ($scope.attachments.length == 0) {
                    $scope.IsVisible = false;
                  } else {
                    $scope.IsVisible = true;
                  }
                  if ($scope.attachments.length != 0) {
                    $scope.permissions = JSON.parse(
                      $scope.attachments[0]["permissions"]
                    );
                  }

                  for (var i = 0; i < $scope.attachments.length; i++) {
                    $scope.attachments[i].isSelected = false;
                    $scope.attachments[i].date = $scope.getReadableDateRight(
                      data.data[i].create_date
                    );
                    $scope.ngcolor = sparrow.global.get(
                      sparrow.global.keys.ROW_COLOR
                    );
                  }

                  if ($scope.attachments.length >= 1) {
                    $scope.propertyDetails(
                      $scope.attachments[0].name,
                      $scope.attachments[0].title,
                      $scope.attachments[0].subject,
                      $scope.attachments[0].description,
                      $scope.attachments[0].id,
                      $scope.attachments,
                      0,
                      $scope.attachments[0].is_public,
                      $scope.attachments[0].uid,
                      $scope.attachments[0].app_name,
                      $scope.attachments[0].model_name,
                      $scope.attachments[0].model_exist,
                      $scope.attachments[0].selected_tags
                    );
                    if (
                      $scope.appName == "production" &&
                      $scope.modelName == "mfg_order_attachment"
                    ) {
                      var workCenter = $(
                        "#attach_id_workcenter"
                      ).magicSuggest();
                      if (
                        $scope.attachments[0].workcenter_id &&
                        $scope.attachments[0].workcenter_name
                      ) {
                        workCenter.setSelection([
                          {
                            id: $scope.attachments[0].workcenter_id,
                            name: $scope.attachments[0].workcenter_name,
                          },
                        ]);
                      } else {
                        workCenter.clear();
                      }
                    }
                    $scope.attachment_data = $scope.attachments[0];
                  }
                  // $scope.totalAttachments = data.total_attachments;
                  $scope.totalAttachments = data.record_total;
                });
              }
            );
          }
           function treeViewTags(tags) {
              $("#treeview")
                .treeview({
                  data: tags,
                  levels: 1,
                  expandIcon:
                    "glyphicon glyphicon-chevron-right btn-xs newicon",
                  collapseIcon:
                    "glyphicon glyphicon-chevron-down  btn-xs newicon",
                  emptyIcon: "glyphicon glyphicon-chevron-down btn-xs newicon",
                })
                .on("nodeSelected", function (event, node) {
                  getAttachments("", "", node.text);
                });
                $("#treeview").treeview("expandAll", { silent: true });
           };

          $scope.docSearch = function () {
            getAttachments("", "doc");
          };
          $(".tag_div").hide();
          $scope.onTagViewChange = function (val) {
            if (val === true) {
              $(".tag_div").show();
              treeViewTags($scope.tags)

            } else {
              $(".tag_div").hide();
              getAttachments("", "doc");
            }
          };

          // var searchQuery = document.getElementById("searchQuery");
          // searchQuery.addEventListener("keydown", function (e) {
            // data = $("#searchQuery").val().trim();
            // $scope.searchFilters.search_filter = data;
            // $scope.documentsdata = data;

            // getAttachments($scope.searchFilters, "doc");
          // });
          // document.onkeydown = function (e) {
          //   search_data();
          // };

          search_data = function ($event) {
            if (event.keyCode == 13 || event.keyCode == 8) {
              data = $("#searchQuery").val().trim();
              $scope.searchFilters.search_filter = data;
              $scope.documentsdata = data;
              getAttachments($scope.searchFilters, "doc");
            }
          };
          $scope.searchTag = function (data) {
            cussearchParam.push(data.search_filter[0]);
            // $scope.$apply(() => {
            //   $scope.cussearchParam = data.search_filter[0];
            // });
            getAttachments(data, "tag");
          };
          var customer = $("#id_customer").magicSuggest();
          $(customer).on("selectionchange", function (e, m) {
            var customer_id = $("#hid_customer").val();
            if (customer_id) {
              $("#id_message").hide();
              $("#id_customer").css("border-color", "#ccc");
            }
          });
          $scope.upload = function (event) {
            var customer = $("#hid_customer").val();
            var tag = "";
            if ($("#hid_tag").val()) {
              var tag = $("#hid_tag").val();
            }
            if (!customer) {
              $("#id_message").show();
              $("#id_customer").css("border-color", "#a94442");
              return;
            }
            permission = $scope.permissions;
            if (permission["can_upload_document"] == false) {
              event.preventDefault();
              sparrow.showMessage(
                "appMsg",
                sparrow.MsgType.Error,
                "You do not have permission to perform this action",
                10
              );
              return;
            }

            event.preventDefault();
            var files = $scope.files;
            var fileType_id = $("#id_file_type").find(":selected").val();
            var makePublic = $("#is_make_public").is(":checked");
            if (files.length > 5) {
              sparrow.showMessage(
                "appMsg",
                sparrow.MsgType.Error,
                "You can upload maximum 5 documents at a time.",
                10
              );
              return false;
            }
            if (files && files.length) {
              for (var i = 0; i < files.length; i++) {
                if (files[i].size > 10000000) {
                  sparrow.showMessage(
                    "appMsg",
                    sparrow.MsgType.Error,
                    "File more than 10MB size is not allowed.",
                    10
                  );
                  return false;
                }
                if (files != "") {
                  if (files[0].name.length > 170) {
                    sparrow.showMessage(
                      "appMsg",
                      sparrow.MsgType.Error,
                      "File name is too long.",
                      3
                    );
                    return;
                  }
                }
                $("#loading-image").show();
                Upload.upload({
                  url: "/attachment/upload_attachment",
                  data: {
                    file: files[i],
                    object_id: $scope.entityId,
                    app: $scope.appName,
                    model: $scope.modelName,
                    file_type: fileType_id,
                    makePublic: makePublic,
                    source_doc: $scope.sourceDoc,
                    customer_id: customer,
                    tag_id: tag,
                  },
                }).then(
                  function (resp) {
                    if (resp.data.code == 1) {
                      $route.reload();
                      var attachment = resp.data.data[0];
                      attachment.date = $scope.getReadableDateRight(
                        attachment.create_date
                      );
                      attachment.id = attachment.attachment_id;
                      attachment.object_id = attachment.entity_id;
                      attachment.app_name = $scope.appName;
                      attachment.model_name = $scope.modelName;
                      attachment.permissions = $scope.permissions;
                      $("#onAttachmentDailougeModel").hide();
                      $("#loading-image").hide();
                      $scope.attachments.push(attachment);
                      $scope.propertyDetails(
                        $scope.attachments.at(-1).name,
                        $scope.attachments.at(-1).title,
                        $scope.attachments.at(-1).subject,
                        $scope.attachments.at(-1).description,
                        $scope.attachments.at(-1).id,
                        $scope.attachments,
                        0,
                        $scope.attachments.at(-1).is_public,
                        $scope.attachments.at(-1).uid,
                        $scope.attachments.at(-1).app_name,
                        $scope.attachments.at(-1).model_name,
                        $scope.attachments.at(-1).model_exist,
                        $scope.attachments.at(-1).selected_tags
                      );
                      if (
                        $scope.appName == "production" &&
                        $scope.modelName == "mfg_order_attachment"
                      ) {
                        var workCenter = $(
                          "#attach_id_workcenter"
                        ).magicSuggest();
                        if (
                          $scope.attachments.at(-1).workcenter_id &&
                          $scope.attachments.at(-1).workcenter_name
                        ) {
                          workCenter.setSelection([
                            {
                              id: $scope.attachments.at(-1).workcenter_id,
                              name: $scope.attachments.at(-1).workcenter_name,
                            },
                          ]);
                        } else {
                          workCenter.clear();
                        }
                      }
                      $scope.ngcolor = sparrow.global.get(
                        sparrow.global.keys.ROW_COLOR
                      );
                      $scope.attachments[0].isSelected = false;
                      $scope.attachments.at(-1).isSelected = true;
                      $scope.attachment_data = $scope.attachments.at(-1);
                      $scope.updateCount($scope.attachments.length);
                    } else {
                      $("#loading-image").hide();
                      sparrow.showMessage(
                        "appMsg",
                        sparrow.MsgType.Error,
                        resp.data.msg,
                        10
                      );
                    }
                  },
                  function (resp) {
                    $("#loading-image").hide();
                    sparrow.showMessage(
                      "appMsg",
                      sparrow.MsgType.Error,
                      resp.status,
                      10
                    );
                  }
                );
              }
            }
          };
        },

        link: function ($scope, elem, attrs, Upload) {
          setTimeout(function () {
            setAutoLookup(
              "id_tag_search",
              "/b/lookups/companies/",
              "",
              false,
              false,
              false,
              null
            );
          }, 100);
          setTimeout(function () {
            var msTagSearch = $("#id_tag_search").magicSuggest();
            $(msTagSearch).on("selectionchange", function (e, m) {
              var selection = msTagSearch.getSelection();
              ids = [];
              for (i = 0; i <= selection.length - 1; i++) {
                ids.push(selection[i]["id"]);
              }
              $scope.searchFilters.search_filter = ids;
              $scope.com_id = ids;
              $scope.searchTag($scope.searchFilters);
            });
          }, 100);

          $scope.updateCount = function (count) {
            if ($("#" + $scope.countId) != undefined) {
              $("#" + $scope.countId).hide();
              if (count > 0) {
                $("#" + $scope.countId).text("(" + count + ")");
                $("#" + $scope.countId).show();
              }
            }
          };

          if (
            $scope.appName == "production" &&
            $scope.modelName == "mfg_order_attachment"
          ) {
            $scope.showWorkcenter = true;
            setTimeout(function () {
              setAutoLookup(
                "attach_id_workcenter",
                "/b/lookups/workcenter/",
                "",
                false
              );
              var workCenter = $("#attach_id_workcenter").magicSuggest();
              $(workCenter).on("selectionchange", function (e, m) {
                var selection = workCenter.getSelection()[0];
                if (selection) {
                  $scope.propertySave(
                    "workcenter_id",
                    selection.id,
                    "production",
                    "mfg_order_attachment"
                  );
                } else {
                  $scope.propertySave(
                    "workcenter_id",
                    "",
                    "production",
                    "mfg_order_attachment"
                  );
                }
              });
            }, 0);
          }
          $scope.IsVisible = false;
          $scope.attachment_name = "";
          $scope.attachment_id = 0;

          $scope.propertyDetails = function (
            attachment_name,
            attachment_title,
            attachment_subject,
            attachment_description,
            attachment_id,
            attachment,
            index,
            attachment_is_public,
            attachment_uid,
            app_name,
            model_name,
            model_exist,
            selected_tag
          ) {
            $scope.currentIndex = index;
            for (var i = 0; i < $scope.attachments.length; i++) {
              if (index == i) {
                if ($scope.attachments[i].isSelected) {
                  $scope.attachments[i].isSelected = false;
                } else {
                  $scope.attachments[i].isSelected = true;
                }
              } else {
                $scope.attachments[i].isSelected = false;
              }
            }
            $scope.is_public = attachment_is_public;
            $scope.attachment_data = attachment;
            $scope.attachment_name = attachment_name;
            $scope.title = attachment_title;
            $scope.app_name = app_name;
            $scope.model_name = model_name;
            $scope.subject = attachment_subject;
            $scope.description = attachment_description;
            $scope.attachment_id = attachment_id;
            $scope.attachment_uid = attachment_uid;
            $scope.model_exist = model_exist;
            $scope.IsVisible = true;
            if (
              $scope.appName == "production" &&
              $scope.modelName == "mfg_order_attachment"
            ) {
              var workCenter = $("#attach_id_workcenter").magicSuggest();
              if (attachment.workcenter_id && attachment.workcenter_name) {
                workCenter.setSelection([
                  {
                    id: attachment.workcenter_id,
                    name: attachment.workcenter_name,
                  },
                ]);
              } else {
                workCenter.clear();
              }
            }
            $(".tagDiv").css("display", "none");
            if ($scope.model_exist) {
              $(".tagDiv").css("display", "block");
              var tagAutoLookupConfig = {
                iframeData: {
                  url: "#/attachment/tag/0",
                  title: "Add tag",
                },
                addLooupItemTitle: "Add tag",
              };
              setAutoLookup(
                "id_tag",
                "/b/lookups/companies/",
                "",
                false,
                false,
                false,
                null,
                10,
                null,
                null
                // tagAutoLookupConfig
              );
              $scope.setTag(selected_tag);
            }
          };

          $scope.setTag = function (selected_tag) {
            var msTag = $("#id_tag").magicSuggest();

            // Define event to save tag data.
            $(msTag)
              .off("blur")
              .on("blur", function (e, m) {
                var selection = msTag.getSelection();
                tagList = [];
                tagNameList = [];

                for (i = 0; i <= selection.length - 1; i++) {
                  tagList.push(selection[i]["id"]);
                  tagNameList.push(selection[i]["name"]);
                }

                postData = {
                  attachment_id: $scope.attachment_id,
                  tag_list: tagList.toString(),
                  tag_name_list: tagNameList.toString(),
                  app_name: $scope.app_name,
                  model_name: $scope.model_name,
                };

                sparrow.post(
                  "/attachment/save_doc_tag/",
                  postData,
                  false,
                  function (data) {
                    $scope.attachments[$scope.currentIndex].selected_tags =
                      data.data;
                  }
                );
              });

            // Set tag data.
            if (selected_tag.length == 0) {
              msTag.clear();
            } else {
              msTag.setSelection(selected_tag);
            }
          };

          $scope.isImage = function (extension) {
            if (
              extension == "bmp" ||
              extension == "gif" ||
              extension == "png" ||
              extension == "ico" ||
              extension == "jpg" ||
              extension == "jpeg"
            ) {
              return true;
            } else {
              return false;
            }
          };

          $scope.fileSize = function (filesize) {
            var intFileSize = parseInt(filesize);
            if (intFileSize > 1) {
              return true;
            } else {
              return false;
            }
          };

          $scope.getPreviewImage = function (fileName) {
            var isImage = false;
            var extension = $scope.getFileExtension(fileName);
            var previewImageUrl = "";
            isImage = $scope.isImage($scope.getFileExtension(fileName));
            if (isImage) {
              $("image-attachment").css("padding-bottom", "0px !important");
              var msgAttachIndex = fileName.lastIndexOf("/") + 1;
              previewImageUrl =
                fileName.slice(0, msgAttachIndex) +
                "t-" +
                fileName.slice(msgAttachIndex);
              previewImageUrl = "/static/base/images/file-icons/image.svg";
              return previewImageUrl;
            } else {
              switch (extension) {
                case "doc":
                  previewImageUrl = "/static/base/images/file-icons/word.svg";
                  return previewImageUrl;
                case "docx":
                  previewImageUrl = "/static/base/images/file-icons/word.svg";
                  return previewImageUrl;

                case "pdf":
                  previewImageUrl = "/static/base/images/file-icons/pdf.svg";
                  return previewImageUrl;
                case "ppt":
                  previewImageUrl =
                    "/static/base/images/file-icons/powerpoint.svg";
                  return previewImageUrl;
                case "pptx":
                  previewImageUrl =
                    "/static/base/images/file-icons/powerpoint.svg";
                  return previewImageUrl;
                case "xlsx":
                  previewImageUrl = "/static/base/images/file-icons/excel.svg";
                  return previewImageUrl;
                case "xls":
                  previewImageUrl = "/static/base/images/file-icons/excel.svg";
                  return previewImageUrl;
                case "csv":
                  previewImageUrl = "/static/base/images/file-icons/csv.svg";
                  return previewImageUrl;
                case "xml":
                  previewImageUrl = "/static/base/images/file-icons/xml.svg";
                  return previewImageUrl;
                case "txt":
                  previewImageUrl = "/static/base/images/file-icons/txt.svg";
                  return previewImageUrl;
                case "zip":
                  previewImageUrl = "/static/base/images/file-icons/zip.svg";
                  return previewImageUrl;
                case "rar":
                  previewImageUrl = "/static/base/images/file-icons/rar.svg";
                  return previewImageUrl;
                case "html":
                  previewImageUrl =
                    "/static/base/images/file-icons/html-file.svg";
                  return previewImageUrl;
                default:
                  previewImageUrl = "/static/base/images/file-icons/file.svg";
                  return previewImageUrl;
              }
            }
            return previewImageUrl;
          };
          $scope.editDocument = function (e, doc_id, is_url) {
            permission = $scope.permissions;
            if (is_url == null) {
              if (permission["can_add_update"] == true) {
                $("#loading-image").show();
                window.location.hash = "/document/edit/" + doc_id;
              } else {
                sparrow.showMessage(
                  "appMsg",
                  sparrow.MsgType.Error,
                  "You do not have permission to perform this action",
                  3
                );
                return;
              }
            }else{
              if (permission["can_add_update_link"] == true) {
                window.location.hash = "/document/editlink/" + doc_id;
              } else {
                sparrow.showMessage(
                  "appMsg",
                  sparrow.MsgType.Error,
                  "You do not have permission to perform this action",
                  3
                );
                return;
              }
            }
          };
          $scope.getFileExtension = function (fileName) {
            var extensionIndex = fileName.lastIndexOf(".") + 1;
            var extension =
              parseInt(extensionIndex) > 0
                ? fileName.substr(extensionIndex).toLowerCase()
                : "";
            return extension;
          };

          $scope.propertySave = function (
            field_name,
            value,
            app_name,
            model_name
          ) {
            var value = value;
            var filedName = field_name;
            if (filedName == "title") {
              $scope.attachments[$scope.currentIndex].title = value;
            } else if (filedName == "description") {
              $scope.attachments[$scope.currentIndex].description = value;
            } else if (filedName == "subject") {
              $scope.attachments[$scope.currentIndex].subject = value;
            }
            sparrow.post(
              "/attachment/attachment_properties/",
              {
                field_name: field_name,
                value: value,
                attachment_id: $scope.attachment_id,
                app: app_name,
                model: model_name,
                object_id: $scope.entityId,
              },
              false,
              function (data) {
                for (var i = 0; i < data.data.length; i++) {
                  data.data[i].date = $scope.getReadableDateRight(
                    data.data[i].create_date
                  );
                  if (i == $scope.currentIndex) {
                    data.data[i].isSelected = true;
                    $scope.ngcolor = sparrow.global.get(
                      sparrow.global.keys.ROW_COLOR
                    );
                  }
                }
                $scope.$digest();
              },
              "json",
              "appMsg",
              undefined,
              undefined,
              undefined,
              { hideLoading: true }
            );
          };

          $scope.getReadableDateRight = function (createdOn) {
            $scope.readableDateRight = "";
            var readableDate = "";
            // var year = createdOn.split("/")[2];
            // if (moment(new Date().getFullYear()) == year) {
            //   readableDate = moment.tz(createdOn).utc().format("MMM D");
            // } else {
            //   readableDate = moment.tz(createdOn).utc().format("MMM D");
            // }
            $scope.readableDateRight = readableDate;
            return $scope.readableDateRight;
          };

          $scope.toggleAccess = function (attachment_data) {
            permission = $scope.permissions;
            if (attachment_data.is_url == null) {
              if (permission["can_make_attachment_public"] == false) {
                sparrow.showMessage(
                  "appMsg",
                  sparrow.MsgType.Error,
                  "You do not have permission to perform this action",
                  10
                );
                return;
              }
              sparrow.post(
                "/attachment/attachment_change_access/",
                {
                  id: attachment_data.id,
                  app: attachment_data.app_name,
                  model: attachment_data.model_name,
                  is_url: false
                },
                false,
                function (data) {
                  if (data.code == 0) {
                    sparrow.showMessage(
                      "appMsg",
                      sparrow.MsgType.Error,
                      data.msg,
                      10
                    );
                    return;
                  }
                  $(".navbar-nav").load(window.location.href + " .navbar-nav");
                  attachment_data.is_public = data.access;
                  $scope.$digest();
                }
              );
            } else{
              if (permission["can_make_link_public"] == false) {
                sparrow.showMessage(
                  "appMsg",
                  sparrow.MsgType.Error,
                  "You do not have permission to perform this action",
                  10
                );
                return;
              }
              sparrow.post(
                "/attachment/attachment_change_access/",
                {
                  id: attachment_data.id,
                  app: attachment_data.app_name,
                  model: attachment_data.model_name,
                  is_url: true
                },
                false,
                function (data) {
                  if (data.code == 0) {
                    sparrow.showMessage(
                      "appMsg",
                      sparrow.MsgType.Error,
                      data.msg,
                      10
                    );
                    return;
                  }
                  $(".navbar-nav").load(window.location.href + " .navbar-nav");
                  attachment_data.is_public = data.access;
                  $scope.$digest();
                }
              );
            }
          };
          $scope.copyLink = function (uid, app, model, link) {
            sparrow.showMessage(
              "appMsg",
              sparrow.MsgType.Success,
              "URL copied to clipboard.",
              10
            );
            if (link) {
              var finalLink = link
              CopyToClipboard(finalLink);
            } else{
              linkText =
              "/attachment/dwn_attachment/?uid=" +
              uid +
              "&a=" +
              app +
              "&m=" +
              model;
              url = document.URL.split("/");
              var finalLink = window.location.protocol + "//" + url[2] + linkText;
              CopyToClipboard(finalLink);
            }
          };
          },
        templateUrl: function (element, attr) {
          return attr.templateUrl || "angular-attachments.html";
        },
      };
    });
})();

angular.module("angular-attachments").run([
  "$templateCache",
  function ($templateCache) {
    $("#descriptionDiv").hide();
    ("use strict");
    $templateCache.put(
      "angular-attachments.html",
      '<div class = "col-sm-12" style="min-height:100px;">\
          <style>\
          .textcenter>th{\
            text-align:center\
          }\
          div.scrollable {\
              width: 100%;\
              height: 550px;\
              margin: 0;\
              padding: 0;\
              overflow: auto;\
          }\
          .float-container {\
              display: grid;\
              grid-template-columns: 1fr 1fr;\
              grid-gap: 20px;\
          }\
          .detailsTag>div {\
              text-overflow: ellipsis;\
              overflow: hidden;\
              width: 125px;\
              height: 1.2em;\
              white-space: nowrap;\
          }\
          .documentTag {\
            text-overflow: ellipsis;\
            overflow: hidden;\
            width: 160px;\
            height: 1.2em;\
            white-space: nowrap;\
            padding-left: 10px;\
          }\
          .newicon {\
            color:#888888 !important;\
            font-size: 9px !important;\
          }\
          .list-group-item{\
            padding:5px 10px;\
          }\
          .searchbar {\
                float: right !important;\
                margin: 14px 10px 16px 0px !important;\
                width: 99% !important;\
            }\
            .search-input {\
                margin-right: -2px;\
                line-height: 20px !important;\
                padding: 2px 5px 2px 10px;\
                outline: none;\
                border: 0px;\
                width: 95%;\
            }\
            .searchbar-input-wrap {\
                margin-left:10px;\
                float: left;\
                width: 100%;\
                border: 1px solid rgb(206, 206, 206);\
                border-radius: 4px;\
                font-size: 14px;\
                padding: 3px 0px;\
            }\
            .drop-box {\
              background: #F8F8F8;\
              border: 1px dashed #999999;\
              width: auto;\
              text-align: center;\
              padding: 40px 10px;\
              --margin-left: 10px;\
              font-size: 15px;\
              height: 100px;\
              cursor: pointer;\
              color: #1174da;\
            }\
            .drop-box.dragover {\
              border: 5px dashed blue;\
            }\
            .attachmentShow:hover{\
              background:#f2f2f2\
            }\
            #onAttachmentDailougeModel ul{\
              list-style-type:none\
            }\
            span.file-size {\
             color: #6d6c6c ;\
             margin-left: 10px;\
             font-size: 13px;\
            }\
            .active-attachment{\
               background-color: #ffffcc;\
            }\
            .tagDetails{\
              cursor:pointer;\
            }\
            .attachmentDetail{\
              border-bottom:1px solid #dddddd;padding:8px;padding-right:0px;cursor:pointer;\
            }\
            .attachmentIcons{\
              height:30px;\
            }\
            .attachmentLockUnlock{\
              display:inline-block;width:60px;float:right;margin-top:7px;margin-right:8px;\
            }\
            .attachmentUser{\
              float:right;padding-left:5px;padding-top:1.5%;\
            }\
            .attachmentUsers{\
              margin-top:3px;float:right;text-align:right\
            }\
            .attachmentUserImage{\
              border-radius:50%;\
            }\
            .attachmentTitle{\
              \
            }\
            .editIcon{\
              text-align:center;\
            }\
            .attachmentDialog{\
              margin: 58px 10px 16px 0px\
            }\
            .attachmentDate{\
              color:#5f6368;margin-top:1.7%;padding-right:5px;\
            }\
            .attachmentPropertyfile{\
              font-size:20px;\
            }\
            .attachmentPropertyImage{\
              height:30px;\
            }\
            .attachmentproperties{\
              padding-top:5px;\
            }\
            .attachmentPropertyTitle{\
              padding-top:7px;\
            }\
            .attachmentPropertyTitleTxt{\
              \
            }\
            .attachmentPropertyBorder{\
              border-bottom:1px solid #dddddd;\
            }\
            label.header {\
                font-weight: bold !important;\
            }\
            .searchbar-tags{\
              width:28%;\
              margin-left:2%;\
              width: 100%;\
              border-radius: 4px;\
              font-size: 14px;\
              padding: 3px 0px;\
            }\
            .tagList{\
              width:50px;\
              max-width:100%;\
              padding:3px;\
              overflow-wrap: break-word;\
              border-radius:5px;\
              background:#ffe5ee;"\
            }\
           .att-lock {font-size: 15px;vertical-align: middle;margin-left: 8px;cursor:pointer;}\
           .sourcedoc{\
             inline-size: 150px;\
            overflow-wrap: break-word;\
            }\
            .msg-show{\
              color:#a94442;\
              display: none;\
            }\
        </style>\
        <div ng-if = "entityId == 0" class="searchbar">\
              <div class="row">\
                <div class="col-sm-5">\
                  <div class="searchbar-input-wrap">\
                        <input id="searchQuery" type="search" placeholder="Search documents.." class="search-input" onKeyPress="search_data(event)">\
                        <span class="search-icon glyphicon glyphicon-search" style="margin-bottom: 3px;"></span>\
                  </div>\
                </div>\
                <div class="col-sm-3">\
                  <div class="searchbar-tags">\
                    <input type="text" class="form-control" id="id_tag_search" name="tag_search"  style="height:auto;" >\
                  </div>\
                </div>\
                <div class="col-sm-3">\
                  <span style="margin-left: 20px; margin-right:15px"><b>Show :</b></span>\
                  <input type="radio" id="normal" name="view" value="normal" checked ng-click="onTagViewChange(false)">\
                  <label for="normal" style=" margin-right:15px">Normal</label>\
                  <input type="radio" id="tag_view" name="view" value="tag_view" ng-click="onTagViewChange(true)">\
                  <label for="tag_view">Tag</label>\
                </div>\
              </div>\
          </div>\
        <div class="form-group" data-ng-class="{\'attachmentDialog\':entityId == 0}"> \
          <div id="id_staff_file">\
              <div ngf-drop="uploadDailouge($files)" ngf-select="uploadDailouge($files)" class="drop-box"\
                ngf-drag-over-class="dragover" ngf-multiple="true">Click here to select file or Drop file here</div>  \
              <div ngf-no-file-drop>File Drag/Drop is not supported for this browser</div>\
          </div>\
        </div>\
        <table class="table table-bordered">\
          <tbody>\
            <tr>\
              <td class="col-sm-2 tagDetails tag_div">\
                  <div class="container">\
                      <div class="float-container">\
                        <h5><b>Tags</b></h5>\
                        <h5 ng-click="docSearch()" style="text-align:right"><a>Display all</a></h5>\
                      </div>\
                      <div id="treeview"></div>\
                  </div>\
              </td>\
              <td class="col-sm-6">\
                    <div ng-if = "attachments.length == 0;">\
                        <div style="text-align: center;color: #808080;font-size: 18px;margin-top: 100px;">No document(s) available.</div>\
                    </div>\
                    <div ng-if = "attachments.length>0;" class="col-sm-12 attachmentDetail">\
                        <label class="col-sm-3 header"> &nbsp; &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Document</label>\
                        <label class="col-sm-2 header">Detail</label>\
                        <label class=" col-sm-2 header">Customer</label>\
                        <label class=" col-sm-2 header">Tag</label>\
                        <label class="col-sm-2 header">Uploaded on</label>\
                        <label class="col-sm-1 header"></label>\
                    </div>\
                    <div class=scrollable>\
                    <div class="col-sm-12 attachmentDetail" ng-repeat="attachment in attachments track by $index" ng-style="attachment.isSelected && {\'background-color\':ngcolor}"\
                    ng-click="propertyDetails(attachment.name, attachment.title, attachment.subject, attachment.description, attachment.id, attachment, $index, attachment.is_public, attachment.uid,attachment.app_name,attachment.model_name,attachment.model_exist,attachment.selected_tags)"  >\
                        <div class="col-sm-3" >\
                            <div class="col-sm-2" ng-if="!attachment.is_url">\
                                <img class="attachmentIcons" ng-src="{[{getPreviewImage(attachment.name)}]}"class="image-attachment" ng-class="{\'no-image\':!isImage(getFileExtension(attachment.name)),\'image-file-background\':isImage(getFileExtension(attachment.name))}">\
                            </div>\
                            <div class="col-sm-2" ng-if="attachment.is_url">\
                                <img ng-src="https://www.google.com/s2/favicons?domain={[{attachment.description}]}&sz=50" style="height:27px;"/>\
                            </div>\
                            <div class="col-sm-10" ng-if="!attachment.is_url">\
                                <a id="child" ng-click="childClick();$event.stopPropagation();"href="/attachment/dwn_attachment/?uid={[{attachment.uid}]}&a={[{attachment.app_name}]}&m={[{attachment.model_name}]}"target="_blank"><p class="documentTag" ng-if="attachment.title">{[{attachment.title}]}</p><p class="documentTag" ng-if="attachment.title==\'\'">{[{attachment.name}]}</p></a>&nbsp<span style="color:#5f6368"ng-if="fileSize(attachment.size)">({[{attachment.size}]})</span><br>\
                                <div style="margin-top:8px;">\
                                  <span class="tagList" ng-repeat="tag in attachment.selected_tags" style="margin-right:10px;margin-bottom: 100px;line-height: 26px;">{[{tag.name}]} </span>\
                                </div>\
                            </div>\
                            <div class="col-sm-10" ng-if="attachment.is_url">\
                                <a id="child" href="{[{attachment.description}]}" target="_blank" title="Click to open URL in new tab"><p class="documentTag" ng-if="attachment.title">{[{attachment.title}]}</p><p class="documentTag" ng-if="attachment.title==\'\'">{[{attachment.name}]}</p></a>&nbsp<span style="color:#5f6368"ng-if="fileSize(attachment.size)">({[{attachment.size}]})</span><br>\
                                <div style="margin-top:8px;">\
                                  <span class="tagList" ng-repeat="tag in attachment.selected_tags" style="margin-right:10px;margin-bottom: 100px;line-height: 26px;">{[{tag.name}]} </span>\
                                </div>\
                            </div>\
                        </div>\
                        <div class="col-sm-2">\
                            <div ng-if="!attachment.is_url" class="col-sm-6 detailsTag">\
                              <div>{[{attachment.title}]}</div>\
                              <div style="color:#555555">{[{attachment.subject}]}</span></div>\
                              <div style="color:#888888">{[{attachment.description}]}</div>\
                            </div>\
                        </div>\
                        <div class="col-sm-2">\
                            <span class="attachmentDate">{[{attachment.customer_name}]}</span>\
                        </div>\
                        <div class="col-sm-2">\
                            <span style="inline-size:110px; overflow-wrap: break-word;">{[{attachment.tag}]}</span>\
                        </div>\
                        <div class="col-sm-2">\
                            <span class="attachmentDate">{[{attachment.create_date}]}</span>\
                        </div>\
                        <div class="col-sm-1">\
                            <div class="col-sm-8">\
                              <img class="attachmentUserImage" id="taskUserImg" ng-src="{[{attachment.user_pic}]}" title="{[{attachment.user__username}]}" onerror="this.src=\'/static/task/js/images/man.png\'" width="25" height="25">\
                            </div>\
                        </div>\
                    </div>\
                  </div>\
              </td>\
              <td class="col-sm-4">\
                    <div ng-show="IsVisible" >\
                        <div class="col-sm-12" style="margin-top:8px;" >\
                            <div class="col-sm-7" style="padding-left:15px; display:flex;">\
                                <span class="attachmentPropertyfile" style="display:flex;">\
                                <img ng-if="!attachment_data.is_url" class="attachmentPropertyImage" ng-src="{[{getPreviewImage(attachment_name)}]}" class="image-attachment" ng-class="{\'no-image\':!isImage(getFileExtension(attachment_name)), \'image-file-background\':isImage(getFileExtension(attachment_name))}">\
                                <img ng-if="attachment_data.is_url" ng-src="https://www.google.com/s2/favicons?domain={[{attachment_data.description}]}&sz=50" style="height:27px;"/>\
                                <b ng-if="!attachment_data.is_url" style="margin-left:10px;font-size: 17px;word-break: break-all">{[{attachment_name}]}</b>\
                                <a ng-if="attachment_data.is_url" title="Click to open URL in new tab" href="{[{attachment_data.description}]}" target="_blank"><p style="margin-left:10px;font-size: 17px;word-break: break-all;font-weight: bolder;color: #1a73e8;">{[{attachment_name}]}</p></a>\
                                </span>\
                                <span style="margin-left:10px;font-color:#656565;margin-top: 8px;" ng-if="attachment_data.is_public" class="icon-users"></span>\
                            </div>\
                            <div class="col-sm-5">\
                              <div ng-if="attachment_data.req_user == \'true\'" id="id_staff_file_dlt">\
                                <i ng-if="!attachment_data.is_url" style="float:right;margin-right:3px;" class="icon-trash list-btn fa fa-trash-o fa-bold" ng-click="delete(attachment_data);$event.stopPropagation();" title="Delete document" ref="{[{attachment_data.uid}]}" ></i>\
                                <i ng-if="attachment_data.is_url" style="float:right;margin-right:3px;" class="icon-trash list-btn fa fa-trash-o fa-bold" ng-click="delete(attachment_data);$event.stopPropagation();" title="Delete link" ref="{[{attachment_data.uid}]}" ></i>\
                              </div>\
                              <div ng-if="attachment_data.req_user == \'true\'" id="id_staff_file_dlt">\
                              <a ng-if="getFileExtension(attachment_data.name) == \'html\'">\
                                <i style="float:right;margin-right:3px;" ng-if="!attachment_data.is_url" class="icon-pencil-1 list-btn editIcon" ng-click="editDocument($event,attachment_data.id,attachment_data.is_url)" title="Edit document"></i>\
                              </a>\
                              <a ng-if="attachment_data.is_url">\
                                <i style="float:right;margin-right:3px;" class="icon-pencil-1 list-btn editIcon" ng-click="editDocument($event,attachment_data.id,attachment_data.is_url)" title="Edit link"></i>\
                              </a>\
                            </div>\
                              <a style="float:right;margin-top:6px;" ng-if="!attachment_data.is_url" ng-click="childClick();$event.stopPropagation();" href="/attachment/dwn_attachment/?uid={[{attachment_data.uid}]}&a={[{attachment_data.app_name}]}&m={[{attachment_data.model_name}]}" title="Download document" target="_blank">\
                                <i class="icon-download-2" style="font-weight:bold;color:black;margin-right:9px;"></i>\
                              </a>\
                              <div class="attachmentLockUnlock">\
                                <div id="id_staff_file_lock">\
                                  <i style="float:right;margin-right:5px"  ng-if="attachment_data.is_public && attachment_data.req_user == \'true\'" ng-click="toggleAccess(attachment_data)" title="Revoke public" class="icon-unlocked fa fa-unlock att-lock " /></div>\
                                  <i  style="color:red;float:right;margin-right:5px" ng-if="!attachment_data.is_public  && attachment_data.req_user == \'true\'  && !attachment_data.is_url" ng-click="toggleAccess(attachment_data)" title="Make document public"  class="icon-lock fa fa-lock att-lock " /></a>\
                                  <i  style="color:red;float:right;margin-right:5px" ng-if="!attachment_data.is_public  && attachment_data.req_user == \'true\'  && attachment_data.is_url" ng-click="toggleAccess(attachment_data)" title="Make link public"  class="icon-lock fa fa-lock att-lock " /></a>\
                                  <i  style="padding-left:2px;" ng-if="attachment_data.is_public && !attachment_data.is_url" ng-click="copyLink(attachment_data.uid,attachment_data.app_name,attachment_data.model_name, None)" title="Copy public URL" class="icon-file-copy fa fa-copy att-lock " />\
                                  <i  style="padding-left:2px;" ng-if="attachment_data.is_public && attachment_data.is_url" ng-click="copyLink(None, None, None, attachment_data.description)" title="Copy public URL" class="icon-file-copy fa fa-copy att-lock " />\
                              </div>\
                            </div>\
                        </div>\
                        <div ng-if="!attachment_data.is_url" class="col-sm-12 attachmentproperties">\
                            <div class="col-sm-1">\
                            </div>\
                            <div class="col-sm-3 attachmentPropertyTitle">\
                                <label>Title</label>\
                            </div>\
                            <div class="col-sm-8 attachmentPropertyTitleTxt">\
                                <input type="text" ng-blur="propertySave(\'title\',title,app_name,model_name);" ng-model="title" class="form-control"  id="id_attachment_title" name="title" placeholder="Title">\
                            </div>\
                        </div>\
                        <div ng-if="!attachment_data.is_url" class="col-sm-12">\
                            <div class="col-sm-1">\
                            </div>\
                            <div class="col-sm-3" style="padding-top:5px;">\
                                <label>Subject</label>\
                            </div>\
                            <div class="col-sm-8">\
                                <input type="text" class="form-control" ng-blur="propertySave(\'subject\',subject,app_name,model_name);" ng-model="subject"  id="id_subject" name="subject" placeholder="Subject" ><br>\
                            </div>\
                        </div>\
                        <div ng-if="!attachment_data.is_url" class="col-sm-12">\
                            <div class="col-sm-1">\
                            </div>\
                            <div class="col-sm-3">\
                                <label>Description</label>\
                            </div>\
                            <div class="col-sm-8">\
                                <textarea id="id_description" ng-blur="propertySave(\'description\',description,app_name,model_name);" ng-model="description"  class="form-control"  name="description" placeholder="Description" ></textarea>\
                            </div>\
                        </div><br>\
                        <div class="col-sm-12 tagDiv-div" style="display:none">\
                            <div class="col-sm-1">\
                            </div>\
                            <div class="col-sm-3">\
                                <label>Tag</label>\
                            </div>\
                            <div class="col-sm-8">\
                            <input type="text" class="form-control" id="id_tag_"  style="height:auto;" name="tag_" ng-disabled="false">\
                            </div>\
                        </div>\
                        <div class="col-sm-12" style="margin-top:3%">\
                            <div class="col-sm-1">\
                            </div>\
                            <div ng-if="showWorkcenter" class="col-sm-3">\
                                <label>Workcenter</label><br><br>\
                            </div>\
                            <div ng-if="showWorkcenter" class="col-sm-8">\
                                <input type="text" class="form-control" id="attach_id_workcenter" name="workcenter" ng-disabled="false"><br><br>\
                            </div>\
                        </div>\
                    </div>\
              </td>\
            </tr>\
          </tbody>\
        </table>\
      <div id="onAttachmentDailougeModel" class="modal fade" tabindex="-1" role="dialog">\
          <div class="modal-dialog modal-lg" role="document" style="width:34%">\
              <div class="modal-content">\
                  <div class="modal-header">\
                      <button type="button" class="close" data-dismiss="modal" aria-label="Close" ng-click="closeDailouge($event);">\
                          <span aria-hidden="true">&times;</span>\
                      </button>\
                      <h4 class="modal-title" id="onAttachmentDailouge" ng-bind="onAttachmentDailougeTitle">Uploaded file(s)</h4>\
                  </div>\
                  <div class="modal-body" style="height: 140px;">\
                      <div class="form-group">\
                        <div id ="file_info" class="form-group">\
                            <label class="control-label col-sm-3">File</label>\
                            <div class="col-sm-9">\
                              <ul style="margin: 0 0 0 -39px;"><li ng-repeat="file in files" style="overflow-wrap: break-word;"><span>{{file.name}}</span> <span class="file-size">Size: {{file.size/1024|number : 2}} KB</span></li></ul>\
                            </div>\
                        </div><br><br>\
                        <div class="col-md-12 col-sm-12">\
                          <div class="form-group">\
                              <label  for="id_customer" class="control-label col-sm-3 required">Customer</label>\
                              <div class="col-sm-9">\
                                  <input class="form-control" id="id_customer" name="customer" value="" type="text" style="height: auto;" required/>\
                                  <span class="msg-show" id="id_message" style="display: none;color:#a94442;">This field is required.</span>\
                              </div>\
                          </div>\
                        </div><br><br>\
                        <div class="col-md-12 col-sm-12">\
                        <div class="form-group">\
                            <label  for="id_doc_tag" class="control-label col-sm-3">Tag</label>\
                            <div class="col-sm-9">\
                                <input class="form-control" id="id_doc_tag" name="tag" value="" type="text" style="height: auto;"/>\
                            </div>\
                        </div>\
                        </div>\
                      </div>   \
                  </div>\
                  <div class="modal-footer">\
                      <button class="btn" data-dismiss="modal" aria-hidden="true" ng-click="closeDailouge($event);">Close</button>\
                      <button class="btn btn-primary" id="btnUpload" ng-click="upload($event);" ng-disabled="btnUploadDisabled">Upload</button>\
                  </div>\
              </div>\
          </div>\
        </div>'
    );
  },
]);
