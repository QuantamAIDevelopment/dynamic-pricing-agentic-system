#!/usr/bin/env python3
"""
Test script for the Dynamic Pricing Agent System
Demonstrates the integration of Web Scraping, Competitor Monitoring, and Supervisor agents
"""

import os
import sys
import json
import time
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agents import (
    run_web_scraping_agent,
    run_competitor_monitoring_agent,
    run_supervisor_agent,
    competitor_monitoring_agent
)

def test_web_scraping_agent():
    """Test the Web Scraping Agent"""
    print("=" * 60)
    print("Testing Web Scraping Agent")
    print("=" * 60)
    
    # Test data
    test_input = {
        "domain": "amazon.com",
        "category": "books",
        "product_name": "Python Programming"
    }
    
    print(f"Input: {json.dumps(test_input, indent=2)}")
    
    try:
        result = run_web_scraping_agent(test_input)
        print(f"Result: {json.dumps(result, indent=2, default=str)}")
        return result
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_competitor_monitoring_agent():
    """Test the Competitor Monitoring Agent"""
    print("\n" + "=" * 60)
    print("Testing Competitor Monitoring Agent")
    print("=" * 60)
    
    # Test data
    test_data = {
        "product_id": "test_001",
        "product_name": "Python Programming Book",
        "competitor_name": "amazon.com",
        "competitor_price": 29.99,
        "category": "books",
        "scraped_at": datetime.now()
    }
    
    print(f"Input: {json.dumps(test_data, indent=2, default=str)}")
    
    try:
        result = run_competitor_monitoring_agent(test_data)
        print(f"Result: {json.dumps(result, indent=2, default=str)}")
        return result
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_similar_products_search():
    """Test similar products search functionality"""
    print("\n" + "=" * 60)
    print("Testing Similar Products Search")
    print("=" * 60)
    
    try:
        similar_products = competitor_monitoring_agent.get_similar_products(
            "Python Programming", "books", limit=3
        )
        print(f"Similar products found: {len(similar_products)}")
        for i, product in enumerate(similar_products, 1):
            print(f"{i}. {product.get('product_name', 'Unknown')} - ${product.get('competitor_price', 0)}")
        return similar_products
    except Exception as e:
        print(f"Error: {e}")
        return []

def test_supervisor_agent():
    """Test the Supervisor Agent"""
    print("\n" + "=" * 60)
    print("Testing Supervisor Agent")
    print("=" * 60)
    
    # Test products
    test_products = [
        {
            "product_id": "prod_001",
            "product_name": "Python Programming Book",
            "domain": "amazon.com",
            "category": "books"
        },
        {
            "product_id": "prod_002",
            "product_name": "Data Science Handbook",
            "domain": "amazon.com",
            "category": "books"
        }
    ]
    
    print(f"Input products: {json.dumps(test_products, indent=2)}")
    
    try:
        result = run_supervisor_agent({"products": test_products})
        print(f"Result: {json.dumps(result, indent=2, default=str)}")
        return result
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_pricing_history():
    """Test pricing history retrieval"""
    print("\n" + "=" * 60)
    print("Testing Pricing History")
    print("=" * 60)
    
    try:
        from agents.supervisor_agent import supervisor_agent
        history = supervisor_agent.get_pricing_history("test_001", days=7)
        print(f"Pricing history for test_001: {len(history)} records")
        for record in history:
            print(f"- {record['competitor_name']}: ${record['competitor_price']} at {record['scraped_at']}")
        return history
    except Exception as e:
        print(f"Error: {e}")
        return []

def test_agent_integration():
    """Test the complete agent integration workflow"""
    print("\n" + "=" * 60)
    print("Testing Complete Agent Integration")
    print("=" * 60)
    
    print("Step 1: Web Scraping")
    scraping_result = test_web_scraping_agent()
    
    if scraping_result and scraping_result.get("status") == "success":
        print("\nStep 2: Competitor Monitoring")
        monitoring_result = test_competitor_monitoring_agent()
        
        if monitoring_result and monitoring_result.get("status") == "success":
            print("\nStep 3: Supervisor Agent")
            supervisor_result = test_supervisor_agent()
            
            if supervisor_result and supervisor_result.get("status") == "success":
                print("\n✅ All agents working together successfully!")
                return True
    
    print("\n❌ Agent integration test failed")
    return False

def main():
    """Main test function"""
    print("Dynamic Pricing Agent System - Agent Tests")
    print("=" * 60)
    print(f"Test started at: {datetime.now()}")
    print()
    
    # Check environment
    print("Environment Check:")
    print(f"- Redis Host: {os.getenv('REDIS_HOST', 'localhost')}")
    print(f"- Pinecone API Key: {'Set' if os.getenv('PINECONE_API_KEY') else 'Not set'}")
    print(f"- Database URL: {'Set' if os.getenv('DATABASE_URL') else 'Not set'}")
    print(f"- LLM API Key: {'Set' if os.getenv('OPENROUTER_API_KEY') or os.getenv('GROQ_API_KEY') else 'Not set'}")
    print()
    
    # Run individual tests
    test_web_scraping_agent()
    test_competitor_monitoring_agent()
    test_similar_products_search()
    test_supervisor_agent()
    test_pricing_history()
    
    # Run integration test
    test_agent_integration()
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)

if __name__ == "__main__":
    main() 