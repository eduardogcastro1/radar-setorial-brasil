import json, re, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
p = ROOT / 'assets/data.js'
raw = p.read_text(encoding='utf-8')
data = json.loads(re.search(r'window\.RADAR_DATA\s*=\s*(.*);\s*$', raw, re.S).group(1))
UPDATED = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
data['updated'] = UPDATED

new_sectors = {
    'saneamento': {
        'name': 'Saneamento', 'slug': 'saneamento', 'status': 'Concessões / capex', 'kind': 'ativo',
        'summary': 'Setor regulado, intensivo em capital e ligado à universalização dos serviços básicos.',
        'home_note': 'Concessões, regulação, capex, tarifas e universalização.',
        'executive': 'Saneamento combina tese estrutural de longo prazo com risco de execução, regulação e necessidade elevada de investimento.',
        'thesis': 'O saneamento brasileiro é uma tese de infraestrutura regulada com horizonte longo. O valor depende de concessões, revisões tarifárias, eficiência operacional e capacidade de financiar capex sem destruir retorno. A leitura principal é separar empresas com escala, governança e acesso a capital de histórias mais regionais e sensíveis a regulação.',
        'drivers': ['Universalização exige capex elevado e disciplina de execução.', 'Privatizações e concessões podem destravar eficiência, mas aumentam escrutínio regulatório.', 'Tarifas, inadimplência e custo de capital são variáveis críticas para retorno.'],
        'companies': [
            {'ticker':'SBSP3.SA','symbol':'SBSP3','name':'Sabesp','segment':'Saneamento / concessões','quality':8.0,'dividends':4.8,'growth':7.2,'risk':4.6,'note':'Maior escala do setor, tese ligada a eficiência pós-privatização, concessões e capex.'},
            {'ticker':'CSMG3.SA','symbol':'CSMG3','name':'Copasa','segment':'Saneamento regional','quality':6.1,'dividends':6.8,'growth':4.4,'risk':5.6,'note':'Ativo regional com apelo de dividendos, mas menor opcionalidade e mais sensibilidade regulatória.'},
            {'ticker':'SAPR11.SA','symbol':'SAPR11','name':'Sanepar','segment':'Saneamento regional','quality':6.4,'dividends':6.3,'growth':4.8,'risk':5.4,'note':'Perfil defensivo/regulado, com retorno dependente de tarifas, capex e governança.'},
        ]
    },
    'commodities': {
        'name': 'Commodities', 'slug': 'commodities', 'status': 'Ciclo global / câmbio', 'kind': 'ativo',
        'summary': 'Setor exposto a petróleo, minério, aço, celulose, câmbio e China.',
        'home_note': 'Petróleo, minério, aço, celulose, dólar, China e ciclo global.',
        'executive': 'Commodities é o bloco mais macro do radar: alto potencial de caixa, mas grande dependência de preços internacionais.',
        'thesis': 'Empresas de commodities tendem a gerar muito caixa nos ciclos favoráveis, mas carregam volatilidade estrutural. A análise exige separar petróleo, minério, siderurgia e papel/celulose. Câmbio, China, disciplina de capital, dividendos e risco político são os filtros centrais.',
        'drivers': ['China e atividade global influenciam minério, aço e celulose.', 'Petróleo e câmbio afetam caixa, capex e dividendos.', 'Governança, alocação de capital e intervenção política podem pesar tanto quanto preço da commodity.'],
        'companies': [
            {'ticker':'PETR4.SA','symbol':'PETR4','name':'Petrobras','segment':'Petróleo integrado','quality':7.2,'dividends':8.2,'growth':4.8,'risk':6.6,'note':'Geração de caixa elevada e dividendos, com risco político e exposição ao petróleo.'},
            {'ticker':'VALE3.SA','symbol':'VALE3','name':'Vale','segment':'Minério de ferro','quality':7.4,'dividends':6.8,'growth':4.6,'risk':6.0,'note':'Tese muito ligada a China, minério, disciplina de capital e passivos socioambientais.'},
            {'ticker':'PRIO3.SA','symbol':'PRIO3','name':'Prio','segment':'Óleo & gás independente','quality':7.8,'dividends':1.5,'growth':8.4,'risk':6.2,'note':'Histórico de execução e crescimento, com maior sensibilidade a petróleo e M&A.'},
            {'ticker':'GGBR4.SA','symbol':'GGBR4','name':'Gerdau','segment':'Siderurgia','quality':6.6,'dividends':6.2,'growth':4.4,'risk':5.8,'note':'Siderurgia cíclica, dependente de construção, indústria, China e spreads.'},
            {'ticker':'CSNA3.SA','symbol':'CSNA3','name':'CSN','segment':'Siderurgia / mineração','quality':5.2,'dividends':4.8,'growth':4.8,'risk':7.2,'note':'Maior alavancagem e volatilidade, com exposição a aço, mineração e execução.'},
            {'ticker':'SUZB3.SA','symbol':'SUZB3','name':'Suzano','segment':'Celulose','quality':7.0,'dividends':3.8,'growth':6.2,'risk':5.8,'note':'Líder global em celulose, sensível a preços internacionais, câmbio e alavancagem.'},
            {'ticker':'KLBN11.SA','symbol':'KLBN11','name':'Klabin','segment':'Papel e celulose','quality':6.8,'dividends':4.8,'growth':5.6,'risk':5.4,'note':'Portfólio mais diversificado, mas ainda dependente de ciclo de celulose e capex.'},
            {'ticker':'BRAV3.SA','symbol':'BRAV3','name':'Brava Energia','segment':'Óleo & gás independente','quality':5.4,'dividends':1.0,'growth':7.0,'risk':7.6,'note':'Tese de produção independente com risco operacional, dívida, integração e petróleo.'},
        ]
    },
    'varejo': {
        'name': 'Varejo / Consumo', 'slug': 'varejo', 'status': 'Juros / renda / margem', 'kind': 'ativo',
        'summary': 'Setor cíclico, sensível a juros, crédito, renda disponível e competição.',
        'home_note': 'Juros, renda, inflação, e-commerce, margem e competição.',
        'executive': 'Varejo é o termômetro do ciclo doméstico: melhora quando juros, renda e crédito ajudam; sofre quando margem e competição apertam.',
        'thesis': 'O varejo brasileiro é heterogêneo. Supermercados e atacarejo têm dinâmica mais defensiva; moda e bens duráveis são mais cíclicos; e-commerce e pet carregam crescimento, mas também pressão competitiva. A leitura central é separar empresas com execução e balanço resiliente de histórias dependentes de reabertura de múltiplos.',
        'drivers': ['Juros e crédito definem apetite para consumo discricionário.', 'Inflação, renda e emprego afetam volume e mix.', 'Margem, estoque, logística e competição digital diferenciam vencedores e perdedores.'],
        'companies': [
            {'ticker':'LREN3.SA','symbol':'LREN3','name':'Lojas Renner','segment':'Moda / consumo discricionário','quality':7.0,'dividends':3.8,'growth':5.6,'risk':5.4,'note':'Marca e execução fortes, mas sensível a ciclo de consumo e crédito.'},
            {'ticker':'MGLU3.SA','symbol':'MGLU3','name':'Magazine Luiza','segment':'E-commerce / bens duráveis','quality':4.8,'dividends':0.5,'growth':6.8,'risk':8.0,'note':'Alta opcionalidade em ciclo de juros, mas risco elevado de margem e competição.'},
            {'ticker':'ASAI3.SA','symbol':'ASAI3','name':'Assaí','segment':'Atacarejo','quality':6.8,'dividends':1.8,'growth':7.0,'risk':5.8,'note':'Crescimento em atacarejo, com atenção a alavancagem, margem e execução.'},
            {'ticker':'PCAR3.SA','symbol':'PCAR3','name':'Pão de Açúcar','segment':'Varejo alimentar','quality':4.8,'dividends':1.0,'growth':4.8,'risk':7.4,'note':'Varejo alimentar em reestruturação, com risco elevado de margem, dívida e execução.'},
            {'ticker':'GMAT3.SA','symbol':'GMAT3','name':'Grupo Mateus','segment':'Varejo alimentar regional','quality':6.6,'dividends':1.5,'growth':7.4,'risk':5.4,'note':'Crescimento regional relevante, com risco de execução e expansão.'},
            {'ticker':'VIVA3.SA','symbol':'VIVA3','name':'Vivara','segment':'Joias / consumo premium','quality':7.2,'dividends':2.5,'growth':7.0,'risk':5.0,'note':'Marca premium e expansão, sensível a consumo discricionário e execução.'},
            {'ticker':'BHIA3.SA','symbol':'BHIA3','name':'Casas Bahia','segment':'Varejo de bens duráveis','quality':3.8,'dividends':0.0,'growth':5.2,'risk':8.6,'note':'Turnaround de alto risco, dependente de crédito, margem, dívida e execução.'},
        ]
    },
    'saude': {
        'name': 'Saúde', 'slug': 'saude', 'status': 'Sinistralidade / consolidação', 'kind': 'ativo',
        'summary': 'Setor ligado a hospitais, diagnósticos, planos, verticalização e envelhecimento populacional.',
        'home_note': 'Sinistralidade, ocupação, tíquete, reajustes e consolidação.',
        'executive': 'Saúde tem demanda estrutural, mas o retorno depende de controle de sinistralidade, integração e disciplina de capital.',
        'thesis': 'Saúde é uma tese estrutural no Brasil, apoiada por envelhecimento populacional e demanda resiliente. Mas as empresas têm perfis muito diferentes: hospitais dependem de ocupação e mix; diagnósticos dependem de volume e tíquete; planos de saúde sofrem com sinistralidade; e farmacêuticas carregam risco regulatório e de portfólio.',
        'drivers': ['Sinistralidade e reajustes definem rentabilidade dos planos.', 'Ocupação, mix e integração afetam hospitais e redes verticalizadas.', 'Consolidação, dívida e execução pós-aquisições são riscos recorrentes.'],
        'companies': [
            {'ticker':'RDOR3.SA','symbol':'RDOR3','name':'Rede D’Or','segment':'Hospitais','quality':7.6,'dividends':1.5,'growth':7.2,'risk':5.6,'note':'Rede hospitalar líder, com crescimento e execução como principais filtros.'},
            {'ticker':'FLRY3.SA','symbol':'FLRY3','name':'Fleury','segment':'Diagnósticos','quality':7.0,'dividends':5.0,'growth':5.4,'risk':4.8,'note':'Diagnósticos premium, marca forte e sensibilidade a volume/tíquete.'},
            {'ticker':'HAPV3.SA','symbol':'HAPV3','name':'Hapvida','segment':'Planos verticalizados','quality':5.8,'dividends':0.5,'growth':7.2,'risk':7.2,'note':'Grande escala e verticalização, mas sinistralidade e integração seguem críticos.'},
            {'ticker':'ODPV3.SA','symbol':'ODPV3','name':'Odontoprev','segment':'Planos odontológicos','quality':7.2,'dividends':6.5,'growth':3.8,'risk':3.8,'note':'Perfil defensivo, caixa e dividendos, com crescimento mais limitado.'},
            {'ticker':'BLAU3.SA','symbol':'BLAU3','name':'Blau Farmacêutica','segment':'Farmacêutica','quality':5.8,'dividends':2.2,'growth':5.6,'risk':6.4,'note':'Tese ligada a portfólio, capacidade produtiva e regulação.'},
            {'ticker':'ONCO3.SA','symbol':'ONCO3','name':'Oncoclínicas','segment':'Oncologia','quality':5.6,'dividends':0.5,'growth':7.0,'risk':7.4,'note':'Crescimento em oncologia, com atenção a dívida, execução e margem.'},
            {'ticker':'PNVL3.SA','symbol':'PNVL3','name':'Dimed/Panvel','segment':'Farmácias','quality':6.0,'dividends':2.0,'growth':5.8,'risk':5.8,'note':'Varejo farmacêutico regional, com expansão e competição como filtros.'},
        ]
    }
}

