# Manual Operacional CitizenTech: Triagem Inteligente, Protocolos e Privacidade

- **Fonte:** Documentação Técnica CitizenTech — Módulo de Atendimento e Zeladoria Cidadã
- **URL:** https://www.gov.br/citizentech/pt-br/manual-atendimento-e-protocolos
- **Categoria:** Atendimento e Protocolos
- **Data de Consulta:** 2026-11-12

## Como Funciona o Fluxo Integrado CitizenTech (RPA + IA)
A plataforma CitizenTech integra um robô de automação (RPA) com um assistente conversacional baseado em Inteligência Artificial Generativa (RAG). Quando o cidadão envia uma solicitação:
1. O endereço é validado automaticamente via API pública **ViaCEP** a partir do CEP informado.
2. Um modelo de classificação de linguagem natural identifica a área responsável (*Infraestrutura*, *Iluminação Pública*, *Limpeza Urbana* ou *Saúde e Saneamento*) e define a prioridade (*ALTA*, *MÉDIA* ou *BAIXA*).
3. O sistema grava o chamado em banco de dados auditável e gera um número de protocolo único no padrão **PROT-XXXX** (exemplo: `PROT-1001`).

## Consulta e Acompanhamento de Protocolos
Após o processamento, o cidadão recebe um comprovante automático por e-mail contendo o número do protocolo (`PROT-XXXX`), o setor encaminhado e o prazo estimado de atendimento. Caso o cidadão não receba o e-mail em até 15 minutos, deve verificar a caixa de spam ou consultar o status diretamente na aba de acompanhamento do portal CitizenTech informando o número do protocolo.

## Regra de Revisão Humana (Human-in-the-Loop)
Para evitar erros de encaminhamento, sempre que o relato do cidadão for muito vago ou a confiança da Inteligência Artificial na triagem ficar abaixo do limiar de **0.55 (55%)**, o sistema não descarta o pedido: a solicitação é encaminhada automaticamente para a fila de **Revisão Humana**, onde um atendente especializado analisa e classifica a demanda em até **24 horas úteis**.

## Privacidade e Proteção de Dados (LGPD)
Em conformidade com a Lei Geral de Proteção de Dados (Lei nº 13.709/2018), o Assistente CitizenTech aplica minimização de dados: o cidadão **não deve informar CPF, RG, senhas ou dados bancários** durante a conversa. Caso dados sensíveis sejam digitados acidentalmente, o filtro de segurança realiza o mascaramento automático antes do processamento.