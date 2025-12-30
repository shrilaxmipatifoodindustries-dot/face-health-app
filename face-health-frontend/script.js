let recorder, stream, chunks=[];
const user = localStorage.getItem("user") || "Unknown_Agent";
const status = document.getElementById("status");
const video = document.getElementById("video");
const spinner = document.getElementById("spinner");
const dashboard = document.getElementById("dashboard");
const scanInterface = document.getElementById("scan-interface");
const countdownEl = document.getElementById("countdown");

// Show Date
if(document.getElementById("date-display")) {
    document.getElementById("date-display").innerText = new Date().toDateString();
}

// Start Camera
navigator.mediaDevices.getUserMedia({video:true})
.then(s=>{
  stream=s;
  video.srcObject=stream;
  status.innerText="🟢 System Online. Analyzing Topology...";
  
  recorder=new MediaRecorder(stream);
  recorder.ondataavailable=e=>chunks.push(e.data);
  recorder.onstop=upload;
  recorder.start();

  // 10 Seconds Recording
  let timeLeft = 10;
  if(countdownEl) countdownEl.classList.remove("hidden");
  
  const timer = setInterval(() => {
    timeLeft--;
    if(countdownEl) countdownEl.innerText = timeLeft;
    status.innerText = `🔴 Recording Analysis Data... ${timeLeft}s`;
    if(timeLeft <= 0) clearInterval(timer);
  }, 1000);

  setTimeout(()=>stop(), 10000);
})
.catch((err)=>{
    console.error(err);
    status.innerText="❌ Camera Error. Check Permissions.";
});

function stop(){
 if(recorder && recorder.state !== 'inactive') recorder.stop();
 if(stream) stream.getTracks().forEach(t=>t.stop());
 status.innerText="Uploading to Cloud & Processing 25+ Metrics...";
 if(spinner) spinner.classList.remove("hidden");
 if(countdownEl) countdownEl.classList.add("hidden");
}

async function upload(){
 let blob=new Blob(chunks,{type:"video/webm"});
 let data=new FormData();
 data.append("video",blob);
 data.append("user",user);

 try {
     status.innerText="⏳ Generating Holistic Health Report...";
     
     // 1. Upload Video & Get Main AI Report
     const response = await fetch("/upload", { method:"POST", body:data });
     const result = await response.json();
     
     if(spinner) spinner.classList.add("hidden");

     if(result.status === "success"){
         status.style.display = 'none';
         scanInterface.style.display = 'none'; // Hide camera
         dashboard.classList.remove("hidden"); // Show Super Dashboard

         // --- POPULATE DATA ---
         
         // 1. AI Report & Score
         // New lines ko HTML break mein convert aur bold tags ko preserve karte hue
         let formattedReport = result.ai_report.replace(/\n/g, "<br>");
         document.getElementById("ai-content").innerHTML = formattedReport;
         
         // Score handling
         document.getElementById("score-val").innerText = result.score || 85;

         // 2. Fetch Extra Features (Parallel)
         fetchExtras(result.ai_report); // Pass report to guess keywords
         
     } else {
         status.innerText = "⚠️ Error: " + result.message;
     }

 } catch (err) {
     console.error(err);
     status.innerText = "❌ Server Connection Failed";
 }
}

// Fetch all the cool new features from Backend APIs
async function fetchExtras(reportText) {
    // Determine condition keyword for diet based on report text
    let condition = "aging";
    if(reportText && reportText.toLowerCase().includes("acne")) condition = "acne";
    if(reportText && reportText.toLowerCase().includes("dry")) condition = "dry";

    try {
        // Call all new APIs in parallel for speed
        const [yogaRes, dietRes, tipRes, prodRes, ageRes] = await Promise.all([
            fetch("/face_yoga").then(r=>r.json()),
            fetch(`/diet/${condition}`).then(r=>r.json()),
            fetch("/daily_tip").then(r=>r.json()),
            fetch("/products").then(r=>r.json()),
            fetch("/skin_age").then(r=>r.json())
        ]);

        // Update UI Elements
        if(document.getElementById("yoga-tip")) 
            document.getElementById("yoga-tip").innerText = yogaRes.exercise;
        
        // Diet List
        if(document.getElementById("diet-plan") && dietRes.plan) {
            const dietList = dietRes.plan.map(item => `• ${item}`).join("<br>");
            document.getElementById("diet-plan").innerHTML = dietList;
        }

        if(document.getElementById("daily-tip"))
            document.getElementById("daily-tip").innerText = tipRes.tip;
        
        if(document.getElementById("skin-age"))
            document.getElementById("skin-age").innerText = `Est. Skin Age: ${ageRes.estimated_age}`;

        // Products List
        if(document.getElementById("product-list")) {
            const prodHtml = `
                <li>🧼 ${prodRes.cleanser}</li>
                <li>🧴 ${prodRes.moisturizer}</li>
                <li>☀️ ${prodRes.sunscreen}</li>
            `;
            document.getElementById("product-list").innerHTML = prodHtml;
        }
    } catch (e) {
        console.error("Error fetching extras:", e);
    }
}