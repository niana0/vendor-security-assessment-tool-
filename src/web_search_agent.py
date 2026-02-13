"""
Web Search Agent - Searches for vendor security information from public sources
"""
from typing import Dict, List, Any, Optional
import re


class WebSearchAgent:
    """Search for vendor security information and convert to evidence format"""

    SECURITY_CONTROL_KEYWORDS = [
        'encryption', 'authentication', 'mfa', 'soc 2', 'iso 27001',
        'penetration test', 'vulnerability scan', 'compliance', 'certification',
        'audit', 'security policy', 'access control', 'data protection',
        'incident response', 'backup', 'disaster recovery', 'gdpr', 'hipaa'
    ]

    INCIDENT_KEYWORDS = [
        'breach', 'hack', 'attack', 'vulnerability', 'exploit', 'data leak',
        'security incident', 'compromised', 'ransomware', 'malware'
    ]

    def __init__(self):
        self.search_results = {
            'controls': [],
            'incidents': [],
            'certifications': []
        }
        self.evidence_items = []

    def search_vendor_security(self, vendor_name: str) -> Dict[str, Any]:
        """
        Main search orchestrator - performs multiple searches for vendor security info

        Args:
            vendor_name: Name of the vendor to search for

        Returns:
            Dictionary with search results categorized by type
        """
        if not vendor_name or not vendor_name.strip():
            return self.search_results

        # Perform multiple targeted searches for better results
        all_controls = []
        all_incidents = []

        # Search 1: Official trust/security pages
        trust_query = f'"{vendor_name}" (trust center OR security OR compliance)'
        trust_results = self._perform_search(trust_query, max_results=5)
        all_controls.extend(self._extract_control_information(trust_results, vendor_name))

        # Search 2: Specific certifications
        cert_query = f'"{vendor_name}" (SOC 2 OR "ISO 27001" OR "ISO 27018")'
        cert_results = self._perform_search(cert_query, max_results=5)
        all_controls.extend(self._extract_control_information(cert_results, vendor_name))

        # Search 3: Security features and practices
        features_query = f'"{vendor_name}" (encryption OR "data protection" OR "security features")'
        features_results = self._perform_search(features_query, max_results=5)
        all_controls.extend(self._extract_control_information(features_results, vendor_name))

        # Search 4: Security incidents - recent breaches
        breach_query = f'"{vendor_name}" (breach OR hacked OR "data leak") 2020..2026'
        breach_results = self._perform_search(breach_query, max_results=8)
        all_incidents.extend(self._extract_incident_information(breach_results, vendor_name))

        # Search 5: Security vulnerabilities
        vuln_query = f'"{vendor_name}" (vulnerability OR CVE OR "security flaw")'
        vuln_results = self._perform_search(vuln_query, max_results=5)
        all_incidents.extend(self._extract_incident_information(vuln_results, vendor_name))

        # Remove duplicates based on URL
        self.search_results['controls'] = self._deduplicate_results(all_controls)
        self.search_results['incidents'] = self._deduplicate_results(all_incidents)

        return self.search_results

    def _perform_search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Execute web search using DuckDuckGo or configured search API

        Args:
            query: Search query string
            max_results: Maximum number of results to return

        Returns:
            List of search results with title, snippet, url
        """
        results = []

        try:
            # Try DuckDuckGo first (free, no API key needed)
            results = self._search_duckduckgo(query, max_results)

            if results:
                return results

            # Fallback to other search providers if configured
            results = self._search_google_custom(query, max_results)
            if results:
                return results

            results = self._search_bing(query, max_results)
            if results:
                return results

        except Exception as e:
            print(f"Search error: {e}")

        return results

    def _search_duckduckgo(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search using DuckDuckGo (free, no API key required)

        Args:
            query: Search query
            max_results: Maximum results to return

        Returns:
            List of search results
        """
        try:
            from ddgs import DDGS

            results = []
            print(f"🔍 Searching DuckDuckGo for: {query}")

            # Use DDGS directly (new API)
            search_results = DDGS().text(query, max_results=max_results)

            for result in search_results:
                results.append({
                    'title': result.get('title', ''),
                    'snippet': result.get('body', ''),
                    'url': result.get('href', '')
                })

            print(f"✅ DuckDuckGo returned {len(results)} results")
            return results

        except ImportError as e:
            error_msg = "DuckDuckGo search library not installed. Run: pip install ddgs"
            print(f"❌ {error_msg}")
            raise ImportError(error_msg)
        except Exception as e:
            print(f"❌ DuckDuckGo search error: {e}")
            raise Exception(f"DuckDuckGo search failed: {str(e)}")

    def _search_google_custom(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search using Google Custom Search API (requires API key)

        Set environment variables:
        - GOOGLE_API_KEY: Your Google API key
        - GOOGLE_SEARCH_ENGINE_ID: Your Custom Search Engine ID

        Args:
            query: Search query
            max_results: Maximum results to return

        Returns:
            List of search results
        """
        try:
            import os
            import requests

            api_key = os.getenv('GOOGLE_API_KEY')
            search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')

            if not api_key or not search_engine_id:
                return []

            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': api_key,
                'cx': search_engine_id,
                'q': query,
                'num': min(max_results, 10)  # Google allows max 10 per request
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            results = []
            for item in data.get('items', []):
                results.append({
                    'title': item.get('title', ''),
                    'snippet': item.get('snippet', ''),
                    'url': item.get('link', '')
                })

            return results

        except Exception as e:
            print(f"Google Custom Search error: {e}")
            return []

    def _search_bing(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search using Bing Search API (requires API key)

        Set environment variable:
        - BING_API_KEY: Your Bing Search API key

        Args:
            query: Search query
            max_results: Maximum results to return

        Returns:
            List of search results
        """
        try:
            import os
            import requests

            api_key = os.getenv('BING_API_KEY')

            if not api_key:
                return []

            url = "https://api.bing.microsoft.com/v7.0/search"
            headers = {'Ocp-Apim-Subscription-Key': api_key}
            params = {
                'q': query,
                'count': max_results,
                'textDecorations': False,
                'textFormat': 'HTML'
            }

            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            results = []
            for item in data.get('webPages', {}).get('value', []):
                results.append({
                    'title': item.get('name', ''),
                    'snippet': item.get('snippet', ''),
                    'url': item.get('url', '')
                })

            return results

        except Exception as e:
            print(f"Bing Search error: {e}")
            return []

    def _extract_control_information(self, results: List[Dict[str, Any]], vendor_name: str) -> List[Dict[str, Any]]:
        """
        Parse security controls from search results

        Args:
            results: Raw search results
            vendor_name: Vendor name for filtering

        Returns:
            List of control information dictionaries
        """
        controls = []
        vendor_name_lower = vendor_name.lower()

        # Extract key terms from vendor name (e.g., "Acme Corp" -> "acme")
        vendor_key_terms = [term.lower() for term in vendor_name.split()
                           if len(term) > 3 and term.lower() not in ['inc', 'corp', 'ltd', 'llc', 'the']]

        for result in results:
            title = result.get('title', '')
            snippet = result.get('snippet', '')
            url = result.get('url', '')
            combined_text = f"{title} {snippet}".lower()

            # MUST mention the vendor to be relevant
            vendor_mentioned = (vendor_name_lower in combined_text or
                              any(term in combined_text for term in vendor_key_terms))

            if not vendor_mentioned:
                continue

            # Check for security control keywords
            matched_keywords = [kw for kw in self.SECURITY_CONTROL_KEYWORDS
                              if kw in combined_text]

            if matched_keywords:
                # Determine confidence based on source and keyword matches
                confidence = self._assess_confidence(url, len(matched_keywords), combined_text)

                # Boost confidence if vendor domain is in URL
                if any(term in url.lower() for term in vendor_key_terms):
                    if confidence == 'LOW':
                        confidence = 'MEDIUM'
                    elif confidence == 'MEDIUM':
                        confidence = 'HIGH'

                controls.append({
                    'title': title,
                    'snippet': snippet,
                    'url': url,
                    'keywords': matched_keywords,
                    'confidence': confidence,
                    'vendor_name': vendor_name
                })

        return controls

    def _extract_incident_information(self, results: List[Dict[str, Any]], vendor_name: str) -> List[Dict[str, Any]]:
        """
        Parse security incidents from search results

        Args:
            results: Raw search results
            vendor_name: Vendor name for filtering

        Returns:
            List of incident information dictionaries
        """
        incidents = []
        vendor_name_lower = vendor_name.lower()

        # Extract key terms from vendor name
        vendor_key_terms = [term.lower() for term in vendor_name.split()
                           if len(term) > 3 and term.lower() not in ['inc', 'corp', 'ltd', 'llc', 'the']]

        # Patterns that indicate an ACTUAL incident (not just discussion of security)
        incident_indicators = [
            r'was (breached|hacked|compromised|attacked)',
            r'suffered (a )?(breach|hack|attack|data leak)',
            r'exposed.*credentials',
            r'leaked.*data',
            r'security incident.*affected',
            r'confirmed.*breach',
            r'disclosed.*vulnerability',
            r'announced.*breach',
            r'(breach|incident|hack).*\b20\d{2}\b'  # Incident with year
        ]

        # Filter out URLs that are NOT incidents
        exclude_patterns = [
            'trust', 'security-rating', 'vendor-risk', 'security-scorecard',
            'compliance', 'certification', 'trust-center', 'security-practices',
            '/careers/', '/jobs/', '/about-us/'
        ]

        for result in results:
            title = result.get('title', '')
            snippet = result.get('snippet', '')
            url = result.get('url', '').lower()
            combined_text = f"{title} {snippet}".lower()

            # MUST mention the vendor to be relevant
            vendor_mentioned = (vendor_name_lower in combined_text or
                              any(term in combined_text for term in vendor_key_terms))

            if not vendor_mentioned:
                continue

            # Skip if URL suggests it's not an incident report
            if any(pattern in url for pattern in exclude_patterns):
                continue

            # Skip generic security pages
            if 'trust hub' in combined_text or 'security rating' in combined_text:
                continue

            # Check for incident keywords
            matched_keywords = [kw for kw in self.INCIDENT_KEYWORDS
                              if kw in combined_text]

            if not matched_keywords:
                continue

            # Look for actual incident indicators (verb patterns)
            is_real_incident = any(re.search(pattern, combined_text) for pattern in incident_indicators)

            # Only include if it looks like a real incident
            if is_real_incident:
                # Extract year if present
                year_match = re.search(r'\b(20\d{2})\b', combined_text)
                year = year_match.group(1) if year_match else 'Unknown'

                incidents.append({
                    'title': title,
                    'snippet': snippet,
                    'url': url,
                    'keywords': matched_keywords,
                    'year': year,
                    'vendor_name': vendor_name
                })

        return incidents

    def _assess_confidence(self, url: str, keyword_count: int, text: str) -> str:
        """
        Assess confidence level based on source and content

        Args:
            url: Source URL
            keyword_count: Number of matched keywords
            text: Combined text content

        Returns:
            Confidence level: HIGH, MEDIUM, or LOW
        """
        # High confidence sources
        high_conf_domains = ['aicpa.org', 'iso.org', 'trustpage.com', 'securityscorecard.com']

        # Medium confidence sources
        medium_conf_domains = ['wikipedia.org', 'docs.', 'help.', 'support.']

        if any(domain in url.lower() for domain in high_conf_domains):
            return 'HIGH'

        # High keyword match count
        if keyword_count >= 3:
            return 'HIGH'

        if any(domain in url.lower() for domain in medium_conf_domains) or keyword_count == 2:
            return 'MEDIUM'

        return 'LOW'

    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate results based on URL

        Args:
            results: List of result dictionaries

        Returns:
            List with duplicates removed
        """
        seen_urls = set()
        unique_results = []

        for result in results:
            url = result.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)

        return unique_results

    def to_evidence_format(self) -> List[Dict[str, Any]]:
        """
        Convert search results to standard evidence format compatible with EvidenceExtractor

        Returns:
            List of evidence items in standard format
        """
        self.evidence_items = []

        # Convert controls to evidence
        for control in self.search_results.get('controls', []):
            self.evidence_items.append({
                "text": f"{control['title']}. {control['snippet']}",
                "keywords": control['keywords'],
                "source": f"Web Search: {control['url']}",
                "confidence": control['confidence'],
                "type": "web_search_control"
            })

        # Convert incidents to evidence
        for incident in self.search_results.get('incidents', []):
            self.evidence_items.append({
                "text": f"[{incident['year']}] {incident['title']}. {incident['snippet']}",
                "keywords": incident['keywords'],
                "source": f"Web Search: {incident['url']}",
                "confidence": 'HIGH',  # Incidents are high confidence if found
                "type": "web_search_incident"
            })

        return self.evidence_items

    def get_incidents_count(self) -> int:
        """Get count of security incidents found"""
        return len(self.search_results.get('incidents', []))

    def get_controls_count(self) -> int:
        """Get count of security controls found"""
        return len(self.search_results.get('controls', []))
