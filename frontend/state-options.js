(() => {
  const names={AR:'अरुणाचल प्रदेश',MN:'मणिपुर',ML:'मेघालय',MZ:'मिजोरम',NL:'नागालैंड',SK:'सिक्किम',TR:'त्रिपुरा',AN:'अंडमान और निकोबार',CH:'चंडीगढ़',DN:'दादरा और नगर हवेली और दमन और दीव',LA:'लद्दाख',LD:'लक्षद्वीप',PY:'पुडुचेरी'};
  function add(){const s=document.getElementById('state');if(!s)return;Object.entries(names).forEach(([code,name])=>{if(!s.querySelector(`option[value="${code}"]`)){const o=document.createElement('option');o.value=code;o.textContent=name;s.appendChild(o)}})}
  document.addEventListener('DOMContentLoaded',()=>{add();const s=document.getElementById('state');if(s)s.addEventListener('change',()=>setTimeout(add,50));setInterval(add,1500)});
})();