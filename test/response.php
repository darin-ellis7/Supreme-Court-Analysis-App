<?php
	// connect to database
	include_once("db_connect.php");

	$col = array(
		0 => 'title',
		1 => 'source',
		2 => 'date'
	);

	// grab full chunk of data
	$sql ="SELECT title,source,date FROM article";
	$query=mysqli_query($connect,$sql);
	$totalData=mysqli_num_rows($query);
	$totalFilter=$totalData;

	// get little chunk
	$sql .= " ORDER BY ".$col[$_REQUEST['order'][0]['column']]." ".$_REQUEST['order'][0]['dir']."  LIMIT ". $_REQUEST['start']."  ,".$_REQUEST['length'];
	$query=mysqli_query($connect,$sql);
	while($row=mysqli_fetch_array($query)) {
	    $subdata=array();
	    $subdata[]=$row['title']; //id
	    $subdata[]=$row['source']; //name
	    $subdata[]=$row['date']; //salary
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