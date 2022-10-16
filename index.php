<?php

session_start();
$errorMsg = $_SESSION['errorMsg'];
$_SESSION['errorMsg'] = ''; //remove message, so error doesn't show up in subsequent successful activations

//$_SESSION['checkMsg'] = 'checkMsg';

$log = fopen('logs.txt', 'a') or die('Unable to open file!'); //consider better documentation of log
fwrite($log, 'inside index error message $errorMsg\n');


?>

<!DOCTYPE html>
<html>



<head>
<script type='text/javascript' src='jsProgs/switch.js'></script>

<!--
ERROR PROOFING/EXPERIMENTAL SCRIPTS
<script type='text/javascript' src='jsProgs/switch2.js'></script>
<script type='text/javascript' src='jsProgs/scrap.js'></script>
<script type='text/javascript' src='picAnalysis/items.json'></script>
-->

<link rel='stylesheet' type='text/css' href='styleSheet.css'/>
<title>Analysis Page</title>
<meta charset='UTF-8'>
<meta name='viewport' content='width=device-width, initial-scale=1.0'>
</head>

<!--<body onload='colorSwitches()' probably could delete below>-->
<body onload='makeSwitchesActive();imageDisplay();'>
<!-- could put color switches in create JSON file, loading prexisting data, using program that moves into active/deactive, not needed -->


<div class ='header'>Projects</div>

<!-- Navigation Bar -->
<div class="navbar">
  <a href="#">Prosthesis Analysis</a>
  <a href="#">Medicare Expenditure Calculations (coming soon...)</a>
  <!--<a href="#">other</a>-->
</div>

    <div class='uploadAndEdgeAnalysis' id='imgAnalysisDisplay'>
    
      <div class='uploadArea'>
      <h2>Xray Upload </h2><!--and edge detection method--><br></br>
        <form action='upload.php' method='post' enctype='multipart/form-data' ><!--Select an Xray to Upload-->
          <input type='button' class='pointer' name='file' id='fileLoad' value='Upload Xray File' onclick='document.getElementById("file").click();'/>
          <input type='file' style='display:none;' id='file' name='file' onchange='this.form.submit();document.getElementById("imgAnalysisDisplay").style.cursor="wait"'/> 
          </form>
          <!--<span class='edgeDetectionMethod'>Select an Edge Detection Method <input type='submit' layer=0 value ='Difference Based Detection'  status='active'  class='layer0 pointer' id='differenceBased0' name='option'></input>
        //onclick='document.getElementById("imgProsthesis".submit() 
        -->

         
         <!---->
      
      <form action='createDir.php' method='post' >
        <input  type='submit' value='Use Preloaded Image' />
      </form> 


      </div>
      
    </div>


