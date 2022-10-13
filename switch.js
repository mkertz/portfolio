function startProcessing(elem){
  
    return new Promise(function (resolve, reject) {
      
      elem.style.cursor= 'wait';
      document.body.style.cursor = 'wait';
      
      
      /*
      const list = document.getElementsByClassName("pointer").classList; 
      list.add("waity");
      list.remove("pointer");
    */
    if ('true') {
      resolve("Stuff worked!");
    } else {
      reject(Error("It broke"));
    }
    });
  
  }
  
  function endProcessing(elem){
    return new Promise(function (resolve, reject) {
      elem.style.cursor= 'pointer';
      document.body.style.cursor = 'default';
      /*
      const list = document.getElementsByClassName("waity").classList;
      list.remove("waity");
      list.add("pointer");*/
      if ('true') {
        resolve("Stuff worked!");
      } else {
        reject(Error("It broke"));
      }
      });
  }
  
  
  
  
  
  function processHold(){
    return new Promise(function (resolve, reject) {
      setTimeout(x=5, 2000);
      if ('aokay') {
        resolve("Stuff worked!");
      } else {
        reject(Error("It broke"));
      }
      });
      
    }
    
  
    function delay(){
       //function is just to allow for delay with setTimer 
      var delay = 1;
    }
  
  
  
  
  
  
  function check(){
    document.getElementById('check').innerHTML = 'check function working';
  }
  
  
  function makeSwitchesActive(){
    const analysisOptions = document.getElementsByName('option');
  
    for (let i =0; i < analysisOptions.length; i++) {
      elemOption = analysisOptions[i];
      if (elemOption.value.endsWith('Off')) {
        switchOnOff(elem);
      }
    }
  }
  
  
  function choiceEntered(elem){
    ///*
    return new Promise(function (resolve, reject) {
    switchOnOff(elem);
    
    if ('true') {
      resolve("Stuff worked!");
    } else {
      reject(Error("It broke"));
    }
    });//*/
    
    }
    //giveIncompleteNotice(elem);//kept here for simplicity, could be slightly more efficient but less simple if in switchOnOff()//showNotice(elem);
  
    async function switchOnOff1(elem){ 
      setTimeout(() => {
        console.log("Delayed for 1 second.");
      }, "2000");
    }
  
  function switchOnOff(elem){
    return new Promise(function (resolve, reject) {//(resolve, reject) 
      
    //document.getElementById('switchOnOffTime').innerHTML = "switchOnOff() start " + new Date().getTime();
  
    //document.getElementById('prosthInterface').style.cursor = "wait";
    let layer = elem.getAttribute('layer');
    var filled = sessionStorage.getItem('selectionsLayerFilled_'+layer);//refine variable to match layer that is present
    let noSelectionNum = sessionStorage.getItem('noSelectionNum');
  
    if (elem.value.endsWith('Off')){ //switch will be turned on, endsWith doesn't work with internet explorer
      elem.value = elem.value.slice(0,-3) + 'On'; //used instead of replace as On or Off may be elsewhere in value
      elem.setAttribute("status", "active");
      elem.style.color="black";
      filled = parseInt(filled)+parseInt(1); 
      //change items here as well
      if(filled == 1){ //make sure this results in appropriate warning
        noSelectionNum = parseInt(noSelectionNum) + parseInt(1);
      }
    }  
    else { //switch is in 'On', and will be turned off below
      elem.value = elem.value.slice(0,-2) + 'Off'; 
      elem.setAttribute("status", "inactive");
      elem.style.color="grey";    
      filled = parseInt(filled)-parseInt(1);
      if(filled == 0){ //no selectionNum negative or zero means it doesn't work
        noSelectionNum = parseInt(noSelectionNum) - parseInt(1); //remove overhead/upload warning
      }
    }
    
    
    //document.getElementById('switchOnOffTimeEnd').innerHTML = "switchOnOff() end   " + new Date().getTime();
    if ('true') {
      resolve("Stuff worked!");
    } else {
      reject(Error("It broke"));
    }
    });
  
    /*
    resolve("Stuff worked!");
    });*/
  }
  
  
  //below is for previous a version with a non-interactive display
  function giveIncompleteNotice(elem){
    let layer = elem.getAttribute('layer');
    filled = sessionStorage.getItem('selectionsLayerFilled_'+ layer);
  
    noSelectionNum = sessionStorage.getItem('noSelectionNum');
  
    warningElemLayer = document.getElementById('selectionsLayerID_'+layer);
    warningElemUpload = document.getElementById('uploadWarning');//+= 'noselectionnum ' + noSelectionNum;
  
    if(filled==0){
      warningElemLayer.innerHTML = 'Select a button for layer '+layer; //'Buttons selected: '+filled + COME BACK TO THIS, CREATE ALERT FUNCTION IN CSS, HIGHLIGHT BUTTON ALSO
      styleLayerIncomplete(warningElemLayer);
      //warningElemLayer.style.color = 'red';
    }
    else{
      warningElemLayer.innerHTML = '';
    }
    if(noSelectionNum < 1){
      warningElemUpload.innerHTML = 'Cannot proceed with upload, choices incomplete below';
      warningElemUpload.style.color = 'red';
      document.getElementById("fileLoad").disabled = true;
      document.getElementById("fileLoad").style.color="grey";
      document.getElementById("fileLoad").value="selections incomplete";
      document.getElementById("fileLoad").style.cursor = "not-allowed";
    } else {
      warningElemUpload.innerHTML = '&nbsp';//&nbsp is for a space, this ensures line returns to regular spacing in html/page doesn't move
      document.getElementById("fileLoad").disabled = false;
      document.getElementById("fileLoad").style.color="black";
      document.getElementById("fileLoad").value="Choose xray for upload";
      document.getElementById("fileLoad").style.cursor = "auto";
    }  
  }
  
  const warningStyle = document.createElement('warningStyle');
  
  warningStyle.textContent = `#color: red;`;
  
  function styleLayerIncomplete(elem){
    elem.style.color = 'red';
    const style = document.createElement('style');
  }
  
  
  function OLdvarExchange(elem) {
    //this function creates a timeOut to allow time for the cursor to change before delaying the execution
    return new Promise(function (resolve, reject) {
      //setTimeout(VarExchangeBody, 5);
      if (url) {
        resolve("Stuff worked!");
      } else {
        reject(Error("It broke"));
      }
    });
  }
  
  
  function varExchange(elem){
    return new Promise(function (resolve, reject) {
    //document.getElementById('varExchangeTime').innerHTML = 'varExchange Start '+new Date().getTime();  
    
    var xhttp = new XMLHttpRequest();
    xhttp.onload = function() {document.getElementById("checkvarExchange").innerHTML = this.responseText;}
  
    var item = elem.getAttribute('item');
    var itemType = elem.getAttribute('itemType');
    var status = elem.getAttribute('status');
    
    var url="../picAnalysis/varExchange.php";
    url +="?"
    url+="item="+item;
    url+="&itemType="+itemType;
    url+="&status="+status;
    
    xhttp.open("GET", url, false); //should this be false for synchronous? If clicked in rapid succession could create problems updating json file
    
    xhttp.send();
  
    //document.getElementById('varExchangeTimeEnd').innerHTML = 'varExchange End   '+new Date().getTime();  
      
    if (url) {
        resolve("Stuff worked!");
      } else {
        reject(Error("It broke"));
      }
    });
  }
  
  
  
  
  
  
  
  /*
  function showImg(src) {
    try{
      var imgPath = <?php echo json_encode($_SESSION['imgPathFromHtmlDir']); ?>;
      onload {
              var img = document.createElement('img');
              img.src = imgPath;
              document.getElementById('imgDisplay').appendChild(img);
          }
    } 
    catch(err){
      //pass
    }
  
  */
  