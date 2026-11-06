# Incremento POC 01 — Aditivos, aprovacao e renegociacao

Laboratorio **independente e executavel** (stdlib), com contratos e analistas ficticios.
Mantem o escopo original de aditivos e acrescenta controles transversais:

- **Dor 6 / H6.5:** alerta de renegociacoes repetidas (limite 3 **APENAS ILUSTRATIVO**, nao homologado).
- **Dor 9:** cadeia de hashes para historico de alteracoes, versoes, aceite e evidencia.
- **Dor 11 / H11.1:** separacao de funcoes na concessao de credito de Medicina; nao implica que o processo atual nao tenha revisao.

## Rodar a partir da raiz do repositorio

```powershell
python -m upgrade_dores_6_9_11 --output .\upgrade_dores_6_9_11\output
python -m unittest discover -s .\upgrade_dores_6_9_11\tests -v
```

Saidas geradas: `trilha_aditivos.csv`, `analise_creditos.csv`, `alertas.csv`, `manifesto.json`.
**Limites:** hashes locais nao constituem assinatura digital nem storage imutavel; aprovacao requer controle externo de identidade e perfis. Nada aqui acessa sistemas corporativos.

## Evolucao real

Solicitar tabelas/view de contrato, aditivo, aceite, historico, politica de renegociacao e trilha de aprovacao;
validar chaves e segregacao dos perfis de Medicina com Operacao, Juridico e TI;
nao publicar evidencias pessoais no Git. Veja `docs/SEGURANCA_E_DADOS_REAIS.md`.