<div class = 'row'>
  <div class = 'side'>
    

      <h2 title='Prosthesis edges are detected by finding large gradients between neighboring pixels'>Edge Display Options  </h2><div class='edgeOptions'>&nbsp&nbsp&nbsp&nbsp</div>
      <br></br>
      <input type='submit' class='pointer' layer=1 value ='Horizontal Edges On' title='horizontal edges are edges along the x-axis of the upright prosthesis image' status='active'  itemType='edges' item='y_edges_diff' name='option'> </input>
      <input type='submit' class='pointer'  layer=1 value ='Vertical Edges On'  title='vertical edges are edges along the x-axis of the upright prosthesisstatus='active'  itemType='edges' item='t_edges_diff' name='option'> </input>
      <span id='selectionsLayerID_1'></span>
      <br class='optionsSelectionDivision'></br>

      <p id='check1'></p>
  
      
      <h2 title='Edges are distributed into groups, or segments, which contain pixels of a uniform brightness'>Group Display Options  </h2><div class='groupOptions'>&nbsp&nbsp&nbsp&nbsp</div>
      <br></br>
      <input  type='submit' class='pointer' layer=2 value ='Horizontal Span Groups On'  status='active'  itemType='groups' item='y_groups_raw_diff' name='option'> </input>
      <input  type='submit' class='pointer' layer=2 value ='Vertical Span Groups On'  status='active'  itemType='groups' item='x_groups_raw_diff' name='option'> </input>
      <input  type='submit' class='pointer' layer=2 value ='Horizontal Span Groups (Filtered) On'  status='active'  itemType='groups' item='y_groups_diff' name='option'> </input>
      <input  type='submit' class='pointer' layer=2 value ='Vertical Span Groups (Filtered) On'  status='active'  itemType='groups' item='x_groups_diff' name='option'> </input>
      <input  title='Inverse groups are segments of decreased intensity within masses. These are used to form inverse masses, which can indicate features such as insertion/extraction holes' type='submit' class='pointer' layer=2 value ='Vertical Inverse Groups On'  status='active'  itemType='groups' item='y_min_inverse_groups_diff' name='option'> </input>
      <span id='selectionsLayerID_2'></span>
      <br class='optionsSelectionDivision'></br>

      
      <h2 title='Contiguous groups are combined into masses, composed of multiple groups. Large masses are isolated and combined'>Mass Display Options  </h2><div class='massOptions'>&nbsp&nbsp&nbsp&nbsp</div>
      <br></br>
      <input title='combo masses are combined vertical and horizontal masses' type='submit' class='pointer' layer=3 value ='Combo Masses On'  status='active'  itemType='masses' item='combo_masses_diff' name='option'> </input>
      <input type='submit' class='pointer' layer=3 value ='Inverse Masses On'  status='active'  itemType='masses' item='inverse_masses' name='option'> </input>
      <input type='submit' class='pointer' layer=3 value ='Horizontal Masses On'  status='active'  itemType='masses' item='y_masses_diff' name='option'> </input>
      <input type='submit' class='pointer' layer=3 value ='Vertical Masses On'  status='active'   itemType='masses' item='y_x_masses_diff' name='option'> </input>
      <input type='submit' class='pointer' layer=3 value ='Weighted Horizontal Masses On'  status='active'  itemType='masses' item='y_masses_by_mass_diff' name='option'> </input>
      <input type='submit' class='pointer' layer=3 value ='Weighted Vertical Masses On'  status='active'   itemType='masses' item='y_x_masses_by_mass_diff' name='option'> </input>
      <span id='selectionsLayerID_3'></span>
      <br class='optionsSelectionDivision'></br>
    <!--
    <h2 >Feature Display Options</h2>
    <div class='featureOptions'>&nbsp&nbsp&nbsp&nbsp</div>
    <br></br>
    <input type='submit' class='pointer' layer=4 value ='Extraction Canal On'  status='active'  itemType='features' item='extraction_hole' name='option'> </input>
    <input type='submit' class='pointer' layer=4 value ='Shell On'  status='active'  itemType='features' item='shell_info' name='option'> </input>
    <span id='selectionsLayerID_4'></span>
    -->
    <!--</div>-->
    <br></br>
    <div class='possibleChanges'>
    <h2>Upcoming/Potential Changes:</h2>
    <h3>Prosthesis Analysis:</h3>
    <p>
      Program that categorizes uploaded prosthesis by feature
    </p>
    <p>
      Improve functionality for poor quality xrays and xray types
    </p>
    <p>
      Have option of selecting edge detection approach
    </p>
    <p>
      Improve + reincorporate prosthesis orientation correction function (makes uploaded image upright and oriented for analysis)
    </p>
    <h3>Prosthesis Display:</h3>
    <p> 
        Consistent and current image display, responsive display during loading, consistent image display after refresh
    </p>
    <p> 
        Program to increase efficiency of image creation
    </p>
    <p> 
        Multiple color gradations or color selection for greater clarity
    </p>

    <h3>General Improvements:</h3>
    <p> 
        Bug Fixes, error display for user, smooth sequential functioning using onclick()
    </p>
</div>
  
  </div>
  
      <img id= 'imgProsthesis' class=prosthImage src="sample.jpeg" onerror="this.onerror=null; this.src='sample.jpeg'"></img>
      <div class='imgBackground'></div>
   
   </div>
  
  </div>
</div>



</div>



</body>
<div class = "footer">
  updated 10/2022
</div>




<script> 
/*document.getElementById("prosthInterface").style.cursor = "wait";//may use related line of code again*/

function imageDisplay(){
    return new Promise(function (resolve, reject){
    var imgProsthesis = document.getElementById(id='imgProsthesis');
    var timestamp = new Date().getTime();  
    var queryString = "?t=" + timestamp;
    var imgProSource = <?php echo json_encode($_SESSION['imgPathFromHtmlDir']); ?>;
    imgProsthesis.src = imgProSource + queryString;
    

   
    if ('true') {
      resolve("worked!");
    } else {
      reject(Error("didn't work"));
    }
    });

}

async function cursPoint(elem){elem.style.cursor='pointer'; }

let fields = document.querySelectorAll('input');
for (let field of Array.from(fields)) {//need to filter out upload button, could also do it within file
  field.addEventListener('mousedown', async event => {
    //document.getElementById("prosthInterface").style.cursor = "wait";
    if(event.target.hasAttribute('itemType')){ 
      elem=event.target;
      switchOnOff(elem);//disables pointer, indicates processing
      elem.style.cursor='wait';  
    }
  });
  
  field.addEventListener('mouseup', async event => {
    //document.getElementById("prosthInterface").style.cursor = "wait";
    if(event.target.hasAttribute('itemType')){ 
      elem=event.target;
      elem.style.cursor='pointer';
      varExchange(elem) //switches colors and gives warning notice if unfilled information, current status used in mark_array
      .then(imageDisplay());
      
      
      } 
 
    });
  }
  /*
  The code below was written to address an asyn issue I had been having

  //load with select options - show only certain highlighted features
  //load correct, marked image immediately after upload, use async for this
  
  //document.onload = imageDisplay(); figure out how to show image after the image loads

      //startProcessing(elem)
      //.then(processHold())
      //.then(
      
      //startProcessing();
      //await processHoldAsync();//timed delay to allow for cursor/visual changes
      
  //async function cursChange(elem){setTimeout(() => {elem.style.cursor='pointer'; return 1000;}, '200'); }
  */



  
  </script>



    <!--
        HTML code I may use again.
        
        <input type='submit' layer=0 value ='Brightness Based Off' status='active' class='layer0' id='brightnessBased0' name='option'> </input>-->
      



</html>

