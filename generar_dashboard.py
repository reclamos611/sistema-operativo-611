#!/usr/bin/env python3
"""
generar_dashboard.py - 611 Logistica Dashboard Operativo
Se ejecuta automaticamente via GitHub Actions cuando se suben xlsx a /data/
Regenera dashboard_operativo.html con los datos actualizados
"""
import pandas as pd
import json, re, os, sys, math
from datetime import datetime

print("=" * 60)
print("611 Logistica - Generador Dashboard Operativo")
print("=" * 60)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# ── Helpers ───────────────────────────────────────────────────────────────────
def si(v, d=0):
    try: return d if (v is None or (isinstance(v, float) and math.isnan(v))) else int(v)
    except: return d
def sf(v, d=0.0):
    try: return d if (v is None or (isinstance(v, float) and math.isnan(v))) else float(v)
    except: return d
def find(name, kw=None):
    name_n = name.lower().replace("_"," ")
    for f in os.listdir(DATA_DIR):
        if not f.endswith(".xlsx"): continue
        fn = f.lower().replace("_"," ")
        if fn == name_n or f.lower() == name.lower():
            return os.path.join(DATA_DIR, f)
    if kw:
        for f in sorted(os.listdir(DATA_DIR)):
            if f.endswith(".xlsx") and kw in f.lower():
                return os.path.join(DATA_DIR, f)
    return None

# ── Proveedores clave ─────────────────────────────────────────────────────────
PEPSICO = 'Pepsico de Argentina SRL'
MOLINOS = 'MOLINOS RIO DE LA PLATA SA'
SOFTYS  = 'SOFTYS ARGENTINA SA'
MOTIVO_MAP = {
    1.0:'Cerrado', 2.0:'No hizo pedido', 3.0:'Sin Dinero',
    5.0:'Sin Stock', 6.0:'Mal armado / Mal facturado',
    7.0:'No esta el dueno', 16.0:'Direccion incorrecta',
    18.0:'Zona peligrosa', 25.0:'Error de preventa',
    10000.0:'Devolucion administrativa'
}

# ── Leer archivos ─────────────────────────────────────────────────────────────
print("\nLeyendo archivos...")

ma_path = find("maestro_de_articulos.xlsx","articulos")
mc_path = find("maestro_clientes.xlsx","clientes")
va_path = find("venta_anterior.xlsx","anterior")
vc_path = find("venta_actual.xlsx","actual")
cart_path = find("cartones.xlsx","carton")
mov_path  = find("movimientos.xlsx","movimiento")

missing = []
for name, path in [("maestro_de_articulos",ma_path),("maestro_clientes",mc_path),
                   ("venta_anterior",va_path),("venta_actual",vc_path)]:
    if not path: missing.append(name)
if missing:
    print(f"ADVERTENCIA: archivos no encontrados: {missing}")
    print("El dashboard se generara con los datos disponibles.")

# ── Maestros ──────────────────────────────────────────────────────────────────
art_peso = {}
art_prov = {}
if ma_path:
    ma = pd.read_excel(ma_path)
    art_peso = {int(r['codigo']): float(r['peso']) if pd.notna(r.get('peso')) and float(r.get('peso',0) or 0)>0 else 0.0
                for _,r in ma.iterrows() if pd.notna(r.get('codigo'))}
    print(f"  Articulos con peso: {len(art_peso)}")

def get_peso(code):
    try: return art_peso.get(int(code), 0.0)
    except: return 0.0

# ── Venta anterior ────────────────────────────────────────────────────────────
va = pd.DataFrame()
if va_path:
    va = pd.read_excel(va_path)
    va['Importe']  = pd.to_numeric(va['Importe'],  errors='coerce').fillna(0)
    va['Cantidad'] = pd.to_numeric(va['Cantidad'], errors='coerce').fillna(0)
    va['tipo_venta'] = va['tipo_venta'].fillna('Venta')
    va['chofer']   = va['chofer'].fillna('Sin chofer').str.strip()
    va['proveedor']= va['proveedor'].fillna('Sin proveedor').str.strip()
    va['motivodev']= pd.to_numeric(va['motivodev'], errors='coerce')
    va['Fecha']    = pd.to_datetime(va['Fecha'], errors='coerce')
    va['fecha_str']= va['Fecha'].dt.strftime('%Y-%m-%d')
    va['reparto']  = pd.to_numeric(va['reparto'], errors='coerce')
    va['camion']   = pd.to_numeric(va['camion'],  errors='coerce').fillna(0)
    art_prov = dict(zip(va['Art'].dropna().astype(int), va['proveedor']))
    print(f"  Venta anterior: {len(va):,} filas")

