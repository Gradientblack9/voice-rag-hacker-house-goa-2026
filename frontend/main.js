const start=document.querySelector('#start'),status=document.querySelector('#status'),result=document.querySelector('#result');let busy=false,recorder,chunks=[];
const show=(message)=>status.textContent=message;
function render(data){result.hidden=false;document.querySelector('#transcript').textContent=data.transcript?`Transcript: ${data.transcript}`:'';document.querySelector('#answer').textContent=data.answer;const source=data.citations?.[0]?.source;document.querySelector('#details').textContent=`${data.status} · ${data.grounded?'grounded':'not grounded'} · ${Math.round(data.latency_ms?.total||0)}ms${source?` · Source: ${source}`:''}`;show(data.status==='answered'?'Answer ready':`Response: ${data.reason||data.status}`)}
async function send(audio){show('Transcribing…');const f=new FormData();f.append('audio',audio,'voice.webm');const r=await fetch('/api/v1/voice-query',{method:'POST',body:f});if(!r.ok)throw new Error((await r.json()).detail||'Voice request failed');render(await r.json())}
async function listen(){if(busy)return;busy=true;result.hidden=true;try{const stream=await navigator.mediaDevices.getUserMedia({audio:true});chunks=[];recorder=new MediaRecorder(stream);recorder.ondataavailable=e=>chunks.push(e.data);recorder.onstop=async()=>{try{await send(new Blob(chunks,{type:'audio/webm'}))}catch(e){show(e.message)}finally{stream.getTracks().forEach(t=>t.stop());busy=false;start.innerHTML='<i class="fa-solid fa-microphone"></i> Ask by voice'}};recorder.start();show('Listening… click again to send');start.innerHTML='<i class="fa-solid fa-stop"></i> Send question'}catch(e){busy=false;show('Microphone permission is required for voice questions.')}}
start.addEventListener('click',()=>recorder?.state==='recording'?recorder.stop():listen());document.querySelectorAll('.signin').forEach(b=>b.addEventListener('click',()=>start.click()));
const splitFlapRoot=document.querySelector('#builder-credit');
function createSplitFlap(root,text){
  const charset='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  const reduced=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const target=[...text.toUpperCase()];
  root.classList.add('split-flap-text');
  const tiles=target.map((character,index)=>{
    const tile=document.createElement('span');tile.className='split-flap-text__tile';tile.setAttribute('aria-hidden','true');
    tile.innerHTML='<span class="split-flap-text__half split-flap-text__half--top"><span class="split-flap-text__char"></span></span><span class="split-flap-text__half split-flap-text__half--bottom"><span class="split-flap-text__char"></span></span><span class="split-flap-text__flap split-flap-text__flap--front"><span class="split-flap-text__char"></span></span><span class="split-flap-text__flap split-flap-text__flap--back"><span class="split-flap-text__char"></span></span>';
    root.appendChild(tile);return {tile,character,index};
  });
  const paint=(entry,char,flipping=false)=>{entry.tile.classList.toggle('is-flipping',flipping);entry.tile.querySelectorAll('.split-flap-text__char').forEach(node=>node.textContent=char===' '?'\u00a0':char)};
  tiles.forEach(entry=>paint(entry,reduced?entry.character:' '));
  if(reduced)return;
  tiles.forEach(entry=>{let step=0;const start=180+entry.index*42;setTimeout(()=>{const timer=setInterval(()=>{step+=1;paint(entry,step>=7?entry.character:charset[Math.floor(Math.random()*charset.length)],step<7);if(step>=7)clearInterval(timer)},58)},start)});
}
if(splitFlapRoot)createSplitFlap(splitFlapRoot,'BUILT BY PINKU SHARMA');
