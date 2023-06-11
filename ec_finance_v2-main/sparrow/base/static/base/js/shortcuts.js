Mousetrap.reset()

//for tab
Mousetrap.bind('shift+t+1', function() {
	$("#tab1").click()
});
Mousetrap.bind('shift+t+2', function() {
	$("#tab2").click()
});
Mousetrap.bind('shift+t+3', function() {
	$("#tab3").click()
});
Mousetrap.bind('shift+t+4', function() {
	$("#tab4").click()
});
Mousetrap.bind('shift+t+5', function() {
	$("#tab5").click()
});
Mousetrap.bind('shift+t+6', function() {
	$("#tab6").click()
});
Mousetrap.bind('shift+t+7', function() {
	$("#tab7").click()
});

//history
Mousetrap.bind("shift+h", function(){
	$("#btnRoleHistory").click()
	$("#btnHistory").click()
});

// export
Mousetrap.bind("shift+x", function(){
	const element = document.getElementById('btnExport');
	if (!element.disabled) {
		$("#btnExport").click()
	}
});

//file
Mousetrap.bind("shift+f", function(){
	$("#btnFiles").click()
});

//load
Mousetrap.bind('shift+o',function(){
	$("#load_btn").click()
})

//save on enter
var id = false
$(document).on('show.bs.modal', '.modal', function () {
	id = $(this).attr('id');
});
Mousetrap.bind("enter", function(e){
 	if($('#confirmModal').is(':visible') == false){
		if(id){
			if($("#"+id).is(':visible') == true){
				$("#"+id+" button[type='submit']").click()
			}
			else{
				id = false
		    }
	    }
	}
});