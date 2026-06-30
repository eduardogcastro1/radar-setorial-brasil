import json, re, urllib.request, shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path('/root/radar-setorial-brasil')
UPDATED = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
BASE = '/radar-setorial-brasil'

sectors = {
    'energia': {
        'name': 'Energia elétrica', 'slug': 'energia', 'status': 'Defensivo / dividendos', 'kind': 'ativo',
        'summary': 'Fluxos mais previsíveis, regulação forte e sensibilidade à taxa de juros.',
        'home_note': 'Defensivo, regulado, dividendos e sensibilidade a juros.',
        'thesis': 'O setor elétrico brasileiro tende a ser menos cíclico do que varejo, indústria ou commodities, porque parte relevante da receita vem de contratos, concessões e regulação. A leitura correta exige separar transmissão, distribuição, geração e empresas integradas.',
        'executive': 'Setor defensivo, bom para dividendos, mas a comparação exige separar transmissão, distribuição e geração.',
        'drivers': ['Queda de juros melhora o valor presente dos fluxos e o apelo de dividendos.', 'Regulação e revisão tarifária podem alterar percepção de risco.', 'Alavancagem, capex e eventos hidrológicos diferenciam as teses.'],
        'companies': [
            {'ticker':'EGIE3.SA','symbol':'EGIE3','name':'Engie Brasil','segment':'Geração / renováveis','quality':8.2,'dividends':7.8,'growth':5.8,'risk':3.0,'note':'Perfil defensivo, geração de caixa consistente e histórico de dividendos.'},
            {'ticker':'ALUP11.SA','symbol':'ALUP11','name':'Alupar','segment':'Transmissão + geração','quality':7.2,'dividends':7.4,'growth':5.2,'risk':3.8,'note':'Portfólio balanceado entre transmissão e geração, com perfil defensivo.'},
            {'ticker':'TAEE11.SA','symbol':'TAEE11','name':'Taesa','segment':'Transmissão','quality':7.0,'dividends':8.4,'growth':4.2,'risk':3.8,'note':'Transmissora previsível, forte apelo de dividendos e crescimento mais limitado.'},
            {'ticker':'EQTL3.SA','symbol':'EQTL3','name':'Equatorial Energia','segment':'Distribuição','quality':7.4,'dividends':4.2,'growth':7.2,'risk':5.2,'note':'Histórico de turnaround em distribuição, mais crescimento e mais risco operacional.'},
            {'ticker':'ENGI11.SA','symbol':'ENGI11','name':'Energisa','segment':'Distribuição','quality':6.8,'dividends':4.8,'growth':6.6,'risk':5.0,'note':'Distribuidora relevante, exposta a execução, capex e dinâmica regulatória.'},
            {'ticker':'NEOE3.SA','symbol':'NEOE3','name':'Neoenergia','segment':'Distribuição + geração','quality':6.2,'dividends':5.2,'growth':6.2,'risk':5.4,'note':'Operação grande e diversificada, com alavancagem e execução como pontos de atenção.'},
            {'ticker':'AURE3.SA','symbol':'AURE3','name':'Auren Energia','segment':'Geração','quality':6.0,'dividends':5.8,'growth':5.6,'risk':5.0,'note':'Plataforma de geração com tese ligada a portfólio e preços de energia.'},
            {'ticker':'CMIG4.SA','symbol':'CMIG4','name':'Cemig','segment':'Integrada','quality':5.8,'dividends':6.8,'growth':4.8,'risk':5.8,'note':'Empresa integrada com desconto potencial, mas maior ruído político/regulatório.'},
            {'ticker':'CPFE3.SA','symbol':'CPFE3','name':'CPFL Energia','segment':'Distribuição + geração','quality':6.2,'dividends':6.0,'growth':4.8,'risk':4.8,'note':'Companhia integrada, boa escala e sensibilidade a ciclos de investimento.'},
        ]
    },
    'bancos': {
        'name': 'Bancos', 'slug': 'bancos', 'status': 'Ciclo de crédito / ROE', 'kind': 'ativo',
        'summary': 'Setor sensível a juros, inadimplência, crescimento de crédito e qualidade de capital.',
        'home_note': 'Crédito, inadimplência, ROE, capital e ciclo de Selic.',
        'thesis': 'Bancos combinam escala, marca, distribuição e gestão de risco. Incumbentes costumam ter rentabilidade mais previsível; bancos públicos carregam ruído político; bancos digitais e de investimento têm mais opcionalidade e volatilidade.',
        'executive': 'Setor mais cíclico que energia: ROE, inadimplência e qualidade do crédito são os principais filtros.',
        'drivers': ['Queda de juros pode estimular crédito, mas comprime spreads em alguns segmentos.', 'Inadimplência e provisões determinam a qualidade do lucro.', 'ROE, capital e eficiência operacional separam bancos de primeira linha dos demais.'],
        'companies': [
            {'ticker':'ITUB4.SA','symbol':'ITUB4','name':'Itaú Unibanco','segment':'Incumbente privado','quality':8.8,'dividends':6.8,'growth':6.2,'risk':3.0,'note':'Banco de alta qualidade, escala, diversificação e histórico consistente de rentabilidade.'},
            {'ticker':'BBAS3.SA','symbol':'BBAS3','name':'Banco do Brasil','segment':'Banco público','quality':7.4,'dividends':8.0,'growth':5.4,'risk':5.0,'note':'ROE e dividendos fortes, com desconto estrutural por risco político e governança.'},
            {'ticker':'BBDC4.SA','symbol':'BBDC4','name':'Bradesco','segment':'Incumbente privado','quality':6.8,'dividends':6.4,'growth':5.2,'risk':4.6,'note':'Franquia grande em recuperação operacional, ainda sob escrutínio de rentabilidade.'},
            {'ticker':'SANB11.SA','symbol':'SANB11','name':'Santander Brasil','segment':'Incumbente privado','quality':6.6,'dividends':6.0,'growth':5.0,'risk':4.4,'note':'Banco relevante, com tese ligada a eficiência, crédito e retomada de rentabilidade.'},
            {'ticker':'BPAC11.SA','symbol':'BPAC11','name':'BTG Pactual','segment':'Banco de investimento','quality':8.0,'dividends':4.6,'growth':8.2,'risk':5.2,'note':'Crescimento e execução fortes, mais sensível a mercado de capitais e valuation.'},
            {'ticker':'NUBR33.SA','symbol':'NUBR33','name':'Nubank BDR','segment':'Banco digital','quality':7.0,'dividends':1.0,'growth':9.0,'risk':6.8,'note':'Tese de crescimento e plataforma digital, com maior volatilidade e menor foco em dividendos.'},
            {'ticker':'BRSR6.SA','symbol':'BRSR6','name':'Banrisul','segment':'Banco regional','quality':5.6,'dividends':6.8,'growth':3.8,'risk':6.0,'note':'Banco regional com apelo de dividendos, mas menor escala e liquidez.'},
            {'ticker':'BPAN4.SA','symbol':'BPAN4','name':'Banco Pan','segment':'Crédito ao consumidor','quality':4.8,'dividends':2.2,'growth':5.8,'risk':7.2,'note':'Mais exposto a crédito ao consumidor, funding, inadimplência e execução.'},
        ]
    }
}
upcoming = [
    ('saneamento','Saneamento','Concessões, regulação, capex e universalização.'),
    ('commodities','Commodities','Minério, petróleo, câmbio, China e distribuição de caixa.'),
    ('varejo','Varejo','Juros, renda, consumo, margem e competição.'),
    ('saude','Saúde','Sinistralidade, ocupação, ticket e consolidação.'),
]

