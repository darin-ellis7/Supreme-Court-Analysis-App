<?php
    session_start();
    $logged_in = isset($_SESSION['authority']) && $_SESSION['authority'] > 0 && isset($_SESSION['email']) && isset($_SESSION['idUser']) && isset($_SESSION['name']);
    $allowAccess = true;
    $showError = false;
    $currentPage = explode('?',basename($_SERVER['REQUEST_URI']))[0];
    if(!$logged_in && $currentPage != "login.php") {
        $allowAccess = false;
        $_SESSION['redirectBackTo'] = basename($_SERVER['REQUEST_URI']);
        $destination = "login.php";
    }
    else if($logged_in && $currentPage == "login.php") {
        $allowAccess = false;
        $destination = "index.php";
    }
    else if($currentPage == "verify_user.php" && $_SESSION['authority'] != 2) {
        $allowAccess = false;
        $showError = true;
        $msg = "Administrator status is required.";
        $destination = "index.php";
    }

    if(!$allowAccess) {
        if($showError) {
            $msg = "You don't have access to this page: " . $msg;
            $html = 
                            "<!DOCTYPE html>
                            <html>
                                <head>
                                    <meta charset='utf-8'>
                                    <title>SCOTUSApp - Access Denied</title>
                                </head>
                                <body>
                                    <h1>Access Denied</h1>
                                    <p>" . $msg . "</p>
                                </body>
                            </html>";
            echo $html;
        }
        else {
            header("Location: $destination");
        }
        exit();
    }
?>