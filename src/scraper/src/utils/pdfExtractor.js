/**
 * PDF text extraction utility
 */
const pdfParse = require('pdf-parse');
const axios = require('axios');
const { cleanText } = require('./textProcessing');
const { withRetry } = require('./retry');

/**
 * Extract text from PDF content
 * 
 * @param {Buffer} pdfBuffer - PDF content as buffer
 * @returns {Promise<string>} - Extracted text
 */
async function extractTextFromPdf(pdfBuffer) {
  try {
    const data = await pdfParse(pdfBuffer);
    return cleanText(data.text);
  } catch (error) {
    console.error('Error extracting text from PDF:', error);
    return 'Error extracting text from PDF';
  }
}

/**
 * Download and extract text from a PDF URL
 * 
 * @param {string} url - URL of the PDF to download and extract
 * @returns {Promise<string>} - Extracted text
 */
async function extractTextFromPdfUrl(url) {
  try {
    // Download PDF with retry logic
    const response = await withRetry(async () => {
      const res = await axios.get(url, { responseType: 'arraybuffer' });
      if (res.status !== 200) {
        throw new Error(`Failed to download PDF: ${res.status}`);
      }
      return res;
    });
    
    // Extract text from PDF
    return await extractTextFromPdf(Buffer.from(response.data));
  } catch (error) {
    console.error(`Error downloading or extracting PDF from ${url}:`, error);
    return `Error processing PDF from ${url}`;
  }
}

module.exports = {
  extractTextFromPdf,
  extractTextFromPdfUrl
};