def fetch_chart(ticker):
    url = f'https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range=1y&interval=1wk'
    try:
        req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=12) as r: data = json.load(r)
        res = (data.get('chart',{}).get('result') or [])[0]
        ts = res.get('timestamp') or []
        closes = res.get('indicators',{}).get('quote',[{}])[0].get('close') or []
        out=[]
        for t,c in zip(ts, closes):
            if c is not None:
                out.append({'date': datetime.fromtimestamp(t, timezone.utc).strftime('%Y-%m-%d'), 'close': round(float(c),2)})
        return out
    except Exception:
        return []

def pct(a,b): return round((b/a-1)*100,1) if a and b else 0.0
for sector in sectors.values():
    for c in sector['companies']:
        rows=fetch_chart(c['ticker'])
        if rows:
            first,last=rows[0]['close'],rows[-1]['close']
            idx6=max(0,len(rows)-27)
            c.update(price=last, return12m=pct(first,last), return6m=pct(rows[idx6]['close'],last), normalized=[{'date':r['date'],'value':round(r['close']/first*100,2)} for r in rows])
        else:
            c.update(price=0, return12m=0, return6m=0, normalized=[])
        momentum_score=max(0,min(10,5+c['return6m']/4))
        c['score']=round(c['quality']*.34+c['dividends']*.20+c['growth']*.22+momentum_score*.14+(10-c['risk'])*.10,1)
    sector['companies'].sort(key=lambda x:x['score'], reverse=True)
    vals=sector['companies']
    for field,out in [('score','score'),('return6m','momentum6m'),('return12m','momentum12m'),('risk','risk'),('dividends','dividends'),('growth','growth')]:
        sector[out]=round(sum(c[field] for c in vals)/len(vals),1)

