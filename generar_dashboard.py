#!/usr/bin/env python3
"""
generar_dashboard.py - 611 Logistica Dashboard Operativo
Lee: venta_actual.xlsx, movimientos.xlsx (opcional), cartones.xlsx (opcional), Registro_de_Rechazos.xlsx (opcional)
"""
import pandas as pd, json, os, sys, math
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
    try:
        for f in os.listdir(DATA_DIR):
            if f.lower() == name.lower():
                return os.path.join(DATA_DIR, f)
        kw = name.lower().split(".")[0]
        for f in sorted(os.listdir(DATA_DIR)):
            if f.endswith(".xlsx") and kw in f.lower():
                return os.path.join(DATA_DIR, f)
    except: pass
    return None

def make_chunks(var_name, data, chunk=8000):
    if isinstance(data, dict):
        stmts = [f'var {var_name}={{}};']
        buf, bsize = {}, 0
        for k,v in data.items():
            vj = json.dumps(v, ensure_ascii=True, separators=(',',':'))
            if bsize+len(vj)>chunk and buf:
                stmts.append(f'Object.assign({var_name},{json.dumps(buf,ensure_ascii=True,separators=(",",":"))});')
                buf, bsize = {}, 0
            buf[k]=v; bsize+=len(vj)
        if buf:
            stmts.append(f'Object.assign({var_name},{json.dumps(buf,ensure_ascii=True,separators=(",",":"))});')
    elif isinstance(data, list):
        stmts = [f'var {var_name}=[];']
        buf, bsize = [], 0
        for item in data:
            ij = json.dumps(item, ensure_ascii=True, separators=(',',':'))
            if bsize+len(ij)>chunk and buf:
                stmts.append(f'{var_name}={var_name}.concat({json.dumps(buf,ensure_ascii=True,separators=(",",":"))});')
                buf, bsize = [], 0
            buf.append(item); bsize+=len(ij)
        if buf:
            stmts.append(f'{var_name}={var_name}.concat({json.dumps(buf,ensure_ascii=True,separators=(",",":"))});')
    else:
        stmts = [f'var {var_name}={json.dumps(data,ensure_ascii=True,separators=(",",":"))};']
    return '\n'.join(stmts)

PEPSICO = 'Pepsico de Argentina SRL'
MOLINOS = 'MOLINOS RIO DE LA PLATA SA'
SOFTYS  = 'SOFTYS ARGENTINA SA'
MOTIVO_MAP = {1.0:'Cerrado',2.0:'No hizo pedido',3.0:'Sin Dinero',
              5.0:'Sin Stock',6.0:'Mal armado',7.0:'No esta el dueno',
              16.0:'Direccion incorrecta',18.0:'Zona peligrosa',
              25.0:'Error de preventa',10000.0:'Dev. administrativa'}
CHOFER_MAP = {
    'AVALOS GOMEZ RODRIGO SEBASTIAN': 'RODRIGO AVALOS',
    'BELEN EMILIANO AGUSTIN':         'BELEN AGUSTIN',
    'CANELO PABLO FERNANDO':          'PABLO CANELO',
    'CARO MAXIMILIANO ALBERTO':       'MAXIMILANO  CARO',
    'GONZALEZ CECILIA GUADALUPE':     'CECILIA GONZALEZ',
    'GUEVARA ENRIQUE LEONARDO':       'LEONARDO GUEVARA',
    'GUZMAN DIEGO NORBERTO':          'GUZMAN DIEGO',
    'JUAREZ LUIS ENRIQUE':            'LUIS JUAREZ',
    'LUJAN LUCAS':                    'LUCAS LUJAN',
    'MARTINEZ PEREZ JORGE LEANDRO':   'MARTINEZ LEANDRO',
    'MOLINA JORGE GABRIEL':           'JORGE MOLINA',
    'OYOLA GASTON AGUSTIN':           'GASTON OYOLA',
    'PALLOTI DUILIO':                 'DUILIO PALLOTTI',
    'RAFAELLI DIEGO DANIEL':          'DIEGO RAFAELLI',
    'RICAPA PAREDES JOSE ANTONIO':    'JOSE RICAPA',
    'ROMANO RODRIGO ERNESTO':         'RODRIGO ROMANO',
    'SUAREZ TOBIAS EMIR':             'SUAREZ EMIR',
    'TALAVERA ADRIAN ISMAEL':         'TALAVERA ADRIAN',
}

