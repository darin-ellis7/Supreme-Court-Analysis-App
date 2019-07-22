<?php
    function sendConfirmationEmail($email,$name) {
        $login_url = "http://" . $_SERVER['SERVER_NAME'] . dirname($_SERVER['PHP_SELF']) . "/login.php";
        $to = array($name=>$email);
        $subject = "SCOTUSApp Authorization";
        $body = "Hi $name,<br><br>
                Our administrators have now authorized you to use SCOTUSApp. <a href='$login_url'>Click this link</a> to login and begin use.<br><br>
                Thanks,<br>
                SCOTUSApp Team";
        $email = sendEmail($to,$subject,$body);
        return $email;
    }

    include_once("authenticate.php");
    include_once("email.php");
    if(isset($_SESSION['redirectBackTo'])) {
        unset($_SESSION['redirectBackTo']);
    }

    if(isset($_GET['idUser'])) {
        include_once("db_connect.php");
        $idUser = mysqli_real_escape_string($connect,(int)$_GET['idUser']);
        $sql = "SELECT email,name,idUser,authority FROM user WHERE idUser=$idUser";
        $result = mysqli_query($connect, $sql) or die(mysqli_connect_error());
        $row = mysqli_fetch_assoc($result);
        if(!$row) {
            $msg = "Invalid user id.";
        }
        else if ($row['authority'] != 0) {
            $msg = "User has already been authorized.";
        }
        else {
            $sql = "UPDATE user SET authority=1 WHERE idUser=$idUser";
            mysqli_query($connect,$sql);
            $email = $row['email'];
            $name = $row['name'];
            $email_success = sendConfirmationEmail($email,$name);
            if($email_success) {
                $msg = "This user has now been authorized - they should receive a confirmation email momentarily.";
            }
            else {
                $msg = "This user has now been authorized, but their confirmation email failed to send. You may need to contact them directly at $email.";
            }   
        } 
    }
    else {
        $msg = "No user id provided.";
    }
?>

<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <title>SCOTUSApp - Verify User</title>
    </head>
    <body>
        <h1>SCOTUSApp</h1>
        <h2>Verify User</h2>
        <p><?php echo $msg; ?></p>
    </body>
</html>