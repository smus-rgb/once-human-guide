/* Online DB status — does not mutate the pack. */
(function(){
  const badge = document.getElementById('syncBadge');
  if(!badge || location.protocol === 'file:') return;
  fetch('/integrity').then(r=>r.json()).then(data=>{
    if(!data || data.ok === undefined) return;
    badge.textContent = data.ok ? 'DB OK' : 'DB CHECK';
    badge.classList.toggle('on', !!data.ok);
    badge.title = 'records ' + (data.records||'?') + ' / ' + (data.expected_records||'?');
  }).catch(()=>{});
  fetch('/stats').then(r=>r.json()).then(s=>{
    if(s && s.total && badge.title) badge.title += ' · links ' + (s.links||0);
  }).catch(()=>{});
})();
