const tools = {
  gripper: {name:'Gripper',title:'A careful grip.\nA clean little snip.',copy:'Opposing fingers and an underside scissor mechanism bring holding and trimming together in one detachable tool.',detail:'Spring-return mechanisms · camera stays on the arm',alt:'FreeCAD screenshot of the detachable gripper and scissors attachment',skill:'The gripper specialist would plan holding and trimming for the selected target. The shared core would coordinate the approach, arm position and retreat.'},
  seedling: {name:'Seedling',title:'Good things start small.',copy:'A dedicated syringe attachment brings the seed dispenser, barrel clamp and geared plunger mechanism together as one removable module.',detail:'Seed pickup and placement concept · dosing needs calibration',alt:'FreeCAD screenshot of the detachable seed syringe, clamp and gearbox',skill:'The Seedling specialist would handle seed pickup, dosing and release decisions. The shared core would coordinate movement between the seed container and the planting location.'},
  scooper: {name:'Scooper',title:'A little scoop.\nA new angle.',copy:'A detachable bowl with a powered roll-joint concept lets the scoop turn around the arm’s length to reposition or tip loose material.',detail:'Powered wrist roll concept · payload and torque need testing',alt:'FreeCAD screenshot of the powered scooper roll joint, motor and belt drive',skill:'The Scooper specialist would plan gathering and releasing loose material, including tool roll. The shared core would coordinate the arm path and the destination.'},
  bully: {name:'Bully',title:'Make a little room.',copy:'A broad, ribbed push blade is designed for moving light, loose material around the garden surface.',detail:'Light-duty concept · not rated for excavation',alt:'FreeCAD screenshot of the detachable flat push blade',skill:'The Bully specialist would plan short passes for clearing light surface material. The shared core would position the blade and coordinate movement through the work area.'},
  nursery: {name:'Nursery',title:'Give new growth\na place to begin.',copy:'A cutting holder and trimmer, a rooting-gel dosing provision and a small planting dibber explore how one attachment could support propagation.',detail:'Concept assembly · gel pump and protocols still to select',alt:'FreeCAD screenshot of the nursery attachment with cutting holder, gel cartridge provision and planting dibber',skill:'The Nursery specialist would sequence holding, trimming, gel application and placement for a cutting. The shared core would coordinate those steps with the requested plant, quantity and destination.'},
  weeder: {name:'Weeder',title:'Catch the little\nuninvited guests.',copy:'A flat bar with rear-facing teeth is designed to snag small weeds as the arm pulls back, then lift to clear them.',detail:'Passive comb concept · root-pulling forces need testing',alt:'FreeCAD screenshot of the detachable seven-tooth weeding bar',skill:'The Weeder specialist would help select the weed target and plan a snag-and-pull action. The shared core would coordinate approach, retraction and clearing movement.'}
};
const tabs=[...document.querySelectorAll('.tool-tab')];
function selectTool(tab, focus=false){
  const data=tools[tab.dataset.tool];
  tabs.forEach(item=>{const active=item===tab;item.classList.toggle('active',active);item.setAttribute('aria-selected',String(active));item.tabIndex=active?0:-1;});
  document.querySelector('#tool-title').textContent=data.title;
  document.querySelector('#tool-copy').textContent=data.copy;
  document.querySelector('#tool-detail').textContent=data.detail;
  const imagePath='assets/tools/'+tab.dataset.tool+'.webp?v=r15b';
  const photo=document.querySelector('#tool-photo');photo.src=imagePath;photo.alt=data.alt;
  const photoButton=document.querySelector('.tool-photo-open');photoButton.dataset.image=imagePath;photoButton.dataset.caption=data.alt+'. Prototype geometry; physical testing required.';
  document.querySelectorAll('.skill-choice').forEach(item=>{const active=item.dataset.skill===tab.dataset.tool;item.classList.toggle('selected',active);item.setAttribute('aria-pressed',String(active));item.querySelector('.skill-state').textContent=active?'Active in preview':'Standby in preview';});
  document.querySelectorAll('[data-skill-path]').forEach(path=>path.classList.toggle('selected',path.dataset.skillPath===tab.dataset.tool));
  document.querySelector('#active-skill-label').textContent=data.name+' model active in preview';
  document.querySelector('#active-skill-copy').textContent=data.skill;
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
document.querySelectorAll('.skill-choice').forEach(button=>button.addEventListener('click',()=>selectTool(tabs.find(tab=>tab.dataset.tool===button.dataset.skill))));
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
