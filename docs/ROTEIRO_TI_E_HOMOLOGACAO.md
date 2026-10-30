# Workshop com TI e negócio | POC 01

## Perguntas prioritárias (ordem sugerida)

1. Onde fica o contrato-base por marca? Ele é versionado ou sobrescrito?
2. No Gioconda, qual a jornada real do termo aditivo e do aceite? Existe serviço de consulta de status e evidência? **Não confundir termo de estágio com aditivo do contrato educacional.**
3. No Lyceum, quais eventos geram alterações contratuais e quais módulos fornecem as versões/aceites? É possível API, webhook, extração incremental ou view read-only?
4. Existem chaves estáveis de aluno, contrato, matrícula, benefício e histórico de disciplinas?
5. Quem determina a **data de eficácia** e como lidar com alterações retroativas ou múltiplos eventos?
6. Que termos precisam de assinatura versus simples ciência? Quem valida modelos e requisitos de prova?
7. O financeiro reflete valores automaticamente? Onde consultar o valor faturado e estornos por competência?
8. A Vitru pode liberar **extratos sintéticos / esquema / amostras anonimizadas** sem conceder acesso transacional ao sistema?
9. Como monitorar rejeições e manter evidências com autenticação, LGPD, RBAC e prazo de retenção?

## Critérios de homologação

- [ ] Dicionário real de campos e eventos por sistema validado.
- [ ] Regra de exigência de aditivo aprovada pelo Jurídico.
- [ ] Template do documento e mecanismo de assinatura/aceite aprovados.
- [ ] Eventos de alteração, cancelamento, reingresso e bolsa cobertos.
- [ ] Reprocessamento idempotente e exceções de dados testados.
- [ ] Relatório de conciliação bate com CAR em amostra aprovada.
- [ ] Permissões e exportação autorizada formalizadas.
- [ ] Nenhuma escrita habilitada antes de aprovação institucional.

## Roteiro de demonstração de 5 minutos

1. Abra `dados_ficticios/eventos_academicos.csv` e mostre a transferência e a bolsa.
2. Rode `python -m poc_aditivos`.
3. Abra `saida_demo/aditivos.csv` e as minutas `ADT-EV-001.md` e `ADT-EV-002.md`.
4. Compare `saida_demo/conciliacao_financeira.csv`: **LYC-202** foi faturado a novo valor sem aceite sintético.
5. Mostre `saida_demo/excecoes.csv` (cancelamento exige fluxo próprio) e trilha hash.
6. Feche com decisões: **captura, aceite, eficácia e integração**.
