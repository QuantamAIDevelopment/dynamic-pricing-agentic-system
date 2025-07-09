from .scrape_tool import scrape_products, ScrapeProductInput
from .search_tool import search_product_listing_page, generate_product_id_from_url, clean_domain, is_valid_amazon_url
from .database_utils import check_db_connection, recreate_tables
from .pricing_tools import (
    calculate_price_elasticity,
    analyze_competitor_pricing,
    calculate_optimal_price,
    get_pricing_recommendations
)
from .demand_tools import (
    calculate_sales_velocity,
    calculate_demand_score,
    forecast_demand,
    analyze_demand_signals
)
from .inventory_tools import (
    calculate_reorder_point,
    analyze_inventory_health,
    forecast_inventory_needs,
    optimize_inventory_levels
)

__all__ = [
    # Existing tools
    'scrape_products',
    'ScrapeProductInput',
    'search_product_listing_page',
    'generate_product_id_from_url',
    'clean_domain',
    'is_valid_amazon_url',
    'check_db_connection',
    'recreate_tables',
    
    # Pricing tools
    'calculate_price_elasticity',
    'analyze_competitor_pricing',
    'calculate_optimal_price',
    'get_pricing_recommendations',
    
    # Demand tools
    'calculate_sales_velocity',
    'calculate_demand_score',
    'forecast_demand',
    'analyze_demand_signals',
    
    # Inventory tools
    'calculate_reorder_point',
    'analyze_inventory_health',
    'forecast_inventory_needs',
    'optimize_inventory_levels'
]
