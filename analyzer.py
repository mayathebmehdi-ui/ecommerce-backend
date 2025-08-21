from openai import AsyncOpenAI
import json
import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class PolicyAnalyzer:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        self.client = AsyncOpenAI(api_key=api_key)

    async def analyze_policies(self, scraped_data: Dict) -> Dict[str, str]:
        """Analyze scraped content and extract structured policy information"""
        
        # Prepare content for analysis
        content_text = self._prepare_content(scraped_data)
        
        # Define the function schema for structured extraction
        function_schema = {
            "name": "extract_ecommerce_policies",
            "description": "Extract and structure shipping and return policy information from e-commerce website content",
            "parameters": {
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "The domain name of the website"
                    },
                    "shipping_policy": {
                        "type": "string",
                        "description": "Detailed summary of shipping policy including costs, timeframes, and conditions. Format: 'Standard shipping (X days) costs $X for orders under $X and is free for orders over $X. Express shipping costs $X...'"
                    },
                    "shipping_url": {
                        "type": "string",
                        "description": "Direct URL to the shipping policy page"
                    },
                    "return_policy": {
                        "type": "string", 
                        "description": "Detailed summary of return policy including timeframes, conditions, and process. Format: 'Returns accepted within X days for Y conditions. Process: Z. Refund/exchange policy: W.'"
                    },
                    "return_url": {
                        "type": "string",
                        "description": "Direct URL to the return policy page"
                    },
                    "self_help_returns": {
                        "type": "string",
                        "description": "Whether customers can initiate returns themselves online. Format: 'Yes - customers can initiate returns through [portal/account/etc]' or 'No - returns require contacting customer service'"
                    },
                    "self_help_url": {
                        "type": "string",
                        "description": "URL to self-service return portal if available"
                    },
                    "insurance": {
                        "type": "string",
                        "description": "Whether shipping insurance or protection is offered. Format: 'Yes - optional shipping protection costs $X (≈Y%) covering Z' or 'No - no shipping insurance offered'"
                    },
                    "insurance_url": {
                        "type": "string",
                        "description": "URL with insurance/protection information if available"
                    }
                },
                "required": ["domain", "shipping_policy", "shipping_url", "return_policy", "return_url", "self_help_returns", "self_help_url", "insurance", "insurance_url"]
            }
        }

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert e-commerce policy analyst. Your task is to extract and structure shipping and return policy information from website content.

CRITICAL INSTRUCTIONS - EXTRACT EVERYTHING:
1. ALWAYS extract information even if it's partial or incomplete
2. Look for ANY mention of shipping, delivery, returns, refunds, warranties, exchanges, or policies
3. Extract costs, timeframes, conditions, and processes with MAXIMUM detail
4. Be thorough - check ALL content provided, not just obvious sections
5. If exact information isn't found, infer from context or related information

SPECIFIC EXTRACTION TARGETS:
- RETURNS: "accepts returns", "within X days", "unworn", "tags attached", "original condition", "return shipping costs", "processing time", "5-7 days", "return authorization"
- SHIPPING: "FREE shipping", "Ground:", "2-Day:", "Next-Day:", "$X.XX", "business days", "1:00pm ET", delivery windows
- SELF-SERVICE: "returns portal", "Returns Center", "return authorization", URLs like "returns.domain.com"
- INSURANCE: "Route", "package protection", "insurance", "protected from loss"

NEVER return empty or "not available" unless content is truly empty. Combine related sentences into comprehensive summaries.
6. NEVER leave fields empty - always provide what you found

FORMATTING REQUIREMENTS (CONCISE BUT COMPLETE):
- shipping_policy: Summarize key shipping info in 1-2 sentences (main costs, timeframes, free shipping threshold). Example: "FREE shipping over $50, otherwise $6.99. Standard 3-6 days, Express 3-4 days ($3.99), Overnight available ($22.99)."
- return_policy: Summarize return policy in 1-2 sentences (timeframe, conditions, process). Example: "30-day returns for unworn items with tags. Process within 14 days, original postage non-refundable."
- self_help_returns: "Yes - [brief description]" or "No - [brief alternative process]"
- insurance: "Yes - [brief coverage/cost]" or "No - [brief explanation]"

EXTRACTION STRATEGY - SEARCH FOR EVERYTHING:
- Keywords: shipping, delivery, livraison, returns, retours, refunds, remboursement, policy, politique, warranty, guarantee, exchange, free shipping, expedited, standard, overnight
- Costs: $, €, £, free, gratuit, prices, tarifs, cost, charge, fee
- Timeframes: days, jours, business days, weeks, semaines, hours, same day, next day, 2-3 days, 5-7 days, 30 days, 60 days, 90 days
- Conditions: within X days, unopened, original packaging, tags attached, unused, defective, damaged, change of mind
- Processes: contact, email, phone, portal, self-service, form, return label, prepaid, customer service