def fetch_chart(ticker):
    url = f'https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range=1y&interval=1wk'
    try:
        req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=12) as r:
            j = json.load(r)
        res = (j.get('chart',{}).get('result') or [])[0]
        ts = res.get('timestamp') or []
        closes = res.get('indicators',{}).get('quote',[{}])[0].get('close') or []
        rows=[]
        for t,c in zip(ts, closes):
            if c is not None:
                rows.append({'date':datetime.fromtimestamp(t, timezone.utc).strftime('%Y-%m-%d'), 'close':round(float(c),2)})
        return rows
    except Exception as e:
        print('fetch failed', ticker, e)
        return []

def pct(a,b): return round((b/a-1)*100,1) if a and b else 0.0

def complete_sector(sec):
    for c in sec['companies']:
        rows = fetch_chart(c['ticker'])
        if rows:
            first,last=rows[0]['close'], rows[-1]['close']
            idx6=max(0, len(rows)-27)
            c['price']=last
            c['return12m']=pct(first,last)
            c['return6m']=pct(rows[idx6]['close'],last)
            c['normalized']=[{'date':r['date'], 'value':round(r['close']/first*100,2)} for r in rows]
        else:
            c['price']=0; c['return12m']=0; c['return6m']=0; c['normalized']=[]
        momentum=max(0,min(10,5+c['return6m']/4))
        c['score']=round(c['quality']*.34+c['dividends']*.20+c['growth']*.22+momentum*.14+(10-c['risk'])*.10,1)
    sec['companies'].sort(key=lambda x:x['score'], reverse=True)
    vals=sec['companies']
    for field,out in [('score','score'),('return6m','momentum6m'),('return12m','momentum12m'),('risk','risk'),('dividends','dividends'),('growth','growth')]:
        sec[out]=round(sum(c[field] for c in vals)/len(vals),1)
    return sec

for key, sec in new_sectors.items():
    data['sectors'][key] = complete_sector(sec)

# Recompute existing sector aggregates defensively if needed
for sec in data['sectors'].values():
    vals=sec['companies']
    for field,out in [('score','score'),('return6m','momentum6m'),('return12m','momentum12m'),('risk','risk'),('dividends','dividends'),('growth','growth')]:
        sec[out]=round(sum(c.get(field,0) for c in vals)/len(vals),1)

p.write_text('window.RADAR_DATA = ' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n', encoding='utf-8')
print('updated sectors', list(data['sectors']))
for k,s in data['sectors'].items():
    print(k, 'companies', len(s['companies']), 'score', s['score'], 'mom6m', s['momentum6m'])
