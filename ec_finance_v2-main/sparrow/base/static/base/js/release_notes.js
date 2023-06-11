function releaseNotesInit() {
    var releaseNotes = {};
    sparrow.registerCtrl('releaseNotesCtrl', function ($scope, $rootScope, $route, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, ModalService) {
        $('#is_saved').hide();
        $('#id_release_note_count').find('span').remove();
        var config = {
            pageTitle: 'Release notes',
            topActionbar: {
                extra: [
                    {
                        id: 'btnAddOrder',
                        function: onAddRelease,
                    },
                    {
                        id: 'btnEditRelease',
                        function: OnEditRelease,
                    },
                    {
                        id: 'btnDeleteRelease',
                        function: OnDeleteRelease,
                        multiselect: true,
                    },
                ],
            },
            listing: [
                {
                    index: 1,
                    search: {
                        params: [
                            {
                                key: 'created_on',
                                name: 'Label name',
                                type: 'datePicker',
                            },
                        ],
                    },
                    url: '/base/search_release_notes/',
                    paging: true,
                    scrollBody: true,
                    crud: true,
                    columns: [
                        {
                            name: 'version',
                            title: 'Release version',
                        },
                        {
                            name: 'created_on',
                            title: 'Release date',
                        },
                        {
                            name: '',
                            title: '',
                            sort: false,
                            renderWith: function (data, type, full, meta) {
                                console.log(full.latest);
                                return '<a id="release_note" style="cursor: pointer; title="Release note" ng-click="onReleaseNote(' + full.id + ')">' + 'View details' + '</a>';
                            },
                        },
                    ],
                },
            ],
        };

        $scope.onReleaseNote = function (note_id) {
            window.location.hash = '/base/release_note/' + note_id + '/';
        };

        // $('#id_release_note_count').find('span').remove();

        function OnEditRelease() {
            var selectId = $scope.getSelectedIds(1)[0];
            sparrow.post(
                '/base/edit_release_note/',
                {
                    id: selectId,
                },
                false,
                function (data) {
                    $('#id_release_date').val(data.created_on);
                    $('#edit_id').val(data.id);
                    $('#id_release_version').val(data.version);
                    $('.release_note').summernote({
                        height: $(window).height() - 350,
                        callbacks: {
                            onImageUpload: function (image, editor, welEditable) {
                                uploadImage(image[0]);
                            },
                            onPaste: function (e) {
                                var clipboardData = e.originalEvent.clipboardData;
                                if (clipboardData && clipboardData.items && clipboardData.items.length) {
                                    var item = clipboardData.items[0];
                                    if (item.kind === 'file' && item.type.indexOf('image/') !== -1) {
                                        e.preventDefault();
                                    }
                                }
                            },
                        },
                    });
                    $('.release_note').summernote('code', data.note);
                    $('#dialogReleaseNotes').modal('show');
                }
            );
        }

        function OnDeleteRelease() {
            sparrow.showConfirmDialog(ModalService, 'Are you sure you want to delete record?', 'Delete record', function (confirm) {
                if (!confirm) {
                    return;
                }
                var selectedIds = $scope.getSelectedIds(1).join([(separator = ',')]);
                sparrow.post(
                    '/base/delete_release_note/',
                    {
                        ids: selectedIds,
                    },
                    true,
                    function (data) {
                        if (data.code == 1) {
                            $scope.reloadData(1);
                        }
                    }
                );
            });
        }

        function onAddRelease() {
            $('#dialogReleaseNotes').modal('show');
            $('.release_note').summernote({
                height: $(window).height() - 350,
                callbacks: {
                    onImageUpload: function (image, editor, welEditable) {
                        uploadImage(image[0]);
                    },
                    onPaste: function (e) {
                        var clipboardData = e.originalEvent.clipboardData;
                        if (clipboardData && clipboardData.items && clipboardData.items.length) {
                            var item = clipboardData.items[0];
                            if (item.kind === 'file' && item.type.indexOf('image/') !== -1) {
                                e.preventDefault();
                            }
                        }
                    },
                    onInit: function () {
                        setReleaseNotes();
                    },
                },
            });
            if ((localStorage.getItem('summernotedata') != null) & (localStorage.getItem('summernotedata') != '')) {
                $('#is_saved').show();
                $('.release_note').summernote('code', localStorage.getItem('summernotedata'));
            }
        }

        function uploadImage(image) {
            var data = new FormData();
            data.append('image', image);
            $.ajax({
                url: '/base/upload_release_note_media/',
                cache: false,
                contentType: false,
                processData: false,
                data: data,
                type: 'POST',
                success: function (data) {
                    var image = $('<img>')
                        .attr('src', 'https://sparrow-releasenotes.s3.amazonaws.com/' + data.filename)
                        .css('height', '250px');
                    $('.release_note').summernote('insertNode', image[0]);
                },
                error: function (data) {
                    console.log(data);
                },
            });
        }

        $scope.saveReleaseNote = function () {
            postData = {
                release_version: $('#id_release_version').val(),
                release_note: $('#id_release_note').val(),
                release_date: $('#id_release_date').val(),
                id: $('#edit_id').val(),
            };

            sparrow.post('/base/save_release_note/', postData, false, function (data) {
                console.log(data);
                if (data.code == 0) {
                    sparrow.showMessage('appMsg', sparrow.MsgType.Error, data.msg, 10);
                    return;
                }
                if (data.code == 1) {
                    sparrow.showMessage('appMsg', sparrow.MsgType.success, data.msg, 10);
                    localStorage.removeItem('summernotedata');
                    $('#dialogReleaseNotes').modal('hide');
                    // $scope.reloadData(1);
                }

                $route.reload();
            });
        };

        $scope.cencelReleaseNote = function () {
            resetReleaseNote();
            $('#dialogReleaseNotes').modal('hide');
            $route.reload();
        };

        function resetReleaseNote() {
            $('.release_note').summernote('reset');
            $('#id_release_version').val('');
        }

        var interval;
        function setReleaseNotes() {
            if (!interval) {
                interval = setInterval(function () {
                    localStorage.setItem('summernotedata', $('.release_note').summernote('code'));
                }, 10000); // every 5 second interval
            }
        }

        $('#dialogReleaseNotes').on('hidden.bs.modal', function (e) {
            if (!$('#dialogReleaseNotes').is(':visible')) {
                clearInterval(interval);
                interval = null;
            }
        });

        sparrow.setup($scope, $rootScope, $route, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, config);
    });

    return releaseNotes;
}

releaseNotesInit();
