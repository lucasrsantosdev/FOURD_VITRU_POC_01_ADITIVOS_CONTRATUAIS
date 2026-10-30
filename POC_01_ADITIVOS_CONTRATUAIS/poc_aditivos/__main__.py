import argparse
import json
from pathlib import Path
from .engine import executar, validar_trilha

parser = argparse.ArgumentParser(description="POC 01 - Aditivos contratuais fictícios")
parser.add_argument("--entrada", type=Path, default=Path(__file__).resolve().parents[1] / "dados_ficticios")
parser.add_argument("--saida", type=Path, default=Path(__file__).resolve().parents[1] / "saida_demo")
args = parser.parse_args()
resumo = executar(args.entrada, args.saida)
assert validar_trilha(args.saida / "auditoria_hash_chain.jsonl"), "Trilha não íntegra"
print(json.dumps(resumo, indent=2, ensure_ascii=False))
print(f"Saída: {args.saida.resolve()}")
