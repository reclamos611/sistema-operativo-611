#!/usr/bin/env python3
"""
generar_dashboard.py - 611 Logistica Dashboard Operativo (simplificado)
Lee: venta_actual.xlsx, movimientos.xlsx (opcional), cartones.xlsx (opcional)
"""
import pandas as pd, json, re, os, sys, math
from datetime import datetime

print("=" * 60)
print("611 Logistica - Generador Dashboard Operativo")
print("=" * 60)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

def si(v,d=0):
    try: return d if (v is None or (isinstance(v,float) and math.isnan(v))) else int(v)
    except: return d

def sf(v,d=0.0):
    try: return d if (v is None or (isinstance(v,float) and math.isnan(v))) else float(v)
    except: return d

def find(name):
    for f in os.listdir(DATA_DIR):
        if f.lower().replace(" ","_") == name.lower() or f.lower() == name.lower():
            return os.path.join(DATA_DIR, f)
    kw = name.lower().split(".")[0].replace("_"," ")
    for f in sorted(os.listdir(DATA_DIR)):
        if f.endswith(".xlsx") and kw in f.lower():
            return os.path.join(DATA_DIR, f)
    return None

def make_chunks(var_name, data, chunk=8000):
    if isinstance(data, dict):
        stmts = [f'var {var_name}={{}};\n']
        buf, bsize = {}, 0
        for k,v in data.items():
            vj = json.dumps(v, ensure_ascii=True, separators=(',',':'))
            if bsize+len(vj)>chunk and buf:
                stmts.append(f'Object.assign({var_name},{json.dumps(buf,ensure_ascii=True,separators=(",",":"))});\n')
                buf, bsize = {}, 0
            buf[k]=v; bsize+=len(vj)
        if buf:
            stmts.append(f'Object.assign({var_name},{json.dumps(buf,ensure_ascii=True,separators=(",",":"))});\n')
    elif isinstance(data, list):
        stmts = [f'var {var_name}=[];\n']
        buf, bsize = [], 0
        for item in data:
            ij = json.dumps(item, ensure_ascii=True, separators=(',',':'))
            if bsize+len(ij)>chunk and buf:
                stmts.append(f'{var_name}={var_name}.concat({json.dumps(buf,ensure_ascii=True,separators=(",",":"))});\n')
                buf, bsize = [], 0
            buf.append(item); bsize+=len(ij)
        if buf:
            stmts.append(f'{var_name}={var_name}.concat({json.dumps(buf,ensure_ascii=True,separators=(",",":"))});\n')
    else:
        stmts = [f'var {var_name}={json.dumps(data,ensure_ascii=True,separators=(",",":"))};\n']
    return ''.join(stmts)

PEPSICO = 'Pepsico de Argentina SRL'
MOLINOS = 'MOLINOS RIO DE LA PLATA SA'
SOFTYS  = 'SOFTYS ARGENTINA SA'
MOTIVO_MAP = {1.0:'Cerrado',2.0:'No hizo pedido',3.0:'Sin Dinero',
              5.0:'Sin Stock',6.0:'Mal armado',7.0:'No esta el dueno',
              16.0:'Direccion incorrecta',18.0:'Zona peligrosa',
              25.0:'Error de preventa',10000.0:'Dev. administrativa'}

print("\nLeyendo archivos...")

# ── VENTA ACTUAL (requerido) ───────────────────────────────────────────────────
vc_path = find("venta_actual.xlsx")
if not vc_path:
    print("ERROR: no se encontro venta_actual.xlsx en /data/"); sys.exit(1)

vc = pd.read_excel(vc_path)
vc['Importe']   = pd.to_numeric(vc['Importe'],   errors='coerce').fillna(0)
vc['Cantidad']  = pd.to_numeric(vc['Cantidad'],  errors='coerce').fillna(0)
vc['tipo_venta']= vc['tipo_venta'].fillna('Venta') if 'tipo_venta' in vc.columns else 'Venta'
vc['chofer']    = vc['chofer'].fillna('Sin chofer').str.strip() if 'chofer' in vc.columns else 'Sin chofer'
vc['proveedor'] = vc['proveedor'].fillna('Sin proveedor').str.strip() if 'proveedor' in vc.columns else 'Sin proveedor'
vc['motivodev'] = pd.to_numeric(vc.get('motivodev'), errors='coerce')
vc['Fecha']     = pd.to_datetime(vc['Fecha'], errors='coerce')
vc['fecha_str'] = vc['Fecha'].dt.strftime('%Y-%m-%d')
vc['reparto']   = pd.to_numeric(vc.get('reparto'),  errors='coerce')
vc['camion']    = pd.to_numeric(vc.get('camion'),   errors='coerce').fillna(0)
if 'Comprobante' not in vc.columns: vc['Comprobante'] = ''
if 'Razon_Social' not in vc.columns: vc['Razon_Social'] = ''
if 'localidad'   not in vc.columns: vc['localidad']   = ''
if 'Direccion'   not in vc.columns: vc['Direccion']   = ''

