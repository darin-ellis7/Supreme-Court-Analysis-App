<!DOCTYPE html>

<html>
    <head>
        <title>Search Database</title>
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
                            $("#results-table").DataTable({
                            		"searching":false, 
                            		"order": [[2,"desc"]],
                                    "pageLength": 25
                                });
                            $('.datebox').datepicker({clearBtn: true });
                          });
        </script>
    </head>

    <body style=" height:100%; background: linear-gradient(0deg, rgb(153, 204, 255), rgb(208, 230, 255)) no-repeat;">
        
        <!-- image header -->
        <div style="background: white">
            <img class="flagimgs first" src="CAS.png" width=100% height=10%></img>
            <img class="flagimgs first" src="PS.png" width=500 height=150 style="background: white"></img>
            <p><font size="8">&nbsp;Supreme Court Coverage/Analytics Application</font></p>
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
                                <input class='form-control' type="text" name="search_query" style="width: 430px !important;" placeholder='Type search query here... (leave empty to see all)' <?php if(isset($_GET['search_query'])) echo " value='{$_GET['search_query']}'"; ?> >
                                <button type='submit' class='btn btn-default'>
                                    <span class='glyphicon glyphicon-search'></span>
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
                echo "<button class=\"btn btn-default\"><a style=\"color:black; text-decoration:none\" href=\""; echo $downloadURL; echo "\">Download Results</a></button> &nbsp;"; 
            ?>
        </div>

        <hr>

        <?php

            // connect to database (or not)
            $connect = mysqli_connect("localhost", "root", "") or die(mysqli_connect_error());
            mysqli_set_charset($connect, "utf8");
            mysqli_select_db($connect, "SupremeCourtApp") or die(mysqli_connect_error());
            

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

        <!-- display query results as table -->
        <div class="mainWrapper" style="overflow:hidden;">

            <div class="floatLeft" style="width: 18%; float:left">
                    <br>
                    <div class="panel panel-default">
                        <div class="panel-heading" style="font-size:20px">
                            Sources (<?php echo mysqli_num_rows($source_query) ?>)
                        </div>
                        <div class="panel-body" style="font-size: 16px">
                            <?php
                                // build search filter panel (list of sources with checkboxes)
                                // Known "defect" - because we're using two forms (the search form and filter form), any changes to the search parameters after a filter has been applied will be ignored (like changing the date range after selecting specific sources) - a new search will have to be done
                                // not enough time to come up with a more elegant solution

                                if(mysqli_num_rows($source_query) == 0)
                                {
                                    echo "No sources";
                                }
                                else
                                {
                                    echo "<form action='' method='GET'>";
                                    echo "<button type='submit' class='btn btn-primary' name='submit'>Apply Filter</button><br><br>";

                                    $names = ['search_query','dateFrom','dateTo'];

                                    // pass in search parameters (if any) into filter form
                                    foreach($names as $var)
                                    {
                                        if(isset($_GET[$var]))
                                        {
                                            echo "<input type='hidden' name=$var value=" . $_GET[$var] . ">";
                                        }
                                    }

                                    // get list of sources from search query
                                    $i = 0;
                                    while ($row = mysqli_fetch_array($source_query)) 
                                    {
                                        $source = $row['source'];

                                        // more than 30 results in the search box will result in a collapsible button that when clicked will show the remainder of sources (since large amounts of sources results in an ugly, long box that spans far down the webpage)

                                        if($i == 30) // after 30 sources, create source button and collapsible div
                                        {
                                            echo "<br><a href='#more' class='btn btn-info' data-toggle='collapse'>More Sources</a><br><br>";
                                            echo "<div id='more' class='collapse'>";
                                        }


                                        // get and display the number of articles from each specific source that meet the search criteria
                                        $temp_count_sql = $source_count_sql . "'$source'";
                                        $count_query = mysqli_query($connect,$temp_count_sql) or die(mysqli_connect_error());
                                        $count = mysqli_num_rows($count_query);

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
                                        $endIndex = mysqli_num_rows($source_query) - 1;
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

            <div class="floatRight" style="width:81%; float: right; ">
                <table id="results-table" style="background-color: white" width="92%" class="stripe hover"  align="center">
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
            </div>
        </div>

        <div style="height:200px"></div>

    </body>
</html>