print("\nLeyendo archivos...")

# ── VENTA ACTUAL ──────────────────────────────────────────────────────────────
vc_path = find("venta_actual.xlsx")
if not vc_path:
    print("ERROR: no se encontro venta_actual.xlsx"); sys.exit(1)

vc = pd.read_excel(vc_path)
vc['Importe']    = pd.to_numeric(vc['Importe'],   errors='coerce').fillna(0)
vc['Cantidad']   = pd.to_numeric(vc['Cantidad'],  errors='coerce').fillna(0)
vc['tipo_venta'] = vc['tipo_venta'].fillna('Venta') if 'tipo_venta' in vc.columns else 'Venta'
vc['chofer']     = vc['chofer'].fillna('Sin chofer').str.strip() if 'chofer' in vc.columns else 'Sin chofer'
vc['proveedor']  = vc['proveedor'].fillna('Sin proveedor').str.strip() if 'proveedor' in vc.columns else 'Sin proveedor'
vc['motivodev']  = pd.to_numeric(vc.get('motivodev'), errors='coerce')
vc['Fecha']      = pd.to_datetime(vc['Fecha'], errors='coerce')
vc['fecha_str']  = vc['Fecha'].dt.strftime('%Y-%m-%d')
vc['reparto']    = pd.to_numeric(vc.get('reparto'),  errors='coerce')
vc['camion']     = pd.to_numeric(vc.get('camion'),   errors='coerce').fillna(0)
if 'Comprobante'  not in vc.columns: vc['Comprobante']  = ''
if 'Razon_Social' not in vc.columns: vc['Razon_Social'] = ''
if 'localidad'    not in vc.columns: vc['localidad']    = ''
if 'Direccion'    not in vc.columns: vc['Direccion']    = ''
if 'cod_ven'      not in vc.columns: vc['cod_ven']      = ''
if 'cantxcap'     not in vc.columns: vc['cantxcap']     = 0

# Importe neto = neto (col M) x cantidad (col F)
if 'neto' in vc.columns:
    vc['neto']         = pd.to_numeric(vc['neto'], errors='coerce').fillna(0)
    vc['importe_neto'] = vc['neto'] * vc['Cantidad'].abs()
else:
    vc['importe_neto'] = vc['Importe']

vc['chofer_up'] = vc['chofer'].str.strip().str.upper()

mes  = int(vc['Fecha'].dt.month.mode()[0])
anio = int(vc['Fecha'].dt.year.mode()[0])
MESES = {1:'Enero',2:'Febrero',3:'Marzo',4:'Abril',5:'Mayo',6:'Junio',
         7:'Julio',8:'Agosto',9:'Septiembre',10:'Octubre',11:'Noviembre',12:'Diciembre'}
PERIODO = f"{MESES.get(mes,'?')} {anio}"
print(f"  Venta actual: {len(vc):,} filas  Periodo: {PERIODO}")

# ── RECHAZOS ──────────────────────────────────────────────────────────────────
dev = vc[vc['tipo_venta']=='Devolucion'].copy()
dev['motivo_desc'] = dev['motivodev'].map(MOTIVO_MAP).fillna('Otro')

comp_cls = vc.groupby('Comprobante')['tipo_venta'].apply(list).reset_index()
comp_cls['all_dev']   = comp_cls['tipo_venta'].apply(lambda ts: all(t=='Devolucion' for t in ts))
comp_cls['has_venta'] = comp_cls['tipo_venta'].apply(lambda ts: 'Venta' in ts)
rej_comps = set(comp_cls[comp_cls['all_dev']]['Comprobante'])

