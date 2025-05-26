/**
 * Main entry point for the Lambda function
 */
const GoogleNewsScraper = require('./services/googleNewsScraper');
const ArticleScraper = require('./services/articleScraper');
const config = require('./config');
const { S3Client, PutObjectCommand } = require('@aws-sdk/client-s3');


/**
 * Lambda handler function
 * 
 * @param {Object} event - Lambda event object
 * @returns {Promise<Object>} - Lambda response object
 */
exports.handler = async (event) => {
  console.log('Received event:', JSON.stringify(event, null, 2));
  
  try {
    // Parse input topics from event
    const record = event.Records[0];
    payload = JSON.parse(record.body);
    const topics = payload.topics || ['US Politics']; // test topic
    
    // Run the main function
    const articles = await main(topics);

    // serialize to s3
    await saveToS3(articles, topics);    
    
    // Return the results
    return {
      statusCode: 200,
      body: JSON.stringify({
        message: 'Successfully processed articles',
        count: articles.length,
        articles
      })
    };
  } catch (error) {
    console.error('Error processing request:', error);
    
    return {
      statusCode: 500,
      body: JSON.stringify({
        message: 'Error processing request',
        error: error.message
      })
    };
  }
};

/**
 * Save articles to S3 bucket
 * 
 * @param {Array} articles - Array of processed articles
 * @param {Array} topics - Array of topics used for scraping
 * @returns {Promise<void>}
 */
async function saveToS3(articles, topics) {
  const s3Client = new S3Client({ region: process.env.AWS_REGION || 'us-east-1' });
  
  // Create a timestamp for the filename
  const topicsStr = topics.join('-');
  // truncate name to 50 characters to avoid S3 key length issues
  if (topicsStr.length > 50) {
    console.warn(`Topics string "${topicsStr}" is too long, truncating to 50 characters`);
    topicsStr = topicsStr.substring(0, 50);
  }
  // Replace spaces with underscores for S3 compatibility
  const sanitizedTopicsStr = topicsStr.replace(/\s+/g, '_').toLowerCase();
  // Create a filename based on topics
  const filename = `gnews/${sanitizedTopicsStr}.json`;
  
  const params = {
    Bucket: process.env.BUCKET_NAME,
    Key: filename,
    Body: JSON.stringify(articles),
    ContentType: 'application/json'
  };

  try {
    console.log(`Saving articles to S3: ${filename}`);
    await s3Client.send(new PutObjectCommand(params));
    console.log('Successfully saved articles to S3');
  } catch (error) {
    console.error('Error saving to S3:', error);
    throw error;
  }
}

/**
 * Main function to run the Google News Scraper
 * 
 * @param {string[]} topics - Topics to search for
 * @returns {Promise<Array>} - Processed articles
 */
async function main(topics) {
  console.log(`Starting news scraper with topics: ${topics.join(', ')}`);
  
  // Initialize the Google News Scraper
  const gnewsScraper = new GoogleNewsScraper(topics);
  
  // Get articles related to user topics
  const articlesData = await gnewsScraper.getArticles();
  
  if (!articlesData || articlesData.length === 0) {
    console.log('No articles found');
    return [];
  }
  
  console.log(`Retrieved ${articlesData.length} articles`);
  
  // Process articles
  const processedArticles = await processArticles(articlesData);
  
  console.log(`Finished processing ${processedArticles.length} articles`);
  
  return processedArticles;
}

/**
 * Process articles
 * 
 * @param {Array} articlesData - Array of article data
 * @returns {Promise<Array>} - Processed articles
 */
async function processArticles(articlesData) {
  // Initialize the article scraper
  const scraper = new ArticleScraper();
  
  try {
    const results = [];
    
    // Process each article
    for (const article of articlesData) {
      try {
        console.log(`Processing article: ${article.title}`);
        
        // Get the full text
        const fullText = await scraper.getDocumentText(article.url);
        
        // Skip articles with insufficient content
        if (!fullText || fullText.length < config.article.minTextLength) {
          console.warn(`Skipping article with insufficient content: ${article.title.substring(0, 50)}`);
          continue;
        }
        
        // Get the true URL after redirects
        const trueUrl = scraper.browser ? 
          (await scraper.browser.pages())[0]?.url() || article.url : 
          article.url;
        
        // Add to results
        results.push({
          title: article.title,
          url: trueUrl,
          publisher: article.publisher,
          keyword: article.keyword,
          full_text: fullText
        });
        
      } catch (error) {
        console.error(`Error retrieving text for article ${article.title}:`, error);
      }
    }
    
    return results;
  } finally {
    // Close the scraper to clean up resources
    await scraper.close();
  }
}

// For local testing
if (require.main === module) {
  // Example user input
  const topics = ['tariffs', 'israel', 'immigration'];
  
  // Run the main function with user input
  main(topics)
    .then(articles => {
      console.log('Finished processing articles.');
      
      // Print article details
      articles.forEach((article, idx) => {
        console.log(`Title: ${article.title}`);
        console.log(`URL: ${article.url}`);
        console.log(`Full Text (first 500 chars):\n${article.full_text.substring(0, 500)}`);
        console.log('-'.repeat(80));
      });
    })
    .catch(error => {
      console.error('Error running main function:', error);
    });
}
