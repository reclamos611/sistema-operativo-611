// \u2500\u2500 TIPO CHOFER FILTER
function getActiveTipos(){
  var tipos=[];
  ['propio','backup','tercero'].forEach(function(t){
    var el=document.getElementById('ftipo-'+t);
    if(el&&el.checked)tipos.push(t);
  });
  return tipos.length?tipos:['propio','backup','tercero'];
}
function chMatchTipo(ch){
  var tipos=getActiveTipos();
  var t=(window.D_CH_TIPOS&&D_CH_TIPOS[ch])||'tercero';
  return tipos.indexOf(t)>=0;
}
function onTipoChange(){
  INITED={};
  var secs=document.querySelectorAll('.sec.on');
  secs.forEach(function(s){var id=s.id.replace('sec-','');initTab(id);});
}

// \u2500\u2500 HELPERS \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
function F(n){return Number(n||0).toLocaleString('es-AR',{maximumFractionDigits:0});}
function P(n){return (Number(n||0)*100).toFixed(1)+'%';}
function P2(n){return (Number(n||0)*100).toFixed(2)+'%';}
function KPI(v,l,col){return '<div class="kpi"><div class="kpi-v" style="color:'+col+'">'+v+'</div><div class="kpi-l">'+l+'</div></div>';}
function BD(cls,txt){return '<span class="'+cls+'">'+txt+'</span>';}
function PR(pct,col,max){
  var w=Math.min(100,(pct||0)*100/(max||1)*100);
  return '<div class="pw"><div class="pb"><div class="pf" style="width:'+w+'%;background:'+col+'"></div></div></div>';
}
function fmtFecha(s){
  if(!s) return '';
  if(s.indexOf('-')===4) return s.split('-').reverse().join('/');
  return s;
}

// \u2500\u2500 LOGIN \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
var USERS={'sup':{'pass':'sup611','name':'Supervisor'}};
function doLogin(){
  var u=(document.getElementById('lu').value||'').trim().toLowerCase();
  var p=(document.getElementById('lp').value||'').trim();
  var usr=USERS[u];
  if(usr && p===usr.pass){
    document.getElementById('login-overlay').style.display='none';
    document.getElementById('app').style.display='block';
    initApp();
  } else {
    document.getElementById('lerr').style.display='block';
  }
}
function doLogout(){
  document.getElementById('app').style.display='none';
  document.getElementById('login-overlay').style.display='flex';
  document.getElementById('lu').value='';
  document.getElementById('lp').value='';
}

// \u2500\u2500 TABS \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
var INITED={};
function goTab(id,btn){
  document.querySelectorAll('.tab').forEach(function(t){t.classList.remove('on');});
  document.querySelectorAll('.sec').forEach(function(s){s.classList.remove('on');});
  if(btn) btn.classList.add('on');
  var sec=document.getElementById('sec-'+id);
  if(sec) sec.classList.add('on');
  if(!INITED[id]){INITED[id]=true; initTab(id);}
}
function initTab(id){
  if(id==='cartones') initCart();
  else if(id==='rechazos') initRej();
  else if(id==='deposito') initDep();
  else if(id==='ventas') initVentas();
  else if(id==='ruta') initRuta();
}
function initApp(){
  document.getElementById('hdr-periodo').textContent=D_PERIODO||'';
  INITED={};
  initTab('cartones');
}

// \u2500\u2500 CARTONES \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
function initCart(){
  var semMap={};
  D_CART.forEach(function(r){
    var k='Sem '+r.semana;
    if(!semMap[k]){semMap[k]={min:r.fecha,max:r.fecha};}
    if(r.fecha<semMap[k].min)semMap[k].min=r.fecha;
    if(r.fecha>semMap[k].max)semMap[k].max=r.fecha;
  });
  var semSel=document.getElementById('cart-sem');
  semSel.innerHTML='<option value="">Todas las semanas</option>'+
    Object.keys(semMap).sort().map(function(k){
      var r=semMap[k];
      return '<option value="'+k+'">'+k+' ('+fmtFecha(r.min)+' - '+fmtFecha(r.max)+')</option>';
    }).join('');
  var chs=[...new Set(D_CART.map(function(r){return r.chofer;}))].sort();
  var chSel=document.getElementById('cart-ch');
  chSel.innerHTML='<option value="">Todos</option>'+chs.map(function(c){return '<option>'+c+'</option>';}).join('');
  document.getElementById('cart-note').textContent='Cartones '+D_PERIODO;
  renderCart();
}
function renderCart(){
  var vista=document.getElementById('cart-vista').value;
  var ch=document.getElementById('cart-ch').value;
  var sem=document.getElementById('cart-sem').value;
  var semNum=sem?parseInt(sem.replace('Sem ','')):0;
  var rows=D_CART.filter(function(r){
    if(!chMatchTipo(r.chofer))return false;
    if(ch&&r.chofer!==ch)return false;
    if(semNum&&r.semana!==semNum)return false;
    return true;
  });
  var agg={};
  rows.forEach(function(r){
    var key=vista==='mes'?r.chofer:vista==='sem'?(r.chofer+'|'+r.semana):(r.chofer+'|'+r.fecha);
    if(!agg[key])agg[key]={chofer:r.chofer,fecha:r.fecha,semana:r.semana,bs:0,bi:0};
    agg[key].bs+=r.b_sal; agg[key].bi+=r.b_ing;
  });
  var tot_bs=0,tot_bi=0;
  var tbl=Object.values(agg).sort(function(a,b){return a.chofer.localeCompare(b.chofer)||(a.fecha<b.fecha?-1:1);}).map(function(r){
    tot_bs+=r.bs; tot_bi+=r.bi;
    var pct=r.bs>0?r.bi/r.bs:0;
    var est=pct>=0.9?BD('bg','Bien'):pct>=0.7?BD('by','Regular'):BD('br','Bajo');
    var label=vista==='dia'?fmtFecha(r.fecha):vista==='sem'?'Sem '+r.semana:'';
    return '<tr><td><strong>'+r.chofer+'</strong></td><td>'+label+'</td><td>'+r.semana+'</td>'+
      '<td style="text-align:right">'+r.bs+'</td><td style="text-align:right">'+r.bi+'</td>'+
      '<td>'+PR(pct,'#34d399',1)+' '+P(pct)+'</td><td>'+est+'</td></tr>';
  }).join('');
  document.getElementById('cart-tbody').innerHTML=tbl||'<tr><td colspan="7" class="empty">Sin datos de cartones</td></tr>';
  var pctT=tot_bs>0?tot_bi/tot_bs:0;
  document.getElementById('cart-kpis').innerHTML=
    KPI(tot_bs,'B.E. Salida','#e2e8f0')+
    KPI(tot_bi,'B.E. Retorno','#e2e8f0')+
    KPI(P(pctT),'% Retorno',pctT>=0.9?'#34d399':pctT>=0.7?'#fb923c':'#ef4444');
}

