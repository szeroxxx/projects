function logsInit() {
    var logs = {};
    sparrow.registerCtrl('logsCtrl',function($scope, $rootScope, $route, $routeParams, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, $location, ModalService){ 
        model = $routeParams.model.toLowerCase().replace(/\b[a-z]/g, function(letter) { return letter.toUpperCase(); });   
        var title =  model+" Logs";
        var querystring = $location.search();
        if(querystring.title!=''){
            title = 'History - ' + querystring.title; 
        }
        var config = {           
            pageTitle: title,
            topActionbar: {
            },
            listing: [{
                index : 1,
                search: {
                params: [
                        { key: "descr", name: "Desc"}
                    ]
                },                
                url: "/auditlog/logs_search/"+$routeParams.model+"/"+$routeParams.ids,                
                crud: false,
                columns: [                    
                    { name: 'action_by__username', title: 'User'},
                    { name: 'descr', title: 'Action'},
                    { name: 'action_on', title: 'Action On'},
                    { name: 'ip_addr', title: 'IP'},
                ]
            }]
        }
        if(sparrow.inIframe()){
            $('#top_action_bar').hide();
        }
        
        sparrow.setup($scope, $rootScope, $route, $compile, DTOptionsBuilder, DTColumnBuilder, $templateCache, config, ModalService);
    });

    return logs;
}

var logs = logsInit();