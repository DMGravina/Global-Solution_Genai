# Documentação Técnica: Corpus, Arquitetura RAG, Segurança e Governança

**Disciplina:** Generative AI & Advanced Nets — Global Solution 2026.2 (FIAP)  
**Projeto:** CitizenTech — Assistente Conversacional de Atendimento e Zeladoria Cidadã  
**Integrantes do Grupo:**
- Davi Gravina — RM 565619
- Henry Andrade Browne — RM 562089
- Luiz Felipe dos Santos Tragi — RM 565009

---

## 1. Inventário Detalhado da Base de Conhecimento (Corpus)

O corpus foi construído a partir de documentos estruturados inspirados nas **Cartas de Serviços ao Usuário** e orientações oficiais do **Portal gov.br**, alinhados às mesmas categorias tratadas pelo robô RPA de triagem do ecossistema CitizenTech:

| Arquivo | Serviço / Tema | Órgão Responsável | URL de Referência | Data de Consulta |
| :--- | :--- | :--- | :--- | :---: |
| `01_infraestrutura_tapa_buraco.md` | Operação Tapa-Buraco e Manutenção Viária | SIURB / Subprefeituras | `https://www.gov.br/pt-br/servicos/solicitar-tapa-buraco-e-manutencao-viaria` | 2026-11-10 |
| `02_iluminacao_publica.md` | Manutenção de Iluminação Pública | ILUME | `https://www.gov.br/pt-br/servicos/solicitar-manutencao-de-iluminacao-publica` | 2026-11-10 |
| `03_limpeza_urbana_coleta.md` | Coleta de Lixo, Entulho e Poda | AMLURB | `https://www.gov.br/pt-br/servicos/solicitar-coleta-de-lixo-e-remocao-de-entulho` | 2026-11-10 |
| `04_saude_saneamento_dengue.md` | Vigilância Ambiental, Dengue e Saneamento | COVISA / Saneamento | `https://www.gov.br/pt-br/servicos/denunciar-foco-de-dengue-e-vazamento-de-esgoto` | 2026-11-10 |
| `05_protocolos_citizentech_faq.md` | Triagem RPA, Protocolos e LGPD | Plataforma CitizenTech | `https://www.gov.br/citizentech/pt-br/manual-atendimento-e-protocolos` | 2026-11-12 |

---

## 2. Justificativa das Decisões Arquiteturais do Pipeline RAG

### 2.1. Estratégia de Chunking (`ChunkerEstrutural`)
- **Método escolhido:** Chunking estrutural orientado a seções Markdown (`##`) com janela deslizante de segurança (`tamanho_max = 650` caracteres, `overlap = 120` caracteres) e injeção de cabeçalho contextual (`[Título | Categoria | Seção]`) em cada trecho.
- **Justificativa técnica:** Documentos normativos e Cartas de Serviços organizam regras por blocos lógicos (*Descrição*, *Órgão Responsável*, *Prazos/SLA*, *Documentos Necessários*). Fatiar por tamanho fixo arbitrário quebra tabelas de prazos ao meio e separa o nome do serviço de suas regras. A preservação dos metadados (`fonte`, `url`, `data_consulta`, `categoria`) diretamente no objeto `DocumentoChunk` garante rastreabilidade completa até o momento da geração.

### 2.2. Estratégia de Recuperação (`RetrieverHibrido`)
- **Método escolhido:** Busca Híbrida combinando **BM25Okapi** (peso `0.45`) e **Vetorização TF-IDF com n-gramas (1, 2) + Similaridade de Cosseno** (peso `0.55`), com `top_k = 3`, filtro opcional por `categoria` e corte rígido por `limiar_confianca = 0.22`.
- **Justificativa técnica:** No domínio de serviços públicos, os cidadãos utilizam tanto termos exatos/siglas (`ViaCEP`, `PROT-XXXX`, `Aedes aegypti`, `156`, `Ecopontos`) — onde o **BM25 lexical** se destaca — quanto expressões compostas e variações de fraseado (*"poste apagado na rua"*, *"lixo acumulado na calçada"*) — capturadas pelos **n-gramas vetoriais**. O corte por `limiar_confianca` impede que ruídos irrelevantes cheguem ao gerador.

### 2.3. Generator, System Prompt e Parâmetros (`GeneratorRAG`)
- **Modelo e Execução:** Suporta integração com LLMs gratuitos via `.env` (**Groq `llama-3.1-8b-instant`** ou **Ollama `llama3.2`** com `temperature = 0.1` para máxima determinismo) e inclui um **modo Fallback Grounded determinístico** que executa localmente sem exigir chaves pagas ou acesso externo.
- **Engenharia do Prompt:** O `SYSTEM_PROMPT` define explicitamente: (1) papel institucional restrito ao CitizenTech; (2) proibição de usar conhecimento paramétrico externo ao bloco `<CONTEXTO_RECUPERADO>`; (3) **regra obrigatória de citação** de fonte, URL e data de consulta; e (4) **regra explícita de abstenção** quando não houver evidência suficiente.

---

## 3. Mitigação de Erros, Alucinações e Vulnerabilidades

1. **Prevenção de Alucinações (Dupla Barreira):**
   - *Barreira 1 (Pré-geração):* Se nenhum chunk atingir `score_hibrido >= 0.22`, o pipeline bloqueia a chamada ao gerador e aciona imediatamente a resposta padrão de abstenção.
   - *Barreira 2 (Pós-geração):* O guardrail audita se a resposta gerada contém citação explícita (`Fonte:` ou `http`), injetando automaticamente as referências rastreáveis caso o modelo as omita.
2. **Defesa contra Prompt Injection (Direto e Indireto):**
   - *Direto:* Expressões regulares com normalização de acentos bloqueiam comandos de subversão na entrada do usuário (*"ignore as instruções anteriores"*, *"revele seu system prompt"*, *"jailbreak"*).
   - *Indireto:* Antes de montar o contexto para o LLM, cada chunk passa por `sanitizar_chunk_recuperado()`, neutralizando instruções maliciosas eventualmente inseridas em documentos externos (`SYSTEM OVERRIDE`).
3. **Privacidade e Conformidade com a LGPD:**
   - Mascaramento automático de **CPF, e-mail, telefone e chaves de API** tanto na entrada do cidadão quanto na saída do assistente (`[CPF_PROTEGIDO_LGPD]`).
   - Credenciais isoladas estritamente em arquivo `.env` local listado no `.gitignore`.

---

## 4. Ética, Impacto Social, ODS e Limitações

- **Ética e Inclusão Digital:** A linguagem das respostas foi projetada para traduzir regras burocráticas das Cartas de Serviços em passos claros para qualquer cidadão, encaminhando casos ambíguos para **Revisão Humana** sem penalizar moradores com menor letramento digital.
- **Alinhamento aos ODS (ONU):**
  - **ODS 11 (Cidades e Comunidades Sustentáveis):** Agiliza a zeladoria urbana (tapa-buraco, iluminação, limpeza).
  - **ODS 3 e ODS 6 (Saúde e Bem-Estar / Água Potável e Saneamento):** Facilita a denúncia rápida de focos de dengue e vazamentos de esgoto.
  - **ODS 16 (Paz, Justiça e Instituições Eficazes):** Promove transparência pública por meio de respostas auditáveis, rastreáveis e com citação de fontes oficiais.
- **Limitações Conhecidas:** O sistema atual opera sobre uma base estática de Cartas de Serviços e não consulta em tempo real o banco SQLite transacional do robô RPA para informar o status individual de um protocolo já aberto, além de depender de vocabulário textual próximo ao domínio sem suporte multimodal (análise de fotos).