GOODR.COM SPECIFIC - LOOK FOR:
- "30 Day Free Returns" details
- Warranty information (1-year warranty mentioned)
- Exchange policies
- Return shipping costs
- Condition requirements for returns

NEVER say "Information not available" - ALWAYS extract what you found, even if minimal.

Examples:
- shipping_policy: "FREE over $50, otherwise $5.95. Standard 3-7 days, Expedited 2-3 days ($14.95)."
- return_policy: "60-day returns for unopened items with tags. Contact customer service for authorization, refunds in 5-10 days."
- self_help_returns: "No - contact customer service for return authorization number"
- insurance: "No shipping insurance offered"
"""
                    },
                    {
                        "role": "user",
                        "content": f"Analyze this e-commerce website content and extract policy information:\n\nDomain: {scraped_data.get('domain', 'Unknown')}\n\nContent:\n{content_text}"
                    }
                ],
                tools=[{"type": "function", "function": function_schema}],
                tool_choice={"type": "function", "function": {"name": "extract_ecommerce_policies"}},
                temperature=0.1
            )

            # Extract the function call result
            tool_calls = response.choices[0].message.tool_calls
            if tool_calls and tool_calls[0].function.name == "extract_ecommerce_policies":
                try:
                    result = json.loads(tool_calls[0].function.arguments)
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")
                    print(f"Raw arguments: {tool_calls[0].function.arguments}")
                    # Try to fix common JSON issues
                    raw_args = tool_calls[0].function.arguments
                    # Fix unterminated strings and escape quotes
                    raw_args = raw_args.replace('\n', '\\n').replace('\r', '\\r')
                    raw_args = re.sub(r'(?<!\\)"(?=\s*[,}])', '\\"', raw_args)
                    try:
                        result = json.loads(raw_args)
                    except:
                        raise Exception("Failed to parse GPT-4 response")
                
                # Ensure domain is set
                if not result.get('domain'):
                    result['domain'] = scraped_data.get('domain', 'Unknown')
                
                # Ensure URLs are properly formatted
                result = self._validate_and_format_result(result, scraped_data)
                
                return result
            else:
                raise Exception("No valid function call response received")

        except Exception as e:
            print(f"Error in AI analysis: {e}")
            # Return fallback structure
            return self._create_fallback_result(scraped_data)

    def _prepare_content(self, scraped_data: Dict) -> str:
        """Prepare scraped content for AI analysis"""
        content_parts = []
        
        # Add content from all scraped pages
        for page_type, page_data in scraped_data.get('policy_pages', {}).items():
            content_parts.append(f"\n--- {page_type.upper()} PAGE ({page_data['url']}) ---")
            content_parts.append(page_data['content'][:3000])  # Limit content length
        
        return '\n'.join(content_parts)

    def _validate_and_format_result(self, result: Dict, scraped_data: Dict) -> Dict[str, str]:
        """Validate and format the analysis result"""
        base_url = scraped_data.get('main_url', '')
        policy_pages = scraped_data.get('policy_pages', {})
        
        # Ensure all URLs are absolute and valid
        for url_field in ['shipping_url', 'return_url', 'self_help_url', 'insurance_url']:
            if not result.get(url_field) or result[url_field] == "Information not available":
                # Try to find the best matching URL from scraped pages
                if url_field == 'shipping_url' and 'shipping' in policy_pages:
                    result[url_field] = policy_pages['shipping']['url']
                elif url_field == 'return_url' and 'returns' in policy_pages:
                    result[url_field] = policy_pages['returns']['url']
                elif url_field in ['self_help_url', 'insurance_url'] and 'help' in policy_pages:
                    result[url_field] = policy_pages['help']['url']
                else:
                    result[url_field] = base_url  # Fallback to main URL
        
        return result

    def _create_fallback_result(self, scraped_data: Dict) -> Dict[str, str]:
        """Create a fallback result when AI analysis fails"""
        base_url = scraped_data.get('main_url', '')
        domain = scraped_data.get('domain', 'Unknown')
        
        return {
            'domain': domain,
            'shipping_policy': 'Analysis failed - manual review required',
            'shipping_url': base_url,
            'return_policy': 'Analysis failed - manual review required', 
            'return_url': base_url,
            'self_help_returns': 'Analysis failed - manual review required',
            'self_help_url': base_url,
            'insurance': 'Analysis failed - manual review required',
            'insurance_url': base_url
        }