// \u2500\u2500 RECHAZOS \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
function initRej(){
  var pSel=document.getElementById('rej-prov-f');
  if(pSel){
    pSel.innerHTML='<option value="">Todos los proveedores</option>'+
      D_PROV.map(function(p){return '<option value="'+p.prov+'">'+p.prov+'</option>';}).join('');
    pSel.onchange=renderRejAll;
  }
  var chSel=document.getElementById('rej-ch-f');
  if(chSel&&chSel.options.length<=1){
    D_CHS.forEach(function(c){chSel.innerHTML+='<option value="'+c+'">'+c+'</option>';});
  }
  renderRejAll();
}

function renderRejAll(){
  var selProv=(document.getElementById('rej-prov-f')||{}).value||'';
  var selCh=(document.getElementById('rej-ch-f')||{}).value||'';
  var pm=selProv?D_PROV.filter(function(p){return p.prov===selProv;}):D_PROV;
  var vT=pm.reduce(function(s,p){return s+p.venta;},0);
  var rT=pm.reduce(function(s,p){return s+p.rec;},0);
  var fT=pm.reduce(function(s,p){return s+p.fac;},0);
  var nT=pm.reduce(function(s,p){return s+p.no_e;},0);
  var eT=fT>0?fT/(fT+nT):0;
  var tonTotal=(pm.reduce(function(s,p){return s+(p.kg||0);},0)/1000).toFixed(1);

  document.getElementById('rej-kpis').innerHTML=
    KPI('$'+F(vT),'Venta Neta','#34d399')+
    KPI(tonTotal+' tn','Toneladas','#3b82f6')+
    KPI('$'+F(rT),'Rechazo ($)','#ef4444')+
    KPI(P2(vT>0?rT/vT:0),'% Rechazo',(vT>0&&rT/vT>.03)?'#ef4444':'#fb923c')+
    KPI(String(fT),'Pedidos Facturados','#e2e8f0')+
    KPI(String(nT),'No Entregados',nT>0?'#ef4444':'#34d399')+
    KPI(P(eT),'Efectividad',eT<0.95?'#ef4444':'#34d399')+
    KPI(String(D_REINC.length),'Reincidentes','#fb923c');

  document.getElementById('rej-prov-tb').innerHTML=pm.length?
    pm.sort(function(a,b){return b.venta-a.venta;}).map(function(p){
      return '<tr><td><strong>'+p.prov+'</strong></td>'+
        '<td style="text-align:right">$'+F(p.venta)+'</td>'+
        '<td style="text-align:right;color:#ef4444">$'+F(p.rec)+'</td>'+
        '<td>'+PR(p.rec_pct,'#ef4444',0.05)+' '+P2(p.rec_pct)+'</td>'+
        '<td style="text-align:right;color:#fb923c">$'+F(p.cam)+'</td>'+
        '<td>'+P2(p.cam_pct)+'</td>'+
        '<td style="text-align:right">'+p.fac+'</td>'+
        '<td style="text-align:right;color:'+(p.no_e>0?'#ef4444':'#34d399')+'">'+p.no_e+'</td>'+
        '<td>'+P(p.efect)+'</td></tr>';
    }).join(''):'<tr><td colspan="9" class="empty">Sin datos</td></tr>';

  var mData=(selProv && window.D_MOTIVO_PROV && D_MOTIVO_PROV[selProv])?D_MOTIVO_PROV[selProv]:D_MOTIVO;
  var totImp=mData.reduce(function(s,m){return s+m.imp;},0);
  document.getElementById('rej-mot-tb').innerHTML=mData.length?
    mData.map(function(m,idx){
      var pct=totImp>0?m.imp/totImp:0;
      var colors=['#ef4444','#f97316','#f59e0b','#84cc16','#22d3ee','#818cf8','#e879f9','#fb7185','#94a3b8'];
      var col=colors[idx%colors.length];
      var barW=Math.round(pct*100);
      return '<tr>'+
        '<td><div style="display:flex;align-items:center;gap:8px">'+
          '<div style="width:10px;height:10px;border-radius:50%;background:'+col+';flex-shrink:0"></div>'+
          '<strong>'+m.motivo+'</strong></div></td>'+
        '<td style="text-align:right;color:#ef4444;font-weight:700">$'+F(m.imp)+'</td>'+
        '<td style="text-align:right">'+F(m.uds)+' uds</td>'+
        '<td><div style="display:flex;align-items:center;gap:6px">'+
          '<div style="background:#1e2535;border-radius:4px;height:8px;width:100px;overflow:hidden">'+
            '<div style="height:100%;border-radius:4px;background:'+col+';width:'+barW+'%"></div>'+
          '</div>'+
          '<span style="font-size:.78rem;color:#94a3b8;min-width:35px">'+P(pct)+'</span>'+
        '</div></td></tr>';
    }).join(''):'<tr><td colspan="4" class="empty">Sin datos</td></tr>';

  // Rechazos por chofer con vista dia/semana/mes
  var vistaRej=(document.getElementById('rej-vista-ch')||{}).value||'mes';
  var chData=[];
  if(vistaRej==='mes'){
    Object.keys(D_CHPROV).forEach(function(ch){
      if(!chMatchTipo(ch))return;
      if(!selCh||ch===selCh){
        var cpList=(D_CHPROV[ch]||[]).filter(function(m){return !selProv||m.prov===selProv;});
        if(!cpList.length)return;
        var vv=0,rr=0,ff=0,nn=0;
        cpList.forEach(function(m){vv+=m.venta;rr+=m.rec;ff+=m.fac;nn+=m.no_e;});
        if(vv>0)chData.push({lbl:ch,vv:vv,rr:rr,ff:ff,nn:nn,pRec:vv>0?rr/vv:0,ef:ff>0?ff/(ff+nn):0});
      }
    });
  } else {
    var dAgg={};
    D_ROUTES.forEach(function(r){
      if(selCh&&r.ch!==selCh)return;
      var lbl=vistaRej==='sem'?('Sem '+getSemana(r.f)+' \u2014 '+r.ch):(fmtFecha(r.f)+' \u2014 '+r.ch);
      if(!dAgg[lbl])dAgg[lbl]={lbl:lbl,vv:0,rr:0,ff:r.n,nn:r.rej};
      dAgg[lbl].vv+=r.tot; dAgg[lbl].ff+=r.n; dAgg[lbl].nn+=r.rej;
    });
    Object.values(dAgg).forEach(function(r){
      r.pRec=0; r.rr=0; r.ef=r.ff>0?r.ff/(r.ff+r.nn):0;
      chData.push(r);
    });
    chData.sort(function(a,b){return a.lbl.localeCompare(b.lbl);});
  }
  if(!vistaRej||vistaRej==='mes') chData.sort(function(a,b){return b.rr-a.rr;});
  document.getElementById('rej-ch-tb').innerHTML=chData.length?
    chData.map(function(c){
      return '<tr><td><strong>'+c.lbl+'</strong></td>'+
        '<td style="text-align:right">$'+F(c.vv)+'</td>'+
        '<td style="text-align:right;color:#ef4444">$'+F(c.rr)+'</td>'+
        '<td>'+PR(c.pRec,'#ef4444',0.05)+' '+P2(c.pRec)+'</td>'+
        '<td>'+P(c.ef)+'</td></tr>';
    }).join(''):'<tr><td colspan="5" class="empty">Sin datos</td></tr>';

  var reinc=D_REINC.filter(function(r){
    if(selCh && r.choferes.indexOf(selCh)<0) return false;
    if(selProv && !(r.provs||[]).some(function(p){return p.prov===selProv;})) return false;
    return true;
  });
  document.getElementById('rej-reinc-tb').innerHTML=reinc.length?
    reinc.map(function(r,i){
      var provs=(r.provs||[]).map(function(p){
        return '<div style="font-size:.72rem;color:#94a3b8">'+p.prov.split(' ')[0]+': $'+F(p.imp)+'</div>';
      }).join('');
      return '<tr><td>'+(i+1)+'</td>'+
        '<td><strong>'+r.razon+'</strong></td>'+
        '<td style="color:#64748b">'+r.loc+'</td>'+
        '<td style="text-align:right;color:#ef4444;font-weight:700">'+r.n+'</td>'+
        '<td style="text-align:right">$'+F(r.imp)+'</td>'+
        '<td>'+provs+'</td>'+
        '<td style="font-size:.75rem;color:#94a3b8">'+(r.vendedor||'-')+'</td>'+
        '<td style="font-size:.75rem;color:#94a3b8">'+r.choferes+'</td>'+
        '<td style="font-size:.73rem;color:#64748b">'+r.fechas+'</td></tr>';
    }).join(''):'<tr><td colspan="8" class="empty">Sin reincidentes</td></tr>';
}

