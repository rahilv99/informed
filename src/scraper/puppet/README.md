# Puppeteer News Scraper for AWS Lambda

This project is a Node.js implementation of a news article scraper using Puppeteer, designed to run in an AWS Lambda containerized environment. It scrapes Google News for article metadata and extracts full article text from the source websites.

## Project Structure

```
/
├── src/
│   ├── index.js              # Lambda handler entry point
│   ├── config.js             # Configuration settings
│   ├── services/
│   │   ├── googleNewsScraper.js  # Google News article metadata collection
│   │   ├── articleScraper.js     # Article content extraction with Puppeteer
│   │   └── articleResource.js    # Shared utilities and base functionality
│   └── utils/
│       ├── browser.js        # Puppeteer browser management
│       ├── lambda-browser.js # Lambda-specific browser configuration
│       ├── textProcessing.js # Text extraction and cleaning utilities
│       ├── pdfExtractor.js   # PDF text extraction
│       └── retry.js          # Retry mechanism for failed operations
├── package.json              # Node.js dependencies and scripts
├── Dockerfile                # Container configuration for Lambda
└── README.md                 # Documentation
```

## Features

- Google News article metadata scraping
- Full article text extraction using Puppeteer
- PDF content extraction
- Fuzzy matching for article deduplication
- Parallel processing of article batches
- Robust error handling and retry mechanisms
- Lambda-optimized browser configuration
- Containerized deployment for AWS Lambda

## Requirements

- Node.js 18+
- Docker (for building the container)
- AWS CLI (for deployment)

## Local Development

1. Install dependencies:
   ```
   npm install
   ```

2. Run the scraper locally:
   ```
   node src/index.js
   ```

## Lambda Deployment

### Building the Docker Image

1. Build the Docker image:
   ```
   docker build -t puppeteer-news-scraper .
   ```

2. Test the Docker image locally:
   ```
   docker run -p 9000:8080 puppeteer-news-scraper
   ```

### Deploying to AWS Lambda

1. Tag the Docker image for ECR:
   ```
   docker tag puppeteer-news-scraper:latest 905418457861.dkr.ecr.us-east-1.amazonaws.com/puppeteer-news-scraper:latest
   ```

2. Push the Docker image to ECR:
   ```
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 905418457861.dkr.ecr.us-east-1.amazonaws.com
   docker push 905418457861.dkr.ecr.us-east-1.amazonaws.com/puppeteer-news-scraper:latest
   ```

3. Create a Lambda function using the ECR image:
   - Open the AWS Lambda console
   - Create a new function
   - Select "Container image" as the deployment package type
   - Select the ECR image you pushed
   - Configure memory (recommended: at least 1024 MB)
   - Configure timeout (recommended: at least 30 seconds)

## Usage

The Lambda function accepts an event object with the following structure:

```json
{
  "topics": ["topic1", "topic2", "topic3"]
}
```

If no topics are provided, it defaults to `["tariffs", "israel", "immigration"]`.

The function returns a response with the following structure:

```json
{
  "statusCode": 200,
  "body": {
    "message": "Successfully processed articles",
    "count": 10,
    "articles": [
      {
        "title": "Article Title",
        "url": "https://original.url",
        "true_url": "https://final.url",
        "publisher": "Publisher Name",
        "keyword": "search topic",
        "full_text": "Full article text..."
      },
      ...
    ]
  }
}
```

## Lambda Configuration Recommendations

- Memory: At least 1024 MB (2048 MB recommended)
- Timeout: At least 30 seconds (60-120 seconds recommended)
- Ephemeral storage: At least 512 MB

## Improvements Over Python Selenium Version

1. **Performance**:
   - Faster page loading and processing with Puppeteer
   - More efficient resource usage
   - Better control over browser behavior

2. **Stability**:
   - More reliable in headless environments
   - Better error handling capabilities
   - Improved timeout management

3. **Lambda Compatibility**:
   - Optimized for serverless environments
   - Efficient cold start handling
   - Proper resource cleanup

4. **Features**:
   - Built-in request interception for blocking unnecessary resources
   - Network traffic monitoring
   - Performance metrics collection
