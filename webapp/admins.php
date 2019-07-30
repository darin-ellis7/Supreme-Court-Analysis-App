<?php
    function getAdmins($use_name_keys) {
        $admins = array();
        $admins_split = explode(",",getenv("ADMINS"));
        foreach($admins_split as $admin) {
            $admin_split = explode(":",$admin);
            $name = $admin_split[0];
            $email = $admin_split[1];
            $use_name_keys ? $admins[$name] = $email : array_push($admins,$email);
        }
        return $admins;
    }

    function contactLink() {
        $html = "";
        $admins = getAdmins(false);
        if(!empty($admins)) {
            $mailto = "mailto:" . $admins[0];
            if(sizeof($admins) > 1) {
                $mailto .= "?cc=" . join(";",array_slice($admins,1));
            }
            $html = "<div style='float:left; margin-left:1.5%;font-size: 18px; font-family: monospace;'>
                        <a style='color:black;' href='$mailto'>Contact</a>
                    </div>";
        }
        return $html;
    }
?>

