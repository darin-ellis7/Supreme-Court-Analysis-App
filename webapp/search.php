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

	You searched for <?php echo $_POST['search_query']; ?><br>
	From <?php echo $_POST['dateFrom']; ?> To <?php echo $_POST['dateTo']; ?>

	<?php

		//connect to database
		$connect = mysqli_connect("localhost", "root", "cs499", "SupremeCourtApp") or die(mysqli_connect_error());
    mysqli_set_charset($connect, "utf8");

		// base sql query
		            // default search includes entire database
		            $sql = "SELECT DISTINCT date, title, source, idArticle FROM article NATURAL JOIN article_keywords NATURAL JOIN keyword_instances ";
		            $source_sql = "SELECT DISTINCT source FROM article NATURAL JOIN article_keywords NATURAL JOIN keyword_instances ";
		            $source_count_sql = "SELECT DISTINCT idArticle,title,source FROM article NATURAL JOIN article_keywords NATURAL JOIN keyword_instances "; // for displaying in filter sidebar how many occurrences of a specific source there are

		            // build sql query based on search criteria
		            if(isset($_GET['search_query']))
		            {

		                    $search_query = mysqli_real_escape_string($connect, trim($_GET['search_query']));
		                    $query_str = "WHERE (title LIKE '%$search_query%' OR keyword LIKE '%$search_query%') ";
		                    $sql .= $query_str;
		                    $source_sql .= $query_str;
		                    $source_count_sql .= $query_str;
		            }

		            // date range search - if no dates provided, ignore
		            if(!empty($_GET['dateFrom']) && !empty($_GET['dateTo']))
		            {
		                // convert date input to Y-m-d format - this is because the bootstrap datepicker sends dates in Y/m/d while SQL only accepts as Y-m-d
		            	$dateFrom = date("Y-m-d",strtotime($_GET['dateFrom']));
		            	$dateTo = date("Y-m-d",strtotime($_GET['dateTo']));
		                if(isset($_GET['search_query']))
		                {
		                    $date_str = "AND date BETWEEN '$dateFrom' AND '$dateTo' ";
		                }
		                else
		                {
		                    $date_str = "WHERE date BETWEEN '$dateFrom' AND '$dateTo' ";
		                }

		                $sql .= $date_str;
		                $source_sql .= $date_str;
		                $source_count_sql .= $date_str;

		            }

		            // if source filter has been applied and search parameters set, limit the sources to what has been checked
		            if(isset($_GET['sourcebox']))
		            {
		                if(!isset($_GET['search_query']) && !isset($_GET['dateFrom']) && !isset($_GET['dateTo']))
		                {
		                    $sourceFilter_str = "WHERE source in (";
		                }
		                else
		                {
		                    $sourceFilter_str = "AND source in (";

		                }

		                foreach($_GET['sourcebox'] as $source)
		                {

		                    $sourceFilter_str .= "'" . $source . "'";
		                    if($source != end($_GET['sourcebox']))
		                    {
		                        $sourceFilter_str .= ",";
		                    }
		                }

		                $sourceFilter_str .= ") ";

		                $sql .= $sourceFilter_str;
		            }

		            $sql .= "ORDER BY date DESC";
		            $source_sql .= "ORDER BY source ASC";
		            if(!isset($_GET['search_query']) && !isset($_GET['dateFrom']) && !isset($_GET['dateTo']))
		            {
		                $source_count_sql .= "WHERE source = ";

		            }
		            else
		            {
		                $source_count_sql .= "AND source = ";
		            }

		            $query = mysqli_query($connect, $sql) or die(mysqli_connect_error()); // execute search query
		            $source_query = mysqli_query($connect, $source_sql) or die(mysqli_connect_error()); // execute source sidebar query

	?>


			<div class = "sourceBar">
				Sources (<?php echo mysqli_num_rows($source_query) ?>)
				<hr>
				<?php
					if(mysqli_num_rows($source_query) == 0){echo "No sources";}
					else{
						$names = ['search_query','dateFrom','dateTo'];

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

				<table class = "articleTable">
		                    <thead>
		                        <tr align="center">
		                        <td><strong>Title</strong></td>
		                        <td><strong>Source</strong></td>
		                        <td><strong>Date</strong></td>
		                        </tr>
		                    </thead>
		                    <?php
		                        // build search results table
		                        while ($row = mysqli_fetch_array($query))
		                        {
		                            echo "<tr class='clickable-row' href='./display_article.php?idArticle="; echo $row['idArticle']; echo"'>";
		                                echo "<td><button class=\"btn btn-link\" style=\"color:black\"><a href=\"./display_article.php?idArticle="; echo $row['idArticle']; echo "\" style=\"color:black\">"; echo $row['title']; echo "</a></button></td>";
		                                echo "<td>&nbsp"; echo $row['source']; echo"</td>";
		                                echo "<td>"; echo $row['date']; echo "</td>";
		                            echo "</tr>";
		                        }
		                    ?>
		                </table>
			

</body>

</html>
