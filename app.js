const $=id=>document.getElementById(id);
const stages=["queued","downloading","extracting","reconstructing","training","completed"];
const labels=["Queued","Download video","Extract frames","Recover camera poses","Train splats","Complete"];
function stage(s){$("status").textContent=s==="failed"?"Reconstruction failed":s;$("stages").replaceChildren(...labels.map((label,i)=>{const li=document.createElement("li");li.textContent=label;li.className=i===stages.indexOf(s)?"active":i<stages.indexOf(s)?"done":"";return li;}));}
stage("Ready");
async function request(path,options){const res=await fetch("/api?path="+encodeURIComponent(path),options);if(!res.ok){let message="Request failed ("+res.status+")";try{const j=await res.json();message=j.detail||j.message||message;}catch{}throw Error(message);}return res.json();}
let viewer;
async function preview(path){
 const {Viewer,SceneFormat}=await import("https://esm.sh/@mkkellogg/gaussian-splats-3d@0.4.7?deps=three@0.160.0");
 if(viewer){await viewer.dispose();viewer=null;}
 $("placeholder").hidden=true;
 viewer=new Viewer({rootElement:$("preview"),selfDrivenMode:true,useBuiltInControls:true,sharedMemoryForWorkers:false});
 await viewer.addSplatScene(path,{format:SceneFormat.Splat,showLoadingUI:true});viewer.start();
}
$("generate").addEventListener("submit",async e=>{
 e.preventDefault();$("submit").disabled=true;$("downloads").hidden=true;$("error").textContent="";
 try{
 const job=await request("/jobs",{method:"POST",headers:{"Content-Type":"application/json","X-Generation-Key":$("key").value},body:JSON.stringify({url:$("url").value,authorized:$("authorized").checked})});
 stage(job.status);
 while(true){await new Promise(r=>setTimeout(r,2500));const current=await request("/jobs/"+job.id);stage(current.status);if(current.status==="failed")throw Error("Worker reconstruction failed. Check worker logs.");if(current.status==="completed")break;}
 const base="/api?path=";const file=name=>base+encodeURIComponent("/jobs/"+job.id+"/"+name);
 $("ply").href=file("scene.ply");$("splat").href=file("scene.splat");$("ply").download="scene.ply";$("splat").download="scene.splat";$("downloads").hidden=false;
 try{await preview(file("scene.splat"));}catch(e){$("error").textContent="Preview unavailable: "+e.message+"; downloads remain available.";}
 }catch(e){$("error").textContent=e.message;}finally{$("submit").disabled=false;}
});