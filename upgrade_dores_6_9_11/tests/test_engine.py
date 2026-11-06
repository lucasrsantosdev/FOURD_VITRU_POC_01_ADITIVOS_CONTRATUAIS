import tempfile
import unittest
from pathlib import Path
from upgrade_dores_6_9_11.engine import analyze_aditivos, analyze_credito, sample, run

class TestContractControls(unittest.TestCase):
    def test_renegociacoes_e_aceite(self):
        findings, hist = analyze_aditivos(sample()['aditivos'])
        self.assertTrue(any(f['codigo']=='LIMITE_SIMULADO_RENEGOCIACOES_EXCEDIDO' for f in findings))
        self.assertTrue(any(f['codigo']=='EVIDENCIA_DE_ACEITE_AUSENTE' for f in findings))
        self.assertTrue(any(f['codigo']=='SEQUENCIA_DE_VERSAO_INCOMPLETA' for f in findings))
        self.assertEqual(hist[1]['hash_anterior'],hist[0]['hash_evento'])
    def test_segregacao(self):
        findings=analyze_credito(sample()['credito'])
        self.assertEqual(len(findings),3)
        self.assertEqual(set(f['objeto_id'] for f in findings),{'CRED-B','CRED-C'})
    def test_demo_reproduzivel(self):
        with tempfile.TemporaryDirectory() as d:
            x=run(d);y=run(d)
            self.assertEqual(x,y)
            self.assertTrue((Path(d)/'alertas.csv').exists())

if __name__=='__main__':unittest.main()
