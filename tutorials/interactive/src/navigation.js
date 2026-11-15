(function(){
 'use strict';
 const ids=['home','counts','share','population','selection','estimation','inheritance'];
 const labels=['Overview','Expected reproduction','The linear share','Population variation','Selection','Estimation','Inheritance'];
 const storageKey='additive-channels-study-c619349-v1';
 let completed=[];
 try{completed=JSON.parse(localStorage.getItem(storageKey)||'[]').filter(x=>ids.slice(1).includes(x));}catch(e){completed=[];}
 function save(){try{localStorage.setItem(storageKey,JSON.stringify(completed));}catch(e){/* Reading does not require browser storage. */}}
 function progress(){document.getElementById('course-progress-text').textContent=completed.length+' of 6 marked as read';document.getElementById('course-progress').style.width=(100*completed.length/6)+'%';document.querySelectorAll('[data-read]').forEach(b=>{const done=completed.includes(b.dataset.read);b.setAttribute('aria-pressed',String(done));b.textContent=done?'Marked as read':'Mark as read';});}
 for(let i=1;i<ids.length;i++){
  const article=document.getElementById(ids[i]),footer=document.createElement('footer');footer.className='lesson-footer';
  footer.innerHTML=`<a class="btn" href="#${ids[i-1]}">← ${labels[i-1]}</a><button class="btn read-button" type="button" data-read="${ids[i]}" aria-pressed="false">Mark as read</button>${i<ids.length-1?`<a class="btn btn-primary" href="#${ids[i+1]}">${labels[i+1]} →</a>`:'<a class="btn btn-primary" href="#home">Return to overview</a>'}`;
  article.append(footer);
 }
 document.querySelectorAll('[data-read]').forEach(b=>b.addEventListener('click',()=>{const id=b.dataset.read;completed=completed.includes(id)?completed.filter(x=>x!==id):[...completed,id];save();progress();}));
 const menu=document.getElementById('menu-button'),sidebar=document.getElementById('sidebar');
 menu.addEventListener('click',()=>{const open=sidebar.classList.toggle('open');menu.setAttribute('aria-expanded',String(open));});
 function route(){let id=decodeURIComponent(location.hash.slice(1))||'home';if(id==='main-content')id=document.querySelector('.lesson.active')?.id||'home';if(!ids.includes(id)){const target=document.getElementById(id),parent=target?.closest('.lesson');id=parent?.id||'home';}
  document.querySelectorAll('.lesson').forEach(a=>a.classList.toggle('active',a.id===id));
  document.querySelectorAll('#course-nav a').forEach(a=>{if(a.hash==='#'+id)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');});
  sidebar.classList.remove('open');menu.setAttribute('aria-expanded','false');document.title=(id==='home'?'Additive channels':labels[ids.indexOf(id)]+' · Additive channels')+' — interactive study guide';
  window.scrollTo({top:0,behavior:'instant'});
 }
 window.addEventListener('hashchange',route);
 const mathButton=document.getElementById('math-toggle');mathButton.addEventListener('click',()=>{const open=mathButton.getAttribute('aria-pressed')!=='true';document.querySelectorAll('details.derivation').forEach(d=>d.open=open);mathButton.setAttribute('aria-pressed',String(open));mathButton.textContent=open?'Hide derivations':'Show derivations';});
 const symbols=document.getElementById('symbols-dialog');document.getElementById('symbols-button').addEventListener('click',()=>symbols.showModal());document.getElementById('symbols-close').addEventListener('click',()=>symbols.close());symbols.addEventListener('click',e=>{if(e.target===symbols)symbols.close();});
 document.getElementById('print-button').addEventListener('click',()=>window.print());
 document.getElementById('download-html').addEventListener('click',()=>{
  const copy=document.documentElement.cloneNode(true);
  // These controls are created on startup. Remove them from the saved copy
  // so reopening it does not create a second set of navigation or code buttons.
  copy.querySelectorAll('.lesson-footer,.code-download,script[data-runtime-error]').forEach(x=>x.remove());
  copy.classList.remove('js');
  copy.querySelectorAll('dialog[open]').forEach(x=>x.removeAttribute('open'));
  AdditiveGuide.download('Additive_channels_interactive_guide.html','<!doctype html>\n'+copy.outerHTML,'text/html');
 });
 document.querySelectorAll('details.code').forEach((section,i)=>{const pre=section.querySelector('pre');if(!pre)return;const button=document.createElement('button');button.type='button';button.className='btn btn-small code-download';button.textContent='Download this code';button.addEventListener('click',()=>{const code=pre.textContent,extension=/bash run_|git clone/.test(code)?'sh':'py';AdditiveGuide.download('additive_channels_example_'+(i+1)+'.'+extension,code+'\n');});(section.querySelector('div')||section).append(button);});
 try{AdditiveGuide.init();document.documentElement.classList.add('js');route();progress();window.ADDITIVE_GUIDE_READY=true;}catch(error){const box=document.createElement('div');box.className='app-error';box.textContent='A teaching control could not start. The complete lesson text is still available below. '+error.message;document.getElementById('app').prepend(box);window.ADDITIVE_GUIDE_ERROR=error.stack||error.message;}
})();