# ── Venta actual ──────────────────────────────────────────────────────────────
vc = pd.DataFrame()
if vc_path:
    vc = pd.read_excel(vc_path)
    vc['Importe']  = pd.to_numeric(vc['Importe'],  errors='coerce').fillna(0)
    vc['Cantidad'] = pd.to_numeric(vc['Cantidad'], errors='coerce').fillna(0)
    vc['tipo_venta'] = vc['tipo_venta'].fillna('Venta') if 'tipo_venta' in vc.columns else 'Venta'
    vc['chofer']   = vc['chofer'].fillna('Sin chofer').str.strip() if 'chofer' in vc.columns else 'Sin chofer'
    vc['proveedor']= vc['proveedor'].fillna('Sin proveedor').str.strip() if 'proveedor' in vc.columns else 'Sin proveedor'
    print(f"  Venta actual: {len(vc):,} filas")
    # Preparar columnas faltantes en vc si no existen
    if 'motivodev' not in vc.columns: vc['motivodev'] = None
    if 'reparto' not in vc.columns: vc['reparto'] = None
    if 'Razon_Social' not in vc.columns and 'razon_social' in vc.columns:
        vc['Razon_Social'] = vc['razon_social']
    if 'Direccion' not in vc.columns and 'direccion' in vc.columns:
        vc['Direccion'] = vc['direccion']
    if 'localidad' not in vc.columns: vc['localidad'] = None
    if 'Comprobante' not in vc.columns: vc['Comprobante'] = ''
    vc['motivodev'] = pd.to_numeric(vc['motivodev'], errors='coerce')
    vc['Fecha']     = pd.to_datetime(vc['Fecha'], errors='coerce')
    vc['fecha_str'] = vc['Fecha'].dt.strftime('%Y-%m-%d')
    vc['reparto']   = pd.to_numeric(vc['reparto'], errors='coerce')
    vc['camion']    = pd.to_numeric(vc['camion'],  errors='coerce').fillna(0) if 'camion' in vc.columns else 0

# Usar venta_actual para dashboard operativo (Ventas, Rutas, Rechazos)
# Mantener venta_anterior solo para historial de unidades en GUIA_DATA
va_hist = va.copy() if len(va) > 0 else pd.DataFrame()
va = vc.copy() if len(vc) > 0 else va  # operativo lee de actual

def get_prov_name(code):
    try: return art_prov.get(int(code), 'Sin proveedor')
    except: return 'Sin proveedor'

# ── CARTONES ──────────────────────────────────────────────────────────────────
cart_records = []
pepsico_ind  = {'total_fca':0,'total_rmx':0,'pct_rmx_fca':0}

if cart_path:
    cart = pd.read_excel(cart_path)
    if 'FechaSalidaCamion' in cart.columns:
        cart['FechaSalidaCamion'] = pd.to_datetime(cart['FechaSalidaCamion'])
        cart['fecha_str'] = cart['FechaSalidaCamion'].dt.strftime('%Y-%m-%d')
        cart['semana']    = cart['FechaSalidaCamion'].dt.isocalendar().week.astype(int)
        if 'cajasret' in cart.columns:
            cart = cart[cart['cajasret']>0].copy()
        for _,r in cart.iterrows():
            bs = si(r.get('cajasbienret',0))
            bi = si(r.get('cajasbienretdev',0))
            cart_records.append({
                'chofer': str(r.get('razon_social','')).strip(),
                'fecha':  str(r['fecha_str']),
                'semana': int(r['semana']),
                'b_sal':  bs, 'b_ing': bi,
                'salida': si(r.get('cajasret',0)),
                'ingreso':si(r.get('cajasretdev',0)),
                'retorno_b': round(bi/bs,4) if bs>0 else 0.0
            })
    print(f"  Cartones: {len(cart_records)} registros")

# ── MOVIMIENTOS (roturas y merma) ─────────────────────────────────────────────
rot_records = []
rot_resumen = {'total_imp':0,'total_kg':0,'pct_venta':0,'total_venta':0}
merma_prov  = []
merma_det   = []
merma_res   = {'tot_faltante':0,'tot_sobrante':0,'neto':0}
merma_cross = []

