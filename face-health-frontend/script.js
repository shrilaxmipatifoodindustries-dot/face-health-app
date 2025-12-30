let recorder, stream, chunks=[];
const user = localStorage.getItem("user") || "Unknown_Agent";
const status = document.getElementById("status");
const video = document.getElementById("video");
const spinner = document.getElementById("spinner");
const reportCard = document.getElementById("report-card");
const aiContent = document.getElementById("ai-content");

// Start Camera Logic
navigator.mediaDevices.getUserMedia({video:true})
.then(s=>{
  stream=s;
  video.srcObject=stream;
  status.innerText="🟢 Scanning Face Topology...";
  
  recorder=new MediaRecorder(stream);
  recorder.ondataavailable=e=>chunks.push(e.data);
  recorder.onstop=upload;
  recorder.start();

  // --- TIME REVERTED TO 10 SECONDS (For Speed) ---
  let timeLeft = 10; 
  const timer = setInterval(() => {
    timeLeft--;
    status.innerText = ` scaning ${timeLeft}s remaining`;
    if(timeLeft <= 0) clearInterval(timer);
  }, 1000);

  // Stop automatically after 10 seconds
  setTimeout(()=>stop(), 10000); // 10000 ms = 10 seconds
})
.catch(()=>status.innerText="❌ Camera Access Denied");

function stop(){
 recorder.stop();
 stream.getTracks().forEach(t=>t.stop());
 status.innerText="Uploading & Analyzing Data...";
 if(spinner) spinner.classList.remove("hidden");
}

async function upload(){
 let blob=new Blob(chunks,{type:"video/webm"});
 let data=new FormData();
 data.append("video",blob);
 data.append("user",user);

 try {
     status.innerText="⏳ Sending to Gemini AI (Wait 10-15s)...";
     
     // Send to Backend
     const response = await fetch("/upload", {
         method:"POST", 
         body:data
     });

     const result = await response.json();
     
     if(spinner) spinner.classList.add("hidden");

     if(result.status === "success"){
         status.innerText = "✅ Analysis Complete!";
         
         if(video) video.style.display = "none"; 
         if(reportCard) reportCard.classList.remove("hidden");
         
         let formattedReport = result.ai_report ? result.ai_report.replace(/\n/g, "<br>") : "No report generated.";
         
         if(aiContent) {
            aiContent.innerHTML = formattedReport;
         }
     } else {
         status.innerText = "⚠️ Server Error: " + (result.message || "Unknown error");
     }

 } catch (err) {
     console.error(err);
     status.innerText = "❌ Connection Failed";
     if(spinner) spinner.classList.add("hidden");
 }
}