<?php
	// shared script to connect to database
	$connect = mysqli_connect("localhost", "root", "") or die(mysqli_connect_error());
	mysqli_set_charset($connect, "utf8");
	mysqli_select_db($connect, "SupremeCourtApp") or die(mysqli_connect_error());
?>