venta_tot   = float(vc[vc['tipo_venta']=='Venta']['importe_neto'].sum())
all_dev_imp = float(vc[vc['tipo_venta']=='Devolucion']['importe_neto'].sum())
cam_tot     = float(vc[vc['tipo_venta']=='Cambio']['importe_neto'].sum())
venta_neta  = venta_tot - abs(all_dev_imp) - abs(cam_tot)

# Efectividad: neto cliente+fecha <= 0
cli_dia_global = vc.groupby(['Cliente','Fecha'])['importe_neto'].sum().reset_index()
padron_global  = len(cli_dia_global)
no_e_global    = int((cli_dia_global['importe_neto'] <= 0).sum())
fac_global     = padron_global - no_e_global

rej_kpis = {
    'imp_venta':   round(venta_neta,0),
    'imp_dev':     round(abs(all_dev_imp),0),
    'pct_rechazo': round(abs(all_dev_imp)/venta_tot,4) if venta_tot else 0,
    'cam_imp':     round(abs(cam_tot),0),
    'cam_pct':     round(abs(cam_tot)/venta_tot,4) if venta_tot else 0,
    'fac': fac_global, 'no_e': no_e_global,
    'efect': round(fac_global/padron_global,4) if padron_global else 0
}

bm = dev.groupby('motivo_desc').agg(lineas=('Importe','count'),uds=('Cantidad','sum'),isum=('importe_neto','sum')).reset_index()
bm['isum'] = bm['isum'].abs()
by_motivo = [{'motivo':r['motivo_desc'],'lineas':int(r['lineas']),'uds':int(abs(r['uds'])),'imp':round(float(r['isum']),0)}
             for _,r in bm.sort_values('isum',ascending=False).iterrows()]

bc = vc[vc['Comprobante'].isin(rej_comps)].groupby('chofer').agg(n=('Comprobante','nunique'),imp=('importe_neto','sum')).reset_index()
tot_ch = comp_cls.merge(vc[['Comprobante','chofer']].drop_duplicates(),on='Comprobante',how='left')
tot_ch = tot_ch[tot_ch['has_venta']].groupby('chofer').size().reset_index(name='total')
bc = bc.merge(tot_ch,on='chofer',how='left').fillna({'total':0})
bc['pct'] = bc.apply(lambda r: round(r['n']/(r['n']+r['total']),4) if (r['n']+r['total'])>0 else 0, axis=1)
by_chofer = [{'ch':r['chofer'],'n':int(r['n']),'tot':int(r['total']),'imp':round(float(abs(r['imp'])),0),'pct':float(r['pct'])}
             for _,r in bc.sort_values('n',ascending=False).iterrows()]

def prov_met(df_p):
    if df_p.empty: return None
    cli_dia = df_p.groupby(['Cliente','Fecha'])['importe_neto'].sum().reset_index()
    padron = len(cli_dia); no_e = int((cli_dia['importe_neto']<=0).sum()); f = padron-no_e
    v=float(df_p[df_p['tipo_venta']=='Venta']['importe_neto'].sum())
    r=float(df_p[df_p['tipo_venta']=='Devolucion']['importe_neto'].sum())
    c=float(df_p[df_p['tipo_venta']=='Cambio']['importe_neto'].sum())
    kg=float(pd.to_numeric(df_p[df_p['tipo_venta']=='Venta']['cantxcap'],errors='coerce').fillna(0).clip(0,5000).sum()) if 'cantxcap' in df_p.columns else 0.0
    return {'venta':round(v,0),'rec':round(abs(r),0),'cam':round(abs(c),0),
            'rec_pct':round(abs(r)/v,4) if v else 0,'cam_pct':round(abs(c)/v,4) if v else 0,
            'fac':f,'no_e':no_e,'efect':round(f/padron,4) if padron else 0,'kg':round(kg,1)}

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