all_companies=[c for s in sectors.values() for c in s['companies']]
best_score=max(all_companies,key=lambda c:c['score'])
best_momentum=max(all_companies,key=lambda c:c['return6m'])
worst_momentum=min(all_companies,key=lambda c:c['return6m'])

def ensure_dir(p): Path(p).mkdir(parents=True, exist_ok=True)
def write(rel, content):
    p=ROOT/rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(content, encoding='utf-8')
def cls(v): return 'pos' if v >= 0 else 'neg'
def fmtp(v): return f'{v:.1f}%'
def price(v): return 'N/D' if not v else f'R$ {v:.2f}'
def link(path): return BASE + path

style = r'''
:root{--bg:#07080a;--panel:#0d0f14;--line:rgba(255,255,255,.09);--text:#f7f8f8;--muted:#89909c;--soft:#d8dde8;--accent:#7170ff;--green:#17c083;--red:#fb7185;--yellow:#f59e0b;--blue:#60a5fa}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:radial-gradient(circle at 15% -12%,rgba(113,112,255,.30),transparent 32%),radial-gradient(circle at 90% 20%,rgba(23,192,131,.12),transparent 28%),linear-gradient(180deg,#07080a,#020305 70%);color:var(--text);font-family:Inter,system-ui,sans-serif}a{color:inherit;text-decoration:none}.wrap{max-width:1240px;margin:0 auto;padding:26px 20px 70px}.nav{position:sticky;top:0;z-index:5;backdrop-filter:blur(18px);background:rgba(7,8,10,.72);border-bottom:1px solid rgba(255,255,255,.05)}.navin{max-width:1240px;margin:0 auto;padding:14px 20px;display:flex;align-items:center;justify-content:space-between;gap:18px}.brand{display:flex;align-items:center;gap:11px;font-weight:650}.logo{width:32px;height:32px;border-radius:10px;border:1px solid var(--line);background:linear-gradient(135deg,var(--accent),var(--green));box-shadow:0 0 36px rgba(113,112,255,.3)}.links{display:flex;gap:16px;color:var(--muted);font-size:13px;flex-wrap:wrap}.cta,.button{border:1px solid var(--line);padding:9px 13px;border-radius:999px;background:rgba(255,255,255,.035);color:var(--soft);display:inline-flex;gap:8px;align-items:center}.button.primary{background:linear-gradient(135deg,rgba(113,112,255,.28),rgba(23,192,131,.18));border-color:rgba(113,112,255,.35)}.hero{padding:70px 0 38px;display:grid;grid-template-columns:1.05fr .95fr;gap:26px;align-items:center}h1{font-size:clamp(43px,7vw,82px);line-height:.94;letter-spacing:-2px;margin:0 0 20px;font-weight:650}h2{letter-spacing:-.7px}.lead{font-size:19px;line-height:1.62;color:var(--muted);max-width:760px;margin:0 0 25px}.badges,.actions{display:flex;flex-wrap:wrap;gap:10px}.badge{border:1px solid var(--line);background:rgba(255,255,255,.035);color:var(--soft);padding:8px 11px;border-radius:999px;font-size:12px}.panel,.sector-card,.company-card,.watch,.method-card{min-width:0;overflow:hidden}.panel{background:rgba(255,255,255,.028);border:1px solid var(--line);border-radius:22px;padding:22px;box-shadow:inset 0 1px rgba(255,255,255,.04)}.kpis{display:grid;grid-template-columns:repeat(2,1fr);gap:13px}.kpi{padding:18px;border-radius:18px;background:rgba(255,255,255,.04);border:1px solid var(--line)}.kpi small{color:var(--muted);display:block;margin-bottom:8px}.kpi strong{font-size:24px}.section{margin-top:38px}.section-head{display:flex;align-items:flex-end;justify-content:space-between;gap:20px;margin-bottom:16px}.sub{color:var(--muted);line-height:1.55;margin-top:-4px}.sectors{display:grid;grid-template-columns:repeat(4,1fr);gap:13px}.sector-card{padding:18px;border-radius:20px;background:rgba(255,255,255,.03);border:1px solid var(--line)}.sector-card.active{background:linear-gradient(145deg,rgba(113,112,255,.18),rgba(23,192,131,.09));border-color:rgba(113,112,255,.32)}.sector-card span{font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted)}.sector-card p{color:var(--muted);line-height:1.45}.sector-card b{font-size:13px;color:var(--soft)}.grid{display:grid;grid-template-columns:1.2fr .8fr;gap:16px}.grid2{display:grid;grid-template-columns:1fr 1fr;gap:16px}.grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:13px}.editorial{display:grid;grid-template-columns:.75fr 1.25fr;gap:16px}.callout{padding:22px;border-radius:22px;background:linear-gradient(135deg,rgba(113,112,255,.18),rgba(23,192,131,.10));border:1px solid rgba(113,112,255,.32)}.callout b{display:block;font-size:13px;text-transform:uppercase;letter-spacing:.08em;color:#c7c8ff;margin-bottom:10px}.callout p{font-size:20px;line-height:1.45;margin:0}.textblock{color:var(--soft);line-height:1.72}.textblock ul{padding-left:20px}canvas{width:100%!important;max-width:100%;height:390px!important;display:block}table{width:100%;border-collapse:collapse;font-size:14px}th,td{padding:13px 10px;border-bottom:1px solid var(--line);text-align:left}th{color:var(--muted);font-weight:500}td span{display:block;color:var(--muted);font-size:12px;margin-top:3px}td em{font-style:normal;color:var(--muted)}.pos{color:var(--green)}.neg{color:var(--red)}.company-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:13px}.company-card{padding:17px;border:1px solid var(--line);border-radius:18px;background:rgba(255,255,255,.028)}.company-card strong{font-size:20px}.company-card span{display:block;color:var(--muted);font-size:12px;margin-top:4px}.company-card p{color:var(--muted);line-height:1.5;min-height:68px}.scorebar{height:8px;background:rgba(255,255,255,.08);border-radius:999px;overflow:hidden}.scorebar i{display:block;height:100%;background:linear-gradient(90deg,var(--accent),var(--green))}.company-card footer{display:flex;justify-content:space-between;margin-top:12px;font-size:12px}.watch{padding:18px;border:1px solid var(--line);border-radius:18px;background:rgba(255,255,255,.03)}.watch b{display:block;color:var(--muted);font-size:12px;margin-bottom:8px}.watch strong{font-size:24px}.watch p{color:var(--muted);line-height:1.5}.foot{margin-top:50px;color:var(--muted);font-size:13px}.method-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:13px}.method-card{padding:17px;border-radius:18px;border:1px solid var(--line);background:rgba(255,255,255,.025)}.method-card b{display:block;margin-bottom:8px}.method-card p{color:var(--muted);line-height:1.55}.breadcrumb{color:var(--muted);font-size:13px;margin-top:12px}.breadcrumb a{color:var(--soft)}@media(max-width:940px){.hero,.grid,.grid2,.editorial{grid-template-columns:1fr}.sectors,.company-grid{grid-template-columns:repeat(2,1fr)}.grid3,.method-grid{grid-template-columns:1fr}}@media(max-width:560px){.links{display:none}.sectors,.company-grid,.kpis{grid-template-columns:1fr}h1{letter-spacing:-1px}}
'''
write('assets/style.css', style)
write('assets/data.js', 'window.RADAR_DATA = ' + json.dumps({'updated': UPDATED, 'sectors': sectors}, ensure_ascii=False, separators=(',', ':')) + ';\n')
chart_js = r'''
Chart.defaults.color='#89909c';Chart.defaults.borderColor='rgba(255,255,255,.08)';
const palette=['#7170ff','#17c083','#60a5fa','#f59e0b','#fb7185','#a78bfa','#22d3ee','#f472b6','#94a3b8'];
function comps(key){return window.RADAR_DATA.sectors[key].companies;}
function lineChart(id,key){const arr=comps(key).filter(c=>c.normalized&&c.normalized.length);const labels=arr.length?arr[0].normalized.map(p=>p.date.slice(5)):[];new Chart(document.getElementById(id),{type:'line',data:{labels,datasets:arr.map((c,i)=>({label:c.symbol,data:c.normalized.map(p=>p.value),borderColor:palette[i%palette.length],backgroundColor:palette[i%palette.length],tension:.28,pointRadius:0,borderWidth:2}))},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'bottom',labels:{boxWidth:10}}},scales:{y:{ticks:{callback:v=>Number(v).toFixed(0)}}}}});}
function barChart(id,key){const arr=comps(key);new Chart(document.getElementById(id),{type:'bar',data:{labels:arr.map(c=>c.symbol),datasets:[{label:'Score',data:arr.map(c=>c.score),backgroundColor:arr.map((_,i)=>palette[i%palette.length]),borderRadius:8}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{y:{min:0,max:10}}}});}
function sectorRadar(id){new Chart(document.getElementById(id),{type:'radar',data:{labels:['Score','Momentum 6m','Dividendos','Crescimento','Baixo risco'],datasets:Object.entries(window.RADAR_DATA.sectors).map(([k,s],i)=>({label:s.name,data:[s.score,Math.max(0,Math.min(10,5+s.momentum6m/4)),s.dividends,s.growth,10-s.risk],borderColor:palette[i],backgroundColor:palette[i]+'33',pointBackgroundColor:palette[i]}))},options:{responsive:true,maintainAspectRatio:false,scales:{r:{min:0,max:10,grid:{color:'rgba(255,255,255,.08)'},angleLines:{color:'rgba(255,255,255,.08)'}}},plugins:{legend:{position:'bottom'}}}});}
'''
write('assets/charts.js', chart_js)

