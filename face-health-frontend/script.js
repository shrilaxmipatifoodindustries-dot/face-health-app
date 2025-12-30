let recorder, stream, chunks=[];
const user = localStorage.getItem("user") || "builder";
const status = document.getElementById("status");
const video = document.getElementById("video");

navigator.mediaDevices.getUserMedia({video:true})
.then(s=>{
  stream=s;
  video.srcObject=stream;
  status.innerText="🔴 Recording started automatically";

  recorder=new MediaRecorder(stream);
  recorder.ondataavailable=e=>chunks.push(e.data);
  recorder.onstop=upload;
  recorder.start();

  // 15 seconds recording
  setTimeout(()=>stop(),15000);
})
.catch(()=>status.innerText="Camera permission denied");

function stop(){
 recorder.stop();
 stream.getTracks().forEach(t=>t.stop());
 status.innerText="Uploading...";
}

function upload(){
 let blob=new Blob(chunks,{type:"video/webm"});
 let data=new FormData();
 data.append("video",blob);
 data.append("user",user);

 // FIX: Sirf "/upload" use kar, taaki live server pe chale
 fetch("/upload", {method:"POST", body:data});

 status.innerText="Saved successfully";
 chunks=[];
}