function rejTab(id,btn){
  document.querySelectorAll('.rtab').forEach(function(t){t.classList.remove('on');});
  document.querySelectorAll('.rp').forEach(function(p){p.style.display='none';});
  if(btn) btn.classList.add('on');
  var el=document.getElementById('rp-'+id);
  if(el) el.style.display='block';
  if(id==='conc') initConciliacion();
}

// \u2500\u2500 DEPOSITO \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
function renderDep(){initDep();}
function initDep(){
  var dep=D_DEP;
  var hasDep=dep.faltante.length||dep.sobrante.length||dep.roturas.length||dep.consumo.length||dep.vencido.length;
  // Populate proveedor filter
  var provSel=document.getElementById('dep-prov-f');
  if(provSel && provSel.options.length<=1){
    var allRows=dep.faltante.concat(dep.sobrante,dep.roturas,dep.consumo,dep.vencido);
    var provs=[...new Set(allRows.map(function(r){return r.prov;}))].sort().filter(Boolean);
    provs.forEach(function(p){provSel.innerHTML+='<option value="'+p+'">'+p+'</option>';});
  }
  // Compensaciones table
  var comps=dep.compensaciones||[];
  var compEl=document.getElementById('dep-comp-tb');
  if(compEl){
    compEl.innerHTML=comps.length?comps.map(function(c){
      var neto=c.tot_f+c.tot_s;
      return '<tr>'+
        '<td style="color:#ef4444">'+c.falt+'</td>'+
        '<td style="text-align:right;color:#ef4444">'+c.u_f+' uds / $'+F(Math.abs(c.tot_f))+'</td>'+
        '<td style="color:#34d399">'+c.sobr+'</td>'+
        '<td style="text-align:right;color:#34d399">'+c.u_s+' uds / $'+F(c.tot_s)+'</td>'+
        '<td style="text-align:right;color:'+(neto<0?'#ef4444':'#34d399')+'">$'+F(neto)+'</td></tr>';
    }).join(''):'<tr><td colspan="5" class="empty">Sin compensaciones detectadas</td></tr>';
  }
  var noteEl=document.getElementById('dep-note');
  if(!hasDep){
    if(noteEl) noteEl.textContent='Diferencias de Inventario \u2014 subi movimientos.xlsx para ver datos';
    return;
  }
  if(noteEl) noteEl.textContent='Diferencias de Inventario \u2014 '+D_PERIODO;
  var totFalt=dep.faltante.reduce(function(s,r){return s+r.tot;},0);
  var totSobr=dep.sobrante.reduce(function(s,r){return s+r.tot;},0);
  var totRot =dep.roturas.reduce(function(s,r){return s+r.tot;},0);
  var totCons=dep.consumo.reduce(function(s,r){return s+r.tot;},0);
  var totVenc=dep.vencido.reduce(function(s,r){return s+r.tot;},0);
  document.getElementById('dep-kpis').innerHTML=
    KPI('$'+F(totFalt-totSobr),'Merma Neta',(totFalt-totSobr)>0?'#ef4444':'#34d399')+
    KPI('$'+F(totRot),'Roturas',totRot>0?'#ef4444':'#94a3b8')+
    KPI('$'+F(totCons),'Consumo Interno',totCons>0?'#fb923c':'#94a3b8')+
    KPI('$'+F(totVenc),'Vencido',totVenc>0?'#ef4444':'#94a3b8');
  var selDepProv=(document.getElementById('dep-prov-f')||{}).value||'';
  function filterDep(rows){
    return selDepProv?rows.filter(function(r){return r.prov===selDepProv;}):rows;
  }
  function renderDepTb(id,rows){
    var el=document.getElementById(id);
    if(!el) return;
    var filtered=filterDep(rows);
    el.innerHTML=filtered.length?filtered.map(function(r){
      return '<tr><td>'+r.desc+'</td><td style="color:#64748b">'+r.prov+'</td>'+
        '<td style="text-align:right">'+r.u+'</td>'+
        '<td style="text-align:right">$'+F(r.cu)+'</td>'+
        '<td style="text-align:right;color:#ef4444">$'+F(r.tot)+'</td>'+
        '<td style="font-size:.72rem;color:#64748b">'+(r.fecha||'')+'</td></tr>';
    }).join(''):'<tr><td colspan="6" class="empty">Sin movimientos</td></tr>';
  }
  // Recalculate KPIs with filter
  var fFalt=filterDep(dep.faltante),fSobr=filterDep(dep.sobrante);
  var fRot=filterDep(dep.roturas),fCons=filterDep(dep.consumo),fVenc=filterDep(dep.vencido);
  var tFalt=fFalt.reduce(function(s,r){return s+r.tot;},0);
  var tSobr=fSobr.reduce(function(s,r){return s+r.tot;},0);
  var tRot =fRot.reduce(function(s,r){return s+r.tot;},0);
  var tCons=fCons.reduce(function(s,r){return s+r.tot;},0);
  var tVenc=fVenc.reduce(function(s,r){return s+r.tot;},0);
  // % CMV sobre venta del proveedor seleccionado (o total si no hay filtro)
  var ventaBase=selDepProv?
    (D_PROV.find(function(p){return p.prov===selDepProv;})||{}).venta||1 :
    D_KPIS.imp_venta||1;
  function pctCMV(v){return ventaBase>0?(' ('+((v/ventaBase)*100).toFixed(2)+'% CMV)'):''}
  document.getElementById('dep-kpis').innerHTML=
    KPI('$'+F(tFalt-tSobr)+pctCMV(Math.abs(tFalt-tSobr)),'Merma Neta',(tFalt-tSobr)>0?'#ef4444':'#34d399')+
    KPI('$'+F(tRot)+pctCMV(tRot),'Roturas',tRot>0?'#ef4444':'#94a3b8')+
    KPI('$'+F(tCons)+pctCMV(tCons),'Consumo Interno',tCons>0?'#fb923c':'#94a3b8')+
    KPI('$'+F(tVenc)+pctCMV(tVenc),'Vencido',tVenc>0?'#ef4444':'#94a3b8');
  renderDepTb('dep-falt-tb',dep.faltante);
  renderDepTb('dep-sobr-tb',dep.sobrante);
  renderDepTb('dep-rot-tb', dep.roturas);
  renderDepTb('dep-cons-tb',dep.consumo);
  renderDepTb('dep-venc-tb',dep.vencido);
}