# ── RUTAS ─────────────────────────────────────────────────────────────────────
route_index = []; client_map = {}
for rep_id, grp in vc.groupby('reparto'):
    if pd.isna(rep_id): continue
    ch   = str(grp['chofer'].iloc[0]).strip()
    fec  = grp['fecha_str'].iloc[0]
    cam  = si(grp['camion'].iloc[0])
    vgrp = grp[grp['tipo_venta']=='Venta']
    tot  = float(vgrp['importe_neto'].sum())
    pep  = float(vgrp[vgrp['proveedor']==PEPSICO]['importe_neto'].sum())
    mol  = float(vgrp[vgrp['proveedor']==MOLINOS]['importe_neto'].sum())
    sof  = float(vgrp[vgrp['proveedor']==SOFTYS]['importe_neto'].sum())
    oth  = tot - pep - mol - sof
    kg_tot = float(pd.to_numeric(vgrp['cantxcap'],errors='coerce').fillna(0).clip(0,5000).sum())
    # Rechazo total: cliente sin venta en este reparto
    venta_x_cli = vgrp.groupby('Cliente')['importe_neto'].sum()
    todos_cli   = set(grp['Cliente'].unique())
    rej = sum(1 for c in todos_cli if venta_x_cli.get(c,0) <= 0)
    clientes = []
    for cli_id, cg in grp.groupby('Cliente'):
        tipos = list(cg['tipo_venta'].fillna('Venta'))
        venta_cli = float(cg[cg['tipo_venta']=='Venta']['importe_neto'].sum())
        rt = venta_cli <= 0
        dv = 'Devolucion' in tipos and not rt
        cm2= 'Cambio' in tipos
        imp = int(cg[cg['tipo_venta']=='Venta']['importe_neto'].sum())
        cnt = int(cg[cg['tipo_venta']=='Venta']['Cantidad'].sum())
        raz = str(cg['Razon_Social'].iloc[0] or '')[:40]
        dir2= str(cg['Direccion'].iloc[0] or '')[:40]
        loc = str(cg['localidad'].iloc[0] or '')[:22]
        cmp = str(cg['Comprobante'].iloc[0] or '')
        fl  = 1 if rt else(2 if dv else(3 if cm2 else 0))
        clientes.append([si(cli_id),raz,dir2,loc,cmp,imp,cnt,fl])
    route_index.append({'rep':si(rep_id),'ch':ch,'f':str(fec),'cam':cam,
        'n':len(clientes),'tot':round(tot,0),'rej':rej,'kg':round(kg_tot,1),
        'pep':round(pep,0),'mol':round(mol,0),'sof':round(sof,0),'oth':round(oth,0)})
    client_map[str(si(rep_id))]=clientes
route_index.sort(key=lambda x:(x['f'],x['ch']))
print(f"  Rutas: {len(route_index)} repartos")

venta_list=[]
for ch, df_ch in vc.groupby('chofer'):
    bol=df_ch.groupby('Comprobante')['tipo_venta'].apply(list).reset_index()
    bol['ne']=bol['tipo_venta'].apply(lambda ts:all(t=='Devolucion' for t in ts))
    e=int((~bol['ne']).sum()); ne=int(bol['ne'].sum())
    dev_ch=df_ch[df_ch['tipo_venta']=='Devolucion']
    rp=dev_ch.groupby('proveedor').agg(n=('importe_neto','count'),imp=('importe_neto','sum')).reset_index()
    cam_ch=df_ch[df_ch['tipo_venta']=='Cambio']
    ip=cam_ch.groupby('proveedor').agg(n=('importe_neto','count'),imp=('importe_neto','sum')).reset_index()
    venta_list.append({'ch':str(ch),'e':e,'ne':ne,
        'rp':{r['proveedor']:{'n':int(r['n']),'imp':round(float(abs(r['imp'])),0)} for _,r in rp.iterrows()},
        'ip':{r['proveedor']:{'n':int(r['n']),'imp':round(float(abs(r['imp'])),0)} for _,r in ip.iterrows()}})

