<!--This page presents the article text and details about them. There is also a box including keywords in the article. At the bottom is a box for presenting images and entities of the articles.-->
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
      <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
      <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.4/jquery.min.js"></script>
      <script src="js/jquery.js"></script>
      <!-- Latest compiled JavaScript -->
      <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
      <script src="https://oss.maxcdn.com/html5shiv/3.7.3/html5shiv.min.js"></script>
      <script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
			<script>
			function changeResBut(){  //***
				document.getElementById("resBut").style.backgroundColor =  //***
				"#87ceeb" /*sky blue*/;  //***
			}
			function revertResBut(){ //revert style back to original for tab2
				document.getElementById("resBut").style.backgroundColor =  //***
				"rgba(255, 255, 255, 0.7)" /*transparent white*/;  //***
			}
			</script>
   </head>
   <body style=" height:100%; background-color: #fffacd; font-family: monospace; font-weight: bold;">  <!--***-->
		 <!-- header -->
	   <div style="background-color: #fffacd; padding: 30px; text-align: center;">  <!--***-->

	      <h1 style="font-size: 50px; font-family: monospace; font-weight: bold;">US Supreme Court Analysis Tool</h1>  <!--***-->
	      <hr>
	   </div>
		 <div align="right">
			 <a style="color:black; text-decoration:none;" href="index.php">
			 <button class="btn btn-default" id="resBut" onmouseover="changeResBut()" onmouseout="revertResBut()" style="height: 30px; font-weight: bold; font-family: monospace; background-color: rgba(255, 255, 255, 0.45); border: solid 3px; border-radius: 10px;">
			 Restart
		   </button>
		 </a>
		 </div>
        <?php
          include_once("db_connect.php");
          $search_term = $_GET['idArticle'];
          $sql = "SELECT date, title, source, url, FROM article WHERE idArticle='%{$search_term}%'";

          if (isset($_POST['search'])) {
            $search_term = $_GET['idArticle'];
            $sql .= "WHERE idArticle='%{$search_term}%'";
          }
          else {
            $search_term = $_GET['idArticle'];
            $sql = "SELECT date, source, author, title, article_text, url,score,magnitude FROM article WHERE idArticle='{$search_term}'";
            $keywordSQL = "SELECT keyword FROM article_keywords WHERE idKey IN (SELECT idKey FROM keyword_instances WHERE idArticle = '{$search_term}')";

            $imageSQL = "SELECT path FROM image WHERE idArticle IN ('{$search_term}')";
            $imgEntity = "SELECT idEntity, score FROM entity_instances WHERE idImage IN (SELECT idImage FROM image WHERE idArticle IN ('{$search_term}'))";
          }

          $query = mysqli_query($connect, $sql) or die(mysqli_connect_error());
          $keywords = mysqli_query($connect, $keywordSQL) or die(mysqli_connect_error());
          $images = mysqli_query($connect, $imageSQL) or die(mysqli_connect_error());
          $entities = mysqli_query($connect, $imgEntity) or die(mysqli_connect_error());
        ?>
      <div class='container'>
      <div class='content-wrapper'>
      <div>
         <div style="float:left;" class='col-xs-3 col-md-3'>
            <div id="rectangle" style="width:number px; height:number px; background-color:white; border-radius: 25px; padding: 20px; border: 2px solid #000000;">
               <b><big><big><big>Details</big></big></big></b></br></br>
               <b><big>Author</big></b></br>
               <?php ($row = mysqli_fetch_array($query)); echo $row['author']; ?></br></br>
               <b><big>Source</big></b></br>
               <?php echo $row['source']; ?></br></br>
               <b><big>Publication Date</big></b></br>
               <?php echo $row['date']; ?></br></br>
               <b>
                  <big>
                     <div id="dont-break-out" style="word-break: break-word; word-break: break-all; -ms-word-break: break-all; word-wrap: break-word; overflow-wrap: break-word;">URL</div>
                  </big>
               </b>
               <a href="<?php echo $row['url']; ?>"><?php echo substr($row['url'], 0, 30); echo"...";?></a></br></br>
               <b><big>Sentiment Score: <?php echo $row['score']; ?></big></b></br>
               <b><big>Magnitude: <?php echo $row['magnitude']; ?></big></b></br>
            </div>
        </br>
            <div>
                <div id="rectangle" style="width:number px; height:number px; background-color:white; border-radius: 25px; padding: 20px; border: 2px solid #000000;">
                    <b><big><big><big>Key Words</big></big></big></b></br></br>
                   <?php $keywords = mysqli_query($connect, $keywordSQL) or die(mysqli_connect_error());
                       while ($row = mysqli_fetch_array($keywords)){
                          echo $row['keyword']; echo "</br>";
                       }
                    ?>
                </div>
             </div>
         </div>
         </div>
         <div style="float:right;" class='col-xs-9 col-md-9 center-block'>
            <div id="rectangle" style="width:number px; height:number px; background-color:white; border-radius: 25px; padding: 20px; border: 2px solid #000000;">

                <?php $query = mysqli_query($connect, $sql) or die(mysqli_connect_error()); ($row = mysqli_fetch_array($query));?>
               <b><big><?php echo $row['title']; ?></b></big></br>
               <?php echo $row['date']; ?></br>
               <?php echo nl2br($row['article_text']); ?></br>
               </table>
            </div>
         </div>
     </br></br>
         <div style="float:right;" class='col-xs-9 col-md-9 center-block'>
         </br>
            <div id="rectangle" style="width:number px; height:number px; background-color:white; border-radius: 25px; padding: 20px; border: 2px solid #000000;">
                <div>
                <b><big><big><big>Images</big></big></big></b></br></br>
                    <?php
                        $images = mysqli_query($connect, $imageSQL) or die(mysqli_connect_error());
                       $row = mysqli_fetch_array($images);
                       if ($row){

                          echo "<img src=\"../images/"; echo $row['path']; echo "\" style=\"max-width:84%;\"></br>";
                       }
                       else{
                            echo "<b>None</b>";
                          }
                    ?>
               </table>
            </div>
            <div style="float:none;">
		<b><big><big><big>Article ID: </big></big></big></b>
                	<big><big><?php echo $search_term; ?></big></big></br></br>
                <b><big><big><big><br>Entities</big></big></big></b></br></br>
                <?php
                        $entities = mysqli_query($connect, $imgEntity) or die(mysqli_connect_error());
                       $row = mysqli_fetch_array($entities);
                       if ($row){
                          $ID = $row['idEntity'];
                          $SQL = "SELECT entity from image_entities WHERE idEntity IN ('{$ID}')";
                          $sqlQ = mysqli_query($connect, $SQL) or die(mysqli_connect_error());
                          $sqlRow = mysqli_fetch_array($sqlQ);
                          echo $sqlRow['entity']; echo "<div style=\"float:right;\"> Score: "; echo $row['score'];
                              echo "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</div></br>";
                          while ($row = mysqli_fetch_array($entities)){
                              $ID = $row['idEntity'];
                              $SQL = "SELECT entity from image_entities WHERE idEntity IN ('{$ID}')";
                              $sqlQ = mysqli_query($connect, $SQL) or die(mysqli_connect_error());
                              $sqlRow = mysqli_fetch_array($sqlQ);
                              echo $sqlRow['entity']; echo "<div style=\"float:right;\"> Score: "; echo $row['score'];
                              echo "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</div></br>";
                          }
                       }
                       else{
                            echo "<b>None</b>";
                          }
                    ?>
            </div>
            </div>
         </div>
     </div>
      </br></br></br></br></br></br></br></br></br></br>
   </body>
</html>
