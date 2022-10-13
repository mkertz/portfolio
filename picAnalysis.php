<?php

//TODO: come back and condense variables, so accessed within python by variable names transfered fro mphp

session_start();
$log = fopen("picLogs.txt", "w") or die("Unable to open picLogs.txt!");
//fwrite($log, "");

//$uploadDirectory = $_SESSION['uploadDirectory'];

//image uploadedPic is located in unique directory $directoryPathNewRoot, this is the folder where python analysis files will save


$directoryPath = '../'.$_SESSION['directoryPathFromHtmlDir']; //directory path ends with '/', directory path relative to folder/reference not needed
$uploadedPic = '../'.$_SESSION['uploadedPic'];

$imgToNumpy = 'python3 image_to_numpy.py'; //use space after .py if no space in shell_exec

$imgArraryTitle = 'imgArr.npy';//saved as this within imgToNumpy

//$indexPage = '../'.$_SESSION['errorPage'];
$indexPage = '../index.php'; //used to have a different error page


//, consider error output when using shell_exec, $output, $return_var
// have to use directoryPath for file, will not save if filename accessed via sys.argv
if (shell_exec($imgToNumpy .' '. $uploadedPic.' '.$directoryPath)){ //first term is command, second is destination, third is saved title 
    //creates array imgArr
    //$imgArr = $directoryPath.$imgArraryTitle; #save file, could use string names instead
    $imgArr = $directoryPath.'imgArr.npy';
    fwrite($log, "SUCCESSFULLY used shell_exec\n $output, $return_var");
} else {
    $errorMsg = "\n$imgToNumpy failed to execute\n $return_var";
    $_SESSION['errorMsg'] = $errorMsg; //consider fwrite for errorMsg as well
    header("Location: $indexPage?fileDestination=".$indexPage);
    die();
}


fwrite($log, "\nperformed imgToNumpy");

$analyzeArray = 'python3 analyze_array.py'; //need space after .py if grouping adjacently
//$ItemsPickleFileName = strval($fileDestination).strval(.json); = $directoryPathRoot.'imageArray.npy'
$scrap = 'python3 scrap.py';

$ImplantItemsFileName = 'itemsTemplate.json'; //file was previously itemsTemplateWorking.json

if (shell_exec($analyzeArray.' '. $directoryPath.' '.$ImplantItemsFileName.' '.$imgArr)){ //consider consolidating string in single command
    $errorMsg = "$analyzeArray worked";//could delete this later
    $_SESSION['errorMsg'] = $errorMsg;
    fwrite($log, "\n successfully performed analyze array");
    #filter for manipulations, what to higlight.
} else {
    $errorMsg = "\n$analyzeArray failed to execute.\n directoryPath $directoryPath. items title .$ImplantItemsTitle. ";
    $_SESSION['errorMsg'] = $errorMsg; //consider fwrite for errorMsg as well
    fwrite($log, "\n couldn't perform analyze array");
    header("Location: $indexPage?fileDestination=.$indexPage");
    die();
}

$uploadedImgArray = $dirPath.'imgArr.npy';

#$imageName = 'Image.jpeg';
#$activatedItems ='activated items pickle file';//'python3 activate_items.py';//may not use this, could create list from json and js on interface
$markArray = 'python3 mark_array.py';//'python3 scrap.py';//


$itemsFile = $directoryPath.'items.json'; //currently $markArray doesn't load from this file via sysargv, should change
$multipleImages = 'True'; //this marks the progression of the analysis with images for each
if (shell_exec($markArray.' '.$directoryPath.' '.$itemsFile.' '.$multipleImages)){ //consider consolidating string in single command
    $multipleImages = 'False';
    //$imgPath = $directoryPath.'postImage.jpeg'; //consider receiving this variable as output, or inputting into markArray
    //$_SESSION['imgPathFromPicAnalysis'] = $imgPath;
    $_SESSION['imgPathFromHtmlDir'] = $_SESSION['directoryPathFromHtmlDir'].'postImage.jpeg';
    #filter for manipulations, what to higlight.
} else {
    $errorMsg = "\n$markArray failed to execute,--- output $output, ---return $return";
    $_SESSION['errorMsg'] = $errorMsg; //consider fwrite for errorMsg as well
    header("Location: $indexPage?fileDestination=.$indexPage");
    fwrite($log, "\n couldn't perform $markArray");
    die();
}


?>


<script type="text/javascript">
var trial = 'hello';
sessionStorage.setItem('trial', trial);
/*
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


