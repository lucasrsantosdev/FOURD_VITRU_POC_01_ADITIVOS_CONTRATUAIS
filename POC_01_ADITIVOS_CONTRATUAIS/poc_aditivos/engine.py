"""POC 01 — contratos acadêmicos com versionamento e controle de lastro.

DEMONSTRAÇÃO: sem acesso real ao Gioconda/Lyceum; aceite é sintético.
"""
from __future__ import annotations

import csv
import hashlib
import json
import sqlite3
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

CAMPOS_MONITORADOS = ("curso", "polo", "turma", "bolsa_percentual", "valor_mensal", "situacao")
EVENTOS_EXCECAO = {"CANCELAMENTO", "RESCISAO", "FALECIMENTO"}


def ler_csv(caminho: Path) -> list[dict[str, str]]:
    with caminho.open(encoding="utf-8-sig", newline="") as arquivo:
        return list(csv.DictReader(arquivo, delimiter=";"))


def gravar_csv(caminho: Path, linhas: list[dict], colunas: list[str]) -> None:
    with caminho.open("w", encoding="utf-8-sig", newline="") as arquivo:
        w = csv.DictWriter(arquivo, fieldnames=colunas, delimiter=";", extrasaction="ignore")
        w.writeheader()
        w.writerows(linhas)


