import tkinter as tk
from tkinter import filedialog, messagebox
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
        # Save the state to the redo stack as well
        self.redo_stack.append(self.original_state)

    def restore_state(self):
        if self.original_state:
            self.word_frequency = defaultdict(int, self.original_state["word_frequency"])
            self.unique_words = set(self.original_state["unique_words"])
            self.binary_tree.root = self.original_state["binary_tree_root"]

    def undo_last_analysis(self):
        self.save_state()  # Save the current state before undoing
        self.restore_state()  # Restore the state to the original state
        print("Undo last analysis")

    def redo_last_undo(self):
        if self.redo_stack:
            # Save the current state before redoing
            self.save_state()

            # Pop the last state from the redo_stack
            redo_state = self.redo_stack.pop()

            # Update the current state with the redo_state
            self.word_frequency = defaultdict(int, redo_state["word_frequency"])
            self.unique_words = set(redo_state["unique_words"])
            self.binary_tree.root = redo_state["binary_tree_root"]

            # Save the updated state to the undo_stack
            self.undo_stack.append({
                "word_frequency": dict(self.word_frequency),
                "unique_words": set(self.unique_words),
                "binary_tree_root": self.binary_tree.root,
            })

            print("Redo last undone analysis")
            return True  # Indicate that redo was successful
        else:
            print("No analysis to redo")
            return False  # Indicate that there is no analysis to redo


    def analyze_document(self, document):
        self.save_state()  # Save the current state before analysis
        for word in document:
            self.word_frequency[word] += 1
            self.unique_words.add(word)
            self.binary_tree.root = self.binary_tree.insert(self.binary_tree.root, word)

    def word_frequency_analysis(self):
        # Sort words by frequency
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

# GUI setup
def choose_file(text_widget):
    file_path = filedialog.askopenfilename(filetypes=[("Word Documents", "*.docx"), ("PDF Documents", "*.pdf")])
    if file_path:
        if file_path.lower().endswith(".docx"):
            document_content = read_docx(file_path)
        elif file_path.lower().endswith(".pdf"):
            document_content = read_pdf(file_path)
        else:
            document_content = "Unsupported file format"
        
        text_widget.delete(1.0, tk.END)  # Clear previous content
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

def analyze_document(analyzer, text_widget, search_word_entry, results_text):
    document_content = text_widget.get(1.0, tk.END).split()  # Split document content into words

    # Clear the current state of the analyzer before each analysis
    analyzer.__init__()

    # Perform the analysis
    analyzer.analyze_document(document_content)

    # Display analysis results in the GUI
    results_text.delete(1.0, tk.END)  # Clear previous results
    results_text.insert(tk.END, "Word Frequency Analysis:\n")
    results_text.insert(tk.END, "\n".join([f"{word}: {freq}" for word, freq in analyzer.word_frequency_analysis()]))

    search_word = search_word_entry.get()  # Get the search word from the entry widget
    result_node = analyzer.search_word_binary_tree(search_word)

    if result_node:
        word_count = analyzer.word_count_for_search_word(document_content, search_word)

        # Display pop-up message
        message = f"Search for '{search_word}' in binary tree: Word found!\nWord count: {word_count}"
        messagebox.showinfo("Search Result", message)

        results_text.insert(tk.END, f"\n\nSearch for '{search_word}' in binary tree: Word found!")
        results_text.insert(tk.END, f"\nWord count for '{search_word}': {word_count}")
    else:
        # Display pop-up message
        message = f"Search for '{search_word}' in binary tree: Word not found."
        messagebox.showinfo("Search Result", message)

        results_text.insert(tk.END, f"\n\nSearch for '{search_word}' in binary tree: Word not found.")

def undo_last_analysis(analyzer, results_text):
    analyzer.undo_last_analysis()
    results_text.delete(1.0, tk.END)  # Clear the results text after undoing analysis
    print("Analysis undone")

def redo_last_analysis(analyzer, results_text):
    if analyzer.redo_last_undo():
        # Display redone analysis results in the GUI
        results_text.delete(1.0, tk.END)  # Clear previous results
        results_text.insert(tk.END, "Redone Word Frequency Analysis:\n")
        results_text.insert(tk.END, "\n".join([f"{word}: {freq}" for word, freq in analyzer.word_frequency_analysis()]))
        print("Redone analysis displayed in GUI")

        # Display pop-up message
        messagebox.showinfo("Redo Analysis", "Redone analysis displayed.")
    else:
        # Display pop-up message if no analysis to redo
        messagebox.showinfo("Redo Analysis", "No analysis to redo.")

root = tk.Tk()
root.title("Document Analyzer")

analyzer = DocumentAnalyzer()  # Create an instance of DocumentAnalyzer

upload_button = tk.Button(root, text="Upload File", command=lambda: choose_file(text))
upload_button.pack(pady=10)

search_word_label = tk.Label(root, text="Search Word:")
search_word_label.pack(pady=5)

search_word_entry = tk.Entry(root)
search_word_entry.pack(pady=5)

analyze_button = tk.Button(root, text="Analyze Document", command=lambda: analyze_document(analyzer, text, search_word_entry, results_text))
analyze_button.pack(pady=5)

undo_button = tk.Button(root, text="Undo Last Analysis", command=lambda: undo_last_analysis(analyzer, results_text))
undo_button.pack(pady=5)

redo_button = tk.Button(root, text="Redo Last Analysis", command=lambda: redo_last_analysis(analyzer, results_text))
redo_button.pack(pady=5)

text = tk.Text(root, height=15, width=50)
text.pack(padx=10, pady=10)

results_text = tk.Text(root, height=10, width=50)
results_text.pack(padx=10, pady=10)

root.mainloop()
