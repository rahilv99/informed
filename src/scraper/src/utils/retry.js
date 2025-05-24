/**
 * Retry utility for handling transient errors
 */
const config = require('../config');

/**
 * Executes a function with retry logic and exponential backoff
 * 
 * @param {Function} fn - The function to execute
 * @param {Array} args - Arguments to pass to the function
 * @returns {Promise<any>} - Result of the function execution
 */
async function withRetry(fn, ...args) {
  const { maxRetries, baseDelay, maxDelay } = config.retry;
  
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await fn(...args);
    } catch (error) {
      // If this is the last attempt, throw the error
      if (attempt === maxRetries - 1) {
        throw error;
      }
      
      // Calculate delay with exponential backoff and jitter
      const delay = Math.min(
        baseDelay * Math.pow(2, attempt) + Math.random() * 1000,
        maxDelay
      );
      
      console.log(`Attempt ${attempt + 1} failed, retrying in ${delay}ms: ${error.message}`);
      
      // Wait before next attempt
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
}

module.exports = {
  withRetry
};
