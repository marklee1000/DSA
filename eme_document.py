import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from docx import Document
import fitz  # PyMuPDF
from collections import defaultdict

class Node:
    def __init__(self, key):
        self.key = key
        self.left = self.right = None

class BinaryTree:
    def __init__(self):
        self.root = None

    def insert(self, root, key):
        if root is None:
            return Node(key)
        if key.lower() < root.key.lower():
            root.left = self.insert(root.left, key)
        elif key.lower() > root.key.lower():
            root.right = self.insert(root.right, key)
        return root

    def search(self, root, key):
        if root is None:
            return None
        key_lower = key.lower()
        root_key_lower = root.key.lower()
        if key_lower in root_key_lower or root_key_lower in key_lower:
            return root
        if key_lower < root_key_lower:
            return self.search(root.left, key)
        return self.search(root.right, key)

class DocumentAnalyzer:
    def __init__(self):
        self.original_state = None
        self.word_frequency = defaultdict(int)
        self.unique_words = set()
        self.binary_tree = BinaryTree()
        self.undo_stack = []
        self.redo_stack = []

    def save_state(self):
        self.original_state = {
            "word_frequency": dict(self.word_frequency),
            "unique_words": set(self.unique_words),
            "binary_tree_root": self.binary_tree.root,
        }
        self.redo_stack.append(self.original_state)

    def restore_state(self):
        if self.original_state:
            self.word_frequency = defaultdict(int, self.original_state["word_frequency"])
            self.unique_words = set(self.original_state["unique_words"])
            self.binary_tree.root = self.original_state["binary_tree_root"]

    def undo_last_analysis(self):
        self.save_state()
        self.restore_state()
        print("Undo last analysis")

    def redo_last_undo(self):
        if self.redo_stack:
            self.save_state()
            redo_state = self.redo_stack.pop()
            self.word_frequency = defaultdict(int, redo_state["word_frequency"])
            self.unique_words = set(redo_state["unique_words"])
            self.binary_tree.root = redo_state["binary_tree_root"]
            self.undo_stack.append({
                "word_frequency": dict(self.word_frequency),
                "unique_words": set(self.unique_words),
                "binary_tree_root": self.binary_tree.root,
            })
            print("Redo last undone analysis")
            return True
        else:
            print("No analysis to redo")
            return False

    def analyze_document(self, document):
        self.save_state()
        for word in document:
            self.word_frequency[word] += 1
            self.unique_words.add(word)
            self.binary_tree.root = self.binary_tree.insert(self.binary_tree.root, word)

    def word_frequency_analysis(self):
        sorted_words = sorted(self.word_frequency.items(), key=lambda x: x[1], reverse=True)
        return sorted_words

    def search_word_binary_tree(self, word):
        word_lower = word.lower()
        node = self.binary_tree.search(self.binary_tree.root, word_lower)
        return node

    def word_count_for_search_word(self, document, search_word):
        search_word_lower = search_word.lower()
        document_lower = [word.lower() for word in document]
        partial_matches = [word for word in document_lower if search_word_lower in word]
        return len(partial_matches)

# Create an instance of DocumentAnalyzer
analyzer = DocumentAnalyzer()

def choose_file(text_widget):
    file_path = filedialog.askopenfilename(filetypes=[("Word Documents", "*.docx"), ("PDF Documents", "*.pdf")])
    if file_path:
        if file_path.lower().endswith(".docx"):
            document_content = read_docx(file_path)
        elif file_path.lower().endswith(".pdf"):
            document_content = read_pdf(file_path)
        else:
            document_content = "Unsupported file format"
        
        text_widget.delete(1.0, tk.END)
        text_widget.insert(tk.END, document_content)
        return document_content

def read_docx(file_path):
    doc = Document(file_path)
    content = []
    for para in doc.paragraphs:
        content.append(para.text)
    return '\n'.join(content)

def read_pdf(file_path):
    doc = fitz.open(file_path)
    content = []
    for page in doc.pages():
        content.append(page.get_text())
    return '\n'.join(content)

