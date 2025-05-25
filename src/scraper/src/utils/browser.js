/**
 * Browser utility for managing Puppeteer browser instances
 */
const puppeteer = require('puppeteer');
const config = require('../config');
const puppeteerCore = require('puppeteer-core');
const chromium = require('@sparticuz/chromium');

/**
 * Initialize a Puppeteer browser instance
 * 
 * @returns {Promise<Browser>} Puppeteer browser instance
 */
async function initBrowser() {
  console.log('Initializing browser...');
  
  // identify whether we are running locally or in AWS
  const isLocal = process.env.AWS_EXECUTION_ENV === undefined;

  const browser = isLocal
      // if we are running locally, use the puppeteer that is installed in the node_modules folder
      ? await puppeteer.launch({
          headless: config.browser.headless,
          args: config.browser.args,
          defaultViewport: {
            width: config.browser.viewport.width,
            height: config.browser.viewport.height
          }
        })
      // if we are running in AWS, download and use a compatible version of chromium at runtime
      : await puppeteerCore.launch({
          args: chromium.args,
          defaultViewport: {
            width: config.browser.viewport.width,
            height: config.browser.viewport.height
          },
          executablePath: await chromium.executablePath(),
          headless: chromium.headless,
      });
  
  console.log('Browser initialized successfully');
  return browser;
}

/**
 * Safely close a browser instance and clean up resources
 * 
 * @param {Browser} browser - Puppeteer browser instance to close
 */
async function closeBrowser(browser) {
  if (browser) {
    try {
      console.log('Closing browser...');
      const pages = await browser.pages();
        for (let i = 0; i < pages.length; i++) {
          await pages[i].close();
        }
      await browser.close();
      console.log('Browser closed successfully');
    } catch (error) {
      console.error('Error closing browser:', error);
    }
  }
}

/**
 * Create a new page with optimized settings
 * 
 * @param {Browser} browser - Puppeteer browser instance
 * @returns {Promise<Page>} Configured Puppeteer page
 */
async function createPage(browser) {
  const page = await browser.newPage();
  
  // Set default timeout
  page.setDefaultTimeout(5000); // 5 seconds
  
  // Block unnecessary resources to improve performance
  await page.setRequestInterception(true);
  page.on('request', (request) => {
    const resourceType = request.resourceType();
    if (['image', 'stylesheet', 'font', 'media'].includes(resourceType)) {
      request.abort();
    } else {
      request.continue();
    }
  });
  
  // Set user agent
  await page.setUserAgent(
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
  );
  
  return page;
}

module.exports = {
  initBrowser,
  closeBrowser,
  createPage
};
