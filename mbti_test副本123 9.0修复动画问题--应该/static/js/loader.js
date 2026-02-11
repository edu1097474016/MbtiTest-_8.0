(function(){
  function showLoader(){
    var l = document.getElementById('page-loader');
    if(!l) return;
    // 取消隐藏，触发过渡
    l.classList.remove('hidden');
    // 访问一下以触发重绘，确保 CSS 过渡能正确启动
    void l.offsetHeight;
  }
  function hideLoader(){
    var l = document.getElementById('page-loader');
    if(!l) return;
    // 使用 CSS 隐藏并在过渡结束后移除节点
    l.classList.add('hidden');
    setTimeout(function(){ try{ l.parentNode && l.parentNode.removeChild(l); }catch(e){} }, 500);
  }

  // 页面初次加载完成后隐藏
  document.addEventListener('DOMContentLoaded', function(){
    // 让主内容至少显示一次过渡
    setTimeout(hideLoader, 200);

    // 拦截所有本域链接点击，展示 loader
    document.body.addEventListener('click', function(e){
      var a = e.target.closest && e.target.closest('a');
      if(!a) return;
      var href = a.getAttribute('href');
      if(!href) return;
      // 忽略锚点、mailto 和外链（以 http 或 // 开头且非本站）
      if(href.indexOf('#') === 0 || href.indexOf('mailto:') === 0) return;
      // 外部链接：以http或//开头并且hostname不同，则不显示
      if((href.indexOf('http')===0 || href.indexOf('//')===0)){
        try{
          var url = new URL(href, location.href);
          if(url.hostname !== location.hostname) return;
        }catch(e){ }
      }
      showLoader();
    }, true);

    // 提交表单时显示 loader
    document.body.addEventListener('submit', function(e){
      showLoader();
    }, true);
  });

  // 如果页面通过浏览器后退等触发 pageshow，可以尝试隐藏
  window.addEventListener('pageshow', function(e){
    if(e.persisted) setTimeout(hideLoader, 150);
  });

  // 暴露给全局以便在需要时手动控制
  window.__pageLoader = { show: showLoader, hide: hideLoader };
})();
