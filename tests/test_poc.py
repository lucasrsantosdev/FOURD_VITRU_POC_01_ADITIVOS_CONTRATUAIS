import tempfile
import unittest
from pathlib import Path
from poc_aditivos.engine import executar, validar_trilha

BASE = Path(__file__).resolve().parents[1] / "dados_ficticios"

class TestAditivos(unittest.TestCase):
    def test_demo_integracao_e_risco(self):
        with tempfile.TemporaryDirectory() as pasta:
            saida = Path(pasta) / "output"
            r = executar(BASE, saida)
            self.assertEqual(r["aditivos"], 3)
            self.assertEqual(r["pendentes_aceite"], 1)
            self.assertEqual(r["aceites_simulados"], 2)
            self.assertEqual(r["excecoes"], 1)
            self.assertTrue(validar_trilha(saida / "auditoria_hash_chain.jsonl"))
            self.assertIn("RISCO_SEM_LASTRO_PENDENTE_ACEITE", (saida / "conciliacao_financeira.csv").read_text(encoding="utf-8-sig"))
    def test_determinismo(self):
        with tempfile.TemporaryDirectory() as pasta:
            a = Path(pasta) / "a"
            b = Path(pasta) / "b"
            self.assertEqual(executar(BASE, a), executar(BASE, b))
            self.assertEqual((a / "aditivos.csv").read_bytes(), (b / "aditivos.csv").read_bytes())
            self.assertEqual((a / "auditoria_hash_chain.jsonl").read_bytes(), (b / "auditoria_hash_chain.jsonl").read_bytes())

if __name__ == "__main__":
    unittest.main()