// \u2500\u2500 VENTAS \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
function initVentas(){
  var pSel=document.getElementById('ven-prov');
  var cSel=document.getElementById('ven-ch');
  D_PROVS.forEach(function(p){pSel.innerHTML+='<option value="'+p+'">'+p+'</option>';});
  D_CHS.forEach(function(c){cSel.innerHTML+='<option value="'+c+'">'+c+'</option>';});
  renderVentas();
}
function renderVentas(){
  var selProv=document.getElementById('ven-prov').value;
  var selCh  =document.getElementById('ven-ch').value;
  var vista  =(document.getElementById('ven-vista')||{}).value||'mes';
  var pm=D_PROV.filter(function(p){return !selProv||p.prov===selProv;});
  var vT=pm.reduce(function(s,p){return s+p.venta;},0);
  var rT=pm.reduce(function(s,p){return s+p.rec;},0);
  var fT=pm.reduce(function(s,p){return s+p.fac;},0);
  var nT=pm.reduce(function(s,p){return s+p.no_e;},0);
  var eT=fT>0?fT/(fT+nT):0;
  document.getElementById('ven-kpis').innerHTML=
    KPI('$'+F(vT),'Venta Neta','#34d399')+
    KPI('$'+F(rT),'Rechazo ($)','#ef4444')+
    KPI(P2(vT>0?rT/vT:0),'% Rechazo',(vT>0&&rT/vT>.03)?'#ef4444':'#fb923c')+
    KPI(String(fT),'Pedidos Facturados','#e2e8f0')+
    KPI(String(nT),'No Entregados',nT>0?'#ef4444':'#34d399')+
    KPI(P(eT),'Efectividad',eT<0.95?'#ef4444':'#34d399');
  document.getElementById('ven-prov-tb').innerHTML=pm.length?
    pm.sort(function(a,b){return b.venta-a.venta;}).map(function(p){
      return '<tr><td><strong>'+p.prov+'</strong></td>'+
        '<td style="text-align:right">$'+F(p.venta)+'</td>'+
        '<td style="text-align:right;color:#ef4444">$'+F(p.rec)+'</td>'+
        '<td>'+P2(p.rec_pct)+'</td>'+
        '<td>'+P(p.efect)+'</td></tr>';
    }).join(''):'<tr><td colspan="5" class="empty">Sin datos</td></tr>';
  var chRows=[];
  if(vista==='mes'){
    Object.keys(D_CHPROV).forEach(function(ch){
      if(selCh&&ch!==selCh)return;
      if(!chMatchTipo(ch))return;
      var cpList=(D_CHPROV[ch]||[]).filter(function(m){return !selProv||m.prov===selProv;});
      if(!cpList.length)return;
      var vv=0,rr=0,ff=0,nn=0;
      cpList.forEach(function(m){vv+=m.venta;rr+=m.rec;ff+=m.fac;nn+=m.no_e;});
      chRows.push({lbl:ch,vv:vv,rr:rr,ff:ff,nn:nn,ef:ff>0?ff/(ff+nn):0,pRec:vv>0?rr/vv:0});
    });
  } else {
    var diaAgg={};
    D_ROUTES.forEach(function(r){
      if(selCh&&r.ch!==selCh)return;
      var key=vista==='sem'?('Sem '+getSemana(r.f)+' '+r.ch):(fmtFecha(r.f)+' '+r.ch);
      if(!diaAgg[key])diaAgg[key]={lbl:key,vv:0,rr:0,ff:0,nn:0};
      diaAgg[key].vv+=r.tot; diaAgg[key].nn+=r.rej; diaAgg[key].ff+=r.n;
    });
    Object.values(diaAgg).forEach(function(r){
      r.ef=r.ff>0?r.ff/(r.ff+r.nn):0; r.pRec=0; r.rr=0;
      chRows.push(r);
    });
    chRows.sort(function(a,b){return a.lbl.localeCompare(b.lbl);});
  }
  document.getElementById('ven-ch-tb').innerHTML=chRows.length?
    chRows.map(function(r){
      return '<tr><td><strong>'+r.lbl+'</strong></td>'+
        '<td style="text-align:right">$'+F(r.vv)+'</td>'+
        '<td style="text-align:right;color:#ef4444">$'+F(r.rr)+'</td>'+
        '<td>'+P2(r.pRec)+'</td>'+
        '<td>'+P(r.ef)+'</td></tr>';
    }).join(''):'<tr><td colspan="5" class="empty">Sin datos</td></tr>';
}
function getSemana(dateStr){
  if(!dateStr)return 0;
  var d=new Date(dateStr); var jan1=new Date(d.getFullYear(),0,1);
  return Math.ceil(((d-jan1)/86400000+jan1.getDay()+1)/7);
}