def analyze_document(text_widget, search_word_entry, results_text):
    document_content = text_widget.get(1.0, tk.END).split()
    analyzer.__init__()
    analyzer.analyze_document(document_content)

    results_text.delete(1.0, tk.END)
    results_text.insert(tk.END, "Word Frequency Analysis:\n")
    results_text.insert(tk.END, "\n".join([f"{word}: {freq}" for word, freq in analyzer.word_frequency_analysis()]))

    search_word = search_word_entry.get()
    result_node = analyzer.search_word_binary_tree(search_word)

    if result_node:
        word_count = analyzer.word_count_for_search_word(document_content, search_word)
        message = f"Search for '{search_word}' in document: Word found!\nWord count: {word_count}"
        messagebox.showinfo("Search Result", message)
        results_text.insert(tk.END, f"\n\nSearch for '{search_word}' in document: Word found!")
        results_text.insert(tk.END, f"\nWord count for '{search_word}': {word_count}")
    else:
        message = f"Search for '{search_word}' in document: Word not found."
        messagebox.showinfo("Search Result", message)
        results_text.insert(tk.END, f"\n\nSearch for '{search_word}' in document: Word not found.")

def undo_last_analysis(results_text):
    analyzer.undo_last_analysis()
    results_text.delete(1.0, tk.END)
    print("Analysis undone")

def redo_last_analysis(results_text):
    if analyzer.redo_last_undo():
        results_text.delete(1.0, tk.END)
        results_text.insert(tk.END, "Redone Word Frequency Analysis:\n")
        results_text.insert(tk.END, "\n".join([f"{word}: {freq}" for word, freq in analyzer.word_frequency_analysis()]))
        print("Redone analysis displayed in GUI")
        messagebox.showinfo("Redo Analysis", "Redone analysis displayed.")
    else:
        messagebox.showinfo("Redo Analysis", "No analysis to redo.")

# GUI setup
root = tk.Tk()
root.title("Document Analyzer")
root.geometry("800x600")  # Set initial window size

style = ttk.Style()
style.theme_use("clam")

# Menu Bar
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

file_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Open", command=lambda: choose_file(text))
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.destroy)

# File Frame
file_frame = ttk.Frame(root)
file_frame.pack(pady=10)

# Upload Button
upload_icon = ImageTk.PhotoImage(Image.open("upload_icon.png").resize((20, 20), Image.LANCZOS))
upload_button = ttk.Button(file_frame, text="Upload File", image=upload_icon, compound=tk.LEFT, command=lambda: choose_file(text))
upload_button.image = upload_icon
upload_button.pack(side=tk.LEFT, padx=5)

# Analysis Frame
analysis_frame = ttk.Frame(root)
analysis_frame.pack(pady=10)

# Search Word Entry
search_word_label = ttk.Label(analysis_frame, text="Search Word:")
search_word_label.grid(row=0, column=0, padx=5)

search_word_entry = ttk.Entry(analysis_frame)
search_word_entry.grid(row=0, column=1, padx=5)

# Analyze Button
analyze_button = ttk.Button(analysis_frame, text="Analyze Document", command=lambda: analyze_document(text, search_word_entry, results_text))
analyze_button.grid(row=0, column=2, padx=5)

# Undo and Redo Buttons
undo_button = ttk.Button(analysis_frame, text="Undo", command=lambda: undo_last_analysis(results_text))
undo_button.grid(row=0, column=3, padx=5)

redo_button = ttk.Button(analysis_frame, text="Redo", command=lambda: redo_last_analysis(results_text))
redo_button.grid(row=0, column=4, padx=5)

# Notebook
notebook = ttk.Notebook(root)
notebook.pack(pady=10)

doc_tab = ttk.Frame(notebook)
analysis_tab = ttk.Frame(notebook)

notebook.add(doc_tab, text="Document")
notebook.add(analysis_tab, text="Analysis")

# Text Widgets
text = tk.Text(doc_tab, height=20, width=90)
text.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

# Scrollbar for Document Text Widget
text_scrollbar = tk.Scrollbar(doc_tab, command=text.yview)
text_scrollbar.grid(row=0, column=1, sticky="ns")
text['yscrollcommand'] = text_scrollbar.set

results_text = tk.Text(analysis_tab, height=20, width=90)
results_text.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

# Scrollbar for Analysis Text Widget
results_scrollbar = tk.Scrollbar(analysis_tab, command=results_text.yview)
results_scrollbar.grid(row=0, column=1, sticky="ns")
results_text['yscrollcommand'] = results_scrollbar.set

# Status Label
status_label = ttk.Label(root, text="Ready", anchor=tk.W)
status_label.pack(side=tk.BOTTOM, fill=tk.X)

# Configure row and column weights for resizing
for i in range(2):
    root.columnconfigure(i, weight=1)
    root.rowconfigure(i, weight=1)

root.mainloop()