/**
 * Google News scraper for retrieving article metadata
 */
const axios = require('axios');
const ArticleResource = require('./articleResource');
const { withRetry } = require('../utils/retry');
const config = require('../config');

class GoogleNewsScraper extends ArticleResource {
  /**
   * Initialize the Google News scraper
   * 
   * @param {string[]} userTopics - User topics for article search
   */
  constructor(userTopics) {
    super(userTopics);
    console.log('Initializing Google News scraper...');
    
    // Set up Google News parameters
    this.period = config.googleNews.period;
    this.language = config.googleNews.language;
    this.country = config.googleNews.country;
    this.maxResults = config.googleNews.maxResults;
  }
  
  /**
   * Search for news articles related to user topics and store metadata
   * 
   * @returns {Promise<Array>} - Array of article metadata
   */
  async getArticles() {
    console.log('Starting Google News article retrieval');
    
    try {
      const results = [];
      
      // Process each user topic
      for (const topic of this.userInput) {
        try {
          console.log(`Searching for news articles related to: ${topic}`);
          
          // Get news articles from Google News
          const newsResults = await this.fetchNewsForTopic(topic);
          
          console.log(`Found ${newsResults.length} articles for topic: ${topic}`);
          
          // Process each article
          const seenTitles = [];
          for (const article of newsResults) {
            // Extract article information
            const title = article.title || 'No title';
            const url = article.link || '';
            const publisher = article.source || 'Unknown';
            
            if (this.isDuplicateTitle(title, seenTitles)) {
              console.log(`Skipping duplicate article: ${title}`);
              continue;
            }
            
            // Add article to results
            results.push({
              title,
              url,
              publisher,
              keyword: topic
            });
            
            seenTitles.push(title.toLowerCase().trim());
          }
        } catch (error) {
          console.error(`Error processing Google News query for ${topic}:`, error);
        }
      }
      
      // Return results
      if (results.length > 0) {
        console.log(`Retrieved ${results.length} Google News articles in total`);
        
        // Remove duplicates
        const uniqueResults = this.removeDuplicates(results);
        console.log(`After deduplication: ${uniqueResults.length} articles`);
        
        return uniqueResults;
      } else {
        console.warn('No Google News articles found matching the search criteria');
        return [];
      }
    } catch (error) {
      console.error('Error in Google News integration:', error);
      return [];
    }
  }
  
  /**
   * Fetch news articles for a specific topic
   * 
   * @param {string} topic - Topic to search for
   * @returns {Promise<Array>} - Array of article data
   */
  async fetchNewsForTopic(topic) {
    try {
      // Construct the URL for the topic search
      const url = `https://news.google.com/rss/search?q=${encodeURIComponent(topic)}&hl=${this.language}&gl=${this.country}&ceid=${this.country}:${this.language}`;
      
      // Fetch the RSS feed with retry logic
      const response = await withRetry(async () => {
        const res = await axios.get(url);
        if (res.status !== 200) {
          throw new Error(`Failed to fetch news: ${res.status}`);
        }
        return res;
      });
      
      // Parse the XML response
      const articles = this.parseRssXml(response.data);
      
      // Limit results
      return articles.slice(0, this.maxResults);
    } catch (error) {
      console.error(`Error fetching news for topic ${topic}:`, error);
      return [];
    }
  }
  
  /**
   * Parse RSS XML to extract article data
   * 
   * @param {string} xml - RSS XML content
   * @returns {Array} - Array of article data
   */
  parseRssXml(xml) {
    const articles = [];
    
    try {
      // Simple XML parsing using regex for demonstration
      const itemRegex = /<item>([\s\S]*?)<\/item>/g;
      const titleRegex = /<title>([\s\S]*?)<\/title>/;
      const linkRegex = /<link>([\s\S]*?)<\/link>/;
      const sourceRegex = /<source url="[^"]*">([\s\S]*?)<\/source>/;
      
      let match;
      while ((match = itemRegex.exec(xml)) !== null) {
        const itemContent = match[1];
        
        const titleMatch = titleRegex.exec(itemContent);
        const linkMatch = linkRegex.exec(itemContent);
        const sourceMatch = sourceRegex.exec(itemContent);
        
        if (titleMatch && linkMatch) {
          articles.push({
            title: titleMatch[1],
            link: linkMatch[1],
            source: sourceMatch ? sourceMatch[1] : 'Unknown'
          });
        }
      }
    } catch (error) {
      console.error('Error parsing RSS XML:', error);
    }
    
    return articles;
  }
  
  /**
   * Remove duplicate articles from results
   * 
   * @param {Array} articles - Array of article data
   * @returns {Array} - Array of unique article data
   */
  removeDuplicates(articles) {
    const uniqueUrls = new Set();
    return articles.filter(article => {
      if (uniqueUrls.has(article.url)) {
        return false;
      }
      uniqueUrls.add(article.url);
      return true;
    });
  }
}

module.exports = GoogleNewsScraper;