if mov_path:
    mov = pd.read_excel(mov_path)
    mov['cu'] = pd.to_numeric(mov['costo'], errors='coerce').fillna(0)

    # Roturas
    rot = mov[(mov['stockmov_tipo']=='TRA') &
              mov['stockmov_motivo'].str.lower().str.contains('rotura',na=False) &
              (mov['stockmov_cantidad']<0)].copy()
    rot['u']   = rot['stockmov_cantidad'].abs()
    rot['tot'] = rot['u'] * rot['cu']
    rot['prov']= rot['articulo_codigo'].apply(get_prov_name)
    rot['kg']  = rot['articulo_codigo'].apply(get_peso) * rot['u']

    total_venta_imp = float(va[va['tipo_venta']=='Venta']['Importe'].sum()) if len(va) else 1
    rot_grp = rot.groupby(['descripcion','prov']).agg(
        u=('u','sum'),cu=('cu','first'),tot=('tot','sum'),kg=('kg','sum')).reset_index()
    # Get date range of movimientos
    mov_fecha_col = None
    for col in ['fecha','Fecha','stockmov_fecha','FechaMovimiento']:
        if col in mov.columns: mov_fecha_col = col; break
    if mov_fecha_col:
        mov_fechas = pd.to_datetime(mov[mov_fecha_col], errors='coerce').dropna()
        periodo_mov = f"{mov_fechas.min().strftime('%d/%m')} - {mov_fechas.max().strftime('%d/%m/%Y')}" if len(mov_fechas) else ''
    else:
        periodo_mov = ''

    rot_records = [{'desc':str(r['descripcion']),'prov':str(r['prov']),
                    'u':int(r['u']),'cu':round(float(r['cu']),2),
                    'tot':round(float(r['tot']),2),'kg':round(float(r['kg']),3),
                    'pct_venta':round(float(r['tot'])/total_venta_imp,8) if total_venta_imp else 0,
                    'periodo': periodo_mov}
                   for _,r in rot_grp.iterrows()]
    rot_resumen = {'total_imp':round(float(rot['tot'].sum()),2),
                   'total_kg': round(float(rot['kg'].sum()),3),
                   'pct_venta':round(float(rot['tot'].sum())/total_venta_imp,6) if total_venta_imp else 0,
                   'total_venta':round(total_venta_imp,0)}

    # Merma CON neteada
    con = mov[mov['stockmov_tipo']=='CON'].copy()
    con['prov'] = con['articulo_codigo'].apply(get_prov_name)
    con_net = con.groupby(['articulo_codigo','descripcion','prov']).agg(
        neto=('stockmov_cantidad','sum'),cu=('cu','first')).reset_index()
    con_net = con_net[con_net['cu']>0]
    con_neg = con_net[con_net['neto']<0].copy()
    con_pos = con_net[con_net['neto']>0].copy()
    con_neg['u']   = con_neg['neto'].abs(); con_neg['tot'] = con_neg['u']*con_neg['cu']
    con_pos['u']   = con_pos['neto'];       con_pos['tot'] = con_pos['u']*con_pos['cu']

    mp = con_neg.groupby('prov').agg(u=('u','sum'),tot=('tot','sum')).reset_index()
    merma_prov = [{'prov':str(r['prov']),'u':int(r['u']),'tot':round(float(r['tot']),2)}
                   for _,r in mp.sort_values('tot',ascending=False).iterrows()]
    # Get fecha range for movimientos period label
    if mov_fecha_col and mov_fecha_col in con.columns:
        con_fechas = pd.to_datetime(con[mov_fecha_col], errors='coerce').dropna()
        if len(con_fechas):
            fecha_desde = con_fechas.min().strftime('%d/%m/%Y')
            fecha_hasta = con_fechas.max().strftime('%d/%m/%Y')
            periodo_con = f"{fecha_desde} - {fecha_hasta}"
        else:
            periodo_con = periodo_mov
    else:
        periodo_con = periodo_mov

    det_neg = [{'desc':str(r['descripcion']),'prov':str(r['prov']),'u':int(r['u']),
                'cu':round(float(r['cu']),2),'tot':round(float(r['tot']),2),
                'tipo':'faltante','fecha':periodo_con}
               for _,r in con_neg.iterrows()]
    det_pos = [{'desc':str(r['descripcion']),'prov':str(r['prov']),'u':int(r['u']),
                'cu':round(float(r['cu']),2),'tot':round(float(r['tot']),2),
                'tipo':'sobrante','fecha':periodo_con}
               for _,r in con_pos.iterrows()]
    merma_det = sorted(det_neg+det_pos, key=lambda x:x['desc'])
    merma_res = {'tot_faltante':round(float(con_neg['tot'].sum()),2),
                 'tot_sobrante':round(float(con_pos['tot'].sum()),2),
                 'neto':round(float(con_neg['tot'].sum()-con_pos['tot'].sum()),2)}

    # Cross analysis
    def desc_fam(d):
        d=re.sub(r'\d+[gGmMlLxX]+[\d]*','',d).strip(); return d[:20].strip()
    con_neg['fam']=con_neg['descripcion'].apply(desc_fam)
    con_pos['fam']=con_pos['descripcion'].apply(desc_fam)
    cross=con_neg[['fam','descripcion','u','tot','cu']].merge(
        con_pos[['fam','descripcion','u','tot','cu']],on='fam',suffixes=('_f','_s'))
    merma_cross=[{'familia':r['fam'].strip(),'falt_desc':r['descripcion_f'],
                  'falt_u':int(r['u_f']),'sobr_desc':r['descripcion_s'],
                  'sobr_u':int(r['u_s']),'cu':round(float(r['cu_f']),2)}
                 for _,r in cross.iterrows() if r['fam'].strip()]

    # Pepsico FCA/RMX
    fca=mov[(mov['stockmov_tipo']=='COM') &
            mov['stockmov_comprobante'].astype(str).str.startswith('FCA',na=False) &
            mov['descripcion'].str.contains('Carton',case=False,na=False) &
            (mov['deposito_nombre']=='Local')].copy()
    rmx=mov[(mov['stockmov_tipo']=='COM') &
            mov['stockmov_comprobante'].astype(str).str.startswith('RMX',na=False) &
            mov['descripcion'].str.contains('Carton',case=False,na=False) &
            (mov['deposito_nombre']=='Carton') &
            ~mov['stockmov_motivo'].str.startswith('Baja',na=False)].copy()
    total_fca=int(fca['bultos'].abs().sum()) if len(fca) else 0
    total_rmx=int(rmx['bultos'].abs().sum()) if len(rmx) else 0
    total_sal=sum(r['salida'] for r in cart_records)
    pepsico_ind={'total_fca':total_fca,'total_rmx':total_rmx,
                 'pct_rmx_fca':round(total_rmx/total_fca,4) if total_fca else 0}
    print(f"  Roturas: {len(rot_records)}, Merma: {len(merma_det)}, FCA:{total_fca} RMX:{total_rmx}")

# ── VENTAS ─────────────────────────────────────────────────────────────────────
venta_list=[]
rec_prov=[]
cam_prov=[]
provs=[]

