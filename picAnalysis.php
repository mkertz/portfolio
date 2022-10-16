<?php

//program to run python programs that analyze image


session_start();
$log = fopen("picLogs.txt", "w") or die("Unable to open picLogs.txt!");
//fwrite($log, "");


$directoryPath = '../'.$_SESSION['directoryPathFromHtmlDir']; //directory path ends with '/', directory path relative to folder/reference not needed
$uploadedPic = '../'.$_SESSION['uploadedPic'];

$imgToNumpy = 'python3 image_to_numpy.py'; //use space after .py if no space in shell_exec

$imgArraryTitle = 'imgArr.npy';//saved as this title within imgToNumpy

$indexPage = '../index.php'; //used to have a different error page

//when using shell_exec, could put variables in a nested dictionary/json file, so variables aren't transfered individually to python
if (shell_exec($imgToNumpy .' '. $uploadedPic.' '.$directoryPath)){ //first term is command, second is destination, third is saved title 
    $imgArr = $directoryPath.'imgArr.npy';
    fwrite($log, "SUCCESSFULLY used shell_exec\n $output, $return_var");
} else {
    $errorMsg = "\n$imgToNumpy failed to execute\n $return_var";
    $_SESSION['errorMsg'] = $errorMsg; //could use fwrite for errorMsg as well
    header("Location: $indexPage?fileDestination=".$indexPage);
    die();
}


fwrite($log, "\nperformed imgToNumpy");

$analyzeArray = 'python3 analyze_array.py'; //need space after .py if executing in shell_exec without spaces
$scrap = 'python3 scrap.py';

$ImplantItemsFileName = 'itemsTemplate.json'; //file was previously itemsTemplateWorking.json

if (shell_exec($analyzeArray.' '. $directoryPath.' '.$ImplantItemsFileName.' '.$imgArr)){ //consider consolidating string in single command
    $errorMsg = "$analyzeArray worked";//could delete this later
    $_SESSION['errorMsg'] = $errorMsg;
    fwrite($log, "\n successfully performed analyze array");
} else {
    $errorMsg = "\n$analyzeArray failed to execute.\n directoryPath $directoryPath. items title .$ImplantItemsTitle. ";
    $_SESSION['errorMsg'] = $errorMsg; //consider fwrite for errorMsg as well
    fwrite($log, "\n couldn't perform analyze array");
    header("Location: $indexPage?fileDestination=.$indexPage");
    die();
}

$uploadedImgArray = $dirPath.'imgArr.npy';

$markArray = 'python3 mark_array.py';//'python3 scrap.py';//

$itemsFile = $directoryPath.'items.json'; //currently $markArray doesn't load from this file via sysargv, should change
$multipleImages = 'True'; //this marks the progression of the analysis with images for each
if (shell_exec($markArray.' '.$directoryPath.' '.$itemsFile.' '.$multipleImages)){ //consider consolidating string in single command
    $multipleImages = 'False';
    $_SESSION['imgPathFromHtmlDir'] = $_SESSION['directoryPathFromHtmlDir'].'postImage.jpeg';
} else {
    $errorMsg = "\n$markArray failed to execute,--- output $output, ---return $return";
    $_SESSION['errorMsg'] = $errorMsg; //consider fwrite for errorMsg as well
    header("Location: $indexPage?fileDestination=.$indexPage");
    fwrite($log, "\n couldn't perform $markArray");
    die();
}


?>


<script type="text/javascript">
/*
error proofing below
try {
    dirPath ="<?php echo $_SESSION['$directoryPath']; ?>";
    dirPathFromHtmlDir ="<?php echo $_SESSION['directoryPathFromHtmlDir']; ?>"; //json_encode().'items.json'
    sessionStorage.setItem('dirPathFromHtmlDir', dirPathFromHtmlDir);
    const items = require('../picAnalysis/itemsTemplateWorking.json'); //there's a better way to access json file
    const fs = require('fs');
    itemsContent = JSON.stringify(items);
    fs.writeFile(dirPath+"items2.json", itemsContent, function(err) {
        if (err) {
            console.log('oops an error occurred');
        }
    }
 }
catch(err) {
    document.getElementById('check2').innerHTML = 'err1 is '+err;
}
*/
</script>


<?php
header("Location: $indexPage?fileDestination=.$indexPage");
?>


