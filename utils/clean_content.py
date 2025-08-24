import psycopg2
import re


db_access_url = 'postgresql://postgres.uufxuxbilvlzllxgbewh:astrapodcast!@aws-0-us-east-1.pooler.supabase.com:6543/postgres'

def clean_html_code_blocks():
    """
    Clean all content fields in the articles table by removing ```html and ``` code block markers.
    
    This function:
    1. Connects to the database
    2. Retrieves all articles with their content
    3. Removes ```html and ``` markers from content
    4. Updates the cleaned content back to the database
    """
    
    if not db_access_url:
        print("Error: db_access_url is not set. Please set your database connection string.")
        return
    
    conn = None
    cursor = None
    
    try:
        # Connect to database
        conn = psycopg2.connect(dsn=db_access_url, client_encoding='utf8')
        cursor = conn.cursor()
        
        print("Connected to database successfully")
        
        # First, get all articles with their content
        cursor.execute("SELECT id, content FROM articles WHERE content IS NOT NULL")
        articles = cursor.fetchall()
        
        print(f"Found {len(articles)} articles to process")
        
        # Process each article
        updated_count = 0
        for article_id, content in articles:
            if not content:
                continue
                
            # Clean the content by removing ```html and ``` markers
            original_content = content
            
            # Remove ```html (case insensitive)
            cleaned_content = re.sub(r'```html\s*', '', content, flags=re.IGNORECASE)
            
            # Remove all occurrences of ```
            cleaned_content = cleaned_content.replace('```', '')
            
            # Also remove any remaining ``` at the very start or end of content
            cleaned_content = re.sub(r'^```\s*', '', cleaned_content.strip())
            cleaned_content = re.sub(r'\s*```$', '', cleaned_content.strip())
            
            # Only update if content actually changed
            if cleaned_content != original_content:
                cursor.execute(
                    "UPDATE articles SET content = %s WHERE id = %s",
                    (cleaned_content, article_id)
                )
                updated_count += 1
                print(f"Updated article {article_id}")
        
        # Commit all changes
        conn.commit()
        print(f"\nCleaning completed successfully!")
        print(f"Total articles processed: {len(articles)}")
        print(f"Articles updated: {updated_count}")
        print(f"Articles unchanged: {len(articles) - updated_count}")
        
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        if conn:
            conn.rollback()
        return
    except Exception as e:
        print(f"Unexpected error: {e}")
        if conn:
            conn.rollback()
        return
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        print("Database connection closed")

def preview_changes(limit=5):
    """
    Preview what changes would be made without actually updating the database.
    
    Args:
        limit: Number of examples to show
    """
    
    if not db_access_url:
        print("Error: db_access_url is not set. Please set your database connection string.")
        return
    
    conn = None
    cursor = None
    
    try:
        conn = psycopg2.connect(dsn=db_access_url, client_encoding='utf8')
        cursor = conn.cursor()
        
        # Get articles that contain code block markers
        cursor.execute("""
            SELECT id, content 
            FROM articles 
            WHERE content IS NOT NULL""")
        
        articles = cursor.fetchall()
        
        if not articles:
            print("No articles found with code block markers")
            return
        
        print(f"Preview of changes for {len(articles)} articles:\n")
        
        for article_id, content in articles:
            # Apply the same cleaning logic
            cleaned_content = re.sub(r'```html\s*', '', content, flags=re.IGNORECASE)
            cleaned_content = re.sub(r'\n```\s*\n', '\n', cleaned_content)
            cleaned_content = re.sub(r'^```\s*\n', '', cleaned_content, flags=re.MULTILINE)
            cleaned_content = re.sub(r'\n```\s*$', '', cleaned_content, flags=re.MULTILINE)
            cleaned_content = re.sub(r'^```\s*', '', cleaned_content.strip())
            cleaned_content = re.sub(r'\s*```$', '', cleaned_content.strip())
            
            if cleaned_content != content:
                print(f"Article ID: {article_id}")
                print("BEFORE (first 200 chars):")
                print(repr(content[:200]))
                print("AFTER (first 200 chars):")
                print(repr(cleaned_content[:200]))
                print("-" * 50)
        
    except psycopg2.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    print("Content Cleaning Utility")
    print("=" * 40)
    
    # Set your database connection string here
    # db_access_url = "postgresql://username:password@host:port/database"
    
    print("Options:")
    print("1. Preview changes (recommended first)")
    print("2. Clean all content")
    
    choice = input("Enter your choice (1 or 2): ").strip()
    
    if choice == "1":
        preview_changes()
    elif choice == "2":
        confirm = input("Are you sure you want to clean all content? This will modify your database. (yes/no): ")
        if confirm.lower() == 'yes':
            clean_html_code_blocks()
        else:
            print("Operation cancelled")
    else:
        print("Invalid choice")