// \u2500\u2500 HOJA DE RUTA \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
var fRoutes=[], selRep=null;
function initRuta(){
  var fechas=[...new Set(D_ROUTES.map(function(r){return r.f;}))].sort();
  var cams  =[...new Set(D_ROUTES.map(function(r){return r.cam;}))].sort(function(a,b){return a-b;});
  var fSel=document.getElementById('ruta-fecha');
  var cSel=document.getElementById('ruta-cam');
  var chSel=document.getElementById('ruta-ch');
  fechas.forEach(function(f){fSel.innerHTML+='<option value="'+f+'">'+fmtFecha(f)+'</option>';});
  D_CHS.forEach(function(c){chSel.innerHTML+='<option value="'+c+'">'+c+'</option>';});
  cams.forEach(function(c){cSel.innerHTML+='<option value="'+c+'">Cam '+c+'</option>';});
  filtRuta();
}
function filtRuta(){
  var fFec=document.getElementById('ruta-fecha').value;
  var fCh =document.getElementById('ruta-ch').value;
  var fCam=document.getElementById('ruta-cam').value;
  var fQ  =(document.getElementById('ruta-q').value||'').toLowerCase();
  fRoutes=D_ROUTES.filter(function(r){
    if(fFec&&r.f!==fFec)return false;
    if(fCh&&r.ch!==fCh)return false;
    if(fCam&&String(r.cam)!==String(fCam))return false;
    if(!chMatchTipo(r.ch))return false;
    if(fQ){
      var cls=D_CLI[String(r.rep)]||[];
      return cls.some(function(c){return c[1].toLowerCase().includes(fQ)||c[2].toLowerCase().includes(fQ);});
    }
    return true;
  });
  renderSB();
  if(selRep&&fRoutes.find(function(r){return r.rep===selRep;}))selR(selRep);
  else{selRep=null;document.getElementById('rdet').innerHTML='<div style="color:#475569;padding:20px">Seleccion\u00e1 un reparto</div>';}
}
function renderSB(){
  var el=document.getElementById('rsl');
  if(!fRoutes.length){el.innerHTML='<div class="empty">Sin repartos.</div>';return;}
  var tot=0; fRoutes.forEach(function(r){tot+=r.tot;});
  el.innerHTML='<div style="font-size:.75rem;color:#64748b;padding:4px 0 8px">'+fRoutes.length+' repartos \u2014 $'+F(tot)+'</div>'+
  fRoutes.map(function(r){
    var on=selRep===r.rep;
    var cls2=D_CLI[String(r.rep)]||[];
    var rejCount=cls2.filter(function(c){return c[7]===1;}).length;
    var rejTag=rejCount?'<span style="color:#ef4444">\u26a0 '+rejCount+' rej total</span>':'';
    var totProv=r.pep+r.mol+r.sof+r.oth||1;
    var bar='<div class="provbar">'+
      (r.pep?'<div style="flex:'+(r.pep/totProv)+';background:#3b82f6"></div>':'')+
      (r.mol?'<div style="flex:'+(r.mol/totProv)+';background:#8b5cf6"></div>':'')+
      (r.sof?'<div style="flex:'+(r.sof/totProv)+';background:#10b981"></div>':'')+
      (r.oth?'<div style="flex:'+(r.oth/totProv)+';background:#475569"></div>':'')+
    '</div>';
    return '<div class="ri'+(on?' on':'"')+'" onclick="selR('+r.rep+')">'+
      '<div class="ri-top"><span class="ri-ch">'+r.ch+'</span><span class="ri-rep">N\u00b0 '+r.rep+'</span></div>'+
      '<div class="ri-meta">'+
        '<span>\ud83d\udcc5 '+fmtFecha(r.f)+'</span>'+
        '<span>\u26f8 Cam '+r.cam+'</span>'+
        '<span>\ud83d\udc65 '+r.n+' cli</span>'+
        (r.kg?'<span>'+r.kg.toFixed(1)+' kg</span>':'')+
        rejTag+
      '</div>'+
      '<div style="font-size:.8rem;font-weight:700;color:#e2e8f0;margin-top:4px">$'+F(r.tot)+'</div>'+
      bar+'</div>';
  }).join('');
}
function selR(rep){
  selRep=rep;
  renderSB();
  var r=D_ROUTES.find(function(x){return x.rep===rep;});
  var cls=D_CLI[String(rep)]||[];
  if(!r){document.getElementById('rdet').innerHTML='<div class="empty">Sin datos</div>';return;}
  var totProv=r.pep+r.mol+r.sof+r.oth||1;
  var fmap={0:{bd:'bg',lbl:'Entregado'},1:{bd:'br',lbl:'Rech. Total'},2:{bd:'by',lbl:'Rech. Parcial'},3:{bd:'bp',lbl:'Cambio'}};
  var html='<div style="margin-bottom:12px">'+
    '<div style="font-weight:800;font-size:1rem;margin-bottom:4px">Reparto N\u00b0 '+r.rep+' \u2014 '+r.ch+'</div>'+
    '<div style="font-size:.78rem;color:#94a3b8">\ud83d\udcc5 '+fmtFecha(r.f)+' &nbsp; \u26f8 Cami\u00f3n '+r.cam+'</div>'+
    '<div style="display:flex;gap:10px;margin-top:10px;flex-wrap:wrap">'+
      '<div class="kpi" style="min-width:80px"><div class="kpi-v" style="color:#34d399">'+cls.filter(function(c){return c[7]===0;}).length+'</div><div class="kpi-l">Entregados</div></div>'+
      '<div class="kpi" style="min-width:80px"><div class="kpi-v" style="color:#ef4444">'+cls.filter(function(c){return c[7]===1;}).length+'</div><div class="kpi-l">Rej. Total</div></div>'+
      '<div class="kpi" style="min-width:80px"><div class="kpi-v" style="color:#fb923c">'+cls.filter(function(c){return c[7]===2;}).length+'</div><div class="kpi-l">Rej. Parcial</div></div>'+
      '<div class="kpi" style="min-width:80px"><div class="kpi-v" style="color:#818cf8">'+cls.filter(function(c){return c[7]===3;}).length+'</div><div class="kpi-l">Cambios</div></div>'+
      '<div class="kpi" style="min-width:80px"><div class="kpi-v">'+cls.length+'</div><div class="kpi-l">Total</div></div>'+
      '<div class="kpi" style="min-width:100px"><div class="kpi-v" style="color:#e2e8f0">$'+F(r.tot)+'</div><div class="kpi-l">Total $</div></div>'+
      (r.kg?'<div class="kpi" style="min-width:80px"><div class="kpi-v" style="color:#64748b">'+r.kg.toFixed(1)+'</div><div class="kpi-l">Kg</div></div>':'')+
    '</div>'+
    '<div style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap">'+
      (r.pep?'<div class="kpi" style="min-width:90px;border-color:#3b82f6"><div class="kpi-v" style="color:#3b82f6;font-size:1rem">$'+F(r.pep)+'</div><div class="kpi-l">Pepsico</div></div>':'')+
      (r.mol?'<div class="kpi" style="min-width:90px;border-color:#8b5cf6"><div class="kpi-v" style="color:#8b5cf6;font-size:1rem">$'+F(r.mol)+'</div><div class="kpi-l">Molinos</div></div>':'')+
      (r.sof?'<div class="kpi" style="min-width:90px;border-color:#10b981"><div class="kpi-v" style="color:#10b981;font-size:1rem">$'+F(r.sof)+'</div><div class="kpi-l">Softys</div></div>':'')+
      (r.oth?'<div class="kpi" style="min-width:90px;border-color:#475569"><div class="kpi-v" style="color:#94a3b8;font-size:1rem">$'+F(r.oth)+'</div><div class="kpi-l">Otros</div></div>':'')+
    '</div>'+
    '<div class="provbar" style="height:8px;margin-top:8px;border-radius:4px">'+
      (r.pep?'<div style="flex:'+(r.pep/totProv)+';background:#3b82f6"></div>':'')+
      (r.mol?'<div style="flex:'+(r.mol/totProv)+';background:#8b5cf6"></div>':'')+
      (r.sof?'<div style="flex:'+(r.sof/totProv)+';background:#10b981"></div>':'')+
      (r.oth?'<div style="flex:'+(r.oth/totProv)+';background:#475569"></div>':'')+
    '</div>'+
    '</div>';
  html+=cls.map(function(c){
    var fm=fmap[c[7]]||fmap[0];
    return '<div class="cli-row">'+
      '<div><div class="cli-name">'+c[1]+' <span style="font-size:.72rem;color:#64748b">#'+c[0]+'</span></div>'+
      '<div class="cli-addr">'+c[2]+(c[3]?' \u2014 '+c[3]:'')+'</div>'+
      '<div class="cli-meta">'+BD(fm.bd,fm.lbl)+(c[4]?'<span style="font-size:.72rem;color:#64748b">'+c[4]+'</span>':'')+'</div>'+
      '</div>'+
      '<div class="cli-right">'+
        (c[5]?'<div style="font-weight:700">$'+F(c[5])+'</div>':'')+
        (c[6]?'<div style="font-size:.75rem;color:#94a3b8">'+c[6]+' uds</div>':'')+
      '</div></div>';
  }).join('');
  document.getElementById('rdet').innerHTML=html;
}

