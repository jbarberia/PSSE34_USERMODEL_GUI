# code_preview.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit, 
    QPushButton, QMessageBox, QFileDialog, QApplication
)
from PyQt5.QtGui import QFont, QColor, QTextCharFormat, QSyntaxHighlighter
from PyQt5.QtCore import Qt, QRegExp


class FortranSyntaxHighlighter(QSyntaxHighlighter):
    """Resaltador de sintaxis para Fortran 77 / 90 (PSS/E models)"""
    def __init__(self, document):
        super().__init__(document)
        self.rules = []

        # Palabras clave Fortran
        kw_fmt = QTextCharFormat()
        kw_fmt.setForeground(QColor("#0000FF"))  # Azul
        kw_fmt.setFontWeight(QFont.Bold)
        keywords = [
            r"\bSUBROUTINE\b", r"\bEND\b", r"\bCALL\b", r"\bRETURN\b",
            r"\bIF\b", r"\bTHEN\b", r"\bELSE\b", r"\bINTEGER\b",
            r"\bREAL\b", r"\bDO\b", r"\bIMPLICIT\b", r"\bNONE\b",
            r"\bENTRY\b", r"\bCOMMON\b", r"\bDIMENSION\b", r"\bDATA\b"
        ]
        for kw in keywords:
            self.rules.append((QRegExp(kw, Qt.CaseInsensitive), kw_fmt))

        # Arreglos clave de PSS/E (CON, ICON, STATE, DSTATE, VAR)
        psse_fmt = QTextCharFormat()
        psse_fmt.setForeground(QColor("#795E26"))  # Ocre
        psse_fmt.setFontWeight(QFont.Bold)
        for pv in [r"\bCON\b", r"\bICON\b", r"\bSTATE\b", r"\bDSTATE\b", r"\bVAR\b"]:
            self.rules.append((QRegExp(pv, Qt.CaseInsensitive), psse_fmt))

        # Números
        num_fmt = QTextCharFormat()
        num_fmt.setForeground(QColor("#098658"))  # Verde oscuro
        self.rules.append((QRegExp(r"\b[0-9]+(\.[0-9]+)?([eE][+-]?[0-9]+)?\b"), num_fmt))

        # Comentarios Fortran ('!' o columnas 1 con 'C', 'c', '*')
        self.comment_fmt = QTextCharFormat()
        self.comment_fmt.setForeground(QColor("#6A9955"))  # Verde comentario
        self.comment_fmt.setFontItalic(True)

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, fmt)
                index = expression.indexIn(text, index + length)

        if text.startswith(('C', 'c', '*')):
            self.setFormat(0, len(text), self.comment_fmt)
        else:
            c_idx = text.find('!')
            if c_idx != -1:
                self.setFormat(c_idx, len(text) - c_idx, self.comment_fmt)


class CodePreviewWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        self.editor = QPlainTextEdit()
        self.editor.setFont(QFont("Consolas", 10))
        self.editor.setReadOnly(True)
        self.editor.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.highlighter = FortranSyntaxHighlighter(self.editor.document())

        btn_layout = QHBoxLayout()
        self.btn_copy = QPushButton("Copiar Código")
        self.btn_save = QPushButton("Exportar archivo .f")

        self.btn_copy.clicked.connect(self.copy_to_clipboard)
        self.btn_save.clicked.connect(self.save_to_file)

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_copy)
        btn_layout.addWidget(self.btn_save)

        layout.addWidget(self.editor)
        layout.addLayout(btn_layout)

    def set_code(self, code_str: str):
        """Método público para inyectar el código generado"""
        self.editor.setPlainText(code_str)

    def copy_to_clipboard(self):
        QApplication.clipboard().setText(self.editor.toPlainText())
        QMessageBox.information(self, "Portapapeles", "Código copiado exitosamente.")

    def save_to_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "Guardar Subrutina", "", "Archivos Fortran (*.f *.f90)")
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.editor.toPlainText())
            QMessageBox.information(self, "Guardado", f"Archivo guardado en:\n{path}")
