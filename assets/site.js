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
