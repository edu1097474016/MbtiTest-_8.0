(function(){
  // 轻量级视差效果，移动端与低性能设备自动禁用
  var isTouch = ('ontouchstart' in window) || navigator.maxTouchPoints > 1;
  if(isTouch) return;

  var container = document.querySelector('.floating-shapes');
  if(!container) return;
  var shapes = container.querySelectorAll('.floating-shape');
  if(!shapes || shapes.length===0) return;

  // 鼠标移动视差
  var onMove = function(e){
    var w = window.innerWidth;
    var h = window.innerHeight;
    var cx = e.clientX - w/2;
    var cy = e.clientY - h/2;
    shapes.forEach(function(s, idx){
      var speed = parseFloat(s.getAttribute('data-speed')) || (0.02 + idx*0.01);
      var tx = cx * speed;
      var ty = cy * speed;
      s.style.transform = 'translate3d(' + tx.toFixed(2) + 'px,' + ty.toFixed(2) + 'px,0) scale(' + (1 + speed*0.8) + ')';
    });
  };

  // 滚动时的缓慢偏移
  var lastScroll = window.scrollY;
  var onScroll = function(){
    var sy = window.scrollY;
    var d = sy - lastScroll;
    lastScroll = sy;
    shapes.forEach(function(s, idx){
      var r = (idx % 2 === 0 ? 1 : -1);
      var move = (d * 0.15) * ( (parseFloat(s.getAttribute('data-speed'))||0.02) * 6 ) * r;
      // 仅在 Y 方向上微移
      var prev = s._parallaxY || 0;
      var next = prev + move;
      // 限制位移幅度
      next = Math.max(Math.min(next, 30), -30);
      s._parallaxY = next;
      s.style.transform = 'translate3d(0,' + next.toFixed(2) + 'px,0)';
    });
  };

  // 使用节流限制调用频率
  var throttledMove = (function(){
    var raf = null;
    return function(e){
      if(raf) cancelAnimationFrame(raf);
      raf = requestAnimationFrame(function(){ onMove(e); raf = null; });
    };
  })();

  window.addEventListener('mousemove', throttledMove, { passive: true });
  window.addEventListener('scroll', function(){ requestAnimationFrame(onScroll); }, { passive: true });

})();
