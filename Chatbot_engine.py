"""
Chatbot simple basé sur une recherche par mots-clés dans les fichiers
personnels (.txt / .md) placés dans le dossier `documents/`.

Fonctionnement :
1. Chaque fichier est découpé en paragraphes (séparés par une ligne vide).
2. Pour une question donnée, on compare les mots de la question avec les
   mots de chaque paragraphe.
3. On renvoie le paragraphe qui partage le plus de mots avec la question.

C'est volontairement simple (pas de librairie externe) mais fonctionne
bien pour des notes personnelles, journaux, mémos, etc.
"""

import os
import re
import glob

STOPWORDS = {
    "le", "la", "les", "de", "des", "un", "une", "et", "ou", "que", "qui",
    "est", "je", "tu", "il", "elle", "nous", "vous", "ils", "elles",
    "au", "aux", "en", "pour", "sur", "dans", "avec", "ce", "cette",
    "mon", "ma", "mes", "ton", "ta", "tes", "son", "sa", "ses",
    "the", "is", "are", "of", "in", "on", "for", "and", "to",
    "what", "how", "do", "does", "my", "your",
}


class PersonalChatbot:
    """Chatbot qui répond en cherchant dans des fichiers texte personnels."""

    def __init__(self, documents_dir="documents"):
        self.documents_dir = documents_dir
        os.makedirs(self.documents_dir, exist_ok=True)
        self.paragraphs = []  # liste de tuples (nom_fichier, paragraphe)
        self.load_documents()

    def load_documents(self):
        """(Re)charge tous les fichiers .txt et .md du dossier documents/."""
        self.paragraphs = []
        files = []
        for pattern in ("*.txt", "*.md"):
            files.extend(
                glob.glob(os.path.join(self.documents_dir, "**", pattern), recursive=True)
            )

        for filepath in files:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
            except (UnicodeDecodeError, OSError):
                continue

            chunks = [c.strip() for c in re.split(r"\n\s*\n", content) if c.strip()]
            filename = os.path.basename(filepath)
            for chunk in chunks:
                self.paragraphs.append((filename, chunk))

    @staticmethod
    def _tokenize(text):
        words = re.findall(r"\w+", text.lower())
        return [w for w in words if w not in STOPWORDS and len(w) > 1]

    def get_response(self, query):
        # On recharge à chaque question pour prendre en compte les fichiers
        # ajoutés/modifiés pendant que l'app tourne.
        self.load_documents()

        if not self.paragraphs:
            return (
                "Je n'ai trouvé aucune note à explorer. Ajoute des fichiers "
                f".txt ou .md dans le dossier '{self.documents_dir}'."
            )

        query_words = set(self._tokenize(query))
        if not query_words:
            return "Peux-tu reformuler ta question avec un peu plus de détails ?"

        best_score = 0
        best_matches = []

        for filename, paragraph in self.paragraphs:
            paragraph_words = set(self._tokenize(paragraph))
            score = len(query_words & paragraph_words)
            if score > best_score:
                best_score = score
                best_matches = [(filename, paragraph)]
            elif score == best_score and score > 0:
                best_matches.append((filename, paragraph))

        if best_score == 0:
            return (
                "Je n'ai rien trouvé de pertinent dans tes notes pour cette "
                "question. Essaie avec d'autres mots-clés."
            )

        filename, paragraph = best_matches[0]
        snippet = paragraph if len(paragraph) < 500 else paragraph[:500] + "..."
        return f"D'après '{filename}' :\n{snippet}"