def canonic(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256(obj: Any) -> str:
    return hashlib.sha256(canonic(obj).encode("utf-8")).hexdigest()


def dinheiro(valor: str) -> Decimal:
    try:
        return Decimal(str(valor).replace(",", ".")).quantize(Decimal(".01"))
    except InvalidOperation as exc:
        raise ValueError(f"Valor monetário inválido: {valor}") from exc


def gerar_documento(aditivo: dict[str, Any]) -> str:
    alteracoes = "\n".join(
        f"- **{campo}**: `{mudanca['anterior']}` → `{mudanca['novo']}`"
        for campo, mudanca in aditivo["diferencas"].items()
    )
    return f"""# MINUTA DEMONSTRATIVA — ADITIVO CONTRATUAL {aditivo['aditivo_id']}

> **NÃO É UM DOCUMENTO JURÍDICO, CONTRATO VÁLIDO OU COMPROVANTE DE ACEITE.**
> Dados integralmente fictícios. Aprovação jurídica, institucional e aceite válido são indispensáveis.

- Marca: **{aditivo['marca']}**
- Sistema acadêmico de origem (hipotético): **{aditivo['sistema']}**
- Contrato-base: `{aditivo['contrato_id']}` (versão preservada `{aditivo['versao_base']}`)
- Proposta de nova versão: `{aditivo['versao_proposta']}`
- Evento de origem: `{aditivo['evento_id']}` — `{aditivo['tipo_evento']}`
- Data do evento: `{aditivo['data_evento']}`
- Situação de demonstração: **{aditivo['status']}**
- Hash da proposta: `{aditivo['hash_proposta']}`

## Quadro de alterações propostas
{alteracoes}

## Condições da proposta
As cláusulas não alteradas permaneceriam regidas pelo instrumento-base, **sujeito à validação
jurídica**. A produção somente poderia reconhecer o aditivo após registro de aceite válido,
controle de eficácia e conferência das regras contratuais aplicáveis.

## Evidências
Evidência sintética: `{aditivo['evidencia_id'] or 'NÃO DISPONÍVEL'}`.
SHA-256 demonstra integridade do payload, **não autenticidade da assinatura**.

## Validação necessária na Vitru
Verificar: modelo de contrato por marca, termo/aditivo aplicável, representação legal,
registro de consentimento, data efetiva, proteção de dados, retroatividade e integração
com financeiro. O motor da POC nunca grava em sistemas reais.
"""


def executar(entrada: Path, saida: Path) -> dict[str, Any]:
    """Processamento determinístico e idempotente por evento para dados sintéticos."""
    saida.mkdir(parents=True, exist_ok=True)
    (saida / "minutas").mkdir(exist_ok=True)
    contratos_lista = ler_csv(entrada / "contratos.csv")
    eventos = ler_csv(entrada / "eventos_academicos.csv")
    evidencias = ler_csv(entrada / "evidencias_aceite_simulado.csv")
    cobrancas = ler_csv(entrada / "cobrancas.csv")
    contratos = {c["contrato_id"]: dict(c) for c in contratos_lista}
    if len(contratos) != len(contratos_lista):
        raise ValueError("Contratos duplicados na origem")
    evid_por_evento = {e["evento_id"]: e for e in evidencias}
    ids: set[str] = set()
    aditivos: list[dict[str, Any]] = []
    excecoes: list[dict[str, str]] = []
    auditoria: list[dict[str, Any]] = []
    hash_anterior = "GENESIS"
    propostas_pendentes: set[str] = set()
    versions = {cid: 1 for cid in contratos}

    def auditar(tipo: str, item: dict[str, Any]) -> None:
        nonlocal hash_anterior
        dados = {"sequencia": len(auditoria) + 1, "acao": tipo, "objeto": item, "hash_anterior": hash_anterior}
        digest = sha256(dados)
        auditoria.append({**dados, "hash_registro": digest})
        hash_anterior = digest

    for evento in sorted(eventos, key=lambda e: (e["data_evento"], e["evento_id"])):
        eid = evento["evento_id"]
        if eid in ids:
            auditar("EVENTO_DUPLICADO_IGNORADO", {"evento_id": eid})
            continue
        ids.add(eid)
        cid = evento["contrato_id"]
        if cid not in contratos:
            excecoes.append({"evento_id": eid, "contrato_id": cid, "motivo": "CONTRATO_NAO_ENCONTRADO"})
            auditar("EVENTO_REJEITADO", {"evento_id": eid, "motivo": "CONTRATO_NAO_ENCONTRADO"})
            continue
        contrato = contratos[cid]
        if contrato["sistema"] != evento["sistema"]:
            raise ValueError(f"Origem incompatível no evento {eid}")
        if cid in propostas_pendentes:
            excecoes.append({"evento_id": eid, "contrato_id": cid, "motivo": "ALTERACAO_CONCORRENTE_AGUARDANDO_ACEITE"})
            auditar("EVENTO_QUARENTENA", {"evento_id": eid, "motivo": "ALTERACAO_CONCORRENTE"})
            continue
        if evento["tipo_evento"] in EVENTOS_EXCECAO:
            excecoes.append({"evento_id": eid, "contrato_id": cid, "motivo": "EXIGE_FLUXO_JURIDICO_ESPECIFICO"})
            auditar("EXCECAO_JURIDICA", {"evento_id": eid, "tipo": evento["tipo_evento"]})
            continue
        alteracoes = json.loads(evento["novos_valores_json"])
        desconhecidos = set(alteracoes) - set(CAMPOS_MONITORADOS)
        if desconhecidos:
            raise ValueError(f"Campos não mapeados: {desconhecidos}")
        diferencas = {k: {"anterior": contrato[k], "novo": str(v)} for k, v in alteracoes.items() if str(v) != contrato[k]}
        if not diferencas:
            auditar("EVENTO_SEM_MUDANCA", {"evento_id": eid})
            continue
        evidencia = evid_por_evento.get(eid)
        status = "ACEITE_SIMULADO" if evidencia and evidencia["aceite_confirmado"] == "SIM" else "AGUARDANDO_ACEITE"
        versao_base = versions[cid]
        chave = {"contrato_id": cid, "evento_id": eid, "versao_base": versao_base, "diferencas": diferencas}
        proposta = {
            "aditivo_id": f"ADT-{eid}", "contrato_id": cid, "evento_id": eid,
            "sistema": contrato["sistema"], "marca": contrato["marca"], "aluno_id": contrato["aluno_id"],
            "tipo_evento": evento["tipo_evento"], "data_evento": evento["data_evento"],
            "versao_base": versao_base, "versao_proposta": versao_base + 1,
            "diferencas": diferencas, "status": status,
            "evidencia_id": evidencia["evidencia_id"] if status == "ACEITE_SIMULADO" else "",
            "hash_proposta": sha256(chave),
            "observacao": "SIMULACAO; SEM ACEITE JURIDICAMENTE COMPROVADO",
        }
        aditivos.append(proposta)
        auditar("ADITIVO_PROPOSTO", {"aditivo_id": proposta["aditivo_id"], "hash_proposta": proposta["hash_proposta"]})
        if status == "ACEITE_SIMULADO":
            # Somente o estado na POC é evoluído; não há gravação nos sistemas de origem.
            for campo, valor in alteracoes.items():
                contrato[campo] = str(valor)
            versions[cid] = versao_base + 1
            auditar("ACEITE_SINTETICO", {"aditivo_id": proposta["aditivo_id"], "evidencia": proposta["evidencia_id"]})
        else:
            propostas_pendentes.add(cid)
        (saida / "minutas" / f"{proposta['aditivo_id']}.md").write_text(gerar_documento(proposta), encoding="utf-8")

    conciliacoes: list[dict[str, str]] = []
    for cobranca in cobrancas:
        cid = cobranca["contrato_id"]
        if cid not in contratos:
            raise ValueError(f"Cobrança com contrato desconhecido: {cid}")
        contrato = contratos[cid]
        esperado = dinheiro(contrato["valor_mensal"])
        faturado = dinheiro(cobranca["valor_faturado"])
        if cid in propostas_pendentes:
            status = "RISCO_SEM_LASTRO_PENDENTE_ACEITE"
        elif any(e["contrato_id"] == cid and e["motivo"] == "EXIGE_FLUXO_JURIDICO_ESPECIFICO" for e in excecoes):
            status = "EXCECAO_JURIDICA_REVISAR"
        elif esperado != faturado:
            status = "DIVERGENCIA_VALOR_CONTRATO"
        else:
            status = "CONCILIADO_NA_SIMULACAO"
        conciliacoes.append({
            "contrato_id": cid, "aluno_id": contrato["aluno_id"], "marca": contrato["marca"],
            "competencia": cobranca["competencia"], "versao_referencia": str(versions[cid]),
            "valor_vigente_simulado": str(esperado), "valor_faturado": str(faturado),
            "diferenca": str(faturado - esperado), "status": status,
        })
        auditar("COBRANCA_CONFERIDA", {"contrato_id": cid, "status": status})

    gravar_csv(saida / "aditivos.csv", [{**a, "diferencas": canonic(a["diferencas"])} for a in aditivos],
               ["aditivo_id", "contrato_id", "evento_id", "sistema", "marca", "aluno_id", "tipo_evento", "data_evento", "versao_base", "versao_proposta", "diferencas", "status", "evidencia_id", "hash_proposta", "observacao"])
    gravar_csv(saida / "excecoes.csv", excecoes, ["evento_id", "contrato_id", "motivo"])
    gravar_csv(saida / "conciliacao_financeira.csv", conciliacoes, ["contrato_id", "aluno_id", "marca", "competencia", "versao_referencia", "valor_vigente_simulado", "valor_faturado", "diferenca", "status"])
    gravar_csv(saida / "estado_contratual_simulado.csv", [{**c, "versao": versions[cid]} for cid, c in contratos.items()],
               ["contrato_id", "aluno_id", "marca", "sistema", "curso", "polo", "turma", "bolsa_percentual", "valor_mensal", "situacao", "versao"])
    with (saida / "auditoria_hash_chain.jsonl").open("w", encoding="utf-8") as arq:
        for registro in auditoria:
            arq.write(canonic(registro) + "\n")
    banco = saida / "poc_aditivos.sqlite"
    if banco.exists():
        banco.unlink()
    with sqlite3.connect(banco) as conn:
        conn.executescript("""
        CREATE TABLE contratos (contrato_id TEXT PRIMARY KEY, marca TEXT, sistema TEXT, estado_json TEXT, versao INTEGER);
        CREATE TABLE aditivos (aditivo_id TEXT PRIMARY KEY, contrato_id TEXT, evento_id TEXT UNIQUE, status TEXT, diferencas_json TEXT, hash_proposta TEXT);
        CREATE TABLE conciliacao (contrato_id TEXT, competencia TEXT, status TEXT, diferenca TEXT);
        CREATE TABLE trilha_auditoria (sequencia INTEGER PRIMARY KEY, evento TEXT, hash_anterior TEXT, hash_registro TEXT);
        """)
        conn.executemany("INSERT INTO contratos VALUES (?,?,?,?,?)", [(cid, c["marca"], c["sistema"], canonic(c), versions[cid]) for cid, c in contratos.items()])
        conn.executemany("INSERT INTO aditivos VALUES (?,?,?,?,?,?)", [(a["aditivo_id"], a["contrato_id"], a["evento_id"], a["status"], canonic(a["diferencas"]), a["hash_proposta"]) for a in aditivos])
        conn.executemany("INSERT INTO conciliacao VALUES (?,?,?,?)", [(a["contrato_id"], a["competencia"], a["status"], a["diferenca"]) for a in conciliacoes])
        conn.executemany("INSERT INTO trilha_auditoria VALUES (?,?,?,?)", [(a["sequencia"], a["acao"], a["hash_anterior"], a["hash_registro"]) for a in auditoria])
    resumo = {"poc": "POC01_ADITIVOS", "dados": "100% FICTICIOS", "contratos": len(contratos),
              "eventos_unicos": len(ids), "aditivos": len(aditivos),
              "aceites_simulados": sum(a["status"] == "ACEITE_SIMULADO" for a in aditivos),
              "pendentes_aceite": sum(a["status"] == "AGUARDANDO_ACEITE" for a in aditivos),
              "excecoes": len(excecoes), "cobrancas_em_revisao": sum(c["status"] != "CONCILIADO_NA_SIMULACAO" for c in conciliacoes),
              "aviso": "Aceite simulado NAO equivale a assinatura ou validade juridica"}
    (saida / "resumo.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (saida / "RELATORIO_DEMO.md").write_text(
        "# POC 01 | Resultado da execução\n\n" +
        "**Dados 100% fictícios; nenhuma alteração em Gioconda ou Lyceum.**\n\n" +
        "| Indicador | Total |\n|---|---:|\n" +
        "".join(f"| {chave} | {valor} |\n" for chave, valor in resumo.items() if isinstance(valor, int)) +
        "\n## Controles demonstrados\n\nDetecção de alteração → minuta versionada → aceite sintético/pendência → "
        "conciliação da cobrança → trilha de auditoria encadeada em SHA-256.\n\n"
        "**Atenção:** o SHA-256 demonstra integridade, não prova consentimento do aluno.\n", encoding="utf-8")
    return resumo


def validar_trilha(caminho: Path) -> bool:
    anterior = "GENESIS"
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        registro = json.loads(linha)
        digest = registro.pop("hash_registro")
        if registro["hash_anterior"] != anterior or sha256(registro) != digest:
            return False
        anterior = digest
    return True