mes  = int(vc['Fecha'].dt.month.mode()[0])
anio = int(vc['Fecha'].dt.year.mode()[0])
MESES = {1:'Enero',2:'Febrero',3:'Marzo',4:'Abril',5:'Mayo',6:'Junio',
         7:'Julio',8:'Agosto',9:'Septiembre',10:'Octubre',11:'Noviembre',12:'Diciembre'}
PERIODO = f"{MESES.get(mes,'?')} {anio}"
print(f"  Venta actual: {len(vc):,} filas  Periodo: {PERIODO}")

# ── RECHAZOS ───────────────────────────────────────────────────────────────────
dev = vc[vc['tipo_venta']=='Devolucion'].copy()
dev['motivo_desc'] = dev['motivodev'].map(MOTIVO_MAP).fillna('Otro')

# Efectividad global: neto cliente+fecha
cli_dia_global = vc.groupby(['Cliente','Fecha'])['Importe'].sum().reset_index()
padron_global  = len(cli_dia_global)
no_e_global    = int((cli_dia_global['Importe'] <= 0).sum())
fac_global     = padron_global - no_e_global

venta_tot = float(vc[vc['tipo_venta']=='Venta']['Importe'].sum())
all_dev_imp = float(vc[vc['tipo_venta']=='Devolucion']['Importe'].sum())
rej_kpis = {
    'imp_venta': round(venta_tot,0), 'imp_dev': round(abs(all_dev_imp),0),
    'pct_rechazo': round(abs(all_dev_imp)/venta_tot,4) if venta_tot else 0,
    'cam_imp': round(float(vc[vc['tipo_venta']=='Cambio']['Importe'].abs().sum()),0),
    'fac': fac_global, 'no_e': no_e_global,
    'efect': round(fac_global/padron_global,4) if padron_global else 0
}

bm = dev.groupby('motivo_desc').agg(lineas=('Importe','count'),uds=('Cantidad','sum'),isum=('Importe','sum')).reset_index()
bm['isum'] = bm['isum'].abs()
by_motivo = [{'motivo':r['motivo_desc'],'lineas':int(r['lineas']),'uds':int(abs(r['uds'])),'imp':round(float(r['isum']),0)}
             for _,r in bm.sort_values('isum',ascending=False).iterrows()]

bc = vc[vc['Comprobante'].isin(rej_comps)].groupby('chofer').agg(n=('Comprobante','nunique'),imp=('Importe','sum')).reset_index()
tot_ch = comp_cls.merge(vc[['Comprobante','chofer']].drop_duplicates(),on='Comprobante',how='left')
tot_ch = tot_ch[tot_ch['has_venta']].groupby('chofer').size().reset_index(name='total')
bc = bc.merge(tot_ch,on='chofer',how='left').fillna({'total':0})
bc['pct'] = bc.apply(lambda r: round(r['n']/(r['n']+r['total']),4) if (r['n']+r['total'])>0 else 0, axis=1)
by_chofer = [{'ch':r['chofer'],'n':int(r['n']),'tot':int(r['total']),'imp':round(float(abs(r['imp'])),0),'pct':float(r['pct'])}
             for _,r in bc.sort_values('n',ascending=False).iterrows()]

def prov_met(df_p):
    if df_p.empty: return None
    # Efectividad: neto por cliente+fecha. neto<=0 = no entregado
    cli_dia = df_p.groupby(['Cliente','Fecha'])['Importe'].sum().reset_index()
    padron = len(cli_dia)
    no_e   = int((cli_dia['Importe'] <= 0).sum())
    f      = padron - no_e
    # Rechazo $: TODAS las devoluciones
    v=float(df_p[df_p['tipo_venta']=='Venta']['Importe'].sum())
    r=float(df_p[df_p['tipo_venta']=='Devolucion']['Importe'].sum())
    c=float(df_p[df_p['tipo_venta']=='Cambio']['Importe'].abs().sum())
    return {'venta':round(v,0),'rec':round(abs(r),0),'cam':round(c,0),
            'rec_pct':round(abs(r)/v,4) if v else 0,'cam_pct':round(c/v,4) if v else 0,
            'fac':f,'no_e':no_e,'efect':round(f/padron,4) if padron else 0}

