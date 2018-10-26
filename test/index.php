
<!DOCTYPE html>
<html lang="en">
	<head>
		<meta charset="utf-8">
		<title>Test</title>
		<meta name="viewport" content="width=device-width, initial-scale=1">
	    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
	    <script charset="utf-8" src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
	    <script charset="utf-8" src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>

	    <!-- datatable lib -->
	    <link rel="stylesheet" href="https://cdn.datatables.net/1.10.16/css/jquery.dataTables.min.css">
	    <script charset="utf-8" src="https://code.jquery.com/jquery-1.12.4.js"></script>
	    <script charset="utf-8" src="https://cdn.datatables.net/1.10.16/js/jquery.dataTables.min.js"></script>

	    <!--
		<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
		<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.19/css/jquery.dataTables.css">
		<script type="text/javascript" charset="utf8" src="https://cdn.datatables.net/1.10.19/js/jquery.dataTables.js"></script>-->
	</head>
	
	<body>
		<table id="results" class="display" width="100%" cellspacing="0">
			<thead>
				<tr>
					<th>Title</th>
					<th>Source</th>
					<th>Date</th>
				</tr>
			</thead>
		</table>

		<script>
			$(document).ready(function() {
				$('#results').DataTable({
					 "processing": true,
			         "serverSide": true,
			         "ajax":{
			            url :"response.php", // json datasource
			            type: "post",  // type of method  , by default would be get
			          }
			        });   
			});
		</script>
	</body>
</html>