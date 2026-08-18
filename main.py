"""
Application Chatbot Personnel avec Login / Signup.

Structure :
- LoginFrame  : connexion
- SignupFrame : création de compte
- ChatFrame   : discussion avec le chatbot (recherche dans tes notes)

Lancer avec : python main.py
"""

import tkinter as tk
from tkinter import ttk, messagebox

from auth import authenticate_user, register_user
from chatbot_engine import PersonalChatbot

BG_COLOR = "#f4f6f8"
ACCENT_COLOR = "#2c3e50"
LINK_COLOR = "#2980b9"


class ChatbotApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mon Assistant Personnel")
        self.geometry("520x620")
        self.resizable(False, False)

        self.current_user = None
        self.chatbot = PersonalChatbot(documents_dir="documents")

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (LoginFrame, SignupFrame, ChatFrame):
            frame = F(container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginFrame")

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()
        if hasattr(frame, "on_show"):
            frame.on_show()

    def login_success(self, username):
        self.current_user = username
        self.show_frame("ChatFrame")


class LoginFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG_COLOR)
        self.app = app

        tk.Label(
            self, text="Connexion", font=("Segoe UI", 22, "bold"),
            bg=BG_COLOR, fg=ACCENT_COLOR
        ).pack(pady=(70, 30))

        form = tk.Frame(self, bg=BG_COLOR)
        form.pack(pady=10)

        tk.Label(form, text="Nom d'utilisateur", bg=BG_COLOR).grid(row=0, column=0, sticky="w", pady=5)
        self.username_entry = ttk.Entry(form, width=32)
        self.username_entry.grid(row=1, column=0, pady=5)

        tk.Label(form, text="Mot de passe", bg=BG_COLOR).grid(row=2, column=0, sticky="w", pady=5)
        self.password_entry = ttk.Entry(form, width=32, show="*")
        self.password_entry.grid(row=3, column=0, pady=5)
        self.password_entry.bind("<Return>", lambda e: self.handle_login())

        ttk.Button(self, text="Se connecter", command=self.handle_login).pack(pady=25)

        link = tk.Label(
            self, text="Pas encore de compte ? Inscrivez-vous",
            fg=LINK_COLOR, bg=BG_COLOR, cursor="hand2"
        )
        link.pack()
        link.bind("<Button-1>", lambda e: self.app.show_frame("SignupFrame"))

    def on_show(self):
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.username_entry.focus_set()

    def handle_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showwarning("Champs manquants", "Merci de remplir tous les champs.")
            return

        if authenticate_user(username, password):
            self.app.login_success(username)
        else:
            messagebox.showerror("Erreur", "Nom d'utilisateur ou mot de passe incorrect.")


class SignupFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG_COLOR)
        self.app = app

        tk.Label(
            self, text="Créer un compte", font=("Segoe UI", 22, "bold"),
            bg=BG_COLOR, fg=ACCENT_COLOR
        ).pack(pady=(70, 30))

        form = tk.Frame(self, bg=BG_COLOR)
        form.pack(pady=10)

        tk.Label(form, text="Nom d'utilisateur", bg=BG_COLOR).grid(row=0, column=0, sticky="w", pady=5)
        self.username_entry = ttk.Entry(form, width=32)
        self.username_entry.grid(row=1, column=0, pady=5)

        tk.Label(form, text="Mot de passe", bg=BG_COLOR).grid(row=2, column=0, sticky="w", pady=5)
        self.password_entry = ttk.Entry(form, width=32, show="*")
        self.password_entry.grid(row=3, column=0, pady=5)

        tk.Label(form, text="Confirmer le mot de passe", bg=BG_COLOR).grid(row=4, column=0, sticky="w", pady=5)
        self.confirm_entry = ttk.Entry(form, width=32, show="*")
        self.confirm_entry.grid(row=5, column=0, pady=5)
        self.confirm_entry.bind("<Return>", lambda e: self.handle_signup())

        ttk.Button(self, text="S'inscrire", command=self.handle_signup).pack(pady=25)

        link = tk.Label(
            self, text="Déjà un compte ? Connectez-vous",
            fg=LINK_COLOR, bg=BG_COLOR, cursor="hand2"
        )
        link.pack()
        link.bind("<Button-1>", lambda e: self.app.show_frame("LoginFrame"))

    def on_show(self):
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.confirm_entry.delete(0, tk.END)
        self.username_entry.focus_set()

    def handle_signup(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()

        if not username or not password or not confirm:
            messagebox.showwarning("Champs manquants", "Merci de remplir tous les champs.")
            return
        if password != confirm:
            messagebox.showerror("Erreur", "Les mots de passe ne correspondent pas.")
            return
        if len(password) < 4:
            messagebox.showwarning("Mot de passe trop court", "Utilisez au moins 4 caractères.")
            return

        success, message = register_user(username, password)
        if success:
            messagebox.showinfo("Succès", message)
            self.app.show_frame("LoginFrame")
        else:
            messagebox.showerror("Erreur", message)


class ChatFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#ffffff")
        self.app = app

        header = tk.Frame(self, bg=ACCENT_COLOR, height=50)
        header.pack(fill="x")
        self.title_label = tk.Label(
            header, text="Assistant Personnel", bg=ACCENT_COLOR,
            fg="white", font=("Segoe UI", 14, "bold")
        )
        self.title_label.pack(side="left", padx=15, pady=10)

        ttk.Button(header, text="Déconnexion", command=self.handle_logout).pack(side="right", padx=15, pady=8)

        self.chat_area = tk.Text(
            self, state="disabled", wrap="word", bg="#f9f9f9",
            font=("Segoe UI", 10), padx=10, pady=10
        )
        self.chat_area.pack(fill="both", expand=True, padx=10, pady=(10, 0))

        input_frame = tk.Frame(self, bg="#ffffff")
        input_frame.pack(fill="x", padx=10, pady=10)

        self.message_entry = ttk.Entry(input_frame, font=("Segoe UI", 11))
        self.message_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.message_entry.bind("<Return>", lambda e: self.send_message())

        ttk.Button(input_frame, text="Envoyer", command=self.send_message).pack(side="right")

    def on_show(self):
        self.title_label.config(text=f"Assistant Personnel — {self.app.current_user}")
        self.chat_area.config(state="normal")
        self.chat_area.delete("1.0", tk.END)
        self.chat_area.config(state="disabled")
        self.append_message(
            "Assistant",
            "Bonjour ! Pose-moi une question, je vais chercher dans tes notes personnelles."
        )
        self.message_entry.focus_set()

    def append_message(self, sender, text):
        self.chat_area.config(state="normal")
        self.chat_area.insert(tk.END, f"{sender} : {text}\n\n")
        self.chat_area.config(state="disabled")
        self.chat_area.see(tk.END)

    def send_message(self):
        query = self.message_entry.get().strip()
        if not query:
            return

        self.append_message("Vous", query)
        self.message_entry.delete(0, tk.END)

        response = self.app.chatbot.get_response(query)
        self.append_message("Assistant", response)

    def handle_logout(self):
        self.app.current_user = None
        self.app.show_frame("LoginFrame")


if __name__ == "__main__":
    app = ChatbotApp()
    app.mainloop()

