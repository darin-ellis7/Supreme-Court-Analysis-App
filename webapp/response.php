<?php
	include("buildQuery.php");
	include_once("db_connect.php");

	$col = array(
		0 => 'title',
		1 => 'source',
		2 => 'date'
	);

	// grab full chunk of data
	$sql = buildQuery($_GET['search_query'],$_GET['dateFrom'],$_GET['dateTo'],$_GET['sourcebox'],'results');
	$query=mysqli_query($connect,$sql);
	$totalData=mysqli_num_rows($query);
	$totalFilter=$totalData;

	// get little chunk
	$sql .= " ORDER BY ".$col[$_REQUEST['order'][0]['column']]." ".$_REQUEST['order'][0]['dir']."  LIMIT ". $_REQUEST['start']."  ,".$_REQUEST['length'];
	$query=mysqli_query($connect,$sql);
	$data = array();
	while($row=mysqli_fetch_array($query)) {
	    $subdata=array();
	    $article_url = "'./display_article.php?idArticle=" . $row['idArticle'] . "'";
	    $subdata[]="<a style='color:black' href={$article_url}>{$row['title']}</a>";
	    $subdata[]=$row['source'];
	    $subdata[]=$row['date'];
	    $data[]=$subdata;
	}

	$json_data=array(
	    "draw"              =>  intval($_REQUEST['draw']),
	    "recordsTotal"      =>  intval($totalData),
	    "recordsFiltered"   =>  intval($totalFilter),
	    "data"              =>  $data
	);

	echo json_encode($json_data);
?>