def head(title):
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{title}</title><meta name="description" content="Radar Setorial Brasil: dashboards e leitura editorial de setores da bolsa brasileira."><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet"><link rel="stylesheet" href="{BASE}/assets/style.css"><script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script></head><body>'''

def nav():
    return f'''<nav class="nav"><div class="navin"><a class="brand" href="{link('/')}"><span class="logo"></span>Radar Setorial Brasil</a><div class="links"><a href="{link('/setores/')}">Setores</a><a href="{link('/setores/energia/')}">Energia</a><a href="{link('/setores/bancos/')}">Bancos</a><a class="cta" href="{link('/metodologia/')}">Metodologia</a></div></div></nav>'''

def foot(extra=''):
    return f'''<footer class="foot">Gerado por Hermes Agent e publicado com GitHub Pages. Última atualização: {UPDATED}. {extra}</footer></main></body></html>'''

def table_rows(sec):
    return '\n'.join(f"<tr><td><b>{c['symbol']}</b><span>{c['name']}</span></td><td><em>{c['segment']}</em></td><td>{c['score']:.1f}</td><td class='{cls(c['return6m'])}'>{fmtp(c['return6m'])}</td><td class='{cls(c['return12m'])}'>{fmtp(c['return12m'])}</td><td>{price(c['price'])}</td></tr>" for c in sec['companies'])

