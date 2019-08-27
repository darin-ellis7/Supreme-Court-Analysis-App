<?php
	function buildQuery($connect,$search_query,$dateFrom,$dateTo,$sourcebox,$mode) {
        // preventing SQL injections...(sourcebox strings handled farther down)
        $search_query = mysqli_real_escape_string($connect,$search_query);
        $dateFrom = mysqli_real_escape_string($connect,$dateFrom);
        $dateTo = mysqli_real_escape_string($connect,$dateTo);
        
        if($mode == 'download') {
            // old query
            // $sql = "SELECT DISTINCT title, date, source, author, article.url, article.idArticle, article.score, magnitude, entity, article_text, GROUP_CONCAT(DISTINCT keyword) as keywords, MAX(entity_instances.score) as top_entity FROM (article NATURAL JOIN article_keywords NATURAL JOIN keyword_instances) LEFT JOIN (image NATURAL JOIN image_entities NATURAL JOIN entity_instances) ON article.idArticle = image.idArticle ";
            $sql = "SELECT article.idArticle,url,article.source,author,title,date,article_text,article.score,magnitude,keywords,top_entity,top_entity_score,allsides_bias,allsides_confidence,allsides_agree,allsides_disagree,mbfs_bias,mbfs_score
                    FROM article
                    NATURAL JOIN (SELECT idArticle,GROUP_CONCAT(keyword) as keywords FROM article_keywords NATURAL JOIN keyword_instances GROUP BY idArticle) k
                    LEFT JOIN (SELECT idArticle,entity as top_entity, MAX(entity_instances.score) as top_entity_score FROM image NATURAL JOIN image_entities NATURAL JOIN entity_instances GROUP BY idArticle) i ON article.idArticle = i.idArticle
                    LEFT JOIN (
                        (SELECT b1.source,allsides_bias,allsides_confidence,allsides_agree,allsides_disagree,mbfs_bias,mbfs_score FROM source_bias b1 INNER JOIN (SELECT source,MIN(allsides_id) min_id FROM source_bias GROUP BY source) b2 ON b2.source=b1.source AND b1.allsides_id = b2.min_id) 
                        UNION 
                        (SELECT source,allsides_bias,allsides_confidence,allsides_agree,allsides_disagree,mbfs_bias,mbfs_score FROM source_bias WHERE allsides_bias IS NULL and mbfs_bias IS NOT NULL))
                    bias ON article.source=bias.source ";
        }
        else {
            $sql = "SELECT DISTINCT date, title, source, idArticle FROM article NATURAL JOIN article_keywords NATURAL JOIN keyword_instances ";
            if($mode == 'sourcebox') {
                $sql = "SELECT source, count(source) FROM (" . $sql;
            }
        }

        $conditionsExist = false; // boolean to determine whether WHERE or AND is used in query statement (if true, initial condition has already been set so subsequent conditions are prefixed with AND)

        // build sql query based on search criteria
        //if(!empty($search_query) && $mode != "download") // for downloads, search queries require a a HAVING clause at the end rather than a WHERE in the middle, so this block doesn't apply to those
        if(!empty($search_query))
        {
                //$search_query = mysqli_real_escape_string($connect, trim($_GET['search_query']));
                $query_str = "WHERE (title LIKE '%$search_query%' OR keyword LIKE '%$search_query%') ";
                $sql .= $query_str;
                $conditionsExist = true;
        }

        // date range search - if no dates provided, ignore
        if(!empty($dateFrom) && !empty($dateTo)) {
            // convert date input to Y-m-d format - this is because the bootstrap datepicker sends dates in Y/m/d while SQL only accepts as Y-m-d
        	$dateFrom = date("Y-m-d",strtotime($dateFrom));
            $dateTo = date("Y-m-d",strtotime($dateTo));

            if(!$conditionsExist) {
                $date_str = "WHERE date BETWEEN '$dateFrom' AND '$dateTo' ";
                $conditionsExist = true;
            }
            else {
                $date_str = "AND date BETWEEN '$dateFrom' AND '$dateTo' ";
            }
            $sql .= $date_str;
        }

        // if source filter has been applied and search parameters set, limit the sources to what has been checked
        if(!empty($sourcebox) && $mode != 'sourcebox') {
            if(!$conditionsExist) {
                $sourceFilter_str = "WHERE article.source in ("; // had to specify article.source here due to ambiguity with source after all the joins in the download query (also seen below)
                $conditionsExist = true;
            }
            else {
                $sourceFilter_str = "AND article.source in (";
            }

            foreach($sourcebox as $source) {
                $sourceFilter_str .= "'" . mysqli_real_escape_string($connect,$source) . "'";
                if($source != end($sourcebox))
                {
                    $sourceFilter_str .= ",";
                }
            }

            $sourceFilter_str .= ") ";
            $sql .= $sourceFilter_str;
        }

        if($mode == 'sourcebox') {
        	$sql .= ") AS results GROUP BY SOURCE ORDER BY source";
        }
        else if($mode == 'download') {
            /*$sql .= "GROUP BY article.idArticle ";
            if(!empty($search_query)) { // HAVING clause necessary to correctly check search query against list of keywords
                $sql .= "HAVING title LIKE '%$search_query%' OR keywords LIKE '%$search_query%' ";
            }*/
            $sql .= "ORDER BY article.idArticle DESC";
        }

        return $sql;
	}
?>