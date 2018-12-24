<?php
    // does the same SQL search query as the one in search.php for any given search, but outputs the rows to a .csv + article text in .txt
    // everything is stored inside a .zip file

    include_once("db_connect.php");
    include("buildQuery.php");

    ignore_user_abort(true); // still delete temp files if user cancels download
    set_time_limit(120);

    $search_query = (!empty($_GET['search_query']) ? trim($_GET['search_query']) : '');
    $dateFrom = (!empty($_GET['dateFrom']) ? $_GET['dateFrom'] : '');
    $dateTo = (!empty($_GET['dateTo']) ? $_GET['dateTo'] : '');
    $sourcebox = (!empty($_GET['sourcebox']) ? $_GET['sourcebox'] : '');

    $sql = buildQuery($search_query,$dateFrom,$dateTo,$sourcebox,"download");
    $query = mysqli_query($connect, $sql) or die(mysqli_connect_error()); // execute query

    // Download article data into a .zip file consisting of a single .csv file with all of the search results + individual .txt files for each article's content
    $zipName = "articles.zip";
    $zip = new ZipArchive(); // create a zip file
    if ($zip->open($zipName, ZipArchive::CREATE) && $query)
    {
        $csvName = "article_data.csv";
        $csv = fopen($csvName, 'w') or die ("Unable to generate CSV: " . $csvName);

        // CSV column headers
        $arrName = array("Article ID", "Date", "Source", "Title","Sentiment Score","Sentiment Magnitude","Top Image Entity","Entity Score");
        fputcsv($csv, $arrName,"\t");

        $txtFiles = array();

        // build files to go into zip
        while ($row = mysqli_fetch_array($query))
        {
           $arr = array($row['idArticle'],$row['date'], $row['source'], $row['title'], $row['score'],$row['magnitude'],$row['entity'],$row['MAX(entity_instances.score)']);

           fputcsv($csv, $arr,"\t"); // insert row in CSV (tab delimiter necessary for Excel compatibility fix)

           $txtName = $row['idArticle']; // create a text file for each article's text
           $txtName .= ".txt";
           $txtFile = fopen($txtName, "w") or die("Unable to open text file: " . $txtName);
           $txt = $row['article_text'];
           fwrite($txtFile, $txt);
           fclose($txtFile);
           $zip->addFile($txtName, $txtName); // add text file to zip
           array_push($txtFiles,$txtName); // save text file names so we can delete them after the download
        }

        fclose($csv); // CSV finished - all rows inserted

        // the CSV is by default in UTF-8 encoding, which causes some scrambled characters in Excel (like apostrophes), so we convert it to UTF-16LE to fix this
        $data = file_get_contents($csvName); 
        $data = chr(255) . chr(254) . mb_convert_encoding($data, 'UTF-16LE','UTF-8');
        file_put_contents($csvName, $data);

        $zip->addFile($csvName,$csvName); // add completed CSV to zip
        $zip->close(); // finish zip

        ob_end_clean(); // clean output buffer and stop buffering - large downloads are very spotty otherwise

        // set headers to allow for sending the .zip to user
        header('Content-Type: application/zip');
        header("Content-Disposition: attachment; filename=$zipName");
        header("Content-Length: " . filesize($zipName));

        // delete non-zipped files from server
        foreach($txtFiles as $file) {
            unlink($file);
        }
        unlink($csvName);

        readfile($zipName); // download zip
        unlink($zipName); // delete zip from server
    }
    else
    {
        echo "ERROR: Couldn't download file!";
    }
?>