if len(va)>0:
    df_v = va.copy()
    # Boletas no entregadas (todas las lineas de ese comprobante son devolucion)
    bol = df_v.groupby('Comprobante').agg(
        chofer=('chofer','first'),tipos=('tipo_venta',list),
        importe_total=('Importe','sum'),
        cliente=('Cliente','first'),razon=('Razon_Social','first'),
        localidad=('localidad','first'),
        motivos=('motivodev',list)).reset_index()
    bol['no_entregado']=bol['tipos'].apply(lambda ts:all(t=='Devolucion' for t in ts))
    bol_dev=bol[bol['no_entregado']].copy()
    bol_dev['importe_abs']=bol_dev['importe_total'].abs()

    ch_st={}
    for _,r in bol.iterrows():
        ch=r['chofer']
        if ch not in ch_st: ch_st[ch]={'e':0,'ne':0}
        if r['no_entregado']: ch_st[ch]['ne']+=1
        else: ch_st[ch]['e']+=1

    dev=df_v[df_v['tipo_venta']=='Devolucion'].copy()
    cam=df_v[df_v['tipo_venta']=='Cambio'].copy()
    rec_ch=dev.groupby(['chofer','proveedor']).agg(n=('Importe','count'),imp=('Importe','sum')).reset_index()
    cam_ch=cam.groupby(['chofer','proveedor']).agg(n=('Importe','count'),imp=('Importe','sum')).reset_index()

    for ch,st in ch_st.items():
        r2=rec_ch[rec_ch['chofer']==ch]
        i2=cam_ch[cam_ch['chofer']==ch]
        venta_list.append({'ch':ch,'e':int(st['e']),'ne':int(st['ne']),
            'rp':{row['proveedor']:{'n':int(row['n']),'imp':round(float(row['imp']),2)} for _,row in r2.iterrows()},
            'ip':{row['proveedor']:{'n':int(row['n']),'imp':round(float(row['imp']),2)} for _,row in i2.iterrows()}})

    rp=dev.groupby('proveedor').agg(n=('Importe','count'),imp=('Importe','sum')).reset_index()
    cp=cam.groupby('proveedor').agg(n=('Importe','count'),imp=('Importe','sum')).reset_index()
    rec_prov=[{'prov':r['proveedor'],'n':int(r['n']),'imp':round(float(r['imp']),2)} for _,r in rp.iterrows()]
    cam_prov=[{'prov':r['proveedor'],'n':int(r['n']),'imp':round(float(r['imp']),2)} for _,r in cp.iterrows()]
    provs=sorted(df_v['proveedor'].dropna().str.strip().unique().tolist())
    print(f"  Ventas: {len(venta_list)} choferes, {len(bol_dev)} boletas rechazadas")

# ── METRICAS POR PROVEEDOR (efectividad entrega, rechazo por comprobante) ─────
def build_prov_metrics_fn(df_p):
    if df_p.empty: return None
    comp_cls = df_p.groupby('Comprobante')['tipo_venta'].apply(list).reset_index()
    comp_cls['all_dev']   = comp_cls['tipo_venta'].apply(lambda ts: all(t=='Devolucion' for t in ts) and len(ts)>0)
    comp_cls['has_venta'] = comp_cls['tipo_venta'].apply(lambda ts: 'Venta' in ts)
    fac  = int(comp_cls['has_venta'].sum())
    no_e = int(comp_cls['all_dev'].sum())
    rej_comps = comp_cls[comp_cls['all_dev']]['Comprobante'].tolist()
    venta = float(df_p[df_p['tipo_venta']=='Venta']['Importe'].sum())
    rec   = float(df_p[df_p['Comprobante'].isin(rej_comps)]['Importe'].sum())
    cam   = float(df_p[df_p['tipo_venta']=='Cambio']['Importe'].sum())
    efect = round(fac/(fac+no_e),4) if (fac+no_e)>0 else 0
    return {
        'venta': round(venta,0), 'rec_imp': round(rec,0),
        'rec_pct': round(abs(rec)/venta,4) if venta>0 else 0,
        'cam_imp': round(abs(cam),0),
        'cam_pct': round(abs(cam)/venta,4) if venta>0 else 0,
        'fac': fac, 'no_e': no_e, 'efect': efect
    }

prov_metrics_list = []
chofer_prov_map = {}

for p in sorted(va['proveedor'].dropna().str.strip().unique()):
    df_p = va[va['proveedor'].str.strip()==p]
    m = build_prov_metrics_fn(df_p)
    if m and m['venta']>0:
        prov_metrics_list.append({'prov':str(p), **m})

# Per chofer per proveedor
for ch, df_ch in va.groupby('chofer'):
    ch_key = str(ch).strip()
    chofer_prov_map[ch_key] = []
    for p, df_cp in df_ch.groupby('proveedor'):
        m = build_prov_metrics_fn(df_cp.reset_index(drop=True))
        if m and m['venta']>0:
            chofer_prov_map[ch_key].append({'prov':str(p).strip(), **m})

print(f"  Metricas por proveedor: {len(prov_metrics_list)} proveedores")

# ── RECHAZOS GESCOM ────────────────────────────────────────────────────────────
gescom_rechazos=[]
by_motivo_list=[]
by_chofer_list=[]
by_day_list=[]
by_prov_list=[]
reinc_list=[]
rej_kpis={}

