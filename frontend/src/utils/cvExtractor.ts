const BACKEND_URL = import.meta.env.VITE_BACKEND_API_URL || '';

export class CVExtractor {
  /**
   * Extract text from CV file by uploading to backend
   * Backend uses proper libraries (PyPDF2, python-docx) for accurate extraction
   */
  static async extractText(file: File): Promise<string> {
    try {
      // Create FormData to upload file
      const formData = new FormData();
      formData.append('file', file);

      // Call backend API to extract text
      const response = await fetch(`${BACKEND_URL}/api/extract-cv`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || `Failed to extract text from ${file.name}`);
      }

      const result = await response.json();

      if (!result.success || !result.text) {
        throw new Error('Failed to extract text from file');
      }

      return result.text;
    } catch (error) {
      console.error('Error extracting CV:', error);
      throw error;
    }
  }
}

