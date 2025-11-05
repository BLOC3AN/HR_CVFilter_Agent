from src.utils.logger import Logger
logger = Logger(__name__)

import PyPDF2
from docx import Document
from typing import Optional

class CVExtractor:
    """Extract text content from CV files in various formats"""
    
    @staticmethod
    def extract_from_pdf(file) -> str:
        """Extract text from PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            logger.info(f"✅ Successfully extracted text from PDF ({len(text)} characters)")
            return text.strip()
        except Exception as e:
            logger.error(f"❌ Error extracting PDF: {str(e)}")
            return ""
    
    @staticmethod
    def extract_from_docx(file) -> str:
        """Extract text from DOCX file"""
        try:
            doc = Document(file)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            logger.info(f"✅ Successfully extracted text from DOCX ({len(text)} characters)")
            return text.strip()
        except Exception as e:
            logger.error(f"❌ Error extracting DOCX: {str(e)}")
            return ""
    
    @staticmethod
    def extract_from_txt(file) -> str:
        """Extract text from TXT file"""
        try:
            text = file.read().decode('utf-8')
            logger.info(f"✅ Successfully extracted text from TXT ({len(text)} characters)")
            return text.strip()
        except Exception as e:
            logger.error(f"❌ Error extracting TXT: {str(e)}")
            return ""
    
    @staticmethod
    def extract_from_md(file) -> str:
        """Extract text from MD file"""
        try:
            text = file.read().decode('utf-8')
            logger.info(f"✅ Successfully extracted text from MD ({len(text)} characters)")
            return text.strip()
        except Exception as e:
            logger.error(f"❌ Error extracting MD: {str(e)}")
            return ""
    
    @staticmethod
    def extract(file, file_type: str) -> str:
        """
        Extract text from file based on file type

        Args:
            file: Uploaded file object
            file_type: File extension (pdf, docx, doc, txt, md)

        Returns:
            Extracted text content
        """
        file_type = file_type.lower()

        if file_type == "pdf":
            return CVExtractor.extract_from_pdf(file)
        elif file_type in ["docx", "doc"]:
            # Both .docx and .doc can be handled by python-docx
            return CVExtractor.extract_from_docx(file)
        elif file_type == "txt":
            return CVExtractor.extract_from_txt(file)
        elif file_type == "md":
            return CVExtractor.extract_from_md(file)
        else:
            logger.error(f"❌ Unsupported file type: {file_type}")
            return ""

    @staticmethod
    def extract_text(file) -> str:
        """
        Extract text from file by auto-detecting file type from filename

        Args:
            file: Uploaded file object with .name attribute

        Returns:
            Extracted text content
        """
        try:
            # Get file extension from filename
            filename = getattr(file, 'name', '')
            if not filename:
                logger.error("❌ File has no name attribute")
                return ""

            # Extract file extension
            file_ext = filename.split('.')[-1].lower()

            # Extract text based on file type
            return CVExtractor.extract(file, file_ext)

        except Exception as e:
            logger.error(f"❌ Error extracting text: {str(e)}")
            return ""

