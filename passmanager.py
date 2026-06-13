import os
import sys
import sqlite3
import base64
import secrets
import string
import tempfile
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet, InvalidToken


class Tooltip:
    """Pequeño tooltip que se muestra al pasar el mouse sobre un widget."""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, event=None):
        if self.tipwindow or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, background="#ffffe0", relief="solid",
                          borderwidth=1, font=("Segoe UI", 8), padx=4, pady=2)
        label.pack()

    def hide(self, event=None):
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None


ICON_BASE64 = (
    "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"
)


def app_dir():
    """Carpeta donde está el ejecutable (para que la BD viva en el pendrive)."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


DB_PATH = os.path.join(app_dir(), "vault.db")
ITERATIONS = 200_000


def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=ITERATIONS,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode("utf-8")))


class Database:
    def __init__(self, path):
        self.path = path
        self.conn = sqlite3.connect(path)
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS meta (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                salt BLOB NOT NULL,
                verifier BLOB NOT NULL
            )"""
        )
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                username TEXT,
                password BLOB NOT NULL,
                url TEXT,
                notes TEXT
            )"""
        )
        self.conn.commit()

    def is_initialized(self):
        cur = self.conn.execute("SELECT 1 FROM meta WHERE id=1")
        return cur.fetchone() is not None

    def setup_master_password(self, password: str):
        salt = secrets.token_bytes(16)
        key = derive_key(password, salt)
        f = Fernet(key)
        verifier = f.encrypt(b"OK")
        self.conn.execute(
            "INSERT INTO meta (id, salt, verifier) VALUES (1, ?, ?)",
            (salt, verifier),
        )
        self.conn.commit()
        return key

    def get_salt(self):
        cur = self.conn.execute("SELECT salt, verifier FROM meta WHERE id=1")
        return cur.fetchone()

    def check_password(self, password: str):
        row = self.get_salt()
        if not row:
            return None
        salt, verifier = row
        key = derive_key(password, salt)
        try:
            f = Fernet(key)
            f.decrypt(verifier)
            return key
        except InvalidToken:
            return None

    # CRUD de entradas
    def add_entry(self, fernet, title, username, password, url, notes):
        enc = fernet.encrypt(password.encode("utf-8"))
        self.conn.execute(
            "INSERT INTO entries (title, username, password, url, notes) VALUES (?,?,?,?,?)",
            (title, username, enc, url, notes),
        )
        self.conn.commit()

    def update_entry(self, fernet, entry_id, title, username, password, url, notes):
        enc = fernet.encrypt(password.encode("utf-8"))
        self.conn.execute(
            "UPDATE entries SET title=?, username=?, password=?, url=?, notes=? WHERE id=?",
            (title, username, enc, url, notes, entry_id),
        )
        self.conn.commit()

    def delete_entry(self, entry_id):
        self.conn.execute("DELETE FROM entries WHERE id=?", (entry_id,))
        self.conn.commit()

    def list_entries(self):
        cur = self.conn.execute("SELECT id, title, username, url FROM entries ORDER BY title COLLATE NOCASE")
        return cur.fetchall()

    def get_entry(self, fernet, entry_id):
        cur = self.conn.execute(
            "SELECT id, title, username, password, url, notes FROM entries WHERE id=?", (entry_id,)
        )
        row = cur.fetchone()
        if not row:
            return None
        eid, title, username, enc, url, notes = row
        try:
            pwd = fernet.decrypt(enc).decode("utf-8")
        except InvalidToken:
            pwd = "<ERROR AL DESCIFRAR>"
        return {"id": eid, "title": title, "username": username, "password": pwd, "url": url, "notes": notes}


# ---------------- INTERFAZ ----------------

class LoginScreen(tk.Frame):
    def __init__(self, master, db: Database, on_success):
        super().__init__(master, padx=30, pady=30)
        self.db = db
        self.on_success = on_success

        is_new = not db.is_initialized()

        title = "Crear contraseña maestra" if is_new else "Ingresar contraseña maestra"
        tk.Label(self, text="🔒 Gestor de Contraseñas", font=("Segoe UI", 16, "bold")).pack(pady=(0, 5))
        tk.Label(self, text=title, font=("Segoe UI", 11)).pack(pady=(0, 15))

        self.pwd_var = tk.StringVar()
        self.pwd_entry = tk.Entry(self, textvariable=self.pwd_var, show="*", font=("Segoe UI", 11), width=30)
        self.pwd_entry.pack(pady=5)
        self.pwd_entry.focus()

        if is_new:
            tk.Label(self, text="Confirmar contraseña:").pack(pady=(10, 0))
            self.pwd2_var = tk.StringVar()
            self.pwd2_entry = tk.Entry(self, textvariable=self.pwd2_var, show="*", font=("Segoe UI", 11), width=30)
            self.pwd2_entry.pack(pady=5)

        self.show_var = tk.BooleanVar()
        tk.Checkbutton(self, text="Mostrar contraseña", variable=self.show_var,
                       command=self.toggle_show).pack(pady=5)

        btn_text = "Crear base de datos" if is_new else "Ingresar"
        action = self.create_db if is_new else self.login
        tk.Button(self, text=btn_text, command=action, font=("Segoe UI", 10, "bold"),
                  bg="#2d6cdf", fg="white", padx=10, pady=5).pack(pady=15)

        self.pwd_entry.bind("<Return>", lambda e: action())
        if is_new:
            self.pwd2_entry.bind("<Return>", lambda e: action())

        tk.Label(self, text=f"Base de datos: {os.path.basename(db.path)}",
                 fg="gray", font=("Segoe UI", 8)).pack(pady=(10, 0))

    def toggle_show(self):
        show = "" if self.show_var.get() else "*"
        self.pwd_entry.config(show=show)
        if hasattr(self, "pwd2_entry"):
            self.pwd2_entry.config(show=show)

    def create_db(self):
        p1 = self.pwd_var.get()
        p2 = self.pwd2_var.get()
        if not p1:
            messagebox.showerror("Error", "La contraseña no puede estar vacía.")
            return
        if len(p1) < 4:
            messagebox.showerror("Error", "Usá al menos 4 caracteres (se recomienda mucho más).")
            return
        if p1 != p2:
            messagebox.showerror("Error", "Las contraseñas no coinciden.")
            return
        key = self.db.setup_master_password(p1)
        fernet = Fernet(key)
        self.on_success(fernet)

    def login(self):
        p = self.pwd_var.get()
        key = self.db.check_password(p)
        if key is None:
            messagebox.showerror("Error", "Contraseña incorrecta.")
            self.pwd_var.set("")
            return
        fernet = Fernet(key)
        self.on_success(fernet)


class EntryDialog(simpledialog.Dialog):
    def __init__(self, parent, title="Entrada", data=None):
        self.data = data or {}
        self.result_data = None
        super().__init__(parent, title)

    def body(self, master):
        labels = ["Título", "Usuario", "Contraseña", "URL", "Notas"]
        keys = ["title", "username", "password", "url", "notes"]
        self.vars = {}
        for i, (lbl, key) in enumerate(zip(labels, keys)):
            tk.Label(master, text=lbl + ":").grid(row=i, column=0, sticky="e", padx=5, pady=4)
            if key == "notes":
                widget = tk.Text(master, width=30, height=3)
                widget.insert("1.0", self.data.get(key, ""))
                widget.grid(row=i, column=1, padx=5, pady=4, columnspan=2)
                self.vars[key] = widget
            else:
                var = tk.StringVar(value=self.data.get(key, ""))
                show = "*" if key == "password" else ""
                entry = tk.Entry(master, textvariable=var, width=30, show=show)
                entry.grid(row=i, column=1, padx=5, pady=4)
                self.vars[key] = var
                if key == "password":
                    self.pwd_entry_widget = entry
                    btn_frame = tk.Frame(master)
                    btn_frame.grid(row=i, column=2, padx=2)
                    gen_btn = tk.Button(btn_frame, text="🎲", width=3,
                              command=self.generate_password)
                    gen_btn.pack(side="left")
                    Tooltip(gen_btn, "Generar clave")
                    show_btn = tk.Button(btn_frame, text="👁️", width=3,
                              command=self.toggle_show_password)
                    show_btn.pack(side="left")
                    Tooltip(show_btn, "Ver clave")

        return None

    def toggle_show_password(self):
        current = self.pwd_entry_widget.cget("show")
        self.pwd_entry_widget.config(show="" if current == "*" else "*")

    def generate_password(self):
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
        pwd = "".join(secrets.choice(alphabet) for _ in range(16))
        self.vars["password"].set(pwd)
        self.pwd_entry_widget.config(show="")

    def apply(self):
        result = {}
        for key, widget in self.vars.items():
            if key == "notes":
                result[key] = widget.get("1.0", "end").strip()
            else:
                result[key] = widget.get()
        if not result["title"]:
            messagebox.showerror("Error", "El título es obligatorio.")
            return
        self.result_data = result


class MainScreen(tk.Frame):
    def __init__(self, master, db: Database, fernet: Fernet):
        super().__init__(master, padx=10, pady=10)
        self.db = db
        self.fernet = fernet

        top = tk.Frame(self)
        top.pack(fill="x")
        tk.Label(top, text="🔒 Mis contraseñas", font=("Segoe UI", 14, "bold")).pack(side="left")
        tk.Button(top, text="❓ Ayuda", command=self.show_help).pack(side="right", padx=2)
        tk.Button(top, text="💛 Donar", command=self.show_donate).pack(side="right", padx=2)

        search_frame = tk.Frame(self)
        search_frame.pack(fill="x", pady=(8, 0))
        tk.Label(search_frame, text="🔍 Buscar:").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *a: self.refresh())
        tk.Entry(search_frame, textvariable=self.search_var, width=40).pack(side="left", padx=5)

        btns = tk.Frame(self)
        btns.pack(fill="x", pady=8)
        tk.Button(btns, text="➕ Agregar", command=self.add_entry).pack(side="left", padx=2)
        tk.Button(btns, text="✏️ Editar", command=self.edit_entry).pack(side="left", padx=2)
        tk.Button(btns, text="🗑️ Eliminar", command=self.delete_entry).pack(side="left", padx=2)
        tk.Button(btns, text="👁️ Ver contraseña", command=self.show_password).pack(side="left", padx=2)
        tk.Button(btns, text="📋 Copiar contraseña", command=self.copy_password).pack(side="left", padx=2)

        tree_frame = tk.Frame(self)
        tree_frame.pack(fill="both", expand=True)

        columns = ("id", "title", "username", "url")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        self.tree.heading("id", text="ID")
        self.tree.heading("title", text="Título")
        self.tree.heading("username", text="Usuario")
        self.tree.heading("url", text="URL")
        self.tree.column("id", width=40)
        self.tree.column("title", width=180)
        self.tree.column("username", width=150)
        self.tree.column("url", width=200)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", lambda e: self.edit_entry())

        self.refresh()

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        query = self.search_var.get().strip().lower()
        for eid, title, username, url in self.db.list_entries():
            if query:
                haystack = f"{title or ''} {username or ''} {url or ''}".lower()
                if query not in haystack:
                    continue
            self.tree.insert("", "end", values=(eid, title, username or "", url or ""))

    def show_help(self):
        text = (
            "Gestor de Contraseñas Portable\n\n"
            "• Esta aplicación NO utiliza Internet ni ningún tipo de conexión "
            "de red. Todo funciona 100% local, en tu equipo o pendrive.\n\n"
            "• Tus datos se guardan en el archivo 'vault.db', cifrados.\n\n"
            "• Seguridad: la contraseña maestra nunca se almacena. A partir de "
            "ella se deriva una clave criptográfica usando PBKDF2-HMAC-SHA256 "
            "con 200.000 iteraciones y un 'salt' aleatorio único. Esa clave se "
            "usa con Fernet (cifrado AES-128 en modo CBC + autenticación HMAC) "
            "para cifrar cada contraseña individualmente antes de guardarla.\n\n"
            "• Si olvidás la contraseña maestra, los datos NO se pueden "
            "recuperar: es lo que garantiza que nadie más pueda acceder a ellos.\n\n"
            "• Funciones: agregar, editar, eliminar entradas; generador de "
            "contraseñas seguras; ver/copiar contraseñas; búsqueda rápida."
        )
        messagebox.showinfo("Ayuda", text)

    def show_donate(self):
        link = "https://paypal.me/AlejandroBouzas"
        if messagebox.askyesno(
            "Donación voluntaria",
            "Si esta aplicación te resulta útil y querés apoyar al creador, "
            "podés hacer una donación voluntaria en:\n\n" + link +
            "\n\n¿Querés abrir el enlace ahora?",
        ):
            import webbrowser
            webbrowser.open(link)

    def get_selected_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Seleccioná una entrada primero.")
            return None
        return self.tree.item(sel[0])["values"][0]

    def add_entry(self):
        dlg = EntryDialog(self, title="Nueva entrada")
        if dlg.result_data:
            d = dlg.result_data
            self.db.add_entry(self.fernet, d["title"], d["username"], d["password"], d["url"], d["notes"])
            self.refresh()

    def edit_entry(self):
        eid = self.get_selected_id()
        if eid is None:
            return
        entry = self.db.get_entry(self.fernet, eid)
        dlg = EntryDialog(self, title="Editar entrada", data=entry)
        if dlg.result_data:
            d = dlg.result_data
            self.db.update_entry(self.fernet, eid, d["title"], d["username"], d["password"], d["url"], d["notes"])
            self.refresh()

    def delete_entry(self):
        eid = self.get_selected_id()
        if eid is None:
            return
        if messagebox.askyesno("Confirmar", "¿Eliminar esta entrada?"):
            self.db.delete_entry(eid)
            self.refresh()

    def show_password(self):
        eid = self.get_selected_id()
        if eid is None:
            return
        entry = self.db.get_entry(self.fernet, eid)
        messagebox.showinfo(entry["title"], f"Usuario: {entry['username']}\nContraseña: {entry['password']}")

    def copy_password(self):
        eid = self.get_selected_id()
        if eid is None:
            return
        entry = self.db.get_entry(self.fernet, eid)
        self.clipboard_clear()
        self.clipboard_append(entry["password"])
        messagebox.showinfo("Copiado", "Contraseña copiada al portapapeles.\n(Se borrará al cerrar la app si tu sistema lo gestiona así)")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestor de Contraseñas Portable")
        self.geometry("700x480")
        self.resizable(False, False)

        # Ícono embebido (no depende de archivos externos)
        try:
            icon_data = base64.b64decode(ICON_BASE64)
            tmp_icon = os.path.join(tempfile.gettempdir(), "passmanager_icon.ico")
            with open(tmp_icon, "wb") as f:
                f.write(icon_data)
            self.iconbitmap(tmp_icon)
        except Exception:
            pass

        self.db = Database(DB_PATH)

        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.show_login()

    def show_login(self):
        for w in self.container.winfo_children():
            w.destroy()
        login = LoginScreen(self.container, self.db, on_success=self.show_main)
        login.pack(fill="both", expand=True)

    def show_main(self, fernet):
        for w in self.container.winfo_children():
            w.destroy()
        self.resizable(True, True)
        main = MainScreen(self.container, self.db, fernet)
        main.pack(fill="both", expand=True)


if __name__ == "__main__":
    app = App()
    app.mainloop()
