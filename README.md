# CitizenTech GenAI — Assistente Conversacional de Zeladoria Cidadã (RAG)

**Disciplina:** Generative AI & Advanced Nets — Global Solution 2026.2 (FIAP)  
**Turma:** 2TIAPF  
**Integrantes do Grupo:**
- **Davi Gravina** — RM 565619
- **Henry Andrade Browne** — RM 562089
- **Luiz Felipe dos Santos Tragi** — RM 565009

---

## 1. Visão Geral do Projeto
O **Assistente Conversacional CitizenTech** integra-se à solução de triagem inteligente de serviços públicos do grupo para orientar cidadãos sobre zeladoria urbana (**Tapa-Buraco/Infraestrutura**, **Iluminação Pública**, **Limpeza Urbana/Coleta**, **Vigilância Sanitária/Dengue** e **Acompanhamento de Protocolos**).

Diferente de um chatbot genérico, o sistema implementa uma arquitetura **RAG (Retrieval-Augmented Generation)** auditável com:
- **Base de Conhecimento Rastreável (`corpus/`):** Documentos estruturados baseados nas Cartas de Serviços ao Usuário e Portal gov.br, contendo URLs, órgãos responsáveis, prazos (SLAs) e datas de consulta.
- **Chunking Estrutural com Overlap:** Preserva seções semânticas e metadados completos em cada trecho.
- **Retriever Híbrido (BM25 + Vetorial TF-IDF):** Combina busca lexical e similaridade de cosseno, com stemming em português para reconhecer variações morfológicas e limiar mínimo de confiança (`0.22`).
- **Generator com System Prompt Rigoroso:** Exige citação de fonte/URL em todas as respostas e impõe abstenção explícita diante de falta de evidências.
- **Guardrails de Segurança e LGPD (`seguranca.py`):** Bloqueio contra *Prompt Injection* direto e indireto, mascaramento de PII (CPF, e-mail, telefone) e isolamento de credenciais via `.env`.

---

## 2. Estrutura do Repositório

```text
Global-Solution_Genai/
├── .gitignore                          # Ignora configurações locais do VS Code
├── README.md                           # Este guia de instalação e uso
└── citizentech-genai/
    ├── .gitignore                      # Bloqueia .env, ambientes virtuais e caches
    ├── .env.example                    # Modelo de configuração sem credenciais reais
    ├── requirements.txt                # Dependências Python
    ├── corpus/                         # Base de conhecimento rastreável
    ├── seguranca.py                    # Guardrails: LGPD, injection e citação
    ├── rag_pipeline.py                 # Chunking, Retriever Híbrido e Generator RAG
    ├── app_chat.py                     # Interface conversacional interativa (CLI)
    ├── avaliar_rag.py                  # Bateria automatizada de 12 testes e métricas
    ├── DOCUMENTACAO_CORPUS_E_ARQUITETURA.md
    └── RELATORIO_AVALIACAO.md          # Gerado por avaliar_rag.py
```

---

## 3. Como Instalar e Executar (Passo a Passo)

### Pré-requisitos
- **Python 3.10 ou superior** instalado.
- Não é obrigatória nenhuma chave de API paga: o sistema possui o modo `LLM_PROVIDER=fallback` (determinístico e fundamentado no contexto) ativo por padrão.

### Etapa 1: Acessar a pasta e criar o ambiente virtual
```bash
cd citizentech-genai
python -m venv venv

# Ativar no Windows (PowerShell/CMD):
venv\Scripts\activate

# Ativar no Linux ou macOS:
source venv/bin/activate
```

### Etapa 2: Instalar as dependências
```bash
pip install -r requirements.txt
```

### Etapa 3: Configurar variáveis de ambiente
Copie o modelo `.env.example` para `.env`:
```bash
# Windows:
copy .env.example .env

# Linux/macOS:
cp .env.example .env
```
*(Opcional: caso deseje utilizar um LLM externo gratuito, altere `LLM_PROVIDER=groq` no seu `.env` local e insira sua chave gratuita em `GROQ_API_KEY`).*

### Etapa 4: Executar a Bateria de Testes e Gerar o Relatório de Avaliação
```bash
python avaliar_rag.py
```
Este comando executa a comparação entre duas estratégias de Chunking, roda os **12 casos de teste** (respondíveis, sem resposta, ambíguos, multi-turno, fora de escopo e 2 testes adversariais) e gera/atualiza o arquivo **`RELATORIO_AVALIACAO.md`**.

### Etapa 5: Testar o Assistente Conversacional Interativamente
```bash
python app_chat.py
```
Digite suas perguntas no terminal para visualizar em tempo real os trechos recuperados, scores híbridos, alertas de segurança e respostas citadas.

---

## 4. Documentação Complementar
- **Justificativas Técnicas, LGPD e ODS:** Consulte [`DOCUMENTACAO_CORPUS_E_ARQUITETURA.md`](citizentech-genai/DOCUMENTACAO_CORPUS_E_ARQUITETURA.md).
- **Evidências de Testes e Métricas:** Geradas em `citizentech-genai/RELATORIO_AVALIACAO.md` ao executar a avaliação.