prov_metrics_list = []
chofer_prov_map   = {}
for p in sorted(vc['proveedor'].dropna().str.strip().unique()):
    m = prov_met(vc[vc['proveedor'].str.strip()==p])
    if m and m['venta']>0: prov_metrics_list.append({'prov':str(p),**m})
for ch, df_ch in vc.groupby('chofer'):
    chofer_prov_map[str(ch).strip()] = []
    for p, df_cp in df_ch.groupby('proveedor'):
        m = prov_met(df_cp.reset_index(drop=True))
        if m and m['venta']>0: chofer_prov_map[str(ch).strip()].append({'prov':str(p).strip(),**m})

print(f"  Rechazos: {len(rej_comps)} comp. rechazados, {len(by_motivo)} motivos")

# ── VENTAS / RUTAS ─────────────────────────────────────────────────────────────
route_index = []; client_map = {}
for rep_id, grp in vc.groupby('reparto'):
    if pd.isna(rep_id): continue
    ch   = str(grp['chofer'].iloc[0]).strip()
    fec  = grp['fecha_str'].iloc[0]
    cam  = si(grp['camion'].iloc[0])
    vgrp = grp[grp['tipo_venta']=='Venta']
    tot  = float(vgrp['Importe'].sum())
    pep  = float(vgrp[vgrp['proveedor']==PEPSICO]['Importe'].sum())
    mol  = float(vgrp[vgrp['proveedor']==MOLINOS]['Importe'].sum())
    sof  = float(vgrp[vgrp['proveedor']==SOFTYS]['Importe'].sum())
    clientes = []
    for cli_id, cg in grp.groupby('Cliente'):
        tipos = list(cg['tipo_venta'].fillna('Venta'))
        rt=all(t=='Devolucion' for t in tipos); dv='Devolucion' in tipos and not rt; cm2='Cambio' in tipos
        imp=int(cg[cg['tipo_venta']=='Venta']['Importe'].sum())
        cnt=int(cg[cg['tipo_venta']=='Venta']['Cantidad'].sum())
        raz=str(cg['Razon_Social'].iloc[0] or '')[:40]
        dir2=str(cg['Direccion'].iloc[0] or '')[:40]
        loc=str(cg['localidad'].iloc[0] or '')[:22]
        cmp=str(cg['Comprobante'].iloc[0] or '')
        fl=1 if rt else(2 if dv else(3 if cm2 else 0))
        clientes.append([si(cli_id),raz,dir2,loc,cmp,imp,cnt,fl])
    rej=sum(1 for c in clientes if c[7]>=1)
    route_index.append({'rep':si(rep_id),'ch':ch,'f':str(fec),'cam':cam,
        'n':len(clientes),'tot':round(tot,0),'rej':rej,
        'pep':round(pep,0),'mol':round(mol,0),'sof':round(float(vgrp[vgrp['proveedor']==SOFTYS]['Importe'].sum()),0),
        'oth':round(tot-pep-mol-float(vgrp[vgrp['proveedor']==SOFTYS]['Importe'].sum()),0)})
    client_map[str(si(rep_id))]=clientes
route_index.sort(key=lambda x:(x['f'],x['ch']))
print(f"  Rutas: {len(route_index)} repartos")

venta_list=[]
for ch, df_ch in vc.groupby('chofer'):
    bol=df_ch.groupby('Comprobante')['tipo_venta'].apply(list).reset_index()
    bol['ne']=bol['tipo_venta'].apply(lambda ts:all(t=='Devolucion' for t in ts))
    e=int((~bol['ne']).sum()); ne=int(bol['ne'].sum())
    dev_ch=df_ch[df_ch['tipo_venta']=='Devolucion']
    rp=dev_ch.groupby('proveedor').agg(n=('Importe','count'),imp=('Importe','sum')).reset_index()
    cam_ch=df_ch[df_ch['tipo_venta']=='Cambio']
    ip=cam_ch.groupby('proveedor').agg(n=('Importe','count'),imp=('Importe','sum')).reset_index()
    venta_list.append({'ch':str(ch),'e':e,'ne':ne,
        'rp':{r['proveedor']:{'n':int(r['n']),'imp':round(float(r['imp']),0)} for _,r in rp.iterrows()},
        'ip':{r['proveedor']:{'n':int(r['n']),'imp':round(float(r['imp']),0)} for _,r in ip.iterrows()}})

