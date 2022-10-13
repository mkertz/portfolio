<?php

/*
If there is an existing directory path, write over? or make a new path? delete old path specifically?
*/


session_start(); //creates a session for passing variables to python program


$cwd = getcwd();

file_put_contents("logs.txt", ""); //clears logs.txt, consider removing for later records
//log resets with each new user, could also consider creating a log per each use, within unique id folder
$log = fopen("logs.txt", "w") or die("Unable to open error log file from uploads within $cwd directory!");

$errorPage = "index.php"; //replaced fileError.php with index.php (allows for better reupload) on 2022-7-25
$_SESSION['errorPage'] = $errorPage; //creates error page through use of session

$maxUploadSize = "1000000";

if ($_FILES['file']) { //formerly if (isset($_POST['submit']))check if submit button was clicked, use submit, because submit name of button
    $file = $_FILES['file']; //_FILE gets information needed for input from a form, 'file' is name
    
    $fileName = $_FILES['file']['name']; //could also set to $file['name'] instead
    $fileTmpName = $_FILES['file']['tmp_name']; 
    $fileSize = $_FILES['file']['size']; 
    $fileError = $_FILES['file']['error']; 
    $fileType = $_FILES['file']['type']; 

    $fileExt = explode('.', $fileName);
    $fileActualExt = strtolower(end($fileExt));
    $allowedExtensions = array('jpg', 'jpeg', 'png'); //could have ending, but be different file type, could check for this as well
    
} else {
    $errorMsg = "\nError uploading file\n";
    fwrite($log, "error Message $errorMsg");
    $_SESSION['errorMsg'] = $errorMsg;
    header("Location: index.php?fileDestination=../".$errorPage);
    die();
}

if (! in_array($fileActualExt , $allowedExtensions)) {
    $errorMsg = "\nExtension type ($fileActualExt) not recognized\n";
    $_SESSION['errorMsg'] = $errorMsg;
    header("Location: index.php?fileDestination=".$errorPage);
    die();
}

if ($fileError !== 0) {
    $errorMsg = "\nFile Error\n";
    $_SESSION['errorMsg'] = $errorMsg;
    header("Location: index.php?fileDestination=".$errorPage);
    die();
}
            
if ($fileSize < $maxUploadSize) {
    //consider redoing deletion program with glob(uploads/*/*)
    $folder_path = "uploads/"; //for consistency may want to change '/' at end across all files
   
    // List of name of files inside
    // specified folder
    $directories = array_diff(scandir($folder_path), array('..', '.')); //compare with glob
    
    $directoriesCurrent = count($directories);
    $directoriesRemaining = 4;
    $directoriesDeleted = $directoriesCurrent - $directoriesRemaining + 2; //remaining after directory added (why +1?)
} else {
    $errorMsg = "\nFile size too large, file must be less than $maxUploadSize\n";
    $_SESSION['errorMsg'] = $errorMsg;
    header("Location: index.php?fileDestination=".$errorPage); //formerly on index.php
    die();
}

//below deletes older files to conserve space. Would be quicker to save order of files saved, delete last file
//while loop creates more variables within array than expected, and replicates downstream folders
$timedOut = FALSE; //use timer to ensure while loop doesn't run. 
$startTime = time();
$timeLimit = 15;
$dirNum = 0;
while ($dirNum <= $directoriesDeleted) { 
    $directory = $folder_path.$directories[$dirNum];//could order to delete oldest first
    //fwrite($log, "line 57, dirNum $dirNum, directories[dirNum] $directories[$dirNum], directory $directory\n");
    $files = array_diff(scandir($directory), array('..', '.', '')); //each directory scanned multiple times for files
    
    if(time() > $startTime + $timeLimit) {
        $timedOut = TRUE;
        break;
    }
    foreach($files as $file) {
        $filePath = $directory.'/'.$file; //see logs, too many filepahts, and files are rotated through
        //fwrite($log, "line 67, filePath $filePath\n");
        if(is_file($filePath)) {
            unlink($filePath); // Delete the given file
            //fwrite($log, "file unlinked\n");
        } else { //suprisingly many filePath's are not files until the $dirNum = 2 (possibly different based on variables)
            //fwrite($log, "$filePath 62 not a file\n");
        }

        if(time() > $startTime + $timeLimit) {
            $timedOut = TRUE;
            break;
        }
    }
    rmdir($directory); //not sure what happens if multiple users at same time TODO:address this potential issue - probably loose directory of early user
    $dirNum += 1;
}

if ($timedOut == TRUE){
    $errorMsg = "\nTimed Out\n";
    $_SESSION['errorMsg'] = $errorMsg;
    header("Location: index.php?fileDestination=".$errorPage);
    die();
}

//make unique directory to pass image and manipulations amongst files
//TODO: delete these directories in case of error
$directoryPath = $folder_path.uniqid(date("Y:m:d:H:i:s_"), true).'/'; //date done for later so earliest files deleted
//$directoryPath = $folder_path.$directoryNameNew.'/';
if (mkdir($directoryPath)){
    //chdir($directoryPathNew);  //may be more simple not to change directory/to delete this line
} else {
    $errorMsg = "\nmkdir failed, new directory not created\n";
    $_SESSION['errorMsg'] = $errorMsg;
    header("Location: index.php?fileDestination=".$errorPage);
    //die();
}

//upload file to newly created (current) directory

$uploadedPic = $directoryPath.'uploadedPic'; //unique directory names, but not file names
if (move_uploaded_file($fileTmpName, $uploadedPic)) {
    $_SESSION['directoryPathFromHtmlDir'] = $directoryPath; //could send file destination as well
    $_SESSION['uploadedPic'] = $uploadedPic;
    $analysisPage = 'picAnalysis/picAnalysis.php';
    $_SESSION['uploadDirectory'] = __DIR__;
    //below is error proofing - currently works - next try $fileDestination with picAnalysis.php
    /*/
    $displayPage = 'scrap.php'; //for making sure image goes
    header("Location: $displayPage?fileDestination=".$displayPage);
    die();
    //*/

    $errorMsg = "\nswitch successfull\n";
    $_SESSION['errorMsg'] = $errorMsg;
    header("Location: picAnalysis/picAnalysis.php?fileDestination=".$analysisPage);
    die();
} else {
    $errorMsg = "\ndirectory created file failed to move using move_uploaded_file\n";
    $_SESSION['errorMsg'] = $errorMsg;
    header("Location: index.php?fileDestination=".$errorPage);
    die();
} 


?>




