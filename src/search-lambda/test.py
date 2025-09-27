#!/usr/bin/env python3
"""
Simple test script for the search lambda function.
Tests the /search endpoint with various queries and parameters.
"""

import requests
import json
from typing import Optional

# Configuration
BASE_URL = "http://localhost:8000"  # For local testing with uvicorn
TIMEOUT = 30

def test_search_endpoint(query: str, top_k: Optional[int] = None, min_cluster_size: Optional[int] = None):
    """Test the /search endpoint with given parameters."""
    
    # Construct the request URL and parameters
    url = f"{BASE_URL}/search"
    params = {"query": query}
    
    if top_k is not None:
        params["top_k"] = top_k
    if min_cluster_size is not None:
        params["min_cluster_size"] = min_cluster_size
    
    try:
        print(f"\n🔍 Testing search with query: '{query}'")
        print(f"   Parameters: {params}")
        
        response = requests.get(url, params=params, timeout=TIMEOUT)
        
        # Print response details
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Time: {response.elapsed.total_seconds():.2f}s")
        
        if response.status_code == 200:
            data = response.json()
            clusters = data.get("clusters", [])
            print(f"   ✅ Success! Found {len(clusters)} clusters")
            
            # Print cluster summary
            for i, cluster in enumerate(clusters):
                cluster_id = cluster.get("cluster_id", "unknown")
                items_count = len(cluster.get("items", []))
                print(f"      Cluster {cluster_id}: {items_count} items")
                
                # Print first item details if available
                if cluster.get("items"):
                    first_item = cluster["items"][0]
                    title = first_item.get("title", "No title")[:50]
                    print(f"        First item: {title}...")
            
            return data
        else:
            print(f"   ❌ Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"   Error text: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Connection Error: Cannot connect to {BASE_URL}")
        print("   Make sure the server is running with: python app/main.py")
        return None
    except requests.exceptions.Timeout:
        print(f"   ❌ Timeout: Request took longer than {TIMEOUT}s")
        return None
    except Exception as e:
        print(f"   ❌ Unexpected error: {str(e)}")
        return None

def test_health_check():
    """Test if the server is running by checking the root endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        if response.status_code in [200, 404]:  # 404 is OK, means server is running
            print("✅ Server is running")
            return True
    except:
        pass
    
    print("❌ Server is not running or not accessible")
    print(f"Please start the server with: python app/main.py")
    return False

if __name__ == "__main__":
    test_search_endpoint('government')