# ── REINCIDENTES ──────────────────────────────────────────────────────────────
comp_cls2 = vc.groupby('Comprobante')['tipo_venta'].apply(list).reset_index()
comp_cls2['all_dev'] = comp_cls2['tipo_venta'].apply(lambda ts: all(t=='Devolucion' for t in ts))
rej_comps2 = set(comp_cls2[comp_cls2['all_dev']]['Comprobante'])
rej_cli = (vc[vc['Comprobante'].isin(rej_comps2)]
           .groupby('Cliente')
           .agg(n=('Comprobante','nunique'),
                razon=('Razon_Social','first'),
                loc=('localidad','first'),
                imp=('importe_neto','sum'),
                vendedor=('cod_ven','first'),
                choferes=('chofer', lambda x: ', '.join(sorted(set(str(v) for v in x))[:3])),
                fechas=('fecha_str', lambda x: ', '.join(sorted(set(str(v) for v in x))[:5])))
           .reset_index())
# Proveedores con mayor rechazo por cliente
rej_prov_cli = (vc[vc['Comprobante'].isin(rej_comps2)]
                .groupby(['Cliente','proveedor'])['importe_neto'].sum().abs()
                .reset_index().sort_values('importe_neto',ascending=False))
prov_por_cli = {}
for cli, grp in rej_prov_cli.groupby('Cliente'):
    prov_por_cli[int(cli)] = [{'prov':str(r['proveedor']),'imp':round(float(r['importe_neto']),0)}
                               for _,r in grp.head(3).iterrows()]

reinc_list = [{'cid':int(r['Cliente']),'razon':str(r['razon'])[:35],
               'loc':str(r['loc'])[:22] if r['loc'] else '',
               'n':int(r['n']),'imp':round(float(abs(r['imp'])),0),
               'vendedor':str(int(r['vendedor'])) if pd.notna(r.get('vendedor')) and r.get('vendedor') != '' else '-',
               'choferes':str(r['choferes'])[:40],'fechas':str(r['fechas']),
               'provs': prov_por_cli.get(int(r['Cliente']),[]) }
              for _,r in rej_cli[rej_cli['n']>1].sort_values('n',ascending=False).head(50).iterrows()]

# ── CARTONES ──────────────────────────────────────────────────────────────────
cart_records = []
cart_path = find("cartones.xlsx")
if cart_path:
    try:
        cart = pd.read_excel(cart_path)
        if 'FechaSalidaCamion' in cart.columns:
            cart['FechaSalidaCamion'] = pd.to_datetime(cart['FechaSalidaCamion'])
            cart['fecha_str'] = cart['FechaSalidaCamion'].dt.strftime('%Y-%m-%d')
            cart['semana']    = cart['FechaSalidaCamion'].dt.isocalendar().week.astype(int)
            for _,r in cart.iterrows():
                bs=si(r.get('cajasbienret',0)); bi=si(r.get('cajasbienretdev',0))
                cart_records.append({'chofer':str(r.get('razon_social','')).strip(),
                    'fecha':str(r['fecha_str']),'semana':int(r['semana']),
                    'b_sal':bs,'b_ing':bi,'retorno':round(bi/bs,4) if bs>0 else 0})
        print(f"  Cartones: {len(cart_records)} registros")
    except Exception as e:
        print(f"  Cartones: error {e}")
else:
    print("  Cartones: no encontrado (opcional)")