// \u2500\u2500 CONCILIACION \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
var pwaRows=[];
function initConciliacion(){
  var cont=document.getElementById('conc-content');
  var load=document.getElementById('conc-loading');
  if(!cont)return;
  load.style.display='none'; cont.style.display='block';
  pwaRows=window.D_APP||[];
  renderConciliacion();
}
function loadPWA(){initConciliacion();}

function renderConciliacion(){
  var k=window.D_CONC?D_CONC.kpis:{};
  var appGes =window.D_CONC?D_CONC.app_ges:[];
  var appOnly=window.D_CONC?D_CONC.app_only:[];
  var gesOnly=window.D_CONC?D_CONC.ges_only:[];

  // KPIs
  document.getElementById('conc-kpis').innerHTML=
    KPI(String(k.total_app||0),'Rechazos en App','#e2e8f0')+
    KPI(String(k.app_ges||0)+' / $'+F(k.imp_app_ges||0),'\ud83d\udd34 App+Gescom (gestion\u00f3 y se perdi\u00f3)','#ef4444')+
    KPI(String(k.app_only||0),'\ud83d\udfe2 App sin Gescom (se salv\u00f3)','#34d399')+
    KPI(String(k.ges_only||0)+' / $'+F(k.imp_ges_only||0),'\u26ab Gescom sin App (sin gesti\u00f3n)','#64748b')+
    KPI(String(k.with_resp||0),'Vendedores con respuesta','#3b82f6')+
    KPI(String(k.sin_resp||0),'Vendedores sin respuesta','#fb923c')+
    KPI((k.pct_saved||0)+'%','% Gestiones salvadas','#34d399');

  // Ranking choferes (por importe sin gestion)
  var chRank={};
  gesOnly.forEach(function(r){
    if(!chRank[r.chofer])chRank[r.chofer]={ch:r.chofer,n:0,imp:0};
    chRank[r.chofer].n++; chRank[r.chofer].imp+=r.imp;
  });
  var rankCh=Object.values(chRank).sort(function(a,b){return b.imp-a.imp;}).slice(0,10);
  document.getElementById('conc-rank-ch').innerHTML=rankCh.length?
    rankCh.map(function(r,i){
      var urg=r.n>5?BD('br','Urgente'):r.n>2?BD('by','Atenci\u00f3n'):BD('bp','Revisar');
      return '<tr><td>'+(i+1)+'</td><td><strong>'+r.ch+'</strong></td>'+
        '<td style="text-align:right;color:#ef4444">'+r.n+'</td>'+
        '<td style="text-align:right">$'+F(r.imp)+'</td>'+
        '<td>'+urg+'</td></tr>';
    }).join(''):'<tr><td colspan="5" class="empty">Sin datos</td></tr>';

  // Ranking vendedores (sin respuesta)
  var vRank={};
  appGes.forEach(function(r){
    var v=r.vendedor||'Sin vendedor';
    if(!vRank[v])vRank[v]={v:v,total:0,sin_resp:0,imp:0};
    vRank[v].total++; vRank[v].imp+=r.imp;
    if(!r.resp)vRank[v].sin_resp++;
  });
  var rankV=Object.values(vRank).sort(function(a,b){return b.sin_resp-a.sin_resp;}).slice(0,10);
  document.getElementById('conc-rank-vend').innerHTML=rankV.length?
    rankV.map(function(r,i){
      var pctSin=r.total>0?Math.round(r.sin_resp/r.total*100):0;
      var col=pctSin>70?'#ef4444':pctSin>40?'#fb923c':'#34d399';
      return '<tr><td>'+(i+1)+'</td><td><strong>'+r.v+'</strong></td>'+
        '<td style="text-align:right">'+r.total+'</td>'+
        '<td style="text-align:right;color:#ef4444">'+r.sin_resp+'</td>'+
        '<td><span style="color:'+col+';font-weight:700">'+pctSin+'%</span></td>'+
        '<td style="text-align:right">$'+F(r.imp)+'</td></tr>';
    }).join(''):'<tr><td colspan="6" class="empty">Sin datos</td></tr>';

  // Filter
  var fCh =(document.getElementById('conc-f-ch')||{}).value||'';
  var fFec=(document.getElementById('conc-f-fecha')||{}).value||'';
  var fOrd=(document.getElementById('conc-f-ord')||{}).value||'fecha';

  var allRows=appGes.map(function(r){return {type:'ag',data:r};})
                    .concat(gesOnly.map(function(r){return {type:'go',data:r};}));
  allRows=allRows.filter(function(x){
    var r=x.data;
    if(fCh&&r.chofer!==fCh)return false;
    if(fFec&&r.fecha!==fFec)return false;
    return true;
  });
  allRows.sort(function(a,b){
    var ra=a.data,rb=b.data;
    if(fOrd==='imp')return (rb.imp||0)-(ra.imp||0);
    if(fOrd==='chofer')return ra.chofer.localeCompare(rb.chofer);
    return ra.fecha<rb.fecha?-1:ra.fecha>rb.fecha?1:0;
  });

  // Populate filter selects
  var chSel=document.getElementById('conc-f-ch');
  var fSel=document.getElementById('conc-f-fecha');
  if(chSel && chSel.options.length<=1){
    var allChs=[...new Set(appGes.concat(gesOnly).map(function(r){return r.chofer;}))].sort();
    allChs.forEach(function(c){chSel.innerHTML+='<option value="'+c+'">'+c+'</option>';});
  }
  if(fSel && fSel.options.length<=1){
    var allFecs=[...new Set(appGes.concat(gesOnly).map(function(r){return r.fecha;}))].sort();
    allFecs.forEach(function(f){fSel.innerHTML+='<option value="'+f+'">'+fmtFecha(f)+'</option>';});
  }
  document.getElementById('conc-tbody').innerHTML=allRows.length?
    allRows.map(function(x){
      var r=x.data; var isGO=x.type==='go';
      var est=isGO?BD('br','Sin App'):(r.resp?BD('bg','Con respuesta'):BD('br','Sin respuesta'));
      var tipo=isGO?BD('by','Sin gesti\u00f3n'):BD('br','App+Gescom');
      return '<tr>'+
        '<td>'+fmtFecha(r.fecha)+'</td>'+
        '<td><strong>'+r.chofer+'</strong></td>'+
        '<td style="font-size:.75rem">'+(r.razon||r.clientes||'')+'</td>'+
        '<td>'+tipo+'</td>'+
        '<td>'+est+'</td>'+
        '<td style="font-size:.75rem;color:#94a3b8">'+(r.resp||'-')+'</td>'+
        '<td style="text-align:right;color:#ef4444">$'+F(r.imp)+'</td></tr>';
    }).join(''):'<tr><td colspan="7" class="empty">Sin datos</td></tr>';

  // Plan de accion
  document.getElementById('plan-tbody').innerHTML=rankCh.length?
    rankCh.map(function(r,i){
      var urg=r.n>5?BD('br','Urgente'):r.n>2?BD('by','Atenci\u00f3n'):BD('bp','Revisar');
      return '<tr><td>'+(i+1)+'</td><td><strong>'+r.ch+'</strong></td>'+
        '<td style="text-align:right;color:#ef4444">'+r.n+'</td>'+
        '<td style="text-align:right">$'+F(r.imp)+'</td>'+
        '<td>'+urg+'</td>'+
        '<td style="font-size:.75rem;color:#94a3b8">'+r.n+' rechazo'+(r.n>1?'s':'')+' sin documentar</td></tr>';
    }).join(''):'<tr><td colspan="6" class="empty">Sin alertas</td></tr>';
}
