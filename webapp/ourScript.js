//Functions for the toolbar at the top
function changeSH1(){ //on mouseover, change background color of tab1
	document.getElementById("sh1").style.backgroundColor =
	"#87ceeb" /*sky blue*/;
}
function revertSH1(){ //revert style back to original for tab1
	document.getElementById("sh1").style.backgroundColor =
	"rgba(255, 255, 255, 0.7)" /*transparent white*/;
}
function changeSH2(){ //on mouseover, change background color of tab2
	document.getElementById("sh2").style.backgroundColor =
	"#87ceeb" /*sky blue*/;
}
function revertSH2(){ //revert style back to original for tab2
	document.getElementById("sh2").style.backgroundColor =
	"rgba(255, 255, 255, 0.7)" /*transparent white*/;
}
function restartPage(){ //will reload index.html completely
	window.location = "index.php";
}

//Functions for the form (searchbar)
function changeSubBut(){
	document.getElementById("formBut").style.backgroundColor =
	"#87ceeb" /*sky blue*/;
}
function revertSubBut(){ //revert style back to original for tab2
	document.getElementById("formBut").style.backgroundColor =
	"rgba(255, 255, 255, 0.7)" /*transparent white*/;
}
function onSHelp(){ /*script for help button after searchbar*/
	document.getElementById("helpSearch").style.backgroundColor =
	"#87ceeb" /*sky blue*/;
}
function outSHelp(){ /*script for help button*/
	document.getElementById("helpSearch").style.backgroundColor =
	"rgba(255, 255, 255, 0.7)" /*transparent white*/;
}
function helpAlert(){ /*display a help menu for searching*/
	var modal = document.getElementById("helpModal");
	var span = document.getElementsByClassName("modalClose")[0];
	modal.style.display = "block";
	span.onclick = function(){
		modal.style.display = "none";
	}
	window.onclick = function(event){
		if(event.target == modal){
			modal.style.display = "none";
		}
	}
}
function validateForm(){ /*validates user input*/
	var query = document.forms["keySearch"]["query"].value;
	var dFrom = document.forms["keySearch"]["sFrom"].value;
	var dTo = document.forms["keySearch"]["sTo"].value;
	if (query == "" || dFrom == "" || dTo == ""){
		alert("All fields must be filled");
		return false;
	}
}
