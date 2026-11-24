'use strict';
const tools = {
  gripper: {title:'A careful grip.\nA clean little snip.',copy:'Opposing fingers and an underside scissor mechanism bring holding and trimming together in one detachable tool.',detail:'Spring-return mechanisms · camera stays on the arm',art:'<path d="M310 79l47-9 21 30-20 18-15-22-22 7M324 104l21 37 26 4 6-18-22-2-9-29" fill="#a9cbb1" stroke="#315943" stroke-width="3" stroke-linejoin="round"/><path d="M345 125l38 22m-31-30 38 6" stroke="#315943" stroke-width="3"/>'},
  seedling: {title:'Good things start small.',copy:'A dedicated syringe attachment brings the seed dispenser, barrel clamp and geared plunger mechanism together as one removable module.',detail:'Seed pickup and placement concept · dosing needs calibration',art:'<g transform="rotate(25 330 95)" stroke="#315943" stroke-width="3"><rect x="311" y="85" width="36" height="75" rx="5" fill="#d9eadb"/><path d="M329 45v40m-13-40h26m-13 115v35"/><path d="M317 100h12m-12 12h12m-12 12h12"/><rect x="300" y="79" width="58" height="9" rx="3" fill="#9cbd9e"/></g>'},
  scooper: {title:'A little scoop.\nA new angle.',copy:'A detachable bowl with a powered roll-joint concept lets the scoop turn around the arm’s length to reposition or tip loose material.',detail:'Powered wrist roll concept · payload and torque need testing',art:'<g stroke="#315943" stroke-width="3" stroke-linejoin="round"><circle cx="322" cy="96" r="19" fill="#9cbd9e"/><path d="M330 105l13 25 64-2-8 51-51 5-19-39z" fill="#c1d9b8"/><path d="M343 130l7 41 42-5 7-38" fill="#e2eddb"/><path d="M303 66c18-12 42-4 46 12m-7-6 7 6 4-9" fill="none" stroke-linecap="round"/></g>'},
  bully: {title:'Make a little room.',copy:'A broad, ribbed push blade is designed for moving light, loose material around the garden surface.',detail:'Light-duty concept · not rated for excavation',art:'<g stroke="#315943" stroke-width="3" stroke-linejoin="round"><path d="M317 90l30 40"/><path d="M314 120l85-12 5 70-83 14z" fill="#bfd5b8"/><path d="M321 179l83-13 12 12-83 16z" fill="#98bc98"/></g>'},
  nursery: {title:'Give new growth\na place to begin.',copy:'A cutting holder and trimmer, a rooting-gel dosing provision and a small planting dibber explore how one attachment could support propagation.',detail:'Concept assembly · gel pump and protocols still to select',art:'<g stroke="#315943" stroke-width="3" stroke-linejoin="round"><path d="M314 91l30 25 30-1"/><rect x="310" y="117" width="29" height="42" rx="5" fill="#dbe9d4"/><path d="M325 159v20m35-62 23 36m-11-17 23-6"/><path d="M358 102v-32m0 17c-23 0-23-19-23-19 21 0 23 12 23 19m0-5c24 0 23-20 23-20-21 0-23 13-23 20" fill="#9fc193"/></g>'},
  weeder: {title:'Catch the little\nuninvited guests.',copy:'A flat bar with rear-facing teeth is designed to snag small weeds as the arm pulls back, then lift to clear them.',detail:'Passive comb concept · root-pulling forces need testing',art:'<g stroke="#315943" stroke-width="3" stroke-linecap="round"><path d="M318 91l34 41"/><path d="M320 145l81-32 5 15-81 32z" fill="#a9cbb1"/><path d="M329 150l-7 28m22-35-6 29m22-35-6 29m21-35-5 29m20-35-4 29"/></g>'}
};
const tabs=[...document.querySelectorAll('.tool-tab')];
function selectTool(tab, focus=false){
  const data=tools[tab.dataset.tool];
  tabs.forEach(item=>{const active=item===tab;item.classList.toggle('active',active);item.setAttribute('aria-selected',String(active));item.tabIndex=active?0:-1;});
  document.querySelector('#tool-title').textContent=data.title;
  document.querySelector('#tool-copy').textContent=data.copy;
  document.querySelector('#tool-detail').textContent=data.detail;
  document.querySelector('#tool-svg-detail').innerHTML=data.art;
  document.querySelector('#tool-panel').setAttribute('aria-labelledby',tab.id);
  if(focus)tab.focus();
}
tabs.forEach((tab,index)=>{
  tab.addEventListener('click',()=>selectTool(tab));
  tab.addEventListener('keydown',event=>{
    let next;
    if(['ArrowDown','ArrowRight'].includes(event.key))next=(index+1)%tabs.length;
    if(['ArrowUp','ArrowLeft'].includes(event.key))next=(index-1+tabs.length)%tabs.length;
    if(event.key==='Home')next=0;if(event.key==='End')next=tabs.length-1;
    if(next!==undefined){event.preventDefault();selectTool(tabs[next],true);}
  });
});
const menu=document.querySelector('.menu-toggle'),nav=document.querySelector('#navigation');
menu.addEventListener('click',()=>{const open=menu.getAttribute('aria-expanded')!=='true';menu.setAttribute('aria-expanded',String(open));nav.classList.toggle('open',open);});
nav.querySelectorAll('a').forEach(link=>link.addEventListener('click',()=>{menu.setAttribute('aria-expanded','false');nav.classList.remove('open');}));
document.addEventListener('keydown',event=>{if(event.key==='Escape'){menu.setAttribute('aria-expanded','false');nav.classList.remove('open');}});
const dialog=document.querySelector('#image-dialog');
document.querySelectorAll('.gallery-open').forEach(button=>button.addEventListener('click',()=>{
  document.querySelector('#dialog-image').src=button.dataset.image;
  document.querySelector('#dialog-image').alt=button.dataset.caption;
  document.querySelector('#dialog-caption').textContent=button.dataset.caption;
  dialog.showModal();
}));
document.querySelector('.dialog-close').addEventListener('click',()=>dialog.close());
dialog.addEventListener('click',event=>{if(event.target===dialog){const r=dialog.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)dialog.close();}});
document.querySelector('#year').textContent=String(new Date().getFullYear());
function safeHttps(value){try{const url=new URL(value);return url.protocol==='https:'?url.href:null;}catch{return null;}}
async function loadContent(){
  try{
    const response=await fetch('site-content.json',{cache:'no-cache'});if(!response.ok)throw new Error('Site content unavailable');
    const content=await response.json();
    for(const [key,id] of [['founderName','founder-name'],['founderRole','founder-role'],['storyIntro','story-intro']]){if(typeof content[key]==='string')document.getElementById(id).textContent=content[key];}
    if(Array.isArray(content.storyParagraphs)&&content.storyParagraphs.every(text=>typeof text==='string')){
      document.querySelector('#story-body').replaceChildren(...content.storyParagraphs.map(text=>{const p=document.createElement('p');p.textContent=text;return p;}));
    }
    const campaign=safeHttps(content.kickstarterUrl);
    if(campaign&&new URL(campaign).hostname.match(/(^|\.)kickstarter\.com$/)){
      document.querySelectorAll('.campaign-link').forEach(link=>{link.href=campaign;link.target='_blank';link.rel='noopener noreferrer';});
      document.querySelector('#campaign-main').textContent=content.kickstarterButtonText||'Explore Spacefruit on Kickstarter';
      document.querySelector('#campaign-status').textContent='Get the latest campaign details directly on Kickstarter.';
    }else{
      document.querySelectorAll('.campaign-link:not(#campaign-main)').forEach(link=>link.textContent='Follow the Kickstarter journey');
      const creator=safeHttps(content.creatorLinksUrl);if(creator)document.querySelector('#campaign-main').href=creator;
    }
  }catch(error){console.warn('Using the built-in site copy:',error.message);}
}
loadContent();
