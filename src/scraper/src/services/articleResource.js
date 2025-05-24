/**
 * Article resource base class with shared utilities
 */
const stringSimilarity = require('string-similarity');
const axios = require('axios');
const cheerio = require('cheerio');
const config = require('../config');
const { withRetry } = require('../utils/retry');
const { extractTextFromHtml, cleanText } = require('../utils/textProcessing');
const { extractTextFromPdfUrl } = require('../utils/pdfExtractor');

class ArticleResource {
  /**
   * Initialize the article resource
   * 
   * @param {string[]} userInput - User topics for article search
   */
  constructor(userInput) {
    this.userInput = userInput;
    this.fuzzyThreshold = config.article.fuzzyThreshold;
    this.defaultArticleAge = config.article.defaultArticleAge;
    
    // Calculate time constraint
    const today = new Date();
    this.timeConstraint = new Date(today);
    this.timeConstraint.setDate(today.getDate() - this.defaultArticleAge);
  }
  
  /**
   * Check if a title is a duplicate using fuzzy matching
   * 
   * @param {string} newTitle - Title to check
   * @param {string[]} seenTitles - List of previously seen titles
   * @returns {boolean} - True if duplicate, false otherwise
   */
  isDuplicateTitle(newTitle, seenTitles) {
    if (!newTitle || !seenTitles || seenTitles.length === 0) {
      return false;
    }
    
    // Normalize the new title
    newTitle = newTitle.toLowerCase().trim();
    
    // Check for exact match first (faster)
    if (seenTitles.includes(newTitle)) {
      return true;
    }
    
    // Check for fuzzy matches
    for (const seenTitle of seenTitles) {
      // Use string similarity for fuzzy matching
      const similarity = stringSimilarity.compareTwoStrings(newTitle, seenTitle);
      const ratio = similarity * 100;
      
      if (ratio >= this.fuzzyThreshold) {
        console.log(`Fuzzy match found: '${newTitle}' matches '${seenTitle}' with ratio ${ratio}`);
        return true;
      }
    }
    
    return false;
  }
  
  /**
   * Get document text from a URL
   * 
   * @param {string} url - URL to extract text from
   * @returns {Promise<string>} - Extracted text
   */
  async getDocumentText(url) {
    try {
      // For PDF content
      if (url.includes('.pdf')) {
        return await extractTextFromPdfUrl(url);
      }
      
      // For HTML content
      const response = await withRetry(async () => {
        const res = await axios.get(url);
        if (res.status !== 200) {
          throw new Error(`Failed to retrieve document: ${res.status}`);
        }
        return res;
      });
      
      // Extract text from HTML
      const text = extractTextFromHtml(response.data);
      
      // Check for PDF links
      const $ = cheerio.load(response.data);
      const pdfLinks = [];
      
      $('a[href*=".pdf"]').each((_, element) => {
        const link = $(element).attr('href');
        if (link) {
          pdfLinks.push(link);
        }
      });
      
      // Extract text from linked PDFs (first one only to avoid excessive processing)
      let additionalText = '';
      if (pdfLinks.length > 0) {
        try {
          additionalText = await extractTextFromPdfUrl(pdfLinks[0]);
        } catch (error) {
          console.error(`Error retrieving linked PDF: ${error}`);
        }
      }
      
      return text + (additionalText ? `\n${additionalText}` : '');
    } catch (error) {
      console.error(`Error retrieving document: ${error}`);
      return `Error retrieving document: ${error}`;
    }
  }
}

module.exports = ArticleResource;