def cards(sec):
    return '\n'.join(f"<article class='company-card'><div><strong>{c['symbol']}</strong><span>{c['name']}</span></div><p>{c['note']}</p><div class='scorebar'><i style='width:{c['score']*10:.0f}%'></i></div><footer><span>Score {c['score']:.1f}/10</span><span class='{cls(c['return6m'])}'>6m {fmtp(c['return6m'])}</span></footer></article>" for c in sec['companies'])

home_sector_cards = ''.join(f'''<a class="sector-card active" href="{link('/setores/'+k+'/')}"><span>Ativo</span><h3>{s['name']}</h3><p>{s['home_note']}</p><b>{len(s['companies'])} empresas · Abrir setor →</b></a>''' for k,s in sectors.items()) + ''.join(f'''<article class="sector-card"><span>Em breve</span><h3>{name}</h3><p>{desc}</p><b>Pipeline</b></article>''' for slug,name,desc in upcoming[:2])
ranking_rows = ''.join(f'''<tr><td><b>{s['name']}</b><span>{s['status']}</span></td><td>{s['score']:.1f}</td><td class="{cls(s['momentum6m'])}">{fmtp(s['momentum6m'])}</td><td class="{cls(s['momentum12m'])}">{fmtp(s['momentum12m'])}</td><td>{s['risk']:.1f}</td></tr>''' for s in sectors.values())

