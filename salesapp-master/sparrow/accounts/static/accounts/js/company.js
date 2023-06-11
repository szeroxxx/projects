function companyInit() {
    sparrow.registerCtrl('companyCtrl',function($scope, $rootScope, $route, $routeParams, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, ModalService){        
        $scope.addViewButtons('');
        var config = {
            pageTitle: "Company"
        };

        var time_zone=[
            {'id':-720, 'name':'(GMT -12:00) Eniwetok, Kwajalein'},
            {'id':-660, 'name':'(GMT -11:00) Midway Island, Samoa' },
            {'id':-600, 'name':'(GMT -10:00) Hawaii'},
            {'id':-540, 'name':'(GMT -9:00) Alaska'},
            {'id':-480, 'name':'(GMT -8:00) Pacific Time (US, Canada)' },
            {'id':-420, 'name':'(GMT -7:00) Mountain Time (US, Canada)'},
            {'id':-360, 'name':'(GMT -6:00) Central Time (US, Canada), Mexico Cityn'},
            {'id':-300, 'name':'(GMT -5:00) Eastern Time (US, Canada), Bogota, Lima' },
            {'id':-240, 'name':'(GMT -4:00) Atlantic Time (Canada), Caracas, La Paz'},
            {'id':-210, 'name':'(GMT -3:30) Newfoundland'},
            {'id':-180, 'name':'(GMT -3:00) Brazil, Buenos Aires, Georgetown' },
            {'id':-120, 'name':'(GMT -2:00) Mid-Atlantic'},
            {'id':-60, 'name':'(GMT -1:00 hour) Azores, Cape Verde Islands'},
            {'id':0, 'name':'(GMT) Western Europe Time, London, Lisbon, Casablanca' },
            {'id':60, 'name':'(GMT +1:00 hour) Brussels, Copenhagen, Madrid, Paris'},
            {'id':120, 'name':'(GMT +2:00) Kaliningrad, South Africa'},
            {'id':180, 'name':'(GMT +3:00) Baghdad, Riyadh, Moscow, St. Petersburg'},
            {'id':210, 'name':'(GMT +3:30) Tehran'},
            {'id':240, 'name':'(GMT +4:00) Abu Dhabi, Muscat, Baku, Tbilisi'},
            {'id':270, 'name':'(GMT +4:30) Kabul'},            
            {'id':300, 'name':'(GMT +5:00) Ekaterinburg, Islamabad, Karachi, Tashkent'},
            {'id':330, 'name':'(GMT +5:30) Mumbai, Kolkata, Chennai, New Delhi'},
            {'id':345, 'name':'(GMT +5:45) Kathmandu'},
            {'id':360, 'name':'(GMT +6:00) Almaty, Dhaka, Colombo'},
            {'id':420, 'name':'(GMT +7:00) Bangkok, Hanoi, Jakarta' },
            {'id':480, 'name':'(GMT +8:00) Beijing, Perth, Singapore, Hong Kong'},
            {'id':540, 'name':'(GMT +9:00) Tokyo, Seoul, Osaka, Sapporo, Yakutsk'},
            {'id':570, 'name':'(GMT +9:30) Adelaide, Darwin'},
            {'id':600, 'name':'(GMT +10:00) Eastern Australia, Guam, Vladivostok'},
            {'id':660, 'name':'(GMT +11:00) Magadan, Solomon Islands, New Caledonia' },
            {'id':720, 'name':'(GMT +12:00) Auckland, Wellington, Fiji, Kamchatka'}]

        setAutoLookup('time_zone',time_zone, '');

        $scope.model = {
            name: 'Tabs'
        };

        $scope.saveCompany = function (event) {
            event.preventDefault();
            var time_zone = $('#time_zone').magicSuggest();
            var selection = time_zone.getSelection()[0];
            var postData = {}
            if(selection) {
                postData['time_zone_now'] = selection.name
            }
            sparrow.postForm(postData, $('#frmCompany'), $scope,setCompany);
        }

        function setCompany(data) {
            if(data.code == 1){
                location.reload();
            }   
        }

        $('#frmCompany').off('change', '#company_img_change')
        $('#frmCompany').on('change', '#company_img_change', function(e) {
            sparrow.setImagePreview(this, 'company_img')     
        })

        sparrow.setup($scope, $rootScope, $route, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, config, ModalService);
    });
}
companyInit();