# ── CARTONES (opcional) ────────────────────────────────────────────────────────
cart_records = []
cart_path = find("cartones.xlsx")
if cart_path:
    cart = pd.read_excel(cart_path)
    if 'FechaSalidaCamion' in cart.columns:
        cart['FechaSalidaCamion'] = pd.to_datetime(cart['FechaSalidaCamion'])
        cart['fecha_str'] = cart['FechaSalidaCamion'].dt.strftime('%Y-%m-%d')
        cart['semana']    = cart['FechaSalidaCamion'].dt.isocalendar().week.astype(int)
        if 'cajasret' in cart.columns: cart=cart[cart['cajasret']>0].copy()
        for _,r in cart.iterrows():
            bs=si(r.get('cajasbienret',0)); bi=si(r.get('cajasbienretdev',0))
            cart_records.append({
                'chofer':str(r.get('razon_social','')).strip(),
                'fecha':str(r['fecha_str']),'semana':int(r['semana']),
                'b_sal':bs,'b_ing':bi,'retorno':round(bi/bs,4) if bs>0 else 0
            })
    print(f"  Cartones: {len(cart_records)} registros")
else:
    print("  Cartones: no encontrado (opcional)")

# ── MOVIMIENTOS / DEPOSITO (opcional) ──────────────────────────────────────────
dep_data = {'faltante':[],'sobrante':[],'roturas':[],'consumo':[]}
mov_path = find("movimientos.xlsx")
if mov_path:
    mov = pd.read_excel(mov_path)
    mov['cu'] = pd.to_numeric(mov['costo'], errors='coerce').fillna(0)
    art_prov = dict(zip(vc['Art'].dropna().astype(int), vc['proveedor']))
    def get_prov(code):
        try: return art_prov.get(int(code),'Sin proveedor')
        except: return 'Sin proveedor'

    # Fecha range
    fecha_col = next((c for c in ['fecha','Fecha','stockmov_fecha'] if c in mov.columns), None)
    periodo_label = ''
    if fecha_col:
        fechas = pd.to_datetime(mov[fecha_col], errors='coerce').dropna()
        if len(fechas): periodo_label = f"{fechas.min().strftime('%d/%m')}-{fechas.max().strftime('%d/%m/%Y')}"

    def mov_rows(df_m, tipo_col='tipo'):
        rows=[]
        for _,r in df_m.iterrows():
            u=abs(sf(r.get('stockmov_cantidad',r.get('cantidad',0))))
            cu=sf(r.get('costo',0))
            rows.append({'desc':str(r.get('descripcion',''))[:50],
                          'prov':get_prov(r.get('articulo_codigo',r.get('codigo',0))),
                          'u':int(u),'cu':round(cu,2),'tot':round(u*cu,2),'fecha':periodo_label})
        return rows

    tipo_col = 'stockmov_tipo' if 'stockmov_tipo' in mov.columns else 'tipo'
    mot_col  = 'stockmov_motivo' if 'stockmov_motivo' in mov.columns else None

    # Roturas: TRA + motivo rotura
    if mot_col:
        rot=mov[(mov[tipo_col]=='TRA')&mov[mot_col].str.lower().str.contains('rotura',na=False)&(mov['stockmov_cantidad']<0)]
        dep_data['roturas']=mov_rows(rot)
        # Consumo: TRA + motivo consumo
        cons=mov[(mov[tipo_col]=='TRA')&mov[mot_col].str.lower().str.contains('consumo',na=False)&(mov['stockmov_cantidad']<0)]
        dep_data['consumo']=mov_rows(cons)

    # Merma: CON neteada
    if 'CON' in mov[tipo_col].values:
        con=mov[mov[tipo_col]=='CON'].copy()
        con['prov']=con['articulo_codigo'].apply(get_prov)
        con_net=con.groupby(['articulo_codigo','descripcion','prov']).agg(
            neto=('stockmov_cantidad','sum'),cu=('costo','first')).reset_index()
        con_net=con_net[con_net['cu']>0]
        con_neg=con_net[con_net['neto']<0].copy(); con_neg['u']=con_neg['neto'].abs()
        con_pos=con_net[con_net['neto']>0].copy(); con_pos['u']=con_pos['neto']
        dep_data['faltante']=[{'desc':str(r['descripcion'])[:50],'prov':str(r['prov']),
            'u':int(r['u']),'cu':round(float(r['cu']),2),'tot':round(float(r['u']*r['cu']),2),'fecha':periodo_label}
            for _,r in con_neg.iterrows()]
        dep_data['sobrante']=[{'desc':str(r['descripcion'])[:50],'prov':str(r['prov']),
            'u':int(r['u']),'cu':round(float(r['cu']),2),'tot':round(float(r['u']*r['cu']),2),'fecha':periodo_label}
            for _,r in con_pos.iterrows()]

    print(f"  Deposito: {len(dep_data['faltante'])} falt, {len(dep_data['sobrante'])} sobr, {len(dep_data['roturas'])} rot, {len(dep_data['consumo'])} cons")
