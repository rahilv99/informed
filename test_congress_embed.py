#!/usr/bin/env python3
"""
Test script to verify congress scraper integration with embed.py using realistic article titles
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the necessary paths
sys.path.append('src/scraper-lambda')
sys.path.append('src/clusterer-lambda')

def test_congress_scraper_with_real_titles():
    """
    Test the congress scraper with realistic government article titles
    that would come from the clustering system
    """
    try:
        from src.scraper_lambda.logic.congress_scraper import Congress
        
        print("=" * 80)
        print("TESTING CONGRESS SCRAPER WITH REALISTIC ARTICLE TITLES")
        print("=" * 80)
        
        # Realistic government article titles that might come from clustering
        realistic_titles = [
            "Department of Energy Announces $3.2 Billion Investment in Clean Energy Infrastructure",
            "EPA Proposes New Regulations for Carbon Emissions from Power Plants",
            "Treasury Department Issues Guidance on Tax Credits for Renewable Energy Projects",
            "USDA Releases Report on Climate Change Impact on Agricultural Production",
            "Department of Transportation Announces Electric Vehicle Charging Network Expansion"
        ]
        
        print(f"Testing with {len(realistic_titles)} realistic government article titles:")
        for i, title in enumerate(realistic_titles, 1):
            print(f"  {i}. {title}")
        
        print("\n" + "=" * 80)
        
        for i, title in enumerate(realistic_titles, 1):
            print(f"\n🔍 Testing Article {i}: '{title[:60]}...'")
            print("-" * 80)
            
            try:
                # Create Congress instance with the article title as topic
                congress = Congress([title])
                
                # Test get_bills method
                bills = congress.get_bills()
                
                if bills and len(bills) > 0:
                    print(f"✅ Found {len(bills)} relevant bills")
                    print("\nTop 3 most relevant bills:")
                    
                    for j, bill in enumerate(bills[:3]):
                        similarity = bill.get('similarity_score', 0)
                        bill_title = bill.get('title', 'No title')
                        bill_id = bill.get('bill_id', 'No ID')
                        text_length = len(bill.get('text', ''))
                        
                        print(f"\n  {j+1}. {bill_title[:100]}...")
                        print(f"     Bill ID: {bill_id}")
                        print(f"     Similarity Score: {similarity:.4f}")
                        print(f"     Text Length: {text_length} characters")
                        
                else:
                    print(f"❌ No bills found for this article title")
                    
            except Exception as e:
                print(f"❌ Error testing article {i}: {e}")
                import traceback
                traceback.print_exc()
        
        print("\n" + "=" * 80)
        print("✅ CONGRESS SCRAPER TEST WITH REALISTIC TITLES COMPLETED")
        print("=" * 80)
        
    except ImportError as e:
        print(f"❌ Could not import congress scraper: {e}")
        print("Make sure you're running from the project root directory")
    except Exception as e:
        print(f"❌ Error in test: {e}")
        import traceback
        traceback.print_exc()


def test_embed_integration():
    """
    Test the embed.py integration with congress scraper
    """
    try:
        from src.clusterer_lambda.logic.embed import Clusterer
        import pandas as pd
        
        print("\n" + "=" * 80)
        print("TESTING EMBED.PY INTEGRATION WITH CONGRESS SCRAPER")
        print("=" * 80)
        
        # Create mock government articles that would come from the clustering system
        mock_gov_articles = [
            {
                'title': 'EPA Announces New Clean Air Standards for Industrial Facilities',
                'text': 'The Environmental Protection Agency today announced comprehensive new standards for air quality monitoring and emissions reduction across industrial facilities nationwide. The new regulations will require facilities to implement advanced monitoring systems and reduce particulate matter emissions by 40% over the next five years.',
                'url': 'https://www.epa.gov/news/epa-announces-new-clean-air-standards',
                'keyword': 'environmental regulation',
                'source': 'gov'
            },
            {
                'title': 'Department of Energy Launches $2B Clean Energy Innovation Program',
                'text': 'The U.S. Department of Energy unveiled a $2 billion initiative to accelerate clean energy innovation and deployment. The program will fund research into advanced battery technologies, renewable energy systems, and grid modernization projects across 15 states.',
                'url': 'https://www.energy.gov/news/doe-launches-clean-energy-program',
                'keyword': 'clean energy',
                'source': 'gov'
            },
            {
                'title': 'Treasury Issues Final Rules on Electric Vehicle Tax Credits',
                'text': 'The Department of Treasury released final guidance on electric vehicle tax credit eligibility, clarifying requirements for battery component sourcing and final assembly. The rules will take effect January 1, 2025, and are expected to impact consumer EV purchasing decisions.',
                'url': 'https://www.treasury.gov/news/ev-tax-credit-rules',
                'keyword': 'electric vehicles',
                'source': 'gov'
            }
        ]
        
        # Create mock news articles
        mock_news_articles = [
            {
                'title': 'Major Automakers Announce Electric Vehicle Production Targets',
                'url': 'https://example.com/news1',
                'source': 'Reuters',
                'keyword': 'electric vehicles'
            },
            {
                'title': 'Renewable Energy Sector Sees Record Investment in Q3',
                'url': 'https://example.com/news2', 
                'source': 'Bloomberg',
                'keyword': 'clean energy'
            }
        ]
        
        # Convert to DataFrames
        gov_df = pd.DataFrame(mock_gov_articles)
        news_df = pd.DataFrame(mock_news_articles)
        
        print(f"Created mock data:")
        print(f"  - {len(gov_df)} government articles")
        print(f"  - {len(news_df)} news articles")
        
        # Create clusterer instance
        clusterer = Clusterer()
        
        # Test the find_bills_for_gov_articles method
        print(f"\n🔍 Testing find_bills_for_gov_articles with mock clusters...")
        
        # Create mock filtered clusters
        mock_clusters = [{
            'documents': [
                {
                    'source': 'gov',
                    'type': 'primary',
                    'title': article['title']
                } for article in mock_gov_articles
            ]
        }]
        
        bills_data = clusterer.find_bills_for_gov_articles(mock_clusters)
        
        if bills_data:
            print(f"✅ Successfully found bills for {len(bills_data)} government articles")
            for title, bills in bills_data.items():
                print(f"\n📄 Article: '{title[:60]}...'")
                if bills:
                    print(f"   Found {len(bills)} related bills")
                    for i, bill in enumerate(bills[:2]):  # Show top 2
                        print(f"   {i+1}. {bill.get('title', 'No title')[:80]}...")
                        print(f"      Similarity: {bill.get('similarity_score', 0):.4f}")
                else:
                    print(f"   No related bills found")
        else:
            print("❌ No bills data returned")
        
        print("\n" + "=" * 80)
        print("✅ EMBED.PY INTEGRATION TEST COMPLETED")
        print("=" * 80)
        
    except ImportError as e:
        print(f"❌ Could not import required modules: {e}")
    except Exception as e:
        print(f"❌ Error in embed integration test: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("🚀 STARTING COMPREHENSIVE CONGRESS SCRAPER TESTS")
    print("=" * 80)
    
    # Check if environment variables are loaded
    congress_api_key = os.getenv('CONGRESS_API_KEY')
    if congress_api_key:
        print(f"✅ Congress API Key loaded: {congress_api_key[:10]}...")
    else:
        print("❌ Congress API Key not found in environment")
    
    print("=" * 80)
    
    # Run tests
    test_congress_scraper_with_real_titles()
    test_embed_integration()
    
    print("\n🎉 ALL TESTS COMPLETED!")
