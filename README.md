Radiograph Analysis and Analysis Display
analyze_array.py
Evaluates a numpy array formed from the uploaded image
Designed to determine features of the prosthesis

img_to_numpy.py
Converts images into numpy arrays for analysis within analyze_array.py.
The coding is direct and simple.

index.php
The user uploads an image of a prosthesis on this page.
This page also displays the image and interactively highlights the image analysis process.

items.json
Nested dictionary which stores the display information for the steps of analysis, and indicates which steps are displayed.

markArray.py
Marks the radiograph with representations of the activated steps of analysis (this information is stored on items.json, nested within the ‘active’ key).

picAnalysis.php
Runs the python programs img_to_numpy.py, analyze_array.py, and mark_array.py. These programs are responsible for the initial image analysis and markings.

reverseStatus.py
Changes the markers of the display within items.json to reflect whether they are activated or deactivated

switch.js
Contains programs that respond to user input, mostly DOM related, and a function that passes this information to varExchange.php

upload.php
Uploads the image, error checks the image, and assigns a unique identity to the image folder
The unique image folder houses the data related to the user.
This deletes older uploads when new images are uploaded

varExchange.php
Receives user input from index.php and runs reverseStatuses.py and markArray.py to alter the image.


Personal Project
beers_txt_sort.py    
Determines Medicare Part D spending on Beer’s list medications. Medicare Part D is a government sponsored insurance program that covers self-administered medications within elderly populations. Beer's list medications have an elevated potential for adverse effects within elderly populations. This program sorts out Beer’s list medications from the CMS spending and utilization data for Medicare Part D. This also allows for further analysis on the Beer’s list medication data.

