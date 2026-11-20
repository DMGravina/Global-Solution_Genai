import re
import unicodedata
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class ResultadoSegurancaEntrada:
    seguro: bool
    texto_sanitizado: str
    motivo_bloqueio: str = ""
    dados_mascarados: List[str] = field(default_factory=list)


class GuardrailSeguranca:
    """
    Camada de segurança, privacidade (LGPD) e mitigação de vulnerabilidades
    para o Assistente Conversacional CitizenTech.
    """

    PADROES_INJECTION = [
        r"ignore\s+(todas\s+as\s+|as\s+)?instrucoes",
        r"ignore\s+previous\s+instructions",
        r"desconsidere\s+(as\s+)?regras",
        r"esqueca\s+(tudo|as\s+instrucoes)",
        r"revele\s+(o\s+|seu\s+)?(system\s+)?prompt",
        r"mostre\s+(o\s+|seu\s+)?(system\s+)?prompt",
        r"quais\s+sao\s+suas\s+instrucoes\s+internas",
        r"modo\s+desenvolvedor",
        r"developer\s+mode",
        r"jailbreak",
        r"system\s+override",
        r"bypass",
        r"aja\s+como\s+um\s+sistema\s+sem\s+restricoes",
        r"exiba\s+(as\s+)?chaves\s+de\s+api",
        r"mostre\s+(o\s+)?arquivo\s+\.env",
    ]

    REGEX_CPF = re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")
    REGEX_EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
    REGEX_TELEFONE = re.compile(r"\b(?:\+55\s?)?(?:\(?\d{2}\)?\s?)?(?:9\d{4}|\d{4})-?\d{4}\b")
    REGEX_CHAVE_API = re.compile(r"\b(?:gsk_|sk-|hf_|ghp_)[A-Za-z0-9_-]{12,}\b")

    @staticmethod
    def _normalizar_sem_acentos(texto: str) -> str:
        nfkd = unicodedata.normalize("NFKD", texto.lower())
        return "".join(c for c in nfkd if not unicodedata.combining(c))

    def mascarar_dados_sensiveis(self, texto: str) -> Tuple[str, List[str]]:
        """Aplica mascaramento LGPD para CPF, e-mail, telefone e tokens."""
        encontrados: List[str] = []
        texto_limpo = texto

        if self.REGEX_CPF.search(texto_limpo):
            texto_limpo = self.REGEX_CPF.sub("[CPF_PROTEGIDO_LGPD]", texto_limpo)
            encontrados.append("CPF")

        if self.REGEX_EMAIL.search(texto_limpo):
            texto_limpo = self.REGEX_EMAIL.sub("[EMAIL_PROTEGIDO_LGPD]", texto_limpo)
            encontrados.append("E-mail")

        if self.REGEX_TELEFONE.search(texto_limpo):
            texto_limpo = self.REGEX_TELEFONE.sub("[TELEFONE_PROTEGIDO_LGPD]", texto_limpo)
            encontrados.append("Telefone")

        if self.REGEX_CHAVE_API.search(texto_limpo):
            texto_limpo = self.REGEX_CHAVE_API.sub("[CREDENCIAL_BLOQUEADA]", texto_limpo)
            encontrados.append("Chave_API")

        return texto_limpo, encontrados

    def validar_entrada_usuario(self, pergunta: str) -> ResultadoSegurancaEntrada:
        """
        1. Mascara dados pessoais sensíveis (LGPD).
        2. Detecta tentativas de Prompt Injection direto ou extração de system prompt.
        """
        if not pergunta or not pergunta.strip():
            return ResultadoSegurancaEntrada(
                seguro=False,
                texto_sanitizado="",
                motivo_bloqueio="Entrada vazia recebida.",
            )

        texto_mascarado, tipos_pii = self.mascarar_dados_sensiveis(pergunta.strip())
        texto_norm = self._normalizar_sem_acentos(texto_mascarado)

        for padrao in self.PADROES_INJECTION:
            if re.search(padrao, texto_norm):
                return ResultadoSegurancaEntrada(
                    seguro=False,
                    texto_sanitizado=texto_mascarado,
                    motivo_bloqueio=(
                        "Solicitação bloqueada pela política de segurança: tentativa detectada "
                        "de manipulação de instruções (Prompt Injection) ou acesso a dados internos."
                    ),
                    dados_mascarados=tipos_pii,
                )

        return ResultadoSegurancaEntrada(
            seguro=True,
            texto_sanitizado=texto_mascarado,
            dados_mascarados=tipos_pii,
        )

    def sanitizar_chunk_recuperado(self, texto_chunk: str) -> Tuple[str, bool]:
        """
        Mitigação contra Indirect Prompt Injection: remove qualquer tentativa de
        comando malicioso embutido dentro dos documentos da base de conhecimento.
        """
        linhas_seguras: List[str] = []
        houve_injecao = False

        for linha in texto_chunk.splitlines():
            linha_norm = self._normalizar_sem_acentos(linha)
            if any(re.search(p, linha_norm) for p in self.PADROES_INJECTION):
                houve_injecao = True
                linhas_seguras.append("[CONTEUDO_SUSPEITO_REMOVIDO_PELO_GUARDRAIL]")
            else:
                linhas_seguras.append(linha)

        return "\n".join(linhas_seguras), houve_injecao

    def validar_resposta_saida(
        self,
        resposta: str,
        chunks_utilizados: List[Dict],
        absteve: bool,
    ) -> Tuple[str, List[str]]:
        """
        Garante que a saída não vaze PII e contenha citação obrigatória quando
        houver resposta sustentada pela base.
        """
        alertas: List[str] = []
        resposta_segura, pii_saida = self.mascarar_dados_sensiveis(resposta)
        if pii_saida:
            alertas.append(f"PII mascarado na saída: {', '.join(pii_saida)}")

        if not absteve and chunks_utilizados:
            tem_citacao = ("Fonte:" in resposta_segura) or ("http" in resposta_segura)
            if not tem_citacao:
                fontes_unicas = []
                for c in chunks_utilizados:
                    ref = f"- {c['fonte']} ({c['url']} | Consulta: {c['data_consulta']})"
                    if ref not in fontes_unicas:
                        fontes_unicas.append(ref)
                resposta_segura += "\n\n**Fontes Consultadas:**\n" + "\n".join(fontes_unicas)
                alertas.append("Citação obrigatória injetada automaticamente pelo guardrail de pós-processamento.")

        return resposta_segura, alertas