# ── APP RECHAZOS + CONCILIACION ───────────────────────────────────────────────
app_records = []
conc_data   = {'app_ges':[],'app_only':[],'ges_only':[],'kpis':{}}
app_path = find("Registro_de_Rechazos.xlsx")
if app_path:
    try:
        app = pd.read_excel(app_path)
        app['Fecha']      = pd.to_datetime(app['Fecha'], errors='coerce')
        app['fecha_str']  = app['Fecha'].dt.strftime('%Y-%m-%d')
        app['chofer_norm']= app['Chofer'].str.strip().str.upper()
        app['chofer_ges'] = app['chofer_norm'].map(CHOFER_MAP).fillna(app['chofer_norm'])
        for _,r in app.iterrows():
            app_records.append({
                'id':     str(r.get('ID','')),
                'fecha':  str(r['fecha_str']),
                'chofer': str(r['chofer_ges']),
                'cliente':str(r.get('CLIENTE','')) if pd.notna(r.get('CLIENTE')) else '',
                'vendedor':str(r.get('Vendedor','')),
                'motivo': str(r.get('Motivo','')),
                'obs':    str(r.get('Observacion','')) if pd.notna(r.get('Observacion')) else '',
                'foto':   str(r.get('Foto','')) if pd.notna(r.get('Foto')) else '',
                'resp':   str(r.get('Respuesta Vendedor','')) if pd.notna(r.get('Respuesta Vendedor')) else '',
                'estado': str(r.get('Estado','')),
            })
        print(f"  App rechazos: {len(app_records)} registros")
        # Conciliacion: cruce por CLIENTE + FECHA
        vc['fecha_str_up'] = vc['fecha_str']
        ges_grp = vc[vc['tipo_venta']=='Devolucion'].groupby(['Cliente','fecha_str']).agg(
            imp=('importe_neto','sum'),
            chofer=('chofer','first'),
            razon=('Razon_Social','first')
        ).reset_index()
        ges_grp['imp'] = ges_grp['imp'].abs().round(0)
        ges_grp['key'] = ges_grp['Cliente'].astype(str) + '_' + ges_grp['fecha_str']
        ges_dict = {r['key']:{'cliente':str(r['Cliente']),'razon':str(r['razon'])[:35],
                              'chofer':str(r['chofer']),'fecha':str(r['fecha_str']),
                              'imp':float(r['imp'])}
                    for _,r in ges_grp.iterrows()}

        # App: use CLIENTE code + fecha as key
        app['cliente_str'] = app['CLIENTE'].astype(str).str.strip() if 'CLIENTE' in app.columns else ''
        app['key'] = app['cliente_str'] + '_' + app['fecha_str']
        app_dict = {}
        for _,r in app.iterrows():
            cli = str(r.get('CLIENTE','')) if pd.notna(r.get('CLIENTE')) else ''
            if not cli or cli in ('nan',''):
                continue
            k = cli + '_' + str(r['fecha_str'])
            if k not in app_dict:
                app_dict[k] = {
                    'cliente': cli,
                    'chofer':  str(r['chofer_ges']),
                    'fecha':   str(r['fecha_str']),
                    'motivo':  str(r.get('Motivo','')),
                    'vendedor':str(r.get('Vendedor','')),
                    'resp':    str(r.get('Respuesta Vendedor','')) if pd.notna(r.get('Respuesta Vendedor')) else '',
                    'estado':  str(r.get('Estado','')),
                    'n': 0
                }
            app_dict[k]['n'] += 1

        app_keys = set(app_dict.keys()); ges_keys = set(ges_dict.keys())
        for k in app_keys & ges_keys:
            g = ges_dict[k]
            conc_data['app_ges'].append({**app_dict[k],'imp':g['imp'],'razon':g['razon']})
        for k in app_keys - ges_keys:
            conc_data['app_only'].append({**app_dict[k],'imp':0,'razon':''})
        for k in ges_keys - app_keys:
            g = ges_dict[k]
            conc_data['ges_only'].append({'cliente':g['cliente'],'razon':g['razon'],
                'chofer':g['chofer'],'fecha':g['fecha'],'imp':g['imp']})
        with_resp = sum(1 for r in conc_data['app_ges'] if r.get('resp',''))
        sin_resp  = sum(1 for r in conc_data['app_ges'] if not r.get('resp',''))
        pct_saved = round(len(conc_data['app_only'])/len(app_dict)*100,1) if len(app_dict)>0 else 0
        conc_data['kpis'] = {
            'app_ges':len(conc_data['app_ges']),'app_only':len(conc_data['app_only']),'ges_only':len(conc_data['ges_only']),
            'imp_app_ges':round(sum(r['imp'] for r in conc_data['app_ges']),0),
            'imp_ges_only':round(sum(r['imp'] for r in conc_data['ges_only']),0),
            'with_resp':with_resp,'sin_resp':sin_resp,'pct_saved':pct_saved,'total_app':len(app_records)
        }
        print(f"  Conciliacion: {len(conc_data['app_ges'])} app+ges, {len(conc_data['app_only'])} solo app, {len(conc_data['ges_only'])} solo ges")
    except Exception as e:
        print(f"  App rechazos: error {e}")
