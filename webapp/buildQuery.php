<?php
	function buildQuery($search_query,$dateFrom,$dateTo,$sourcebox,$mode) {
        
		$sql = "SELECT DISTINCT date, title, source, idArticle FROM article NATURAL JOIN article_keywords NATURAL JOIN keyword_instances ";

		if($mode == 'sourcebox') {
			$sql = "SELECT source, count(source) FROM (" . $sql;
		}

        // build sql query based on search criteria
        if(!empty($search_query))
        {
                //$search_query = mysqli_real_escape_string($connect, trim($_GET['search_query']));
                $query_str = "WHERE (title LIKE '%$search_query%' OR keyword LIKE '%$search_query%') ";
                $sql .= $query_str;
        }

        // date range search - if no dates provided, ignore
        if(!empty($dateFrom) && !empty($dateTo))
        {
            // convert date input to Y-m-d format - this is because the bootstrap datepicker sends dates in Y/m/d while SQL only accepts as Y-m-d
        	$dateFrom = date("Y-m-d",strtotime($dateFrom));
        	$dateTo = date("Y-m-d",strtotime($dateTo));
            if(!empty($search_query))
            {
                $date_str = "AND date BETWEEN '$dateFrom' AND '$dateTo' ";
            }
            else
            {
                $date_str = "WHERE date BETWEEN '$dateFrom' AND '$dateTo' ";
            }

            $sql .= $date_str;
        }

        // if source filter has been applied and search parameters set, limit the sources to what has been checked
        if(!empty($sourcebox) && $mode != 'sourcebox')
        {
            if(empty($search_query) && empty($dateFrom) && empty($dateTo))
            {
                $sourceFilter_str = "WHERE source in (";
            }
            else
            {
                $sourceFilter_str = "AND source in (";

            }

            foreach($sourcebox as $source)
            {

                $sourceFilter_str .= "'" . $source . "'";
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

        return $sql;
	}

?>