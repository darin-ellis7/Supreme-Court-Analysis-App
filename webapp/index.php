<!DOCTYPE html>
<html>
<head>
	<!-- css -->
	<link rel="stylesheet" type="text/css" href="styles.css">
	<!-- javascript -->
	<script src="ourScript.js"></script>
</head>

<body onload = redirect()>
	<div class = "header">
		<h1>US Supreme Court Analysis Tool</h1>
	</div>

	<div class = "subheader"><!--this is the toolbar at the top-->
		<table class = "subH">
			<tr>
				<th id="sh1" class = "subH" onmouseover = "changeSH1()"
				onmouseout = "revertSH1()"
				onclick = "restartPage()">Restart</th>
				<th id="sh2" class = "subH" onmouseover = "changeSH2()"
				onmouseout = "revertSH2()">Explore</th>
			</tr>
		</table>
	</div>

	<div class = "searchbar"><!--the search fields-->
		<form name = "keySearch" action = "search.php"
		onsubmit = "return validateForm()" method = 'POST'>
			<input class = "search" type = "text" name = "search_query"
			placeholder = "Enter keyword[s]">
			<p id="helpSearch" class="helpB" onmouseover = "onSHelp()"
			onmouseout = "outSHelp()" onclick = "helpAlert()"><tab1>Help<tab1></p>
			<br><br>
			From <input type = "date" name = "dateFrom"> <tab0>
			To <input type = "date" name = "dateTo">
			<input id = "formBut" class = "subBut" type = "submit" value = "Submit"
			onmouseover = "changeSubBut()" onmouseout = "revertSubBut()">
		</form>
	</div>

	<div id = "helpModal" class = "modal"><!--the popup to help user-->
		<div class = "modal-content">
			<span class = "modalClose">&times;</span>
			<h3>Input Type<tab0><tab0>Description</h3>
			<p>Words<tab0><tab0><tab0>Each word separated by a space is a keyword
			e.g. (cars trucks bikes)</p>
			<p>Phrases<tab3><tab0><tab0>Words inside quotations are phrases to be
			searched e.g. ("electrical car" trucks bikes)</p>
			<p>Negation<tab2><tab0><tab0> Excludes the results of whatever was negated
			e.g. (cars -"electrical car")(cars -bmw)(cars NOT 2003)</p>
			<p>Comparison Operator<tab0> Specifies numerical ranges
			e.g. (cars >2003)</p>
		</div>
	</div>

</body>

</html>
