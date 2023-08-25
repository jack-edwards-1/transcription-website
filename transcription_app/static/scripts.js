function startRecording() {
    const startBtn = document.getElementById("startBtn");
    startBtn.style.backgroundColor = "#FF3737";  // Change color to red
    startBtn.textContent = "Recording...";

    fetch('/start_recording/', {method: 'POST'})
    .then(response => response.text())
    .then(data => {
        console.log(data);
    });
}

function stopRecording() {
    const startBtn = document.getElementById("startBtn");
    startBtn.style.backgroundColor = "#007AFF";  // Change color back to blue
    startBtn.textContent = "Start Recording";

    // Show a loading indicator
    const transcriptDiv = document.getElementById('transcript');
    const summaryDiv = document.getElementById('notes');
    transcriptDiv.innerHTML = "<div class='waveform'><div class='waveform__bar'></div><div class='waveform__bar'></div><div class='waveform__bar'></div><div class='waveform__bar'></div></div>";
    summaryDiv.innerHTML = "<div class='waveform'><div class='waveform__bar'></div><div class='waveform__bar'></div><div class='waveform__bar'></div><div class='waveform__bar'></div></div>";
    
    fetch('/stop_recording/', {method: 'POST'})
    .then(response => response.json())
    .then(data => {
        transcriptDiv.innerText = data.transcript;
        summaryDiv.innerText = data.summary;
    });
}


function openTab(tabName) {
    let i;
    const tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    const tablinks = document.getElementsByClassName("tablink");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    document.getElementById(tabName).style.display = "block";
    const activeTab = document.querySelector(`.tablink[onclick="openTab('${tabName}')"]`);
    if (activeTab) {
        activeTab.className += " active";
    }
}

// ... existing code ...

function handleFileUpload() {
    var fileInput = document.getElementById('fileInput');
    var file = fileInput.files[0];

    if (file) {
        console.log("File uploaded:", file.name);
        const transcriptDiv = document.getElementById('transcript');
        const summaryDiv = document.getElementById('notes');
        transcriptDiv.innerHTML = "<div class='waveform'><div class='waveform__bar'></div><div class='waveform__bar'></div><div class='waveform__bar'></div><div class='waveform__bar'></div></div>";
        summaryDiv.innerHTML = "<div class='waveform'><div class='waveform__bar'></div><div class='waveform__bar'></div><div class='waveform__bar'></div><div class='waveform__bar'></div></div>";
        // Create a FormData object to hold the file
        var formData = new FormData();
        formData.append('myfile', file);

        // POST the file to the server
        fetch('/handle_uploaded_file/', {  // Replace '/path_to_your_view/' with the actual URL of your view
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            // Handle the server's response here
            transcriptDiv.innerText = data.transcript;
            summaryDiv.innerText = data.summary;
        })
        .catch(error => {
            console.error("There was an error uploading the file:", error);
        });
    } else {
        alert("Please select a file first.");
    }
}


const words = document.querySelectorAll('.left-panel .word');
const summaryList = document.getElementById('summary-list');

let wordIndex = 0;
let summaryIndex = 0;

const summaries = [
    '• Client flagged 2024 projections',
    '&nbsp;&nbsp;‣ Delegated to Kim.'
];

// Function to animate words
function animateWords() {
    let timingArray = [150,150,300,300,150,150,100,150,200,150,200,150,200,300,200,150,150,200,150,150,150,150,150,150];
    if (wordIndex < words.length) {
        words[wordIndex].style.color = '#FF007A'; // Pink color
        wordIndex++;
        setTimeout(animateWords, timingArray[wordIndex]); // Duration before the next word is highlighted
    } else {
        setTimeout(animateSummary, 1000); // Wait a bit before starting the right panel animation
    }
}

// Function to animate summary
function animateSummary() {
    if (summaryIndex < summaries.length) {
        const listItem = document.createElement('li');
        listItem.innerHTML = summaries[summaryIndex];
        summaryList.appendChild(listItem);
        summaryIndex++;
        setTimeout(animateSummary, 800); // Duration before the next summary point is added
    }
}

// Start the animation
setTimeout(animateWords, 1000); // Start after a short delay

// Select all the feature icons
const featureIcons = document.querySelectorAll('.feature-icon');

// Function to check if an element is in viewport
function isInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
        rect.top <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.bottom >= 0
    );
}

// Add the slide-up animation class when the element is in the viewport
function checkScroll() {
    featureIcons.forEach(icon => {
        if (isInViewport(icon) && !icon.classList.contains('slide-up')) {
            icon.classList.add('slide-up');
        }
    });
}

// Initial check and event listener for the scroll event
checkScroll();
window.addEventListener('scroll', checkScroll);

const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');

let isRecording = false;

startBtn.addEventListener('click', function() {
    if (!isRecording) {
        // Start recording logic here...

        isRecording = true;
        startBtn.disabled = true;
        stopBtn.disabled = false;
    }
});

stopBtn.addEventListener('click', function() {
    if (isRecording) {
        // Stop recording logic here...

        isRecording = false;
        startBtn.disabled = false;
        stopBtn.disabled = true;
    }
});