if len(va)>0:
    dev=va[va['tipo_venta']=='Devolucion'].copy()
    dev['motivo_desc']=dev['motivodev'].map(MOTIVO_MAP).fillna('Otro')

    bol2=va.groupby('Comprobante').agg(
        chofer=('chofer','first'),fecha=('fecha_str','first'),
        cliente=('Cliente','first'),razon=('Razon_Social','first'),
        localidad=('localidad','first'),tipos=('tipo_venta',list),
        importe_total=('Importe','sum'),motivos=('motivodev',list)).reset_index()
    bol2['no_entregado']=bol2['tipos'].apply(lambda ts:all(t=='Devolucion' for t in ts))
    bol_dev2=bol2[bol2['no_entregado']].copy()
    bol_dev2['motivo_desc']=bol_dev2['motivos'].apply(
        lambda ms:MOTIVO_MAP.get(ms[0] if ms else None,'Otro') if ms else 'Otro')
    bol_dev2['importe_abs']=bol_dev2['importe_total'].abs()

    for _,r in bol_dev2.iterrows():
        gescom_rechazos.append({'comp':str(r['Comprobante']),'fecha':str(r['fecha']),
            'cliente':int(r['cliente']) if pd.notna(r['cliente']) else 0,
            'razon':str(r['razon'] or '')[:40],
            'loc':str(r['localidad'] or '')[:25] if pd.notna(r['localidad']) else '',
            'chofer':str(r['chofer']),'motivo':str(r['motivo_desc']),
            'imp':round(float(r['importe_abs']),0)})

    bm=dev.groupby('motivo_desc').agg(lineas=('Importe','count'),isum=('Importe','sum'),uds=('Cantidad','sum')).reset_index()
    bm['isum']=bm['isum'].abs()
    by_motivo_list=[{'motivo':r['motivo_desc'],'lineas':int(r['lineas']),'uds':int(abs(r['uds'])),'imp':round(float(r['isum']),0)}
                    for _,r in bm.sort_values('isum',ascending=False).iterrows()]

    bc=bol_dev2.groupby('chofer').agg(n_rej=('Comprobante','count'),isum=('importe_abs','sum')).reset_index()
    tot=bol2.groupby('chofer').size().reset_index(name='total_bol')
    bc=bc.merge(tot,on='chofer',how='left').fillna({'total_bol':0})
    bc['pct']=bc.apply(lambda r:round(r['n_rej']/r['total_bol'],4) if r['total_bol']>0 else 0,axis=1)
    by_chofer_list=[{'ch':r['chofer'],'n':int(r['n_rej']),'tot':int(r['total_bol']),
                     'imp':round(float(r['isum']),0),'pct':float(r['pct'])}
                    for _,r in bc.sort_values('n_rej',ascending=False).iterrows()]

    bd=bol_dev2.groupby('fecha').agg(n=('Comprobante','count'),isum=('importe_abs','sum')).reset_index()
    by_day_list=[{'f':str(r['fecha']),'n':int(r['n']),'imp':round(float(r['isum']),0)}
                 for _,r in bd.sort_values('fecha').iterrows()]

    bpv=dev.groupby('proveedor').agg(n=('Importe','count'),isum=('Importe','sum')).reset_index()
    bpv['isum']=bpv['isum'].abs()
    by_prov_list=[{'prov':r['proveedor'],'n':int(r['n']),'imp':round(float(r['isum']),0)}
                  for _,r in bpv.sort_values('isum',ascending=False).head(10).iterrows()]

    ri=bol_dev2.groupby('cliente').agg(n=('Comprobante','count'),razon=('razon','first'),
        loc=('localidad','first'),choferes_lst=('chofer',lambda x:', '.join(sorted(set(x))[:3])),
        isum=('importe_abs','sum')).reset_index()
    ri_multi=ri[ri['n']>1].sort_values('n',ascending=False)
    reinc_list=[{'cid':int(r['cliente']),'razon':str(r['razon'])[:35],
                 'loc':str(r['loc'])[:22] if pd.notna(r['loc']) else '',
                 'n':int(r['n']),'imp':round(float(r['isum']),0),
                 'choferes':str(r['choferes_lst'])[:35]}
                for _,r in ri_multi.head(30).iterrows()]

    total_bol_all=len(bol2); total_bol_rej=len(bol_dev2)
    total_imp_rej=float(bol_dev2['importe_abs'].sum())
    total_imp_venta=float(va[va['tipo_venta']=='Venta']['Importe'].sum())
    cam_imp = round(float(cam['Importe'].sum()) if len(cam)>0 else 0, 0)
    rej_kpis={'imp_venta':round(total_imp_venta,0),'imp_dev':round(total_imp_rej,0),
              'imp_cam':cam_imp,
              'pct_rechazo':round(total_imp_rej/total_imp_venta,4) if total_imp_venta else 0,
              'pct_cambio':round(cam_imp/total_imp_venta,4) if total_imp_venta else 0,
              'clientes_afectados':int(bol_dev2['cliente'].nunique()),
              'boletas_rej':total_bol_rej,'total_boletas':total_bol_all,
              'reincidentes':len(reinc_list)}
    print(f"  Rechazos gescom: {len(gescom_rechazos)}, reincidentes: {len(reinc_list)}")

# ── RUTAS ─────────────────────────────────────────────────────────────────────
route_index=[]
client_map={}

