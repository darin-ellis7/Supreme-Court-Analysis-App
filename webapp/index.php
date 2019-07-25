<!-- //*** denotes new lines of code added -->
<!--This is the homepage of the web application. It presents a search form with a datepicker. Sources are listed on the left, and article titles along with their source and date are presented. There is also a download button for a zip folder of the articles currently on the webpage.-->
<!-- originally written by Evan Cole, Darin Ellis, Connor Martin, and Abdullah Alosail, with contributions by John Tompkins, Mauricio Sanchez, and Jonathan Dingess -->

<?php
    include_once("authenticate.php");
    include("buildQuery.php");
    include("admins.php");
?>

<!DOCTYPE html>
<html>
    <head>
        <title>SCOTUSApp</title>
        <meta charset="utf-8">

        <!-- Bootstrap stuff -->
        <meta name="viewport" content="width=device-width,initial-scale=1">
        <!-- Latest compiled and minified CSS -->
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">

        <!-- jQuery library -->
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.4/jquery.min.js"></script>
        <script src="js/jquery.js"></script>
        <!-- Latest compiled JavaScript -->
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
        <script src="https://oss.maxcdn.com/html5shiv/3.7.3/html5shiv.min.js"></script>
        <script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>

        <link rel="stylesheet" type="text/css" href="//cdn.datatables.net/1.10.16/css/jquery.dataTables.css">
        <script type="text/javascript" charset="utf8" src="//cdn.datatables.net/1.10.16/js/jquery.dataTables.js"></script>

        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-datepicker/1.7.1/css/bootstrap-datepicker.min.css" />
        <script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-datepicker/1.7.1/js/bootstrap-datepicker.min.js"></script>
        <script>
            $(document).ready(function() {
                            $('.datebox').datepicker({clearBtn: true });
                          });
        </script>
				<script>  //***  change__But and revert__But are functions for events onmouseover and onmouseout of buttons in the webapp. When the user mouses over a button, it highlights the button, and unhighlights when leaving the button area
					function changeSubBut(){  //***
						document.getElementById("formBut").style.backgroundColor =  //***
						"#87ceeb" /*sky blue*/;  //***
					}
					function revertSubBut(){ //revert style back to original for tab2//***
						document.getElementById("formBut").style.backgroundColor =  //***
						"rgba(255, 255, 255, 0.7)" /*transparent white*/;  //***
					}
					function changeDownBut(){  //***
						document.getElementById("downBut").style.backgroundColor =  //***
						"#87ceeb" /*sky blue*/;  //***
					}
					function revertDownBut(){ //revert style back to original for tab2
						document.getElementById("downBut").style.backgroundColor =  //***
						"rgba(255, 255, 255, 0.7)" /*transparent white*/;  //***
					}
					function changeResBut(){  //***
						document.getElementById("resBut").style.backgroundColor =  //***
						"#87ceeb" /*sky blue*/;  //***
					}
					function revertResBut(){ //revert style back to original for tab2
						document.getElementById("resBut").style.backgroundColor =  //***
						"rgba(255, 255, 255, 0.7)" /*transparent white*/;  //***
					}
					function changeApplyBut(){  //***
						document.getElementById("applyBut").style.backgroundColor =  //***
						"#87ceeb" /*sky blue*/;  //***
					}
					function revertApplyBut(){ //revert style back to original for tab2
						document.getElementById("applyBut").style.backgroundColor =  //***
						"rgba(255, 255, 255, 0.7)" /*transparent white*/;  //***
					}
					function changeMoreBut(){  //***
						document.getElementById("moreBut").style.backgroundColor =  //***
						"#87ceeb" /*sky blue*/;  //***
					}
					function revertMoreBut(){ //revert style back to original for tab2
						document.getElementById("moreBut").style.backgroundColor =  //***
						"rgba(255, 255, 255, 0.7)" /*transparent white*/;  //***
					}
				</script>
    </head>
    <body style="height:100%; background-color: #fffacd; font-family: monospace; font-weight: bold;">  <!--***  changes appearance of webpage-->

        <!-- header -->
        <?php echo contactLink(); ?>
        <div style="float:right; margin-right:1.5%;font-size: 18px; font-family: monospace;">
            <a style="color:black;" href="user_page.php"><?php echo $_SESSION['name']?></a> | <a style="color:black;" href="logout.php">Logout</a>
        </div>
        <div style="background-color: #fffacd; padding: 30px; text-align: center;">  <!--***-->
            <h1 style="font-size: 50px; font-family: monospace; font-weight: bold;"><a href='index.php' style='color:black;'>SCOTUSApp</a></h1>  <!--***-->
            <hr>
        </div>

        <!-- search bar + options -->
        <div class='container'>
            <div class='content-wrapper'>
                <div class='row'>
                    <div class='navbar-form' align="center">
                        <form action='' method='GET'>

                            <br>

                            <!-- php code within these input tags are to remember user input after search is done -->
                            <span class="input-group-btn">
                                <input class='form-control' type="text" name="search_query" style="width: 430px !important;" placeholder='Enter keyword[s] or leave empty' 
                                <?php 
                                    if(isset($_GET['search_query'])) echo " value='{$_GET['search_query']}'"; 
                                ?> >
                                <button id="formBut" type='submit' class='btn btn-default' onmouseover='changeSubBut()' onmouseout='revertSubBut()'
																style = "height: 30px;
																font-weight: bold;
																font-family: monospace;
																background-color: rgba(255, 255, 255, 0.45);
																border: solid 3px;
																border-radius: 10px;">
                                    Submit  <!--***-->
                                </button>
                            </span>

                            <br>

                            From: <input data-provide="datepicker" class="datebox" type="text" name="dateFrom" <?php if(!empty($_GET['dateFrom']) && !empty($_GET['dateTo'])) { echo " value = '{$_GET['dateFrom']}'"; } ?> >
                            To: <input data-provide="datepicker" class="datebox" type="text" name="dateTo" <?php if(!empty($_GET['dateFrom']) && !empty($_GET['dateTo'])) { echo " value = '{$_GET['dateTo']}'";} ?> >
                        </form>
                    </div>
                </div>
            </div>
        </div>

        <!--download button -->
        <div align="right">
            <?php

                // build download url based on search parameters
                $downloadURL = "download.php?";
                if(isset($_GET['search_query']))
                {
                    $downloadURL .= "search_query=" . $_GET['search_query'] . "&";
                }

                if(isset($_GET['dateFrom']))
                {
                    $downloadURL .= "dateFrom=" . $_GET['dateFrom'] . "&";

                }

                if(isset($_GET['dateTo']))
                {
                    $downloadURL .= "dateTo=" . $_GET['dateTo'];
                }

                // if a source filter has been applied, include those in download url
                if(isset($_GET['sourcebox']))
                {
                    foreach($_GET['sourcebox'] as $source)
                    {
                        $downloadURL .= "&sourcebox[]=" . $source;
                    }
                }
								echo "<a style=\"color:black; text-decoration:none;
								\" href=\""; echo "index.php"; echo "\"><button class=\"btn btn-default\" id=\"resBut\" onmouseover=\"changeResBut()\" onmouseout=\"revertResBut()\"
								style=\"height: 30px;
								font-weight: bold;
								font-family: monospace;
								background-color: rgba(255, 255, 255, 0.45);
								border: solid 3px;
								border-radius: 10px;\">Restart</button></a>";

                echo "<button class=\"btn btn-default\" id=\"downBut\" onmouseover=\"changeDownBut()\" onmouseout=\"revertDownBut()\"
								style=\"height: 30px;
								font-weight: bold;
								font-family: monospace;
								background-color: rgba(255, 255, 255, 0.45);
								border: solid 3px;
								border-radius: 10px;\"><a style=\"color:black; text-decoration:none;
								\" href=\""; echo $downloadURL; echo "\">Download Results</a></button> &nbsp;";  //***
            ?>
        </div>

        <hr>

        <?php

            $search_query = (!empty($_GET['search_query']) ? trim($_GET['search_query']) : '');
            $dateFrom = (!empty($_GET['dateFrom']) ? $_GET['dateFrom'] : '');
            $dateTo = (!empty($_GET['dateTo']) ? $_GET['dateTo'] : '');
            $sourcebox = (!empty($_GET['sourcebox']) ? $_GET['sourcebox'] : '');

            // connect to database (or not)
            include_once("db_connect.php");

            $results_sql = buildQuery(mysqli_real_escape_string($connect, $search_query),$dateFrom,$dateTo,$sourcebox,'results');
            $sourcebox_sql = buildQuery(mysqli_real_escape_string($connect, $search_query),$dateFrom,$dateTo,$sourcebox,'sourcebox');
            $sourcebox_query = mysqli_query($connect, $sourcebox_sql) or die(mysqli_connect_error()); // execute source sidebar query
        ?>

        <!-- display query results as table -->
        <div class="mainWrapper" style="overflow:hidden;">

            <div class="floatLeft" style="width: 18%; float:left">
                    <br>
                    <div class="panel panel-default">
                        <div class="panel-heading" style="font-size:20px; background-color: #e0eee0;">  <!--***-->
                            Sources (<?php echo mysqli_num_rows($sourcebox_query) ?>)
                        </div>
                        <div class="panel-body" style="font-size: 16px; background-color: #e0eee0">  <!--***-->
                            <?php
                                // build search filter panel (list of sources with checkboxes)
                                // Known "defect" - because we're using two forms (the search form and filter form), any changes to the search parameters after a filter has been applied will be ignored (like changing the date range after selecting specific sources) - a new search will have to be done
                                // not enough time to come up with a more elegant solution

                                if(mysqli_num_rows($sourcebox_query) == 0)
                                {
                                    echo "No sources";
                                }
                                else
                                {
                                    echo "<form action='' method='GET'>";
                                    echo "<button type='submit' class='btn btn-default' id='applyBut' name='submit' onmouseover='changeApplyBut()' onmouseout='revertApplyBut()'
																		style='height: 30px;
																		font-weight: bold;
																		font-family: monospace;
																		background-color: rgba(255, 255, 255, 0.45);
																		border: solid 3px;
																		border-radius: 10px;'>Apply Filter</button><br><br>";  //***

                                    // pass in search parameters (if any) into filter form
                                    $names = ['search_query','dateFrom','dateTo'];
                                    foreach($names as $var)
                                    {
                                        if(isset($_GET[$var]))
                                        {
                                            echo "<input type='hidden' name=$var value=" . $_GET[$var] . ">";
                                        }
                                    }

                                    // get list of sources from search query
                                    $i = 0;
                                    while ($row = mysqli_fetch_assoc($sourcebox_query))
                                    {
                                        $source = $row['source'];
                                        $count = $row['count(source)'];

                                        // more than 30 results in the search box will result in a collapsible button that when clicked will show the remainder of sources (since large amounts of sources results in an ugly, long box that spans far down the webpage)

                                        if($i == 30) // after 30 sources, create source button and collapsible div
                                        {
                                            echo "<br><a href='#more' class='btn btn-default' id='moreBut' onmouseover='changeMoreBut()' onmouseout='revertMoreBut()' data-toggle='collapse'
																						style='height: 30px;
																						font-weight: bold;
																						font-family: monospace;
																						background-color: rgba(255, 255, 255, 0.45);
																						border: solid 3px;
																						border-radius: 10px;'>More Sources</a><br><br>";  //*** button styling
                                            echo "<div id='more' class='collapse'>";
                                        }

                                        echo "$source ($count) <input type='checkbox' name='sourcebox[]' ";
                                        if(isset($_GET['sourcebox']))
                                        {
                                            if(in_array($source,$_GET['sourcebox']))
                                            {
                                                echo "checked = 'checked' ";
                                            }

                                        }

                                        // if there is a collapsible button/list, then end the collapse div after hte last source
                                        echo "value=$source><br>";
                                        $endIndex = mysqli_num_rows($sourcebox_query) - 1;
                                        if($i >= 30 && $i == $endIndex)
                                        {
                                            echo "</div>";
                                        }

                                        $i += 1;
                                    }
                                    echo "</form>";
                                }
                            ?>
                        </div>
                    </div>
                    <br>
            </div>

			<!--style of table-->
            <div class="floatRight" style="width:81%; float: right; ">
                <table id="results-table" style="background-color: #e0eee0;table-layout: fixed" width="100%" class="stripe hover"  align="center">
                    <thead>
                        <tr align="center">
                        <th width="10%"><strong>ID</strong></th>
                        <th width="75%"><strong>Title</strong></th>
                        <th width="15%"><strong>Source</strong></th>
                        <th width="10%"><strong>Date</strong></th>
                        </tr>
                    </thead>
                </table>

                <script>
                    $(document).ready(function() {
                        $('#results-table').DataTable({
                            "searching":false,
                            "order": [[0,"desc"]],
                            "columnDefs": [
                                {
                                    "targets": [ 0 ], // sort by article ID to avoid "shuffling" articles, but keep the IDs themselves hidden
                                    "visible": false
                                }
                            ],
                            "pageLength": 25,
                             "processing": true,
                             "serverSide": true,
                             "ajax":{
                                url :"response.php", // json datasource
                                type: "get",  // type of method  , by default would be get
                                data: function (d) {
                                    d.search_query = "<?php echo $search_query ?>";
                                    d.dateFrom = "<?php echo $dateFrom ?>";
                                    d.dateTo = "<?php echo $dateTo ?>";
                                    d.sourcebox = <?php echo json_encode($sourcebox) ?>;
                                }
                              }
                            });   
                    });
                </script>
            </div>
        </div>
        <div style="height:200px"></div>
    </body>
</html>