else:
    print("  App rechazos: no encontrado (opcional)")

# ── DEPOSITO ──────────────────────────────────────────────────────────────────
dep_data = {'faltante':[],'sobrante':[],'roturas':[],'consumo':[],'vencido':[]}
mov_path = find("movimientos.xlsx")
if mov_path:
    try:
        mov = pd.read_excel(mov_path)
        art_prov = dict(zip(vc['Art'].dropna().astype(int), vc['proveedor'])) if 'Art' in vc.columns else {}
        def get_prov(code):
            try: return art_prov.get(int(code),'Sin proveedor')
            except: return 'Sin proveedor'
        fecha_col = next((c for c in ['stockmov_fecha','fecha','Fecha'] if c in mov.columns), None)
        periodo_label = ''
        if fecha_col:
            fechas = pd.to_datetime(mov[fecha_col], errors='coerce').dropna()
            if len(fechas): periodo_label = f"{fechas.min().strftime('%d/%m')}-{fechas.max().strftime('%d/%m/%Y')}"
        def mov_rows(df_m):
            rows=[]
            for _,r in df_m.iterrows():
                u=abs(sf(r.get('stockmov_cantidad',r.get('cantidad',0))))
                cu=sf(r.get('costo',0))
                pv=get_prov(r.get('articulo_codigo',r.get('codigo',0)))
                rows.append({'desc':str(r.get('descripcion',''))[:50],'prov':pv,
                              'u':int(u),'cu':round(cu,2),'tot':round(u*cu,2),'fecha':periodo_label})
            return rows
        tipo_col = 'stockmov_tipo' if 'stockmov_tipo' in mov.columns else 'tipo'
        dep_col  = 'deposito_nombre' if 'deposito_nombre' in mov.columns else None
        tra = mov[mov[tipo_col]=='TRA'].copy() if dep_col else pd.DataFrame()
        if dep_col and len(tra):
            rot  = tra[tra[dep_col].astype(str).str.lower().str.contains('roturas deposito', na=False)]
            cons = tra[tra[dep_col].astype(str).str.lower().str.contains('consumo', na=False)]
            venc = tra[tra[dep_col].astype(str).str.lower().str.contains('vencido', na=False)]
            dep_data['roturas'] = mov_rows(rot)
            dep_data['consumo'] = mov_rows(cons)
            dep_data['vencido'] = mov_rows(venc)
        if 'CON' in mov[tipo_col].values:
            con=mov[mov[tipo_col]=='CON'].copy()
            con['prov']=con['articulo_codigo'].apply(get_prov) if 'articulo_codigo' in con.columns else 'Sin proveedor'
            con_net=con.groupby(['articulo_codigo','descripcion','prov']).agg(
                neto=('stockmov_cantidad','sum'),cu=('costo','first')).reset_index()
            con_net=con_net[con_net['cu']>0]
            con_neg=con_net[con_net['neto']<0].copy(); con_neg['u']=con_neg['neto'].abs()
            con_pos=con_net[con_net['neto']>0].copy(); con_pos['u']=con_pos['neto']
            dep_data['faltante']=[{'desc':str(r['descripcion'])[:50],'prov':str(r['prov']),
                'u':int(r['u']),'cu':round(float(r['cu']),2),'tot':round(float(r['u']*r['cu']),2),'fecha':periodo_label}
                for _,r in con_neg.sort_values('u',ascending=False).iterrows()]
            dep_data['sobrante']=[{'desc':str(r['descripcion'])[:50],'prov':str(r['prov']),
                'u':int(r['u']),'cu':round(float(r['cu']),2),'tot':round(float(r['u']*r['cu']),2),'fecha':periodo_label}
                for _,r in con_pos.sort_values('u',ascending=False).iterrows()]
        print(f"  Deposito: {len(dep_data['faltante'])} falt, {len(dep_data['sobrante'])} sobr, {len(dep_data['roturas'])} rot, {len(dep_data['consumo'])} cons, {len(dep_data['vencido'])} venc")
    except Exception as e:
        print(f"  Deposito: error {e}")