home = head('Radar Setorial Brasil') + nav() + f'''<main class="wrap" id="top"><section class="hero"><div><h1>Radar Setorial Brasil</h1><p class="lead">Dashboards e leitura editorial para entender setores da bolsa brasileira. A homepage é a porta de entrada: resumo executivo, ranking setorial e caminhos para páginas dedicadas de cada setor.</p><div class="badges"><span class="badge">Visual escuro</span><span class="badge">60% editorial / 40% dashboard</span><span class="badge">URLs em português</span><span class="badge">Atualizado em {UPDATED}</span></div><div class="actions" style="margin-top:22px"><a class="button primary" href="{link('/setores/')}">Ver setores</a><a class="button" href="{link('/metodologia/')}">Ver metodologia</a></div></div><aside class="panel"><div class="kpis"><div class="kpi"><small>Setores ativos</small><strong>{len(sectors)}</strong></div><div class="kpi"><small>Empresas</small><strong>{len(all_companies)}</strong></div><div class="kpi"><small>Top score</small><strong>{best_score['symbol']}</strong></div><div class="kpi"><small>Momentum 6m</small><strong>{best_momentum['symbol']}</strong></div></div></aside></section><section class="section"><div class="section-head"><div><h2>Setores disponíveis</h2><p class="sub">Clique em um setor ativo para abrir uma página própria com tese, gráficos, tabela e cards de empresas.</p></div></div><div class="sectors">{home_sector_cards}</div></section><section class="section grid"><div class="panel"><h2>Ranking setorial V3</h2><p class="sub">Comparação resumida entre os setores ativos.</p><canvas id="sectorRadar"></canvas></div><div class="panel"><h2>Resumo comparativo</h2><table><thead><tr><th>Setor</th><th>Score</th><th>6m</th><th>12m</th><th>Risco</th></tr></thead><tbody>{ranking_rows}</tbody></table></div></section><section class="section"><div class="section-head"><div><h2>Última leitura</h2><p class="sub">Uma leitura editorial curta para orientar onde investigar primeiro.</p></div></div><div class="grid3"><div class="watch"><b>Melhor score composto</b><strong>{best_score['symbol']}</strong><p>{best_score['name']} lidera a amostra combinando qualidade, crescimento, dividendos, risco e momentum.</p></div><div class="watch"><b>Melhor momentum 6m</b><strong>{best_momentum['symbol']}</strong><p>{fmtp(best_momentum['return6m'])} nos últimos 6 meses dentro da amostra acompanhada.</p></div><div class="watch"><b>Ponto de atenção</b><strong>{worst_momentum['symbol']}</strong><p>{fmtp(worst_momentum['return6m'])} em 6 meses. Vale investigar se é oportunidade, deterioração ou ruído temporário.</p></div></div></section><script src="{BASE}/assets/data.js"></script><script src="{BASE}/assets/charts.js"></script><script>sectorRadar('sectorRadar');</script>''' + foot()
write('index.html', home)

