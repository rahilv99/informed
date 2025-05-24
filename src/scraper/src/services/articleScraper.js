/**
 * Article scraper for extracting full article text using Puppeteer
 */
const { initBrowser, closeBrowser, createPage } = require('../utils/browser');
const { cleanText } = require('../utils/textProcessing');
const { withRetry } = require('../utils/retry');
const config = require('../config');
const { Readability } = require('@mozilla/readability');
const { JSDOM } = require('jsdom');

class ArticleScraper {
  /**
   * Initialize the article scraper
   */
  constructor() {
    console.log('Initializing Article scraper...');
    this.browser = null;
    this.timeout = config.browser.defaultTimeout;
  }
  
  /**
   * Initialize the browser if not already initialized
   * 
   * @returns {Promise<boolean>} - True if browser initialized successfully
   */
  async initBrowser() {
    if (!this.browser) {
      try {
        this.browser = await initBrowser();
        return true;
      } catch (error) {
        console.error('Failed to initialize browser:', error);
        return false;
      }
    }
    return true;
  }
  
  /**
   * Get the full text of an article from its URL
   * 
   * @param {string} googleUrl - URL of the article to scrape
   * @returns {Promise<string>} - Full text of the article
   */
  async getDocumentText(googleUrl) {
    // Initialize browser if needed
    if (!await this.initBrowser()) {
      console.error('Browser not initialized. Cannot proceed.');
      return '';
    }
    
    let page = null;
    let currentUrl = googleUrl;
    
    try {
      // Create a new page
      page = await createPage(this.browser);
      
      // Load the Google News page with a timeout
      console.log('Attempting to load page with Puppeteer...');
      const startTime = Date.now();
      
      try {
        await withRetry(() => page.goto(googleUrl, { 
          waitUntil: 'domcontentloaded',
          timeout: this.timeout
        }));

        console.log(`Page load completed in ${(Date.now() - startTime) / 1000} seconds`);
      } catch (error) {
        console.warn(`Page load timeout for: ${googleUrl}. Moving to the next link.`);
        // Attempt to close with timeout
        try {
          await Promise.race([
            page.close(),
            new Promise((_, reject) => setTimeout(() => reject(new Error('Close timeout')), 5000))
          ]);
        } catch (err) {
          console.error('Failed to close page:', err);
          console.log('Restarting browser...');
          await this.browser.close();
          console.log('Closed browser...');
          this.browser = await initBrowser();
        }
        return '';
      }

      console.log('Starting URL redirect monitoring...');
      
      try {
        // Create custom wait condition that resolves on URL change
        const waitForUrlChange = new Promise((resolve, reject) => {
          const checkInterval = 100; // Check every 100ms
          let elapsedTime = 0;
          
          const intervalId = setInterval(async () => {
            const currentUrl = await page.url();
            if (currentUrl && !currentUrl.includes('news.google.com')) {
              clearInterval(intervalId);
              resolve(currentUrl);
            }
            
            elapsedTime += checkInterval;
            if (elapsedTime >= this.timeout) {
              clearInterval(intervalId);
              reject(new Error('Redirect timeout'));
            }
          }, checkInterval);
        });

        // Wait for either URL change or navigation complete
        const result = await Promise.race([
          waitForUrlChange,
          page.waitForNavigation({ 
            timeout: this.timeout,
            waitUntil: 'networkidle2' 
          })
        ]);

        currentUrl = await page.url();
        if (currentUrl && !currentUrl.includes('news.google.com')) {
          console.log(`URL redirected to: ${currentUrl}`);
        } else {
          console.log('No redirect detected');
        }
      } catch (error) {
        if (error.message === 'Redirect timeout') {
          console.log('No redirect detected within timeout period');
        } else {
          console.warn('Error during redirect monitoring:', error.message);
        }
      }
      
      // Get the content
      const html = await page.content();
      const dom = new JSDOM(html, {
        url: currentUrl, // Provide the current URL for proper base URL resolution
        contentType: 'text/html',
        pretendToBeVisual: true // This helps with content that requires a visual environment
      });
      const reader = new Readability(dom.window.document);
      const content = reader.parse();
      
      // Close the page
      try {
        await Promise.race([
          page.close(),
          new Promise((_, reject) => setTimeout(() => reject(new Error('Close timeout')), 5000))
        ]);
      } catch (err) {
        console.error('Failed to close page:', err);
        console.log('Restarting browser...');
        await this.browser.close();
        console.log('Closed browser...');
        this.browser = await initBrowser();
      }
      console.log(content);
      if (!content) {
        console.error('Failed to parse content with Readability');
        return '';
      } else {
        console.log(`Extracted ${content.textContent.length} characters`);
        return cleanText(content.textContent);
      }
    } catch (error) {
      console.error(`Error following URL ${googleUrl}:`, error);
      try {
        await Promise.race([
          page.close(),
          new Promise((_, reject) => setTimeout(() => reject(new Error('Close timeout')), 5000))
        ]);
      } catch (err) {
        console.error('Failed to close page:', err);
        console.log('Restarting browser...');
        await this.browser.close();
        console.log('Closed browser...');
        this.browser = await initBrowser();
      }
      return '';
    }
  }
  
  
  /**
   * Close the browser and clean up resources
   */
  async close() {
    if (this.browser) {
      await closeBrowser(this.browser);
      this.browser = null;
    }
  }
}

module.exports = ArticleScraper;