if len(va)>0:
    for rep_id,grp in va.groupby('reparto'):
        if pd.isna(rep_id): continue
        ch=str(grp['chofer'].iloc[0]).strip()
        fec=grp['fecha_str'].iloc[0]
        cam_num=int(grp['camion'].iloc[0])
        vgrp=grp[grp['tipo_venta']=='Venta']
        kg=0.0; tot_imp=0.0; pep_imp=0.0; mol_imp=0.0; sof_imp=0.0
        for _,vr in vgrp.iterrows():
            try: kg+=get_peso(vr.get('Art',0))*float(vr['Cantidad'])
            except: pass
            imp=float(vr['Importe']); tot_imp+=imp
            p=str(vr['proveedor'])
            if p==PEPSICO: pep_imp+=imp
            elif p==MOLINOS: mol_imp+=imp
            elif p==SOFTYS: sof_imp+=imp
        clientes=[]
        for cli_id,cg in grp.groupby('Cliente'):
            tipos=list(cg['tipo_venta'].fillna('Venta'))
            rt=all(t=='Devolucion' for t in tipos)
            dv='Devolucion' in tipos and not rt
            cm2='Cambio' in tipos
            imp2=int(cg[cg['tipo_venta']=='Venta']['Importe'].sum())
            cnt=int(cg[cg['tipo_venta']=='Venta']['Cantidad'].sum())
            raz=str(cg['Razon_Social'].iloc[0] or '')[:40]
            dir2=str(cg['Direccion'].iloc[0] or '')[:40] if 'Direccion' in cg.columns else ''
            loc=str(cg['localidad'].iloc[0] if pd.notna(cg['localidad'].iloc[0]) else '')[:22] if 'localidad' in cg.columns else ''
            cmp=str(cg['Comprobante'].iloc[0] or '')
            fl=1 if rt else(2 if dv else(3 if cm2 else 0))
            clientes.append([int(cli_id),raz,dir2,loc,cmp,imp2,cnt,fl])
        oth=tot_imp-pep_imp-mol_imp-sof_imp
        route_index.append({'rep':int(rep_id),'ch':ch,'f':str(fec),'cam':cam_num,
            'n':len(clientes),'tot':round(tot_imp,0),'rej':sum(1 for c in clientes if c[7]==1),
            'kg':round(kg,1),'pep':round(pep_imp,0),'mol':round(mol_imp,0),
            'sof':round(sof_imp,0),'oth':round(oth,0)})
        client_map[str(int(rep_id))]=clientes
    route_index.sort(key=lambda x:(x['f'],x['ch']))
    print(f"  Rutas: {len(route_index)} repartos")

# ── GUIA_DATA y VEND_STATS ─────────────────────────────────────────────────────
GUIA_DATA={}
VEND_STATS={}

if mc_path and len(vc)>0:
    mc=pd.read_excel(mc_path)
    if 'estado' in mc.columns: mc=mc[mc['estado']=='A']
    DIAS=['Lunes','Martes','Miercoles','Jueves','Viernes','Sabado','Domingo']
    MARCAS=['Lays','Doritos','Cheetos','3D','Pep','Pehuamar','Twistos','Tostitos','Otro']

    def get_marca_idx(art_name):
        art_name=str(art_name).lower()
        for i,m in enumerate(MARCAS[:-1]):
            if m.lower() in art_name: return i
        return len(MARCAS)-1

    vc_v=vc[vc['tipo_venta']=='Venta'].copy() if 'tipo_venta' in vc.columns else vc.copy()
    vc_v['Cliente']=pd.to_numeric(vc_v['Cliente'],errors='coerce')
    va_v=va_hist[va_hist['tipo_venta']=='Venta'].copy() if len(va_hist)>0 else pd.DataFrame()
    if len(va_v)>0: va_v['Cliente']=pd.to_numeric(va_v['Cliente'],errors='coerce')

    for _,row in mc.iterrows():
        cli_id=int(row['codigo']) if pd.notna(row.get('codigo')) else None
        vend=int(row['vendedor']) if pd.notna(row.get('vendedor')) else None
        if not cli_id or not vend or vend<31 or vend>65: continue
        razon=str(row.get('razon_social','') or '')[:40]
        loc=str(row.get('localidad','') or '')[:25]
        dire=str(row.get('direccion','') or '')[:40]
        dias_visita=[[dia,vend] for dia in DIAS if row.get(dia,0)]
        if vend in [31,32,33,34,35,36,37,38,39,51]: mesa=400
        elif vend in [41,42,43,44,45,46,47,48,49,52,53,54,55,56,57,58,59]: mesa=500
        else: mesa=300
        uds=[0]*len(MARCAS)
        if len(va_v)>0:
            cli_va=va_v[va_v['Cliente']==cli_id]
            for _,vr in cli_va.iterrows():
                idx=get_marca_idx(str(vr.get('articulo','')))
                uds[idx]+=float(vr.get('Cantidad',0) or 0)
        imp_actual=int(vc_v[vc_v['Cliente']==cli_id]['Importe'].sum()) if len(vc_v)>0 else 0
        GUIA_DATA[str(cli_id)]={'n':razon,'l':loc,'d':dire,'v':vend,'m':mesa,
            'ds':dias_visita if dias_visita else [[DIAS[0],vend]],'u':[int(u) for u in uds],'i':imp_actual}

    for vend in range(31,66):
        cli_vend=mc[mc['vendedor']==vend]['codigo'].dropna().astype(int).tolist()
        if not cli_vend: continue
        cart2=len(cli_vend)
        ccc_m=int(vc_v[vc_v['Cliente'].isin(cli_vend)]['Cliente'].nunique()) if len(vc_v)>0 else 0
        imp=float(vc_v[vc_v['Cliente'].isin(cli_vend)]['Importe'].sum()) if len(vc_v)>0 else 0
        dev_vend=vc[vc['tipo_venta']=='Devolucion'] if 'tipo_venta' in vc.columns else pd.DataFrame()
        rec_imp=float(abs(dev_vend[dev_vend['Cliente'].isin(cli_vend)]['Importe'].sum())) if len(dev_vend)>0 else 0
        VEND_STATS[str(vend)]={'cart':cart2,'ccc_m':ccc_m,
            'pcc_m':round(ccc_m/cart2*100,1) if cart2>0 else 0,
            'imp':int(imp),'rec_imp':int(rec_imp),
            'pct_rec':round(rec_imp/imp*100,2) if imp>0 else 0}
    print(f"  GUIA_DATA: {len(GUIA_DATA)} clientes, VEND_STATS: {len(VEND_STATS)} vendedores")