sector_index_cards = ''.join(f'''<a class="sector-card active" href="{link('/setores/'+k+'/')}"><span>Ativo</span><h3>{s['name']}</h3><p>{s['summary']}</p><b>{len(s['companies'])} empresas · Score {s['score']:.1f}</b></a>''' for k,s in sectors.items()) + ''.join(f'''<article class="sector-card"><span>Em breve</span><h3>{name}</h3><p>{desc}</p><b>Pipeline</b></article>''' for slug,name,desc in upcoming)
setores_page = head('Setores — Radar Setorial Brasil') + nav() + f'''<main class="wrap"><div class="breadcrumb"><a href="{link('/')}">Home</a> / Setores</div><section class="hero"><div><h1>Setores</h1><p class="lead">Índice de cobertura do Radar Setorial Brasil. Energia elétrica e Bancos estão ativos; novos setores entram como páginas próprias, mantendo a homepage limpa.</p><div class="badges"><span class="badge">2 ativos</span><span class="badge">4 em pipeline</span><span class="badge">Template único por setor</span></div></div><aside class="panel"><h2>Como usar</h2><p class="sub">Abra um setor ativo para ver tese editorial, drivers, gráficos, tabela comparativa e cards de empresas.</p></aside></section><section class="section"><div class="sectors">{sector_index_cards}</div></section>''' + foot()
write('setores/index.html', setores_page)

for key,sec in sectors.items():
    page = head(f"{sec['name']} — Radar Setorial Brasil") + nav() + f'''<main class="wrap"><div class="breadcrumb"><a href="{link('/')}">Home</a> / <a href="{link('/setores/')}">Setores</a> / {sec['name']}</div><section class="hero"><div><h1>{sec['name']}</h1><p class="lead">{sec['summary']}</p><div class="badges"><span class="badge">{sec['status']}</span><span class="badge">{len(sec['companies'])} empresas</span><span class="badge">Score setorial {sec['score']:.1f}</span><span class="badge">Atualizado em {UPDATED}</span></div><div class="actions" style="margin-top:22px"><a class="button" href="{link('/setores/')}">← Voltar para setores</a><a class="button" href="{link('/metodologia/')}">Metodologia</a></div></div><aside class="panel"><div class="kpis"><div class="kpi"><small>Momentum 6m</small><strong class="{cls(sec['momentum6m'])}">{fmtp(sec['momentum6m'])}</strong></div><div class="kpi"><small>Retorno 12m</small><strong class="{cls(sec['momentum12m'])}">{fmtp(sec['momentum12m'])}</strong></div><div class="kpi"><small>Risco médio</small><strong>{sec['risk']:.1f}</strong></div><div class="kpi"><small>Empresas</small><strong>{len(sec['companies'])}</strong></div></div></aside></section><section class="section"><div class="editorial"><div class="callout"><b>Resumo executivo</b><p>{sec['executive']}</p></div><div class="panel textblock"><p>{sec['thesis']}</p><ul>{''.join('<li>'+d+'</li>' for d in sec['drivers'])}</ul></div></div></section><section class="section grid"><div class="panel"><h2>{sec['name']} — performance 12 meses</h2><p class="sub">Ações/BDRs normalizados em 100 para comparar trajetória relativa.</p><canvas id="lineChart"></canvas></div><div class="panel"><h2>{sec['name']} — score</h2><p class="sub">Score demonstrativo combinando fatores editoriais, momentum e risco.</p><canvas id="barChart"></canvas></div></section><section class="section"><div class="panel"><h2>Tabela — {sec['name']}</h2><table><thead><tr><th>Empresa</th><th>Perfil</th><th>Score</th><th>6m</th><th>12m</th><th>Preço</th></tr></thead><tbody>{table_rows(sec)}</tbody></table></div></section><section class="section"><div class="section-head"><div><h2>Cards de empresas</h2><p class="sub">Primeira camada para futuras páginas individuais de cada companhia.</p></div></div><div class="company-grid">{cards(sec)}</div></section><script src="{BASE}/assets/data.js"></script><script src="{BASE}/assets/charts.js"></script><script>lineChart('lineChart','{key}');barChart('barChart','{key}');</script>''' + foot()
    write(f'setores/{key}/index.html', page)

