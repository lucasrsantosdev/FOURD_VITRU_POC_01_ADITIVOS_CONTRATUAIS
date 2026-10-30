# Matriz de riscos e controles | POC 01

| ID | Risco de negócio | Controle proposto | Evidência | Proprietário sugerido |
|---|---|---|---|---|
| AC-01 | Cobrança sem condição contratual | Conciliação condição vigente × faturamento | Relatório por contrato, mês e divergência | Financeiro / CAR |
| AC-02 | Mudança acadêmica sem documentação | Detecção de evento e proposta de aditivo | Evento, hash da proposta, minuta e status | Secretaria / Acadêmico |
| AC-03 | Aceite não comprovável | Captura institucional do consentimento | Referência de aceite, texto aceito, timestamp, identidade | Jurídico / TI |
| AC-04 | Reescrita de contrato histórico | Versionamento append-only | v1, proposta v2, histórico e vigência | TI / Jurídico |
| AC-05 | Divergência de fontes | Chave canônica e conciliação entre sistemas | Contrato, RA, marca, origem, competência | Engenharia de Dados |
| AC-06 | Cancelamento cobrado indevidamente | Fila jurídica para rescisão/cancelamento | Evento, data, financeiro/estorno | Secretaria / CAR / Jurídico |
| AC-07 | Falha por reprocessamento | Event ID imutável e deduplicação | Log de evento já processado | Engenharia de Dados |
| AC-08 | Tratamento inseguro de dados de alunos | Privilégio mínimo, pseudonimização e retenção | Matriz de acesso, inventário LGPD | Segurança / DPO |

**Nota de auditoria:** o teste mostra a existência da trilha e capacidade de detecção; não valida eficácia real desses controles até haver procedimento, amostra e evidências institucionais.
