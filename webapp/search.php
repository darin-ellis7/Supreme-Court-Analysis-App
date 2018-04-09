<!DOCTYPE html>
<html>
<head>
	<!-- css -->
	<link rel="stylesheet" type="text/css" href="styles.css">
	<!-- javascript -->
	<script src="ourScript.js"></script>
</head>

<body>
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
		<form name = "keySearch" action = ""
		onsubmit = "return validateForm()" method = 'POST'>
			<input class = "search" type = "text" name = "query"
			placeholder = "Enter keyword[s]">
			<p id="helpSearch" class="helpB" onmouseover = "onSHelp()"
			onmouseout = "outSHelp()" onclick = "helpAlert()"><tab1>Help<tab1></p>
			<br><br>
			From <input type = "date" name = "sFrom"><tab0>
			To <input type = "date" name = "sTo">
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

	You searched for <?php echo $_POST['query']; ?><br>
	From <?php echo $_POST['sFrom']; ?> To <?php echo $_POST['sTo']; ?>

	<?php

		//connect to database
		$connect = mysqli_connect("localhost", "root", "cs499") or die(mysqli_connect_error());
    mysqli_set_charset($connect, "utf8");
    mysqli_select_db($connect, "cs499SupremeCourt") or die(mysqli_connect_error());

	?>

	<div class = "sourceBar">
		Sources (<?php echo mysqli_num_rows(mysqli_query($connect, $sql)) ?>)
		<hr>
		<?php
			if(mysqli_num_rows($source_query) == 0){echo "No sources";}
			else{
				$names = ['query','sFrom','sTo'];

				//get list of sources from search query
				$i = 0;
				while($row = mysqli_fetch_array($source_query)){
					$source = $row['source'];

					// get and display the number of articles from each specific source that meet the search criteria
          $temp_count_sql = $source_count_sql . "'$source'";
          $count_query = mysqli_query($connect,$temp_count_sql) or die(mysqli_connect_error());
          $count = mysqli_num_rows($count_query);

  				echo "$source ($count) <input type='checkbox' name='sourcebox[]' ";
          if(isset($_GET['sourcebox'])){
            if(in_array($source,$_GET['sourcebox'])){
              echo "checked = 'checked' ";
            }

          }

					$i += 1;
				}
			}
		?>
	</div>

</body>

</html>
