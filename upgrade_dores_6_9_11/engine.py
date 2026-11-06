"""Extensao aditiva: aditivos e controle de aprovacao com dados exclusivamente sinteticos."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import date
from pathlib import Path

VERSION = 'poc01-v0.2-sintetica'


def sample():
    return {
        'aditivos': [
            {'contrato_id': 'CONTRATO-A', 'versao': 1, 'evento': 'adesao', 'data': '2026-01-10', 'valor': '1200.00', 'assinado': True, 'registro_origem': 'SIM-001'},
            {'contrato_id': 'CONTRATO-A', 'versao': 2, 'evento': 'renegociacao', 'data': '2026-03-10', 'valor': '1100.00', 'assinado': True, 'registro_origem': 'SIM-002'},
            {'contrato_id': 'CONTRATO-A', 'versao': 3, 'evento': 'renegociacao', 'data': '2026-05-10', 'valor': '1050.00', 'assinado': True, 'registro_origem': 'SIM-003'},
            {'contrato_id': 'CONTRATO-A', 'versao': 4, 'evento': 'renegociacao', 'data': '2026-07-10', 'valor': '1000.00', 'assinado': True, 'registro_origem': 'SIM-004'},
            {'contrato_id': 'CONTRATO-A', 'versao': 5, 'evento': 'renegociacao', 'data': '2026-09-10', 'valor': '950.00', 'assinado': False, 'registro_origem': 'SIM-005'},
            {'contrato_id': 'CONTRATO-B', 'versao': 1, 'evento': 'adesao', 'data': '2026-08-01', 'valor': '900.00', 'assinado': True, 'registro_origem': 'SIM-006'},
            {'contrato_id': 'CONTRATO-B', 'versao': 3, 'evento': 'aditivo', 'data': '2026-09-01', 'valor': '920.00', 'assinado': False, 'registro_origem': 'SIM-007'},
        ],
        'credito': [
            {'solicitacao_id': 'CRED-A', 'contrato_id': 'CONTRATO-A', 'produto': 'medicina', 'analista_id': 'ANALISTA-01', 'aprovador_id': 'GESTOR-02', 'decisao': 'aprovado', 'evidencia_id': 'EVD-01', 'data_decisao': '2026-01-09'},
            {'solicitacao_id': 'CRED-B', 'contrato_id': 'CONTRATO-B', 'produto': 'medicina', 'analista_id': 'ANALISTA-03', 'aprovador_id': 'ANALISTA-03', 'decisao': 'aprovado', 'evidencia_id': 'EVD-02', 'data_decisao': '2026-08-01'},
            {'solicitacao_id': 'CRED-C', 'contrato_id': 'CONTRATO-C', 'produto': 'medicina', 'analista_id': 'ANALISTA-04', 'aprovador_id': '', 'decisao': 'aprovado', 'evidencia_id': '', 'data_decisao': '2026-09-01'},
        ],
    }


def digest(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def analyze_aditivos(records, max_renegociacoes=3):
    """Regra do limite = parametro ilustrativo, nao controle homologado pela Vitru."""
    per_contract = {}
    for item in records:
        required = ('contrato_id','versao','evento','data','valor','assinado','registro_origem')
        if any(key not in item for key in required):
            raise ValueError('Campos obrigatorios ausentes em aditivo')
        date.fromisoformat(item['data'])
        per_contract.setdefault(item['contrato_id'], []).append(item)
    findings, timeline = [], []
    for contrato, items in sorted(per_contract.items()):
        items = sorted(items, key=lambda v: v['versao'])
        previous_hash = 'GENESIS'
        reneg = 0
        expected = 1
        for e in items:
            warnings=[]
            if e['versao'] != expected:
                warnings.append('SEQUENCIA_DE_VERSAO_INCOMPLETA')
            expected = e['versao'] + 1
            if not e['assinado']:
                warnings.append('EVIDENCIA_DE_ACEITE_AUSENTE')
            if not e['registro_origem']:
                warnings.append('REGISTRO_ORIGEM_AUSENTE')
            if e['evento'] == 'renegociacao':
                reneg += 1
                if reneg > max_renegociacoes:
                    warnings.append('LIMITE_SIMULADO_RENEGOCIACOES_EXCEDIDO')
            current_hash=digest({'anterior':previous_hash,'evento':e})
            timeline.append({**e,'hash_anterior':previous_hash,'hash_evento':current_hash})
            previous_hash=current_hash
            for warning in warnings:
                findings.append({'dor':'6' if 'RENEG' in warning else '9','hipotese':'H6.5' if 'RENEG' in warning else 'H9.1','objeto_id':contrato,'codigo':warning,'versao':e['versao']})
    return findings, timeline


def analyze_credito(records):
    findings=[]
    for r in records:
        if r['produto'] != 'medicina' or r['decisao'] != 'aprovado':
            continue
        if not r['aprovador_id'] or r['aprovador_id'] == r['analista_id']:
            findings.append({'dor':'11','hipotese':'H11.1','objeto_id':r['solicitacao_id'],'codigo':'SEM_REVISAO_INDEPENDENTE','versao':''})
        if not r['evidencia_id']:
            findings.append({'dor':'11','hipotese':'H11.1','objeto_id':r['solicitacao_id'],'codigo':'EVIDENCIA_DE_DECISAO_AUSENTE','versao':''})
    return findings


def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields, extrasaction='ignore');w.writeheader();w.writerows(rows)


def run(output):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    source=sample()
    alerts,history=analyze_aditivos(source['aditivos'])
    alerts+=analyze_credito(source['credito'])
    write_csv(output/'trilha_aditivos.csv',history,list(history[0]))
    write_csv(output/'analise_creditos.csv',source['credito'],list(source['credito'][0]))
    write_csv(output/'alertas.csv',alerts,['dor','hipotese','objeto_id','codigo','versao'])
    report={'versao':VERSION,'fonte':'100% SINTETICA / nao homologada','hash_entrada':digest(source),'aditivos':len(history),'creditos':len(source['credito']),'alertas':len(alerts),'politica_renegociacao':'limite 3 = exemplo parametrizavel, requer aprovacao'}
    (output/'manifesto.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    return report


def main():
    p=argparse.ArgumentParser(description='Controle de aditivos e aprovacao - laboratorio sintetico')
    p.add_argument('--output',default='upgrade_dores_6_9_11/output');a=p.parse_args()
    print(json.dumps(run(a.output),indent=2,ensure_ascii=False))

if __name__=='__main__':main()
