/**
 * Text processing utilities for extracting and cleaning article content
 */
const cheerio = require('cheerio');

/**
 * Extract text content from HTML using Cheerio
 * 
 * @param {string} html - HTML content to process
 * @returns {string} - Extracted and cleaned text
 */
function extractTextFromHtml(html) {
  try {
    // Use Cheerio for HTML processing
    const $ = cheerio.load(html);
    
    // Remove script and style elements
    $('script, style').remove();
    
    // Get text content
    let text = $.text();
    
    // Clean the extracted text
    return cleanText(text);
  } catch (error) {
    console.error('Error extracting text from HTML:', error);
    return '';
  }
}

/**
 * Clean extracted text by removing extra spaces, normalizing whitespace,
 * handling special characters, and improving readability
 * 
 * @param {string} text - Text to clean
 * @returns {string} - Cleaned text
 */
function cleanText(text) {
  if (!text) {
    return '';
  }
  
  // Replace multiple spaces with a single space
  text = text.replace(/\s+/g, ' ');
  
  // Replace multiple newlines with a single newline
  text = text.replace(/\n\s*\n/g, '\n\n');
  
  // Fix common extraction issues
  text = text.replace(/(\w)-\s+(\w)/g, '$1$2'); // Fix hyphenation
  text = text.replace(/(\d+)\s*\.\s*(\d+)/g, '$1.$2'); // Fix decimal numbers
  
  // Replace special characters that might be incorrectly encoded
  text = text.replace(/â€™/g, "'");
  text = text.replace(/â€œ/g, '"');
  text = text.replace(/â€/g, '"');
  text = text.replace(/â€"/g, '-');
  text = text.replace(/â€"/g, '--');
  
  // Remove non-printable characters
  text = text.replace(/[^\x20-\x7E\n\t]/g, '');
  
  // Trim leading/trailing whitespace
  text = text.trim();
  
  return text;
}

module.exports = {
  extractTextFromHtml,
  cleanText
};