else:
    print("  Movimientos: no encontrado (opcional)")

# ── SERIALIZAR ────────────────────────────────────────────────────────────────
print("\nSerializando...")
print(f"  Reincidentes: {len(reinc_list)}")

conc_js = 'var D_CONC=' + json.dumps(conc_data, ensure_ascii=True, separators=(',',':')) + ';'

DATA_JS = '\n'.join([
    make_chunks('D_KPIS',   rej_kpis),
    make_chunks('D_MOTIVO', by_motivo),
    make_chunks('D_CHOFER', by_chofer),
    make_chunks('D_PROV',   prov_metrics_list),
    make_chunks('D_CHPROV', chofer_prov_map),
    make_chunks('D_VENTA',  venta_list),
    make_chunks('D_ROUTES', route_index),
    make_chunks('D_CLI',    client_map),
    f"var D_PERIODO={json.dumps(PERIODO)};",
    f"var D_PROVS={json.dumps(sorted(vc['proveedor'].dropna().str.strip().unique().tolist()),ensure_ascii=True,separators=(',',':'))};",
    f"var D_CHS={json.dumps(sorted(vc['chofer'].dropna().str.strip().unique().tolist()),ensure_ascii=True,separators=(',',':'))};",
    make_chunks('D_CART',   cart_records),
    make_chunks('D_APP',    app_records),
    conc_js,
    f"var D_DEP={json.dumps(dep_data,ensure_ascii=True,separators=(',',':'))};",
    f"var D_REINC={json.dumps(reinc_list,ensure_ascii=True,separators=(',',':'))};",
])

# ── INYECTAR ──────────────────────────────────────────────────────────────────
dash_path = os.path.join(BASE_DIR, 'dashboard_operativo.html')
if not os.path.exists(dash_path):
    print(f"ERROR: dashboard_operativo.html no encontrado"); sys.exit(1)

with open(dash_path,'r',encoding='utf-8') as f: html = f.read()

ds = html.find('<!-- DATA_START -->')
de = html.find('<!-- DATA_END -->')
if ds > 0 and de > 0:
    sc_open  = html.rfind('<script>', 0, ds)
    sc_close = html.find('</script>', de) + len('</script>')
    new_block = '<script><!-- DATA_START -->\n' + DATA_JS + '\n<!-- DATA_END --></script>'
    html = html[:sc_open] + new_block + html[sc_close:]
    print(f"  Datos inyectados via marcadores: {len(DATA_JS)//1024}KB")
else:
    auth_tag = html.find('<script src="auth.js">')
    if auth_tag > 0:
        new_block = '<script><!-- DATA_START -->\n' + DATA_JS + '\n<!-- DATA_END --></script>\n'
        html = html[:auth_tag] + new_block + html[auth_tag:]
        print(f"  Datos inyectados antes de auth.js: {len(DATA_JS)//1024}KB")
    else:
        body_end = html.rfind('</body>')
        html = html[:body_end] + '\n<script><!-- DATA_START -->\n' + DATA_JS + '\n<!-- DATA_END --></script>\n' + html[body_end:]
        print(f"  Datos inyectados antes de </body>: {len(DATA_JS)//1024}KB")

build_ts = str(int(datetime.now().timestamp()))
html = html.replace('__BUILD_TS__', build_ts)

with open(dash_path,'w',encoding='utf-8') as f: f.write(html)
print(f"\nDashboard: {os.path.getsize(dash_path)//1024}KB")
print(f"Completado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
print("=" * 60)
