import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json
import os

from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
import redis

from config.database import get_db, SessionLocal
from models.competitor_prices import CompetitorPrice
from config.settings import settings
from models.agent_decisions import AgentDecision

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CompetitorMonitoringAgent:
    """
    Competitor Monitoring Agent that:
    1. Monitors competitor data in PostgreSQL
    2. Uses Sentence Transformers to embed product data
    3. Stores embeddings in Pinecone for similarity search
    4. Subscribes to Web Scraping Agent updates via Redis
    """
    
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            decode_responses=True
        )
        self.pinecone_api_key = os.getenv('PINECONE_API_KEY')
        self.pinecone_index_name = os.getenv('PINECONE_INDEX_NAME', 'competitor-data')
        
        # Initialize Pinecone
        if self.pinecone_api_key:
            self.pc = Pinecone(api_key=self.pinecone_api_key)
            self._ensure_pinecone_index()
        else:
            logger.warning("PINECONE_API_KEY not set. Vector storage will be disabled.")
            self.pc = None
            
        # Subscribe to Redis channel for web scraping updates
        self.pubsub = self.redis_client.pubsub()
        self.pubsub.subscribe('scraped_data')
        
    def _ensure_pinecone_index(self):
        """Ensure Pinecone index exists, create if it doesn't"""
        try:
            # Check if index exists
            existing_indexes = [index.name for index in self.pc.list_indexes()]
            
            if self.pinecone_index_name not in existing_indexes:
                logger.info(f"Creating Pinecone index: {self.pinecone_index_name}")
                self.pc.create_index(
                    name=self.pinecone_index_name,
                    dimension=384,  # all-MiniLM-L6-v2 dimension
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='aws',
                        region='us-east-1'
                    )
                )
                # Wait for index to be ready
                import time
                time.sleep(10)
            
            self.index = self.pc.Index(self.pinecone_index_name)
            logger.info(f"Pinecone index '{self.pinecone_index_name}' is ready")
            
        except Exception as e:
            logger.error(f"Error setting up Pinecone index: {e}")
            self.index = None
    
    def _create_product_embedding(self, product_data: Dict[str, Any]) -> List[float]:
        """Create embedding for product data"""
        # Combine relevant product information for embedding
        text_for_embedding = f"{product_data.get('product_name', '')} {product_data.get('category', '')} {product_data.get('competitor_name', '')}"
        
        # Generate embedding
        embedding = self.model.encode(text_for_embedding)
        return embedding.tolist()
    
    def _store_in_pinecone(self, product_data: Dict[str, Any], embedding: List[float]):
        """Store product data and embedding in Pinecone"""
        if not self.index:
            logger.warning("[CompetitorMonitoringAgent] Pinecone index not available, skipping vector storage")
            return
        try:
            vector_id = f"{product_data['competitor_name']}_{product_data['product_id']}_{product_data['scraped_at'].isoformat()}"
            metadata = {
                'product_id': product_data['product_id'],
                'product_name': product_data.get('product_name', ''),
                'category': product_data.get('category', ''),
                'competitor_name': product_data['competitor_name'],
                'competitor_price': float(product_data['competitor_price']),
                'scraped_at': product_data['scraped_at'].isoformat()
            }
            logger.info(f"[CompetitorMonitoringAgent] Upserting vector to Pinecone: id={vector_id}, metadata={metadata}")
            self.index.upsert(
                vectors=[(vector_id, embedding, metadata)]
            )
            logger.info(f"[CompetitorMonitoringAgent] Stored embedding for product {product_data['product_id']} in Pinecone")
        except Exception as e:
            logger.error(f"[CompetitorMonitoringAgent] Error storing in Pinecone: {e}")
    
    def process_new_competitor_data(self, product_data: Dict[str, Any]):
        """Process new competitor data from web scraping agent"""
        try:
            logger.info(f"[CompetitorMonitoringAgent] Processing new competitor data: {product_data}")
            # Create embedding
            embedding = self._create_product_embedding(product_data)
            logger.info(f"[CompetitorMonitoringAgent] Created embedding for product: {product_data.get('product_name', 'Unknown')}")
            # Store in Pinecone
            self._store_in_pinecone(product_data, embedding)
            # Store in PostgreSQL (if not already done by web scraping agent)
            self._store_in_postgresql(product_data)
            logger.info(f"[CompetitorMonitoringAgent] Successfully processed competitor data for {product_data.get('product_name', 'Unknown')}")
            # Log agent decision
            try:
                db = SessionLocal()
                decision = AgentDecision(
                    product_id=product_data.get("product_id"),
                    agent_name="CompetitorMonitoringAgent",
                    decision_type="monitoring",
                    input_data=json.dumps(product_data),
                    output_data=json.dumps({"embedding": embedding}),
                    confidence_score=None,
                    explanation="Processed competitor data, created embedding, and stored in DB/Pinecone.",
                    timestamp=datetime.now()
                )
                db.add(decision)
                try:
                    db.commit()
                except Exception as e:
                    db.rollback()
                    logger.error(f"[CompetitorMonitoringAgent] Error committing agent decision: {e}")
            except Exception as e:
                logger.error(f"[CompetitorMonitoringAgent] Error logging agent decision: {e}")
            finally:
                if 'db' in locals():
                    db.close()
        except Exception as e:
            logger.error(f"[CompetitorMonitoringAgent] Error processing competitor data: {e}")
    
    def _store_in_postgresql(self, product_data: Dict[str, Any]):
        """Store competitor data in PostgreSQL"""
        db = SessionLocal()
        try:
            existing = db.query(CompetitorPrice).filter(
                CompetitorPrice.product_id == product_data['product_id'],
                CompetitorPrice.competitor_name == product_data['competitor_name'],
                CompetitorPrice.scraped_at == product_data['scraped_at']
            ).first()
            if not existing:
                competitor_price = CompetitorPrice(
                    product_id=product_data['product_id'],
                    product_name=product_data.get('product_name'),
                    category=product_data.get('category'),
                    competitor_name=product_data['competitor_name'],
                    competitor_price=product_data['competitor_price'],
                    scraped_at=product_data['scraped_at']
                )
                db.add(competitor_price)
                db.commit()
                logger.info(f"[CompetitorMonitoringAgent] Stored competitor price in PostgreSQL: {product_data['product_name']}")
            else:
                logger.info(f"[CompetitorMonitoringAgent] Competitor price already exists in PostgreSQL for: {product_data['product_name']}")
        except Exception as e:
            db.rollback()
            logger.error(f"[CompetitorMonitoringAgent] Error storing in PostgreSQL: {e}")
        finally:
            db.close()
    
    def get_similar_products(self, product_name: str, category: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Find similar products using vector similarity search"""
        if not self.index:
            logger.warning("[CompetitorMonitoringAgent] Pinecone index not available, cannot perform similarity search")
            return []
        try:
            query_text = f"{product_name} {category}"
            logger.info(f"[CompetitorMonitoringAgent] Creating embedding for similarity search: '{query_text}'")
            query_embedding = self.model.encode(query_text).tolist()
            logger.info(f"[CompetitorMonitoringAgent] Querying Pinecone for similar products")
            results = self.index.query(
                vector=query_embedding,
                top_k=limit,
                include_metadata=True
            )
            similar_products = []
            for match in results.matches:
                similar_products.append({
                    'product_id': match.metadata['product_id'],
                    'product_name': match.metadata['product_name'],
                    'category': match.metadata['category'],
                    'competitor_name': match.metadata['competitor_name'],
                    'competitor_price': match.metadata['competitor_price'],
                    'scraped_at': match.metadata['scraped_at'],
                    'similarity_score': match.score
                })
            logger.info(f"[CompetitorMonitoringAgent] Found {len(similar_products)} similar products for '{product_name}'")
            return similar_products
        except Exception as e:
            logger.error(f"[CompetitorMonitoringAgent] Error finding similar products: {e}")
            return []
    
    def get_competitor_price_history(self, product_id: str, competitor_name: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get price history for a specific product from a competitor"""
        db = SessionLocal()
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            prices = db.query(CompetitorPrice).filter(
                CompetitorPrice.product_id == product_id,
                CompetitorPrice.competitor_name == competitor_name,
                CompetitorPrice.scraped_at >= cutoff_date
            ).order_by(CompetitorPrice.scraped_at.desc()).all()
            
            price_history = []
            for price in prices:
                price_history.append({
                    'competitor_price': float(price.competitor_price),
                    'scraped_at': price.scraped_at.isoformat()
                })
            
            logger.info(f"Retrieved {len(price_history)} price records for product {product_id}")
            return price_history
            
        except Exception as e:
            logger.error(f"Error retrieving price history: {e}")
            return []
        finally:
            db.close()
    
    def listen_for_updates(self):
        """Listen for updates from Redis Pub/Sub"""
        logger.info("[CompetitorMonitoringAgent] Starting to listen for web scraping updates...")
        try:
            for message in self.pubsub.listen():
                if message['type'] == 'message':
                    try:
                        logger.info(f"[CompetitorMonitoringAgent] Received message from Redis: {message['data']}")
                        data = json.loads(message['data'])
                        self.process_new_competitor_data(data)
                    except json.JSONDecodeError as e:
                        logger.error(f"[CompetitorMonitoringAgent] Error parsing JSON message: {e}")
                    except Exception as e:
                        logger.error(f"[CompetitorMonitoringAgent] Error processing message: {e}")
        except KeyboardInterrupt:
            logger.info("[CompetitorMonitoringAgent] Stopping competitor monitoring agent...")
        finally:
            self.pubsub.unsubscribe()
            self.pubsub.close()
    
    def run_monitoring_cycle(self):
        """Run a single monitoring cycle"""
        logger.info("Running competitor monitoring cycle...")
        
        # Process any pending messages from Redis
        messages = self.redis_client.lrange('pending_competitor_data', 0, -1)
        for message in messages:
            try:
                data = json.loads(message)
                self.process_new_competitor_data(data)
                # Remove processed message
                self.redis_client.lrem('pending_competitor_data', 1, message)
            except Exception as e:
                logger.error(f"Error processing pending message: {e}")
        
        logger.info("Competitor monitoring cycle completed")

# Global instance
competitor_monitoring_agent = CompetitorMonitoringAgent()

def run_competitor_monitoring_agent(input_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Main function to run the competitor monitoring agent"""
    try:
        if input_data:
            # Process specific input data
            competitor_monitoring_agent.process_new_competitor_data(input_data)
            return {
                "status": "success",
                "message": "Competitor data processed successfully",
                "data": input_data
            }
        else:
            # Run monitoring cycle
            competitor_monitoring_agent.run_monitoring_cycle()
            return {
                "status": "success",
                "message": "Competitor monitoring cycle completed"
            }
    except Exception as e:
        logger.error(f"Error in competitor monitoring agent: {e}")
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }

if __name__ == "__main__":
    # Example usage
    result = run_competitor_monitoring_agent()
    print(result)
