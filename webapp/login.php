<?php
    function validLogin($email,$password,$connect,&$errs) {
        $email = mysqli_real_escape_string($connect,$email);
        $is_valid = true;
        $sql = "SELECT idUser,password_hash,name,authority FROM user WHERE email='$email'";
        $result = mysqli_query($connect, $sql) or die(mysqli_connect_error());
        $row = mysqli_fetch_assoc($result);
        $hash = $row ? $row["password_hash"] : null;
        $validPassword = password_verify($password,$hash);
        if(!$row || !$validPassword) {
            array_push($errs,"Invalid email/password combination");
            $is_valid = false;
        }
        else if ($row["authority"] < 1) {
            array_push($errs,"Login was correct, but you haven't been authorized yet.");
            $is_valid = false;
        }
        else {
            $_SESSION['authority'] = $row['authority'];
            $_SESSION['idUser'] = $row['idUser'];
            $_SESSION['name'] = $row['name'];
            $_SESSION['email'] = $email;
        }
        return $is_valid;
    }

    include_once("authenticate.php");
    include_once("db_connect.php");
    $valid_reg = false;
    if($_SERVER['REQUEST_METHOD'] == 'POST') {
        $email = isset($_POST['email']) ? $_POST['email'] : "";
        $password=isset($_POST['password']) ? $_POST['password'] : "";
        $errs = array();
        if(validLogin($email,$password,$connect,$errs)) {
            $destination = ((isset($_SESSION['redirectBackTo'])) ? $_SESSION['redirectBackTo'] : "index.php");
            header("Location: $destination");
            exit();
        }
    }
?>

<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <!-- Latest compiled and minified CSS -->
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.0/css/bootstrap.min.css">
        <!-- jQuery library -->
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>
        <!-- Latest compiled JavaScript -->
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.0/js/bootstrap.min.js"></script>
        <title>SCOTUSApp - Login</title>
        <script>  //***  change__But and revert__But are functions for events onmouseover and onmouseout of buttons in the webapp. When the user mouses over a button, it highlights the button, and unhighlights when leaving the button area
            function changeSubBut(){  //***
                document.getElementById("formBut").style.backgroundColor =  //***
                "#87ceeb" /*sky blue*/;  //***
            }
            function revertSubBut(){ //revert style back to original for tab2//***
                document.getElementById("formBut").style.backgroundColor =  //***
                "rgba(255, 255, 255, 0.7)" /*transparent white*/;  //***
            }
        </script>
    </head>
    <body style="height:100%; background-color: #fffacd; font-family: monospace; font-weight: bold; font-size:14px;">
        <h1 style="text-align: center; font-size: 50px; font-weight: bold;">SCOTUSApp</h1><hr style="background-color:#fffacd;">
        <h2 style="font-size: 30px; font-weight: bold; text-align:center;">Login</h2><br>
        <form method="post" action="" style="margin:0 auto;width:30%;">
            <p>SCOTUSApp can only be used by verified accounts - login will only be successful once you have created an account and have been verified by our administrators. If you haven't registered yet, <a href="register.php">click this link</a> to do so.</p>
            <fieldset class="form-group">
                <?php
                    if(isset($errs) && sizeof($errs) > 0) {
                        echo "<div style='color:red'>";
                        foreach($errs as $err) {
                            echo "<p>" . $err . "</p>";
                        }
                        echo "</div>";
                    }
                ?>
                Email
                <input type="text" class='form-control' name="email" <?php if(isset($email)) echo "value='$email'";?>><br>
                Password
                <input type="password" class='form-control' name="password"><br>
                <button id="formBut" type='submit' class='btn btn-default' onmouseover='changeSubBut()' onmouseout='revertSubBut()'
                    style = "height: 30px;
                    font-weight: bold;
                    font-family: monospace;
                    background-color: rgba(255, 255, 255, 0.45);
                    border: solid 3px;
                    border-radius: 10px;">Submit</button>
            </fieldset>
        </form>
    </body>
</html>