/**
 * Article scraper for extracting full article text using Puppeteer
 */
const { initBrowser, closeBrowser, createPage } = require('../utils/browser');
const { cleanText } = require('../utils/textProcessing');
const { withRetry } = require('../utils/retry');
const config = require('../config');
const { Readability } = require('@mozilla/readability');
const { JSDOM } = require('jsdom');
const cheerio = require('cheerio');

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
      page = await Promise.race([ createPage(this.browser), 
        new Promise((_, reject) => setTimeout(() => reject(new Error('Page creation timeout')), this.timeout+100)) 
      ]);
      if (!page) {
        console.error('Failed to create a new page within the timeout period.');
        return '';
      }
      
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
      
      // Get the content
      const html = await page.content();
      const dom = new JSDOM(html, {
        url: currentUrl, // Provide the current URL for proper base URL resolution
        contentType: 'text/html',
        pretendToBeVisual: true // This helps with content that requires a visual environment
      });
      const reader = new Readability(dom.window.document);
      const content = reader.parse();
      let cleaned; 

      if (content && content.textContent.length > 100) {
        console.log(`Readability parsed content from: ${currentUrl}`);
        console.log(`Extracted ${content.textContent.length} characters`);
        console.log('Text (first 2000 chars): ', content.textContent.slice(0, 2000));
        console.log('Excerpt: ', content.excerpt);
        cleaned = cleanText(content.textContent);
        console.log(`After cleaning text: ${cleaned.length} characters`);
      } else {
        console.warn('Failed to parse content with Readability. Manual parsing ');
        const content = await this.getContent(page);
        console.log(`Extracted ${content.length} characters`);
        console.log('Text (first 2000 chars): ', content.slice(0, 2000));
        cleaned = cleanText(content);
        console.log(`After cleaning text: ${cleaned.length} characters`);
      }

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
      if (!cleaned || cleaned.length === 0) {
        console.warn('No content extracted or cleaned text is empty.');
        return '';
      } else {
        return cleaned; // '' if error, otherwise cleaned text
      }
    } catch (error) {
      console.error(`Error following URL ${googleUrl}:`, error);

      async function isPageOpen(page) {
        try {
          await page.url(); // Will throw if page is closed
          return true;
        } catch (error) {
          return false;
        }
      }

      // Then replace the if (page) check with:
      if (await isPageOpen(page)) {
        try {
          await Promise.race([
            page.close(),
            new Promise((_, reject) => setTimeout(() => reject(new Error('Close timeout')), 5000))
          ]);
        } catch (err) {
          console.error('Failed to close page:', err);
          // ...rest of error handling
        }
      }
      return '';
    }
  }
  
  /**
   * Extract content from a page
   * 
   * @param {Page} page - Puppeteer page object
   * @returns {Promise<string>} - Extracted content
   */
  async getContent(page) {
    console.log(`Attempting to extract content from: ${page.url()}`);
    const OPERATION_TIMEOUT = 5000; // 5 second timeout for each operation
    
    try {
      // Wait for content to load with timeout
      await Promise.race([
        page.waitForSelector('body', { timeout: OPERATION_TIMEOUT }),
        new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Body selector timeout')), OPERATION_TIMEOUT)
        )
      ]);
      
      // Extract article content with timeout
      const content = await Promise.race([
        page.evaluate(() => {
          // Try to find the main article content
          const articleSelectors = [
            'article',
            '[role="article"]',
            '.article-content',
            '.article-body',
            '.story-body',
            '.story-content',
            '.post-content',
            '.entry-content',
            'main',
            '#content',
            '.content'
          ];
          
          let articleElement = null;
          
          // Try each selector until we find content
          for (const selector of articleSelectors) {
            const elements = document.querySelectorAll(selector);
            if (elements.length > 0) {
              // Use the largest element by content length
              let maxLength = 0;
              let bestElement = null;
              
              for (const element of elements) {
                if (element.textContent.length > maxLength) {
                  maxLength = element.textContent.length;
                  bestElement = element;
                }
              }
              
              if (bestElement && maxLength > 500) {
                articleElement = bestElement;
                break;
              }
            }
          }
          
          // If no article element found, use body
          if (!articleElement) {
            articleElement = document.body;
          }
          
          // Remove unwanted elements
          const unwantedSelectors = [
            'script', 'style', 'nav', 'header', 'footer',
            '.nav', '.header', '.footer', '.menu', '.sidebar',
            '.comments', '.advertisement', '.ad', '.social',
            '.related', '.recommended'
          ];
          
          for (const selector of unwantedSelectors) {
            const elements = articleElement.querySelectorAll(selector);
            elements.forEach(el => el.parentNode?.removeChild(el));
          }
          
          return articleElement.textContent || document.body.textContent || '';
        }),
        new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Content extraction timeout')), OPERATION_TIMEOUT)
        )
      ]);
      
      // Clean the extracted text
      const cleanedText = cleanText(content);
      console.log(`Extracted text length: ${cleanedText.length} characters`);
      
      return cleanedText;
      
    } catch (error) {
      console.warn(`Error getting article content: ${error}`);
      
      // Fallback: get HTML and use Cheerio with timeout
      try {
        const html = await Promise.race([
          page.content(),
          new Promise((_, reject) => 
            setTimeout(() => reject(new Error('HTML content timeout')), OPERATION_TIMEOUT)
          )
        ]);
        
        const $ = cheerio.load(html);
        
        // Remove unwanted elements
        $('script, style, nav, header, footer, .nav, .header, .footer, .menu, .sidebar, .comments, .advertisement, .ad, .social, .related, .recommended').remove();
        
        // Get text from article or main content
        let text = '';
        const articleSelectors = [
          'article', '[role="article"]', '.article-content',
          '.article-body', '.story-body', '.story-content',
          '.post-content', '.entry-content', 'main',
          '#content', '.content'
        ];
        
        for (const selector of articleSelectors) {
          if ($(selector).length) {
            text = $(selector).text();
            if (text.length > 500) break;
          }
        }
        
        // If no article found, use body
        if (!text || text.length < 500) {
          text = $('body').text();
        }
        
        const cleanedText = cleanText(text);
        console.log(`Fallback extraction text length: ${cleanedText.length} characters`);
        
        return cleanedText;
        
      } catch (fallbackError) {
        console.error(`Fallback extraction failed: ${fallbackError}`);
        return '';
      }
    }
  }

  /**
   * Close the browser and clean up resources
   */
  async close() {
    if (this.browser) {
      try {
      await Promise.race([
        closeBrowser(this.browser),
        new Promise((_, reject) => setTimeout(() => reject(new Error('Browser close timeout')), 10000))
      ]);
      this.browser = null;
    } catch (error) {
        console.error('Error closing browser:', error);
      }
    }
  }
}

module.exports = ArticleScraper;
