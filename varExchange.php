<?php
session_start();
$item = $_REQUEST["item"];
$itemType = $_REQUEST["itemType"];
$status = $_REQUEST["status"];

$directoryPath = '../'.$_SESSION['directoryPathFromHtmlDir']; //directory path ends with '/', directory path relative to folder/reference not needed
$uploadedPic = '../'.$_SESSION['uploadedPic'];
$itemsFile = $directoryPath.'items.json';


//$imgToNumpy = 'python3 image_to_numpy.py'; //use space after .py if no space in shell_exec

$imgArraryTitle = 'imgArr.npy';//saved as this within imgToNumpy

//$indexPage = '../'.$_SESSION['errorPage'];
$indexPage = '../index.php'; //used to have a different error page

$reverseStatus = 'python3 reverseStatus.py';

if ($status == 'active'){
    $oldStatus = 'inactive';
} else {
    $oldStatus = 'active';
}
    

if (shell_exec($reverseStatus.' '.$itemsFile.' '.$item.' '.$itemType.' '.$oldStatus)){ //consider consolidating string in single command
    //filter for manipulations, what to higlight.
} else {
    $errorMsg = "\n$shellExec failed to execute,--- output $output, ---return $return";
    $_SESSION['errorMsg'] = $errorMsg; //consider fwrite for errorMsg as well
    echo "couldn't perform $reverseStatus";
    fwrite($log, "\n couldn't perform $reverseStatus");
    header("Location: $indexPage?fileDestination=.$indexPage");
    die();
}

//status read as state in shell exec
$multipleImages = 'False'; //POSSIBLE FOR LATER USE, MARKING MULTIPLE IMAGES FOR VARIOUS EDGE DETECTIONS 
$markArray = 'python3 mark_array.py ';//'python3 scrap.py';// change according to folder
if (shell_exec($markArray.' '.$directoryPath.' '.$itemsFile.' '.$multipleImages)){ //consider consolidating string in single command
    $multipleImages = 'False';
    //$imgPath = $directoryPath.'postImage.jpeg'; //consider receiving this variable as output, or inputting into markArray
    //$_SESSION['imgPathFromPicAnalysis'] = $imgPath;
    $_SESSION['imgPathFromHtmlDir'] = $_SESSION['directoryPathFromHtmlDir'].'postImage.jpeg';
    #filter for manipulations, what to higlight.
} else {
    $errorMsg = "\n$markArray failed to execute,--- output $output, ---return $return";
    $_SESSION['errorMsg'] = $errorMsg; //consider fwrite for errorMsg as well
    //header("Location: $indexPage?fileDestination=.$indexPage");
    echo "couldn't perform $markArray";
    fwrite($log, "\n couldn't perform $markArray");
    die();
}


//echo "item is -$item- .......     itemType is -$itemType-........     status is -$status- ";

?>