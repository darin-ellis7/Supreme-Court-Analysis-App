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
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.0/css/bootstrap.min.css">
    </head>
    <body style="height:100%; background-color: #fffacd; font-family: monospace; font-weight: bold; font-size: 14px;">
        <div style="float:right; margin-right:1.5%;font-size: 18px; font-family: monospace;">
            <a style="color:black;" href="user_page.php"><?php echo $_SESSION['name']?></a> | <a style="color:black;" href="logout.php">Logout</a>
        </div><br>
        <h1 style="text-align: center; font-size: 50px; font-weight: bold;"><a href='index.php' style='color:black;'>SCOTUSApp</a></h1><hr style="background-color:#fffacd;">
        <h2 style="font-size: 30px; font-weight: bold; text-align:center;">Verify User</h2><br>
        <p style="text-align:center;"><?php echo $msg; ?></p>
    </body>
</html>