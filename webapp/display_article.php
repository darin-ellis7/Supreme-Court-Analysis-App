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

      <?php
         $connect = mysqli_connect("localhost", "root", "cs499", "SupremeCourtApp") or die(mysqli_connect_error());
         mysqli_set_charset($connect, "utf8");
         $search_term = $_GET['idArticle'];
         $sql = "SELECT date, title, source, url, FROM article WHERE idArticle='%{$search_term}%'";
         //keep it for keyword
         //$keyword = "SELECT title,source, date FROM article NATURAL JOIN article_keywords NATURAL JOIN keyword_instances";



         if (isset($_POST['search'])) {

             $search_term = $_GET['idArticle'];

             $sql .= "WHERE idArticle='%{$search_term}%'";
            echo $sql;
         }
         else {
            $search_term = $_GET['idArticle'];
            $sql = "SELECT date, source, author, title, article_text, url,score,magnitude FROM article WHERE idArticle='{$search_term}'";
                //echo $sql;
            $keywordSQL = "SELECT keyword FROM article_keywords WHERE idKey IN (SELECT idKey FROM keyword_instances WHERE idArticle = '{$search_term}')";

            $imageSQL = "SELECT path FROM image WHERE idArticle IN ('{$search_term}')";
            $imgEntity = "SELECT idEntity, score FROM entity_instances WHERE idImage IN (SELECT idImage FROM image WHERE idArticle IN ('{$search_term}'))";



               }
         $query = mysqli_query($connect, $sql) or die(mysqli_connect_error());
         $keywords = mysqli_query($connect, $keywordSQL) or die(mysqli_connect_error());
         $images = mysqli_query($connect, $imageSQL) or die(mysqli_connect_error());
         $entities = mysqli_query($connect, $imgEntity) or die(mysqli_connect_error());




         ?>
      <div>
      <div>
      <div>
         <div>
            <div>
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

                          echo "<img src=\"images/"; echo $row['path']; echo "\" style=\"max-width:84%;\"></br>";
                       }
                       else{
                            echo "<b>None</b>";
                          }
                    ?>
               </table>
            </div>
            <div style="float:none;">
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
   </body>
</html>
