export class CVExtractor {
  static async extractText(file: File): Promise<string> {
    const fileType = file.name.split('.').pop()?.toLowerCase();

    switch (fileType) {
      case 'txt':
      case 'md':
        return await this.extractTextFromPlainText(file);
      case 'pdf':
        return await this.extractTextFromPDF(file);
      case 'docx':
        return await this.extractTextFromDOCX(file);
      default:
        throw new Error(`Unsupported file type: ${fileType}`);
    }
  }

  private static async extractTextFromPlainText(file: File): Promise<string> {
    return await file.text();
  }

  private static async extractTextFromPDF(file: File): Promise<string> {
    const arrayBuffer = await file.arrayBuffer();
    const uint8Array = new Uint8Array(arrayBuffer);
    const text = new TextDecoder('utf-8').decode(uint8Array);
    
    const lines: string[] = [];
    const textLines = text.split('\n');
    
    for (const line of textLines) {
      const cleanLine = line.trim();
      if (cleanLine && !cleanLine.startsWith('%') && !cleanLine.startsWith('<<')) {
        lines.push(cleanLine);
      }
    }
    
    return lines.join('\n');
  }

  private static async extractTextFromDOCX(file: File): Promise<string> {
    const arrayBuffer = await file.arrayBuffer();
    const uint8Array = new Uint8Array(arrayBuffer);
    const text = new TextDecoder('utf-8').decode(uint8Array);
    
    const lines: string[] = [];
    const textLines = text.split('\n');
    
    for (const line of textLines) {
      const cleanLine = line.trim();
      if (cleanLine && cleanLine.length > 0) {
        lines.push(cleanLine);
      }
    }
    
    return lines.join('\n');
  }
}