# ── SERIALIZAR ────────────────────────────────────────────────────────────────
print("\nSerializando datos...")

def make_chunks(var_name, data, chunk=8000):
    j=json.dumps(data,ensure_ascii=True,separators=(',',':'))
    if isinstance(data,dict):
        stmts=[f'var {var_name}={{}};']
        buf,bsize={},0
        for k,v in data.items():
            vj=json.dumps(v,ensure_ascii=True,separators=(',',':'))
            if bsize+len(vj)>chunk and buf:
                stmts.append(f'Object.assign({var_name},{json.dumps(buf,ensure_ascii=True,separators=(",",":"))});')
                buf,bsize={},0
            buf[k]=v; bsize+=len(vj)
        if buf:
            stmts.append(f'Object.assign({var_name},{json.dumps(buf,ensure_ascii=True,separators=(",",":"))});')
        return '\n'.join(stmts)
    elif isinstance(data,list):
        stmts=[f'var {var_name}=[];']
        buf,bsize=[],0
        for item in data:
            ij=json.dumps(item,ensure_ascii=True,separators=(',',':'))
            if bsize+len(ij)>chunk and buf:
                stmts.append(f'{var_name}={var_name}.concat({json.dumps(buf,ensure_ascii=True,separators=(",",":"))});')
                buf,bsize=[],0
            buf.append(item); bsize+=len(ij)
        if buf:
            stmts.append(f'{var_name}={var_name}.concat({json.dumps(buf,ensure_ascii=True,separators=(",",":"))});')
        return '\n'.join(stmts)
    else:
        return f'var {var_name}={j};'

# Build data object
# Venta $ per proveedor (for % rechazo by proveedor)
venta_prov = {}
if len(va) > 0:
    vv = va[va['tipo_venta']=='Venta']
    vp_grp = vv.groupby('proveedor')['Importe'].sum()
    venta_prov = {str(p): round(float(v),0) for p,v in vp_grp.items()}

# Valorizado deposito: vencido and consumo from movimientos
vencido_imp = 0.0
consumo_u   = 0
consumo_imp = 0.0
if mov_path and 'mov' in dir():
    # Vencido: tipo VEN
    ven_types = mov['stockmov_tipo'].unique().tolist() if 'stockmov_tipo' in mov.columns else []
    if 'VEN' in ven_types:
        ven = mov[mov['stockmov_tipo']=='VEN'].copy()
        ven['cu2'] = pd.to_numeric(ven['costo'], errors='coerce').fillna(0)
        ven['u2']  = ven['stockmov_cantidad'].abs()
        vencido_imp = round(float((ven['u2']*ven['cu2']).sum()), 2)
    # Consumo interno: tipo TRA + motivo contiene 'consumo'
    if 'TRA' in ven_types and 'stockmov_motivo' in mov.columns:
        cons = mov[(mov['stockmov_tipo']=='TRA') &
                   mov['stockmov_motivo'].str.lower().str.contains('consumo',na=False) &
                   (mov['stockmov_cantidad']<0)].copy()
        if len(cons) > 0:
            cons['cu2'] = pd.to_numeric(cons['costo'], errors='coerce').fillna(0)
            cons['u2']  = cons['stockmov_cantidad'].abs()
            consumo_u   = int(cons['u2'].sum())
            consumo_imp = round(float((cons['u2']*cons['cu2']).sum()), 2)

main_data = {
    'cartones':cart_records,'roturas':rot_records,'rot_res':rot_resumen,
    'merma_prov':merma_prov,'merma_det':merma_det,'merma_cross':merma_cross,
    'merma_res':merma_res,'venta':venta_list,'provs':provs,
    'rec_prov':rec_prov,'cam_prov':cam_prov,'pepsico_ind':pepsico_ind,
    'routes':route_index,'venta_prov':venta_prov,
    'vencido_imp':vencido_imp,'consumo_u':consumo_u,'consumo_imp':consumo_imp,
    'prov_metrics':prov_metrics_list,'chofer_prov':chofer_prov_map
}
rej_data = {
    'kpis':rej_kpis,'gescom':gescom_rechazos,'by_motivo':by_motivo_list,
    'by_chofer':by_chofer_list,'by_day':by_day_list,'by_prov':by_prov_list,
    'reincidentes':reinc_list
}

d_js   = make_chunks('D',   main_data)
rd_js  = make_chunks('RD',  rej_data)
cli_js = make_chunks('CLI', client_map)
gd_js  = make_chunks('GUIA_DATA', GUIA_DATA)
vs_js  = f"var VEND_STATS={json.dumps(VEND_STATS,ensure_ascii=True,separators=(',',':'))};"

print(f"  D: {len(d_js):,} chars")
print(f"  RD: {len(rd_js):,} chars")
print(f"  CLI: {len(cli_js):,} chars")
print(f"  GUIA_DATA: {len(gd_js):,} chars")

