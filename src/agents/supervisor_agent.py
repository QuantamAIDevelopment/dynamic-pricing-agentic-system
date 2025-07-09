import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time

from crewai import Agent, Task, Crew, Process
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage
import redis

from src.agents.web_scraping_agent import run_web_scraping_agent
from src.agents.competitor_monitoring_agent import run_competitor_monitoring_agent, competitor_monitoring_agent
from src.config.llm_config import llm
from src.config.database import SessionLocal, save_agent_decision, get_db
from src.models.competitor_prices import CompetitorPrice
from src.models.agent_decisions import AgentDecision

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupervisorAgent:
    """
    Supervisor Agent that:
    1. Orchestrates the pricing cycle and coordinates sub-agents
    2. Uses CrewAI for multi-agent coordination
    3. Retains context with LangChain memory
    4. Manages the overall workflow and decision-making
    """
    
    def __init__(self):
        # Initialize memory for context retention
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Initialize Redis client
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            decode_responses=True
        )
        
        # Initialize CrewAI agents
        self._initialize_agents()
        
        # Pricing cycle state
        self.current_cycle = 0
        self.last_cycle_time = None
        self.cycle_interval = int(os.getenv('PRICING_CYCLE_INTERVAL_MINUTES', 30))
        
    def _initialize_agents(self):
        """Initialize CrewAI agents for the pricing system"""
        
        # Supervisor Agent (this agent)
        self.supervisor_agent = Agent(
            role="Dynamic Pricing Supervisor",
            goal="Orchestrate the pricing cycle and coordinate all sub-agents to optimize product pricing based on market data",
            backstory="""You are an expert pricing strategist with years of experience in dynamic pricing systems. 
            You coordinate multiple specialized agents to gather market intelligence, analyze competitor data, 
            and make optimal pricing decisions. You ensure all agents work together efficiently and maintain 
            context across pricing cycles.""",
            verbose=True,
            allow_delegation=True,
            memory=self.memory,
            llm=llm
        )
        
        # Web Scraping Agent
        self.web_scraping_agent = Agent(
            role="Web Scraping Specialist",
            goal="Scrape competitor product data including prices, descriptions, and availability from e-commerce platforms",
            backstory="""You are a web scraping expert who can extract product information from various e-commerce websites. 
            You use advanced scraping techniques to gather accurate pricing data while respecting website policies. 
            You provide clean, structured data for analysis.""",
            verbose=True,
            allow_delegation=False,
            llm=llm
        )
        
        # Competitor Monitoring Agent
        self.competitor_monitoring_agent = Agent(
            role="Competitor Intelligence Analyst",
            goal="Monitor and analyze competitor pricing data, create embeddings, and store in vector database for similarity search",
            backstory="""You are a competitive intelligence specialist who monitors competitor pricing strategies. 
            You use advanced NLP techniques to create embeddings of product data and store them in vector databases 
            for similarity search and trend analysis. You provide insights on competitor pricing patterns.""",
            verbose=True,
            allow_delegation=False,
            llm=llm
        )
        
        # Pricing Decision Agent
        self.pricing_decision_agent = Agent(
            role="Pricing Strategy Expert",
            goal="Analyze competitor data and demand scores to set optimal prices using LLM logic",
            backstory="""You are a pricing strategy expert with deep knowledge of market dynamics and pricing psychology. 
            You analyze competitor data, demand trends, and market conditions to make optimal pricing decisions. 
            You use advanced algorithms and LLM reasoning to determine the best price points.""",
            verbose=True,
            allow_delegation=False,
            llm=llm
        )
        
        # Demand Analysis Agent
        self.demand_analysis_agent = Agent(
            role="Demand Analytics Specialist",
            goal="Analyze sales data to compute demand scores and identify demand patterns",
            backstory="""You are a demand analytics expert who analyzes sales data to understand customer behavior 
            and demand patterns. You compute demand scores and identify trends that can inform pricing decisions. 
            You use statistical models and time-series analysis to predict future demand.""",
            verbose=True,
            allow_delegation=False,
            llm=llm
        )
        
        # Inventory Tracking Agent
        self.inventory_tracking_agent = Agent(
            role="Inventory Management Specialist",
            goal="Monitor inventory levels and provide real-time inventory data for pricing decisions",
            backstory="""You are an inventory management expert who tracks product inventory levels in real-time. 
            You monitor stock levels, reorder points, and inventory turnover rates. You provide critical inventory 
            data that influences pricing decisions, especially for products with limited stock.""",
            verbose=True,
            allow_delegation=False,
            llm=llm
        )
    
    def _create_web_scraping_task(self, domain: str, category: str, product_name: str = None) -> Task:
        """Create a web scraping task"""
        return Task(
            description=f"""Scrape competitor product data from {domain} in the {category} category.
            Focus on finding the most relevant product that matches '{product_name}' if provided.
            Extract pricing information, product descriptions, and availability data.
            Ensure the data is clean and structured for analysis.""",
            agent=self.web_scraping_agent,
            expected_output="""A structured dataset containing:
            - Product name and description
            - Current price
            - Availability status
            - Competitor name
            - Timestamp of scraping
            - Any additional relevant product information""",
            context=[
                {"domain": domain, "category": category, "product_name": product_name}
            ]
        )
    
    def _create_competitor_monitoring_task(self, scraped_data: Dict[str, Any]) -> Task:
        """Create a competitor monitoring task"""
        return Task(
            description=f"""Process the scraped competitor data and perform analysis:
            1. Create embeddings for the product data using Sentence Transformers
            2. Store the embeddings in Pinecone vector database
            3. Store the raw data in PostgreSQL
            4. Analyze the data for pricing insights
            5. Find similar products using vector similarity search
            
            Scraped data: {json.dumps(scraped_data, indent=2)}""",
            agent=self.competitor_monitoring_agent,
            expected_output="""Analysis results including:
            - Similar products found
            - Price history analysis
            - Competitor pricing insights
            - Vector embeddings stored successfully
            - Database records created""",
            context=[
                {"scraped_data": scraped_data}
            ]
        )
    
    def _create_pricing_decision_task(self, competitor_data: Dict[str, Any], demand_data: Dict[str, Any], inventory_data: Dict[str, Any]) -> Task:
        """Create a pricing decision task"""
        return Task(
            description=f"""Analyze all available data to make optimal pricing decisions:
            
            Competitor Data: {json.dumps(competitor_data, indent=2)}
            Demand Data: {json.dumps(demand_data, indent=2)}
            Inventory Data: {json.dumps(inventory_data, indent=2)}
            
            Consider:
            1. Competitor pricing strategies
            2. Current demand levels
            3. Inventory constraints
            4. Market conditions
            5. Profit margins
            6. Customer price sensitivity
            
            Provide detailed reasoning for your pricing recommendations.""",
            agent=self.pricing_decision_agent,
            expected_output="""Pricing recommendations including:
            - Recommended price points
            - Reasoning for each recommendation
            - Risk assessment
            - Expected impact on sales and profit
            - Implementation timeline""",
            context=[
                {
                    "competitor_data": competitor_data,
                    "demand_data": demand_data,
                    "inventory_data": inventory_data
                }
            ]
        )
    
    def _create_demand_analysis_task(self, product_id: str) -> Task:
        """Create a demand analysis task"""
        return Task(
            description=f"""Analyze demand patterns for product {product_id}:
            1. Retrieve historical sales data
            2. Calculate demand scores
            3. Identify demand trends
            4. Analyze seasonal patterns
            5. Predict future demand
            
            Use statistical models and time-series analysis to provide accurate demand insights.""",
            agent=self.demand_analysis_agent,
            expected_output="""Demand analysis results including:
            - Current demand score
            - Demand trend analysis
            - Seasonal patterns identified
            - Demand forecast
            - Confidence intervals""",
            context=[
                {"product_id": product_id}
            ]
        )
    
    def _create_inventory_tracking_task(self, product_id: str) -> Task:
        """Create an inventory tracking task"""
        return Task(
            description=f"""Monitor inventory levels for product {product_id}:
            1. Check current stock levels
            2. Monitor reorder points
            3. Track inventory turnover
            4. Identify stockout risks
            5. Provide inventory recommendations
            
            Ensure real-time accuracy of inventory data.""",
            agent=self.inventory_tracking_agent,
            expected_output="""Inventory status including:
            - Current stock level
            - Reorder point status
            - Inventory turnover rate
            - Stockout risk assessment
            - Inventory recommendations""",
            context=[
                {"product_id": product_id}
            ]
        )
    
    def run_pricing_cycle(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run a complete pricing cycle for multiple products"""
        logger.info(f"[SupervisorAgent] Starting pricing cycle {self.current_cycle + 1} for {len(products)} products")
        cycle_results = {
            "cycle_number": self.current_cycle + 1,
            "start_time": datetime.now().isoformat(),
            "products": [],
            "overall_status": "success"
        }
        try:
            for product in products:
                logger.info(f"[SupervisorAgent] Processing product: {product}")
                product_result = self._process_single_product(product)
                logger.info(f"[SupervisorAgent] Product result: {product_result}")
                cycle_results["products"].append(product_result)
                if product_result["status"] == "error":
                    cycle_results["overall_status"] = "partial_failure"
            self.current_cycle += 1
            self.last_cycle_time = datetime.now()
            self.memory.save_context(
                {"input": f"Pricing cycle {cycle_results['cycle_number']} completed"},
                {"output": json.dumps(cycle_results, indent=2)}
            )
            logger.info(f"[SupervisorAgent] Pricing cycle {cycle_results['cycle_number']} completed. Results saved to memory.")
            self.redis_client.publish('pricing_cycle_completed', json.dumps(cycle_results, default=str))
            logger.info(f"[SupervisorAgent] Published pricing cycle completion to Redis.")
        except Exception as e:
            logger.error(f"[SupervisorAgent] Error in pricing cycle: {e}")
            cycle_results["overall_status"] = "error"
            cycle_results["error"] = str(e)
        cycle_results["end_time"] = datetime.now().isoformat()
        logger.info(f"[SupervisorAgent] Pricing cycle {cycle_results['cycle_number']} ended at {cycle_results['end_time']}")
        return cycle_results
    
    def _process_single_product(self, product: Dict[str, Any]) -> Dict[str, Any]:
        product_id = product.get("product_id")
        domain = product.get("domain", "amazon.com")
        category = product.get("category", "general")
        product_name = product.get("product_name")
        logger.info(f"[SupervisorAgent] --- Start processing product {product_id}: {product_name} ---")
        try:
            logger.info(f"[SupervisorAgent] Step 1: Web Scraping Agent")
            scraping_result = run_web_scraping_agent({
                "domain": domain,
                "category": category,
                "product_name": product_name
            })
            logger.info(f"[SupervisorAgent] Web Scraping Agent result: {scraping_result}")
            if scraping_result["status"] != "success":
                return {
                    "product_id": product_id,
                    "status": "error",
                    "error": f"Web scraping failed: {scraping_result['message']}"
                }
            scraped_data = scraping_result["data"]
            logger.info(f"[SupervisorAgent] Step 2: Competitor Monitoring Agent")
            monitoring_result = run_competitor_monitoring_agent(scraped_data)
            logger.info(f"[SupervisorAgent] Competitor Monitoring Agent result: {monitoring_result}")
            if monitoring_result["status"] != "success":
                return {
                    "product_id": product_id,
                    "status": "error",
                    "error": f"Competitor monitoring failed: {monitoring_result['message']}"
                }
            similar_products = competitor_monitoring_agent.get_similar_products(
                product_name or "", 
                category, 
                limit=5
            )
            logger.info(f"[SupervisorAgent] Step 3: Similar products found: {similar_products}")
            tasks = [
                self._create_web_scraping_task(domain, category, product_name),
                self._create_competitor_monitoring_task(scraped_data),
                self._create_demand_analysis_task(product_id),
                self._create_inventory_tracking_task(product_id),
                self._create_pricing_decision_task(
                    {"scraped_data": scraped_data, "similar_products": similar_products},
                    {"demand_score": 0.75},
                    {"current_stock": 100}
                )
            ]
            logger.info(f"[SupervisorAgent] Step 4: Running CrewAI workflow with {len(tasks)} tasks.")
            crew = Crew(
                agents=[
                    self.supervisor_agent,
                    self.web_scraping_agent,
                    self.competitor_monitoring_agent,
                    self.pricing_decision_agent,
                    self.demand_analysis_agent,
                    self.inventory_tracking_agent
                ],
                tasks=tasks,
                process=Process.sequential,
                verbose=True
            )
            result = crew.kickoff()
            logger.info(f"[SupervisorAgent] CrewAI workflow result: {result}")
            logger.info(f"[SupervisorAgent] --- End processing product {product_id}: {product_name} ---")
            return {
                "product_id": product_id,
                "status": "success",
                "scraped_data": scraped_data,
                "similar_products": similar_products,
                "crew_result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"[SupervisorAgent] Error processing product {product_id}: {e}")
            return {
                "product_id": product_id,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_pricing_history(self, product_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get pricing history for a product"""
        db = SessionLocal()
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            prices = db.query(CompetitorPrice).filter(
                CompetitorPrice.product_id == product_id,
                CompetitorPrice.scraped_at >= cutoff_date
            ).order_by(CompetitorPrice.scraped_at.desc()).all()
            
            history = []
            for price in prices:
                history.append({
                    'competitor_name': price.competitor_name,
                    'competitor_price': float(price.competitor_price),
                    'scraped_at': price.scraped_at.isoformat()
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Error retrieving pricing history: {e}")
            return []
        finally:
            db.close()
    
    def should_run_cycle(self) -> bool:
        """Determine if a pricing cycle should run based on timing"""
        if self.last_cycle_time is None:
            return True
        
        time_since_last_cycle = datetime.now() - self.last_cycle_time
        return time_since_last_cycle.total_seconds() >= (self.cycle_interval * 60)
    
    def run_continuous_monitoring(self, products: List[Dict[str, Any]], max_cycles: int = None):
        """Run continuous monitoring with automatic pricing cycles"""
        logger.info(f"Starting continuous monitoring for {len(products)} products")
        
        cycle_count = 0
        try:
            while max_cycles is None or cycle_count < max_cycles:
                if self.should_run_cycle():
                    logger.info(f"Running pricing cycle {cycle_count + 1}")
                    result = self.run_pricing_cycle(products)
                    
                    # Log cycle results
                    logger.info(f"Cycle {cycle_count + 1} completed with status: {result['overall_status']}")
                    
                    cycle_count += 1
                    
                    # Wait before next cycle
                    time.sleep(self.cycle_interval * 60)
                else:
                    # Wait a bit before checking again
                    time.sleep(60)
        except KeyboardInterrupt:
            logger.info("Continuous monitoring stopped by user")
        except Exception as e:
            logger.error(f"Error in continuous monitoring: {e}")

# Global instance
supervisor_agent = SupervisorAgent()

def get_best_competitor_price(product_name: str) -> dict:
    """
    For a given product name, scrape both Amazon and Flipkart, compare prices, and return the best value.
    """
    from src.agents.web_scraping_agent import run_web_scraping_agent
    from src.agents.competitor_monitoring_agent import run_competitor_monitoring_agent
    competitors = [
        {"domain": "amazon.in", "category": "", "product_name": product_name},
        {"domain": "flipkart.com", "category": "", "product_name": product_name}
    ]
    results = []
    for comp in competitors:
        result = run_web_scraping_agent(comp)
        if result["status"] == "success" and result["data"]:
            results.append(result["data"])
    if not results:
        return {"status": "error", "message": "No prices found from competitors."}
    # Find the best (lowest) price
    def extract_price(item):
        try:
            return float(item.get("price") or item.get("competitor_price") or 1e12)
        except Exception:
            return 1e12
    best_product = min(results, key=extract_price)
    # Save best value to DB via competitor monitoring agent
    run_competitor_monitoring_agent(best_product)
    # Log agent decision
    try:
        decision_dict = dict(
            product_id=best_product.get("product_id"),
            agent_name="SupervisorAgent",
            decision_type="best_price_selection",
            input_data=json.dumps({"competitors": competitors}),
            output_data=json.dumps(best_product),
            confidence_score=None,
            explanation="Selected best price from all competitors.",
            timestamp=datetime.now()
        )
        with next(get_db()) as db:
            save_agent_decision(db, decision_dict)
    except Exception as e:
        logger.error(f"[SupervisorAgent] Error logging agent decision: {e}")
    return {"status": "success", "data": best_product}

def run_supervisor_agent(input_data: dict = None) -> dict:
    """Main function to run the supervisor agent"""
    try:
        if input_data and "product_name" in input_data:
            product_name = input_data["product_name"]
            result = get_best_competitor_price(product_name)
            if result["status"] == "success":
                return {
                    "status": "success",
                    "message": "Best competitor price found and saved.",
                    "data": result["data"]
                }
            else:
                return {"status": "error", "message": result["message"]}
        elif input_data and "products" in input_data:
            # Legacy: Run a single pricing cycle with provided data
            products = input_data.get("products", [])
            if not products:
                return {
                    "status": "error",
                    "message": "No products provided for pricing cycle"
                }
            result = supervisor_agent.run_pricing_cycle(products)
            return {
                "status": "success",
                "message": "Pricing cycle completed",
                "data": result
            }
        else:
            return {"status": "error", "message": "No product_name provided."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    # Example usage
    result = run_supervisor_agent()
    print(result) 