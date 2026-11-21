(function(){
const fmt=(v,d)=>Number(v).toFixed(d);
function tween(el,to,d){if(to==null){el.textContent='—';return}const from=parseFloat(el.textContent)||0;if(from===to)return;const t0=performance.now();
 (function f(n){const k=Math.min((n-t0)/900,1),e=1-Math.pow(1-k,3);el.textContent=fmt(from+(to-from)*e,d);if(k<1)requestAnimationFrame(f)})(t0);
 el.classList.remove('tick');void el.offsetWidth;el.classList.add('tick')}
window.startLive=function(cb){async function poll(){try{
 const r=await fetch('/api/live/',{credentials:'same-origin'});if(!r.ok)return;const j=await r.json();
 j.stations.forEach(s=>{const q=x=>document.querySelectorAll('[data-station="'+s.id+'"] '+x);
  q('[data-f]').forEach(el=>tween(el,s[el.dataset.f],+el.dataset.d||0));
  q('[data-bar]').forEach(b=>{b.style.animation='none';b.style.width=s[b.dataset.bar]+'%';b.parentNode.classList.toggle('warn',s[b.dataset.bar]<55)});
  q('[data-badge]').forEach(b=>{b.className='badge '+s.status;b.querySelector('em').textContent=s.status_label})});
 document.querySelectorAll('[data-g]').forEach(el=>el.textContent=j[el.dataset.g]);
 const st=document.getElementById('stamp');if(st)st.textContent=j.time;cb&&cb(j)}catch(e){}}
 setInterval(poll,5000);poll()}})();
