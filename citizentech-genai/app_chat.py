from rag_pipeline import AssistenteCitizenTechRAG


def iniciar_chat():
    print("=" * 72)
    print("  CITIZENTECH — ASSISTENTE CONVERSACIONAL DE ZELADORIA CIDADÃ (RAG)")
    print("=" * 72)
    assistente = AssistenteCitizenTechRAG()
    print(f"Base carregada: {len(assistente.chunks)} chunks indexados | Provedor LLM: {assistente.generator.provider}")
    print("Comandos: '/limpar' para reiniciar conversa | '/sair' para encerrar.\n")

    while True:
        try:
            pergunta = input("Cidadão > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nEncerrando assistente CitizenTech.")
            break

        if not pergunta:
            continue
        if pergunta.lower() in ("/sair", "sair", "exit"):
            print("Obrigado por utilizar o CitizenTech!")
            break
        if pergunta.lower() == "/limpar":
            assistente.limpar_historico()
            print("[Sistema] Histórico da conversa limpo.\n")
            continue

        resultado = assistente.responder(pergunta)

        print("\n" + "-" * 72)
        if resultado["alertas_seguranca"]:
            for alerta in resultado["alertas_seguranca"]:
                print(f"[GUARDRAIL] {alerta}")

        if resultado["chunks_recuperados"]:
            print("[EVIDÊNCIAS RECUPERADAS]:")
            for c in resultado["chunks_recuperados"]:
                print(
                    f"  • {c['chunk_id']} | Seção: {c['secao']} | "
                    f"Score Híbrido: {c['score_hibrido']} (BM25={c['score_bm25']}, Vetorial={c['score_vetorial']})"
                )
        else:
            print("[EVIDÊNCIAS RECUPERADAS]: Nenhum trecho atingiu o limiar mínimo de confiança.")

        print("\n[ASSISTENTE CITIZENTECH]:")
        print(resultado["resposta"])
        print("-" * 72 + "\n")


if __name__ == "__main__":
    iniciar_chat()