# ── INYECTAR EN dashboard_operativo.html ──────────────────────────────────────
dash_path = os.path.join(BASE_DIR, 'dashboard_operativo.html')
if not os.path.exists(dash_path):
    print(f"ERROR: dashboard_operativo.html no encontrado en {BASE_DIR}")
    sys.exit(1)

with open(dash_path,'r',encoding='utf-8') as f:
    html = f.read()

# Find the data block using DATA_START/DATA_END markers (permanent fix)
data_start_marker = '<!-- DATA_START -->'
data_end_marker   = '<!-- DATA_END -->'
ds_pos = html.find(data_start_marker)
de_pos = html.find(data_end_marker)

if ds_pos > 0 and de_pos > 0:
    # Replace only the content between markers
    sc_open_start = html.rfind('<script>', 0, ds_pos)
    sc_close_end  = html.find('</script>', de_pos) + len('</script>')
    
    # Build prov_metrics and chofer_prov JS
    pm_js = make_chunks('PROV_METRICS', prov_metrics_list)
    cp_js = make_chunks('CHOFER_PROV', chofer_prov_map)
    
    new_data = ('<script>' + data_start_marker + '\n'
                + d_js + '\n' + rd_js + '\n' + cli_js + '\n'
                + pm_js + '\n' + cp_js + '\n'
                + data_end_marker + '</script>')
    html = html[:sc_open_start] + new_data + html[sc_close_end:]
    print(f"  Datos reemplazados via marcadores ({sc_close_end-sc_open_start:,} -> {len(new_data):,} chars)")
else:
    # Fallback: find by pattern
    d_sc_start = html.find('<script>\nvar D={}')
    if d_sc_start < 0:
        d_sc_start = html.find('<script>\nvar D={')
    if d_sc_start > 0:
        d_sc_end = html.find('</script>', d_sc_start) + len('</script>')
        pm_js = make_chunks('PROV_METRICS', prov_metrics_list)
        cp_js = make_chunks('CHOFER_PROV', chofer_prov_map)
        new_data = ('<script>' + data_start_marker + '\n'
                    + d_js + '\n' + rd_js + '\n' + cli_js + '\n'
                    + pm_js + '\n' + cp_js + '\n'
                    + data_end_marker + '</script>')
        html = html[:d_sc_start] + new_data + html[d_sc_end:]
        print(f"  Datos reemplazados via patron ({len(new_data):,} chars)")
    else:
        pm_js = make_chunks('PROV_METRICS', prov_metrics_list)
        cp_js = make_chunks('CHOFER_PROV', chofer_prov_map)
        print("  ADVERTENCIA: no se pudo inyectar datos")

# Remove old CONC block if exists (datos de ejemplo)
conc_start = html.find('<script>\nvar CONC=')
if conc_start > 0:
    conc_end = html.find('</script>', conc_start) + len('</script>')
    html = html[:conc_start] + html[conc_end:]
    print("  CONC de ejemplo eliminado")

# Replace GUIA_DATA in guia-script deferred
guia_sc_start = html.find('<script id="guia-script"')
guia_sc_end   = html.find('</script>', guia_sc_start+100)
guia_block    = html[guia_sc_start:guia_sc_end]

old_gd = re.search(r'const GUIA_DATA=\{.*?\};', guia_block, re.DOTALL)
if old_gd:
    new_guia_block = guia_block.replace(old_gd.group(), f'const GUIA_DATA={json.dumps(GUIA_DATA,ensure_ascii=True,separators=(",",":"))};', 1)
    old_vs = re.search(r'const VEND_STATS=\{.*?\};', new_guia_block, re.DOTALL)
    if old_vs:
        new_guia_block = new_guia_block.replace(old_vs.group(), f'const VEND_STATS={json.dumps(VEND_STATS,ensure_ascii=True,separators=(",",":"))};', 1)
    html = html[:guia_sc_start] + new_guia_block + html[guia_sc_end:]
    print("  GUIA_DATA y VEND_STATS actualizados")

# Stamp periodo from data
if len(va) > 0 and 'Fecha' in va.columns:
    mes = va['Fecha'].dt.month.mode()[0] if len(va) > 0 else datetime.now().month
    anio = va['Fecha'].dt.year.mode()[0] if len(va) > 0 else datetime.now().year
    meses_es = {1:'Enero',2:'Febrero',3:'Marzo',4:'Abril',5:'Mayo',6:'Junio',
                7:'Julio',8:'Agosto',9:'Septiembre',10:'Octubre',11:'Noviembre',12:'Diciembre'}
    periodo = f"{meses_es.get(int(mes),'?')} {int(anio)}"
else:
    periodo = datetime.now().strftime("%B %Y")

html = re.sub(r'Cartones \(.*?\)', f'Cartones ({periodo})', html)

# No-cache meta
no_cache = ('<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">\n'
            '<meta http-equiv="Pragma" content="no-cache">\n'
            '<meta http-equiv="Expires" content="0">\n')
if 'Cache-Control' not in html:
    html = html.replace('<meta charset="UTF-8">', '<meta charset="UTF-8">\n'+no_cache, 1)

# Inject build timestamp for cache busting
build_ts = str(int(datetime.now().timestamp()))
html = html.replace('__BUILD_TS__', build_ts)

with open(dash_path,'w',encoding='utf-8') as f:
    f.write(html)

fecha = datetime.now().strftime("%d/%m/%Y %H:%M")

size = os.path.getsize(dash_path)
print(f"\nDashboard actualizado: {size//1024}KB")
print(f"Completado: {fecha}")
print("="*60)
