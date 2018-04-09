<?php
    // does the same SQL search query as the one in search.php for any given search, but outputs the rows to a .csv + article text in .txt
    // everything is stored inside a .zip file

    // connect to database (or not)
    $connect = mysqli_connect("localhost", "root", "") or die(mysqli_connect_error());
    mysqli_set_charset($connect, "utf8");
    mysqli_select_db($connect, "SupremeCourtApp") or die(mysqli_connect_error());

    // base sql query
    // default search includes entire database
    $sql = "SELECT DISTINCT title, date, source, article.idArticle, article.score, magnitude, entity, article_text, MAX(entity_instances.score) FROM (article NATURAL JOIN article_keywords NATURAL JOIN keyword_instances) LEFT JOIN (image NATURAL JOIN image_entities NATURAL JOIN entity_instances) ON article.idArticle = image.idArticle ";
   
    // build sql query based on search criteria
    if(isset($_GET['search_query']))
    {

            $search_query = mysqli_real_escape_string($connect, trim($_GET['search_query']));
            $query_str = "WHERE (title LIKE '%$search_query%' OR keyword LIKE '%$search_query%') ";
            $sql .= $query_str; 
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
            $sql .= $date_str;
        }
        else
        {
            $date_str = "WHERE date BETWEEN '$dateFrom' AND '$dateTo' ";
            $sql .= $date_str;
        }
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

    $sql .= "GROUP BY article.idArticle"; // finish query string
    $query = mysqli_query($connect, $sql) or die(mysqli_connect_error()); // execute query

    // Download article data into a .zip file consisting of a single .csv file with all of the search results + individual .txt files for each article's content
    $zipName = "articles.zip";
    $zip = new ZipArchive(); // create a zip file
    if ($zip->open($zipName, ZipArchive::CREATE) && $query)
    {
        $csvName = "article_data.csv";
        $csv = fopen($csvName, 'w');

        // CSV column headers
        $arrName = array("Article ID", "Date", "Source", "Title","Sentiment Score","Sentiment Magnitude","Top Image Entity","Entity Score");
        fputcsv($csv, $arrName);

        $txtFiles = array();

        // build files to go into zip
        while ($row = mysqli_fetch_array($query)) 
        { 
           $arr = array($row['idArticle'],$row['date'], $row['source'], $row['title'], $row['score'],$row['magnitude'],$row['entity'],$row['MAX(entity_instances.score)']);

           fputcsv($csv, $arr); // insert row in CSV

           $txtName = $row['idArticle']; // create a text file for each article's text
           $txtName .= ".txt";
           $txtFile = fopen($txtName, "w") or die("Unable to open file!");
           $txt = $row['article_text'];
           fwrite($txtFile, $txt); 
           fclose($txtFile); 
           $zip->addFile($txtName, $txtName); // add text file to zip
           array_push($txtFiles,$txtName); // save  text file titles so we can delete them at the end (for some reason we had to do this ev)    
        }

        fclose($csv); // CSV finished - all rows inserted
        $zip->addFile($csvName,$csvName); // add completed CSV to zip

        $zip->close(); // finish zip

        // set headers to allow for sending the .zip to user
        header('Content-Type: application/zip');
        header("Content-Disposition: attachment; filename=$zipName");
        readfile($zipName);

        // file created and sent - now, delete files from the server
        unlink($zipName);
        unlink($csvName);
        foreach($txtFiles as $file)
        {
            unlink($file);
        }
    }
    else
    {
        echo "ERROR: Couldn't download file!";
    }

?>