document.addEventListener('DOMContentLoaded',()=>{
  if('serviceWorker' in navigator && location.protocol==='https:'){navigator.serviceWorker.register('/sw.js').catch(()=>{});}
  document.querySelectorAll('.speak-btn').forEach(b=>b.addEventListener('click',()=>{
    if(!('speechSynthesis' in window)) return alert('Bu tarayıcı seslendirmeyi desteklemiyor.');
    speechSynthesis.cancel(); const u=new SpeechSynthesisUtterance(b.dataset.speak||''); u.lang='en-US'; u.rate=.9; speechSynthesis.speak(u);
  }));
  const reveal=document.getElementById('revealBtn'); if(reveal) reveal.addEventListener('click',()=>{document.getElementById('reviewAnswer').classList.add('show'); reveal.style.display='none';});
  const wb=document.getElementById('writingBox'); if(wb) wb.addEventListener('input',()=>{document.getElementById('wordCount').textContent=(wb.value.trim()?wb.value.trim().split(/\s+/).length:0)+' kelime';});
  const sp=document.getElementById('speechStart'); if(sp){ const SR=window.SpeechRecognition||window.webkitSpeechRecognition; if(!SR){sp.disabled=true;sp.textContent='🎤 Tarayıcı desteklemiyor';}else{sp.addEventListener('click',()=>{const r=new SR();r.lang='en-US';r.interimResults=false;sp.textContent='🎤 Dinleniyor...';r.onresult=e=>document.getElementById('speechResult').textContent='Algılanan: '+e.results[0][0].transcript;r.onerror=()=>document.getElementById('speechResult').textContent='Konuşma algılanamadı.';r.onend=()=>sp.textContent='🎤 Telefonda söyle';r.start();});}}
});