else:
    print("  Movimientos: no encontrado (opcional)")

# ── SERIALIZAR E INYECTAR ──────────────────────────────────────────────────────
print("\nSerializando...")

# Reincidentes
comp_cls2 = vc.groupby('Comprobante')['tipo_venta'].apply(list).reset_index()
comp_cls2['all_dev'] = comp_cls2['tipo_venta'].apply(lambda ts: all(t=='Devolucion' for t in ts))
rej_comps2 = set(comp_cls2[comp_cls2['all_dev']]['Comprobante'])
rej_cli = (vc[vc['Comprobante'].isin(rej_comps2)]
           .groupby('Cliente')
           .agg(n=('Comprobante','nunique'),
                razon=('Razon_Social','first'),
                loc=('localidad','first'),
                imp=('Importe','sum'),
                choferes=('chofer', lambda x: ', '.join(sorted(set(str(v) for v in x))[:3])),
                fechas=('fecha_str', lambda x: ', '.join(sorted(set(str(v) for v in x))[:5])))
           .reset_index())
reinc_list = [{'cid':int(r['Cliente']),'razon':str(r['razon'])[:35],
               'loc':str(r['loc'])[:22] if r['loc'] else '',
               'n':int(r['n']),'imp':round(float(abs(r['imp'])),0),
               'choferes':str(r['choferes'])[:40],'fechas':str(r['fechas'])}
              for _,r in rej_cli[rej_cli['n']>1].sort_values('n',ascending=False).head(50).iterrows()]
print(f"  Reincidentes: {len(reinc_list)}")
DATA_JS = '\n'.join([
    make_chunks('D_KPIS',   rej_kpis),
    make_chunks('D_MOTIVO', by_motivo),
    make_chunks('D_CHOFER', by_chofer),
    make_chunks('D_PROV',   prov_metrics_list),
    make_chunks('D_CHPROV', chofer_prov_map),
    make_chunks('D_VENTA',  venta_list),
    make_chunks('D_ROUTES', route_index),
    make_chunks('D_CLI',    client_map),
    f'var D_PERIODO={json.dumps(PERIODO)};',
    f'var D_PROVS={json.dumps(sorted(vc["proveedor"].dropna().str.strip().unique().tolist()),ensure_ascii=True,separators=(",",":"))};',
    f'var D_CHS={json.dumps(sorted(vc["chofer"].dropna().str.strip().unique().tolist()),ensure_ascii=True,separators=(",",":"))};',
    make_chunks('D_CART',   cart_records),
    f'var D_DEP={json.dumps(dep_data,ensure_ascii=True,separators=(",",":"))};',
    f'var D_REINC={json.dumps(reinc_list,ensure_ascii=True,separators=(",",":"))};'
])

dash_path = os.path.join(BASE_DIR, 'dashboard_operativo.html')
if not os.path.exists(dash_path):
    print(f"ERROR: dashboard_operativo.html no encontrado"); sys.exit(1)

with open(dash_path,'r',encoding='utf-8') as f: html = f.read()

# Inject between DATA_START and DATA_END markers
ds = html.find('<!-- DATA_START -->')
de = html.find('<!-- DATA_END -->')
if ds>0 and de>0:
    sc_open  = html.rfind('<script>', 0, ds)
    sc_close = html.find('</script>', de) + len('</script>')
    new_block = '<script>// DATA_START\n' + DATA_JS + '\n// DATA_END\n</script>'
    html = html[:sc_open] + new_block + html[sc_close:]
    print(f"  Datos inyectados: {len(DATA_JS)//1024}KB")
else:
    print("  ERROR: marcadores DATA_START/END no encontrados"); sys.exit(1)

# Build timestamp for cache busting
build_ts = str(int(datetime.now().timestamp()))
html = html.replace('__BUILD_TS__', build_ts)

with open(dash_path,'w',encoding='utf-8') as f: f.write(html)
size = os.path.getsize(dash_path)
fecha = datetime.now().strftime('%d/%m/%Y %H:%M')
print(f"\nDashboard actualizado: {size//1024}KB")
print(f"Completado: {fecha}")
print("=" * 60)