met = head('Metodologia — Radar Setorial Brasil') + nav() + f'''<main class="wrap"><div class="breadcrumb"><a href="{link('/')}">Home</a> / Metodologia</div><section class="hero"><div><h1>Metodologia</h1><p class="lead">Esta página separa o que é dado observado de mercado do que é leitura editorial. O radar é uma ferramenta de triagem e aprendizado, não recomendação de investimento.</p><div class="badges"><span class="badge">Dados reais de preço</span><span class="badge">Score editorial</span><span class="badge">Não é recomendação</span></div></div><aside class="panel"><h2>Resumo</h2><p class="sub">Preços e retornos são coletados de fonte pública; notas de qualidade, dividendos, crescimento e risco são heurísticas transparentes para demonstrar o produto.</p></aside></section><section class="section"><div class="method-grid"><div class="method-card"><b>1. Dados de mercado</b><p>Preços e retornos vêm da API pública de gráficos do Yahoo Finance, com intervalo semanal e possível atraso/indisponibilidade.</p></div><div class="method-card"><b>2. Score editorial</b><p>Qualidade, dividendos, crescimento e risco são notas heurísticas para demonstrar a experiência. O score final também incorpora momentum e penalização de risco.</p></div><div class="method-card"><b>3. Uso correto</b><p>Use como triagem: identificar setores, riscos e empresas que merecem investigação mais profunda.</p></div></div></section><section class="section grid2"><div class="panel textblock"><h2>O que entra no score</h2><ul><li>Qualidade do negócio/franquia.</li><li>Perfil de dividendos.</li><li>Crescimento/opcionalidade.</li><li>Momentum de mercado.</li><li>Risco operacional, regulatório, financeiro ou político.</li></ul></div><div class="panel textblock"><h2>Roadmap metodológico</h2><ul><li>Substituir notas heurísticas por indicadores fundamentalistas auditáveis.</li><li>Criar pesos transparentes por setor.</li><li>Salvar histórico de scores.</li><li>Adicionar páginas individuais por empresa.</li></ul></div></section><section class="section"><div class="panel textblock"><p><b>Aviso:</b> este site é demonstrativo e educacional. Não constitui recomendação de investimento, oferta, solicitação de compra/venda ou análise regulada de valores mobiliários.</p></div></section>''' + foot()
write('metodologia/index.html', met)

# Clean old no-longer-used build helper if present
for f in ['build_v3.py']:
    pass
write('README.md', f'''# Radar Setorial Brasil

Produto híbrido de análise setorial: dashboard visual + leitura editorial.

## V3 — arquitetura multipágina

Estrutura publicada no GitHub Pages:

- `/` — homepage executiva
- `/setores/` — índice de setores
- `/setores/energia/` — página do setor elétrico
- `/setores/bancos/` — página de bancos
- `/metodologia/` — metodologia e limitações

Características:

- visual escuro mantido;
- homepage 60% editorial / 40% dashboard;
- páginas de setor com template único;
- URLs em português;
- CSS e dados separados em `assets/`.

Atualizado em: {UPDATED}

Aviso: página demonstrativa e educacional, não é recomendação de investimento.
''')
print('V3 generated', UPDATED)
print('files: index.html, setores/index.html, setores/energia/index.html, setores/bancos/index.html, metodologia/index.html, assets/*')
print('scores', {k: {'score':s['score'], 'mom6m':s['momentum6m']} for k,s in sectors.items()})
