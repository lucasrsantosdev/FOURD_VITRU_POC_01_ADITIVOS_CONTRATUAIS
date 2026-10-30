# Especificação funcional e técnica | POC 01

## Decisão: alternativa B do quadro — aditivos como padrão

A proposta não exige que todas as marcas sejam migradas ao Gioconda. A **política contratual** pode ser padronizada; a **implementação** deve respeitar os canais e integrações homologados de cada marca. Contrato-base permanece imutável. Aditivos formam uma cadeia versionada por vínculo contratual, nunca uma regravação silenciosa do contrato anterior.

### Fluxo futuro proposto

1. **Captura de eventos:** alteração acadêmica registrada no Gioconda ou Lyceum. Identificador imutável do evento, matrícula/contrato, data do fato e data de processamento.
2. **Normalização:** `contrato_id`, `aluno_id`, `sistema`, `marca`, `tipo_evento`, `antes`, `depois`, `data_eficacia`, `usuario_origem` e `idempotency_key`.
3. **Política de geração:** conferir se a alteração é contratualmente relevante. Exemplos: mudança de preço, desconto, curso, polo, oferta de disciplinas. O jurídico decide quais eventos requerem aditivo, nova contratação, ciência simples ou rescisão.
4. **Pré-validação:** detectar contratos vigentes, eventos duplicados, inconsistências cadastrais, benefícios e alterações retroativas.
5. **Minuta:** carregar template jurídico por marca/curso/modalidade, comparar versão base com alterações e registrar a proposta.
6. **Aceite:** solicitar por mecanismo oficial validado, com autenticação, carimbo temporal e evidência preservada. **A POC não implementa assinatura eletrônica real.**
7. **Efetivação:** promover a versão proposta somente após requisitos legais/operacionais. Eventos concorrentes aguardam resolução.
8. **Financeiro:** confrontar cobrança e período efetivo da alteração; bloquear ou sinalizar cobrança sem lastro conforme política aprovada; publicar diferença para correção na origem autorizada.
9. **Auditoria:** demonstrar a cadeia `aluno > contrato-base > evento > aditivo > aceite > cobrança`, com acesso controlado.

### Abordagens por sistema (hipóteses)

| Dimensão | Lyceum | Gioconda |
|---|---|---|
| Extração | API/read-replica/arquivo se disponível | API/read-replica/arquivo se disponível |
| Identificação | matrícula, vínculo financeiro e contrato | requerimento, vínculo, contrato e aceite |
| Aditivo | fluxo orquestrado, gerando documento no mecanismo aprovado | reaproveitar mecanismo de aditivos/aceite caso confirmado |
| Retorno | referência/id/status do aditivo por integração suportada | referência/id/status do termo por integração suportada |
| Restrição | não presumir módulo nativo ou nomes de tabela | não presumir API ou funcionamento interno |

### Exemplo de contrato canônico

```json
{
  "marca": "UniCesumar",
  "sistema": "LYCEUM",
  "contrato_id": "LYC-101",
  "aluno_id": "ALUNO-FICT-01",
  "versao": 1,
  "condicoes": {"curso": "Engenharia de Software", "polo": "Maringa", "valor_mensal": "750.00"},
  "fonte": "SINTETICA"
}
```

### Exemplo de evento recebido

```json
{
  "evento_id": "EV-001",
  "contrato_id": "LYC-101",
  "tipo_evento": "TRANSFERENCIA_POLO",
  "data_evento": "2026-10-05",
  "novos_valores": {"polo": "Santos", "valor_mensal": "820.00"},
  "fonte": "SINTETICA"
}
```

### Persistência

O SQLite da demonstração contém `contratos`, `aditivos`, `conciliacao` e `trilha_auditoria`. Em produção, adotar storage institucional com RBAC, criptografia, trilha de acesso, retenção/expurgo, chaves estáveis e segregação entre dados brutos e documentos pessoais. O SHA-256 no log é **somente evidência de integridade técnica**, não substitui controles criptográficos de assinatura, timestamping, custódia e controle de acesso.

### Limitações deliberadas do protótipo

- Um evento por contrato em aberto; evento concorrente entra em quarentena.
- Simulação simples de preço mensal; não calcula retroatividade, competência parcial, encargos nem parcelas devidas.
- Sem autorização de escrita no Lyceum/Gioconda, sem captura de aceite real, sem dados pessoais reais.
- Cancelamento tem fluxo próprio de encerramento/restituição, sujeito ao jurídico; não se gera aditivo por padrão.
- Valores da POC não equivalem a valores devidos; são exemplos para discutir o controle.
