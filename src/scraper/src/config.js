/**
 * Configuration settings for the news scraper
 */
module.exports = {
  // Google News settings
  googleNews: {
    language: 'en',
    country: 'US',
    period: '7d',
    maxResults: 20
  },
  
  // Browser settings
  browser: {
    headless: true,
    defaultTimeout: 5000,
    viewport: {
      width: 1920,
      height: 1080
    },
    args: [
      '--no-sandbox',
      '--disable-dev-shm-usage',
      '--disable-gpu',
      '--disable-setuid-sandbox'
    ]
  },
  
  // Retry settings
  retry: {
    maxRetries: 3,
    baseDelay: 330, // milliseconds
    maxDelay: 1000 // milliseconds
  },
  
  // Article processing
  article: {
    minTextLength: 400,
    fuzzyThreshold: 87,
    defaultArticleAge: 7,
    parallelProcessing: {
      maxWorkers: 1
    }
  }
};
