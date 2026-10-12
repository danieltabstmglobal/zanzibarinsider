(function(){
  var h=document.querySelector('.site-header');
  var b=document.querySelector('.burger');
  var n=document.querySelector('.nav');
  function onScroll(){h.classList.toggle('solid',window.scrollY>40)}
  onScroll();window.addEventListener('scroll',onScroll,{passive:true});
  if(b&&n){b.addEventListener('click',function(){
    var o=n.classList.toggle('open');b.setAttribute('aria-expanded',o)
  })}
  var els=document.querySelectorAll('.rv');
  if('IntersectionObserver' in window){
    var io=new IntersectionObserver(function(es){es.forEach(function(e){
      if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}})},{threshold:.12});
    els.forEach(function(el){io.observe(el)});
  }else{els.forEach(function(el){el.classList.add('in')})}
})();

/* Verzeichnis: Filter, Formulare */
(function(){
  var lang=document.body.getAttribute('data-lang')||'de';
  var T={de:{ok:'Danke! Wir prüfen das und melden uns bei Bedarf.',err:'Das hat nicht geklappt. Bitte schreib uns per E-Mail.',wait:'Wird gesendet …',cnt:' Einträge'},
         en:{ok:'Thank you! We will review it and get back to you if needed.',err:'That did not work. Please email us instead.',wait:'Sending …',cnt:' entries'}};
  var t=T[lang]||T.en;
  var list=document.getElementById('entries');
  if(list){
    var cat='',only=false,q='';
    var items=[].slice.call(list.querySelectorAll('.entry'));
    var chips=[].slice.call(document.querySelectorAll('.chip'));
    var none=document.getElementById('none'),count=document.getElementById('count');
    function apply(){
      var n=0;
      items.forEach(function(e){
        var ok=(!cat||e.dataset.cat===cat)&&(!only||e.dataset.status==='geprueft')&&(!q||e.dataset.search.indexOf(q)>-1);
        e.classList.toggle('hide',!ok);if(ok)n++;
      });
      if(none)none.hidden=n>0;
      if(count)count.textContent=n+t.cnt;
    }
    chips.forEach(function(c){c.addEventListener('click',function(){
      chips.forEach(function(x){x.classList.remove('on')});c.classList.add('on');cat=c.dataset.cat;apply()})});
    var qi=document.getElementById('q');if(qi)qi.addEventListener('input',function(){q=qi.value.trim().toLowerCase();apply()});
    var oc=document.getElementById('onlyok');if(oc)oc.addEventListener('change',function(){only=oc.checked;apply()});
    var m=location.search.match(/[?&]c=([a-z]+)/);
    if(m){chips.forEach(function(c){if(c.dataset.cat===m[1])c.click()})}
    apply();
  }
  var opened=Date.now();
  function send(form,payload){
    var msg=form.querySelector('.fmsg');msg.className='fmsg small';msg.textContent=t.wait;
    payload.lang=lang;payload.elapsed=Date.now()-opened;
    fetch('/api/submit',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)})
      .then(function(r){if(!r.ok)throw 0;msg.className='fmsg good';msg.textContent=t.ok;form.reset()})
      .catch(function(){msg.className='fmsg err';msg.textContent=t.err});
  }
  document.querySelectorAll('.cform').forEach(function(f){f.addEventListener('submit',function(e){
    e.preventDefault();var d=new FormData(f);
    send(f,{type:'kommentar',entry:f.dataset.entry,name:d.get('name'),text:d.get('text'),website:d.get('website')})})});
  var tf=document.getElementById('tippform');
  if(tf)tf.addEventListener('submit',function(e){
    e.preventDefault();var d=new FormData(tf);
    send(tf,{type:'tipp',cat:d.get('cat'),name:d.get('name'),text:d.get('text'),contact:d.get('contact'),from:d.get('from'),website:d.get('website')})});
})();
