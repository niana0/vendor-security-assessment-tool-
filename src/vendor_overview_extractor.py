"""
Vendor Overview Extractor - Extracts vendor summary information from documents and web searches
"""
from typing import Dict, List, Any, Optional
import re


class VendorOverviewExtractor:
    """Extract vendor name, services, integrations, and data processing information"""

    SERVICE_KEYWORDS = [
        'platform', 'software', 'service', 'solution', 'application', 'tool',
        'system', 'product', 'api', 'infrastructure', 'cloud', 'saas',
        'analytics', 'monitoring', 'management', 'automation', 'integration'
    ]

    INTEGRATION_KEYWORDS = [
        'integrate', 'integration', 'connect', 'connector', 'plugin', 'extension',
        'api', 'webhook', 'sync', 'compatible', 'works with', 'supports'
    ]

    DATA_KEYWORDS = [
        'data', 'information', 'records', 'personal', 'pii', 'phi', 'sensitive',
        'customer', 'user', 'employee', 'financial', 'payment', 'credential',
        'store', 'process', 'collect', 'handle', 'access', 'transmit'
    ]

    def __init__(self):
        self.overview = {
            'vendor_name': '',
            'services': [],
            'integrations': [],
            'data_processed': [],
            'description': ''
        }

    def extract_overview(self,
                        vendor_name: str,
                        parsed_docs: List[Dict[str, Any]] = None,
                        web_results: Dict[str, Any] = None,
                        evidence: List[Dict[str, Any]] = None,
                        vendor_metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Extract vendor overview from all available sources

        Args:
            vendor_name: Name of the vendor
            parsed_docs: Parsed document contents
            web_results: Web search results
            evidence: Extracted evidence items
            vendor_metadata: User-provided vendor metadata

        Returns:
            Dictionary with vendor overview information
        """
        self.overview['vendor_name'] = vendor_name

        # Extract from user-provided metadata first
        if vendor_metadata:
            self._extract_from_user_metadata(vendor_metadata)

        # Extract from web search results first (usually more structured)
        if web_results:
            self._extract_from_web_results(web_results, vendor_name)

        # Extract from parsed documents
        if parsed_docs:
            self._extract_from_documents(parsed_docs)

        # Extract from evidence items
        if evidence:
            self._extract_from_evidence(evidence)

        # Clean and deduplicate
        self._clean_and_deduplicate()

        # Generate comprehensive description
        self._generate_description(vendor_name, web_results, parsed_docs, vendor_metadata)

        return self.overview

    def _extract_from_user_metadata(self, vendor_metadata: Dict[str, Any]):
        """Extract information from user-provided metadata"""

        # User's service description
        if vendor_metadata.get('services'):
            services_text = vendor_metadata['services']
            # Treat the entire user input as a service description
            if len(services_text) > 10:
                self.overview['services'].insert(0, services_text)

        # User's integration info
        if vendor_metadata.get('integrations'):
            integrations_text = vendor_metadata['integrations']
            # Split by commas or common separators
            integration_list = re.split(r'[,;]|\sand\s', integrations_text)
            for integration in integration_list:
                integration = integration.strip()
                if integration:
                    self.overview['integrations'].append(integration)

        # User's data storage info
        if vendor_metadata.get('data_stored'):
            data_text = vendor_metadata['data_stored']
            # Split by commas or common separators
            data_list = re.split(r'[,;]|\sand\s', data_text)
            for data_type in data_list:
                data_type = data_type.strip()
                if data_type:
                    self.overview['data_processed'].append(data_type)

    def _extract_from_web_results(self, web_results: Dict[str, Any], vendor_name: str):
        """Extract information from web search results"""

        # Analyze control results for services and integrations
        for control in web_results.get('controls', [])[:10]:  # Limit to top 10
            title = control.get('title', '')
            snippet = control.get('snippet', '')
            combined = f"{title}. {snippet}"

            # Extract services
            services = self._extract_services(combined, vendor_name)
            self.overview['services'].extend(services)

            # Extract integrations
            integrations = self._extract_integrations(combined, vendor_name)
            self.overview['integrations'].extend(integrations)

            # Extract data types
            data_types = self._extract_data_types(combined)
            self.overview['data_processed'].extend(data_types)

            # Collect potential description snippets (don't set yet, will synthesize later)
            if not hasattr(self, '_description_snippets'):
                self._description_snippets = []

            if len(snippet) > 50:
                # Look for descriptive sentences
                if any(kw in snippet.lower() for kw in ['platform', 'provides', 'offers', 'solution',
                                                         'software', 'service', 'helps', 'enables',
                                                         'designed', 'allows', 'tool for']):
                    self._description_snippets.append(snippet)

    def _extract_from_documents(self, parsed_docs: List[Dict[str, Any]]):
        """Extract information from parsed documents"""

        for doc in parsed_docs:
            content = doc.get('content', '')

            # Look for service descriptions
            services = self._extract_services(content, self.overview['vendor_name'])
            self.overview['services'].extend(services)

            # Look for integration mentions
            integrations = self._extract_integrations(content, self.overview['vendor_name'])
            self.overview['integrations'].extend(integrations)

            # Look for data processing descriptions
            data_types = self._extract_data_types(content)
            self.overview['data_processed'].extend(data_types)

    def _extract_from_evidence(self, evidence: List[Dict[str, Any]]):
        """Extract information from evidence items"""

        for item in evidence[:50]:  # Limit to avoid processing too much
            text = item.get('text', '')

            # Extract services
            services = self._extract_services(text, self.overview['vendor_name'])
            self.overview['services'].extend(services)

            # Extract integrations
            integrations = self._extract_integrations(text, self.overview['vendor_name'])
            self.overview['integrations'].extend(integrations)

            # Extract data types
            data_types = self._extract_data_types(text)
            self.overview['data_processed'].extend(data_types)

    def _extract_services(self, text: str, vendor_name: str) -> List[str]:
        """Extract service descriptions from text"""
        services = []

        # Pattern: "provides X", "offers X", "X platform", "X solution"
        patterns = [
            r'(?:provide|offer|deliver)s?\s+([a-zA-Z\s]+(?:platform|service|solution|software|tool))',
            r'([a-zA-Z\s]+(?:platform|service|solution|software|tool))\s+(?:for|that|which)',
            r'(?:is|as)\s+a\s+([a-zA-Z\s]+(?:platform|service|solution|provider))',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                service = match.strip()
                if len(service) > 10 and len(service) < 100:
                    services.append(service)

        # Look for bullet points or lists describing services
        lines = text.split('\n')
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(kw in line_lower for kw in ['service', 'feature', 'capability', 'offering']):
                # Check next few lines for items
                for j in range(i+1, min(i+6, len(lines))):
                    next_line = lines[j].strip()
                    if next_line and (next_line.startswith('-') or next_line.startswith('•') or
                                     next_line.startswith('*') or next_line[0].isdigit()):
                        # Clean bullet point
                        service = re.sub(r'^[\-\•\*\d\.\)]+\s*', '', next_line)
                        if len(service) > 5 and len(service) < 100:
                            services.append(service)

        return services

    def _extract_integrations(self, text: str, vendor_name: str) -> List[str]:
        """Extract integration/tool names from text"""
        integrations = []

        # Common tool/platform names patterns
        # Look for capitalized product names after integration keywords
        integration_context_pattern = r'(?:integrat|connect|work|compatible|sync)(?:e|es|ion|s)?\s+with\s+([A-Z][a-zA-Z0-9\s\-]+(?:,\s*(?:and\s+)?[A-Z][a-zA-Z0-9\s\-]+)*)'

        matches = re.findall(integration_context_pattern, text)
        for match in matches:
            # Split on commas and 'and'
            tools = re.split(r',|\sand\s', match)
            for tool in tools:
                tool = tool.strip()
                if len(tool) > 2 and len(tool) < 50:
                    # Filter out common non-tool words
                    if not any(word in tool.lower() for word in ['the', 'our', 'your', 'their', 'this', 'that']):
                        integrations.append(tool)

        # Look for API mentions
        api_pattern = r'([A-Z][a-zA-Z0-9\s]+)\s+API'
        api_matches = re.findall(api_pattern, text)
        for match in api_matches:
            if len(match) > 2 and len(match) < 30:
                integrations.append(f"{match} API")

        return integrations

    def _extract_data_types(self, text: str) -> List[str]:
        """Extract types of data processed/stored"""
        data_types = []

        # Enhanced patterns to catch more data type mentions
        patterns = [
            # Action verbs + data types
            r'(?:store|process|collect|handle|manage|access|transmit|retain|maintain|use|hold|secure|encrypt|protect)(?:s|es|ing)?\s+([a-zA-Z\s]+(?:data|information|records|details))',

            # Data types + passive voice
            r'([a-zA-Z\s]+(?:data|information|records|details))\s+(?:is|are|will be|may be|can be)\s+(?:stored|processed|collected|transmitted|accessed|retained|used)',

            # Lists and examples
            r'(?:including|such as|like|e\.?g\.?)\s+([a-zA-Z\s,]+(?:data|information|records|details))',

            # Types of data
            r'(?:types? of|kinds? of|categories of)\s+(?:data|information)\s+(?:including|such as)?\s*:?\s*([a-zA-Z\s,]+)',

            # Contains/includes patterns
            r'(?:contain|include)(?:s|ing)?\s+([a-zA-Z\s]+(?:data|information|records|details))',

            # Related to pattern
            r'(?:related to|pertaining to|concerning|regarding)\s+([a-zA-Z\s]+(?:data|information|details))',

            # Data about pattern
            r'(?:data|information)\s+(?:about|regarding|concerning)\s+([a-zA-Z\s]+)',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                data_type = match.strip()
                # Clean up multiple spaces
                data_type = re.sub(r'\s+', ' ', data_type)

                if len(data_type) > 5 and len(data_type) < 100:
                    # Clean trailing commas and conjunctions
                    data_type = re.sub(r',?\s*(?:and|or)\s*$', '', data_type)
                    if data_type:
                        data_types.append(data_type)

        # Look for specific data types - Comprehensive list
        specific_types = {
            # Regulatory/Compliance Data Types
            r'\bPII\b': 'Personally Identifiable Information (PII)',
            r'\bPHI\b': 'Protected Health Information (PHI)',
            r'\bPCI\b': 'Payment Card Information (PCI)',
            r'\bPCI-DSS\b': 'Payment Card Industry Data',
            r'\bSPI\b': 'Sensitive Personal Information (SPI)',

            # Identity & Authentication
            r'personal data': 'Personal data',
            r'personal information': 'Personal information',
            r'customer data': 'Customer data',
            r'user data': 'User data',
            r'employee data': 'Employee data',
            r'credentials': 'User credentials',
            r'passwords': 'Passwords',
            r'authentication data': 'Authentication data',
            r'biometric data': 'Biometric data',
            r'biometric information': 'Biometric information',
            r'social security number': 'Social Security Numbers',
            r'\bSSN\b': 'Social Security Numbers (SSN)',
            r'driver\'?s? license': 'Driver\'s license information',
            r'passport': 'Passport information',
            r'national id': 'National ID information',

            # Contact Information
            r'contact information': 'Contact information',
            r'contact details': 'Contact details',
            r'email address': 'Email addresses',
            r'phone number': 'Phone numbers',
            r'mailing address': 'Mailing addresses',
            r'physical address': 'Physical addresses',

            # Financial Data
            r'financial data': 'Financial data',
            r'financial information': 'Financial information',
            r'payment information': 'Payment information',
            r'payment data': 'Payment data',
            r'credit card': 'Credit card information',
            r'debit card': 'Debit card information',
            r'bank account': 'Bank account information',
            r'banking data': 'Banking data',
            r'transaction data': 'Transaction data',
            r'transaction history': 'Transaction history',
            r'billing information': 'Billing information',
            r'billing data': 'Billing data',
            r'invoice data': 'Invoice data',
            r'tax information': 'Tax information',
            r'salary': 'Salary information',
            r'payroll': 'Payroll data',

            # Health Data
            r'health data': 'Health data',
            r'health information': 'Health information',
            r'medical records': 'Medical records',
            r'medical data': 'Medical data',
            r'healthcare data': 'Healthcare data',
            r'diagnosis': 'Diagnosis information',
            r'prescription': 'Prescription data',
            r'treatment': 'Treatment information',

            # Business & Commercial Data
            r'business data': 'Business data',
            r'sales data': 'Sales data',
            r'marketing data': 'Marketing data',
            r'customer relationship': 'Customer relationship data',
            r'\bCRM\b data': 'CRM data',
            r'lead data': 'Lead data',
            r'prospect data': 'Prospect data',
            r'contract data': 'Contract data',
            r'agreement data': 'Agreement data',
            r'purchase history': 'Purchase history',
            r'order data': 'Order data',
            r'inventory data': 'Inventory data',
            r'product data': 'Product data',
            r'pricing data': 'Pricing data',

            # Technical & Operational Data
            r'log data': 'Log data',
            r'system logs': 'System logs',
            r'access logs': 'Access logs',
            r'audit logs': 'Audit logs',
            r'metadata': 'Metadata',
            r'usage data': 'Usage data',
            r'usage information': 'Usage information',
            r'analytics data': 'Analytics data',
            r'performance data': 'Performance data',
            r'telemetry': 'Telemetry data',
            r'ip address': 'IP addresses',
            r'device information': 'Device information',
            r'device data': 'Device data',
            r'session data': 'Session data',
            r'cookie data': 'Cookie data',
            r'browser data': 'Browser data',

            # Location Data
            r'location data': 'Location data',
            r'location information': 'Location information',
            r'geolocation': 'Geolocation data',
            r'gps data': 'GPS data',
            r'geographic data': 'Geographic data',

            # Communication Data
            r'communication data': 'Communication data',
            r'email data': 'Email data',
            r'message data': 'Message data',
            r'chat data': 'Chat data',
            r'call data': 'Call data',
            r'voice data': 'Voice recordings',
            r'video data': 'Video recordings',

            # Content & Media
            r'file data': 'File data',
            r'document data': 'Document data',
            r'image data': 'Image data',
            r'photo data': 'Photo data',
            r'media files': 'Media files',
            r'attachments': 'File attachments',

            # Identity & Access
            r'access control': 'Access control data',
            r'permission data': 'Permission data',
            r'role data': 'Role-based data',
            r'group membership': 'Group membership data',

            # HR & Employment Data
            r'employment data': 'Employment data',
            r'hr data': 'HR data',
            r'personnel data': 'Personnel data',
            r'resume data': 'Resume data',
            r'application data': 'Job application data',
            r'performance review': 'Performance review data',
            r'background check': 'Background check data',

            # Educational Data
            r'educational data': 'Educational data',
            r'academic records': 'Academic records',
            r'student data': 'Student data',
            r'training data': 'Training data',

            # Behavioral & Preference Data
            r'behavioral data': 'Behavioral data',
            r'preference data': 'Preference data',
            r'interest data': 'Interest data',
            r'profile data': 'Profile data',
            r'demographic data': 'Demographic data',

            # Sensitive Categories
            r'government id': 'Government ID data',
            r'immigration': 'Immigration data',
            r'citizenship': 'Citizenship data',
            r'race': 'Race/ethnicity data',
            r'ethnicity': 'Race/ethnicity data',
            r'religion': 'Religious data',
            r'political': 'Political affiliation data',
            r'union membership': 'Union membership data',
            r'genetic': 'Genetic data',
            r'criminal': 'Criminal history data',

            # Aggregate/Combined
            r'sensitive data': 'Sensitive data',
            r'confidential data': 'Confidential data',
            r'proprietary data': 'Proprietary data',
            r'trade secret': 'Trade secret data',
            r'intellectual property': 'Intellectual property data',
        }

        text_lower = text.lower()
        for pattern, data_type in specific_types.items():
            if re.search(pattern, text, re.IGNORECASE):
                data_types.append(data_type)

        return data_types

    def _clean_and_deduplicate(self):
        """Clean and deduplicate extracted information"""

        # Deduplicate and clean services
        services_clean = []
        services_lower = set()
        for service in self.overview['services']:
            service_lower = service.lower().strip()
            if service_lower not in services_lower and len(service_lower) > 5:
                services_clean.append(service.strip())
                services_lower.add(service_lower)
        self.overview['services'] = services_clean[:10]  # Limit to top 10

        # Deduplicate and clean integrations
        integrations_clean = []
        integrations_lower = set()
        for integration in self.overview['integrations']:
            integration_lower = integration.lower().strip()
            if integration_lower not in integrations_lower:
                integrations_clean.append(integration.strip())
                integrations_lower.add(integration_lower)
        self.overview['integrations'] = integrations_clean[:15]  # Limit to top 15

        # Deduplicate and clean data types
        data_clean = []
        data_lower = set()
        for data_type in self.overview['data_processed']:
            data_lower_str = data_type.lower().strip()
            if data_lower_str not in data_lower:
                data_clean.append(data_type.strip())
                data_lower.add(data_lower_str)
        self.overview['data_processed'] = data_clean[:12]  # Limit to top 12

    def _generate_description(self, vendor_name: str, web_results: Dict[str, Any] = None,
                             parsed_docs: List[Dict[str, Any]] = None,
                             vendor_metadata: Dict[str, Any] = None):
        """
        Generate a comprehensive, natural-sounding description of the vendor

        Args:
            vendor_name: Name of the vendor
            web_results: Web search results
            parsed_docs: Parsed documents
            vendor_metadata: User-provided vendor metadata
        """

        # Priority 1: Use user-provided service description if comprehensive
        if vendor_metadata and vendor_metadata.get('services'):
            user_services = vendor_metadata['services'].strip()
            if len(user_services) > 50:
                # User provided a good description
                self.overview['description'] = user_services
                return

        # Priority 2: Extract best description from web search results
        best_description = self._extract_best_web_description(vendor_name, web_results)
        if best_description:
            self.overview['description'] = best_description
            return

        # Priority 3: Synthesize from collected information
        description = self._synthesize_description(vendor_name, vendor_metadata)
        if description:
            self.overview['description'] = description

    def _extract_best_web_description(self, vendor_name: str, web_results: Dict[str, Any] = None) -> str:
        """Extract the best descriptive sentence from web search results"""

        if not web_results:
            return ""

        candidate_sentences = []

        # Collect all snippets
        for control in web_results.get('controls', [])[:15]:
            snippet = control.get('snippet', '')
            title = control.get('title', '')

            # Look for sentences that describe what the vendor does
            for text in [snippet, title]:
                if not text or len(text) < 40:
                    continue

                text_lower = text.lower()
                vendor_lower = vendor_name.lower()

                # Strong indicators of good descriptive content
                has_vendor = vendor_lower in text_lower
                has_verb = any(verb in text_lower for verb in [
                    ' is a ', ' is an ', ' provides ', ' offers ', ' helps ',
                    ' enables ', ' allows ', ' delivers ', ' specializes in '
                ])
                has_service_word = any(word in text_lower for word in [
                    'platform', 'software', 'solution', 'service', 'tool',
                    'system', 'application', 'saas', 'api'
                ])

                if (has_vendor or has_service_word) and (has_verb or has_service_word):
                    # Extract the most relevant sentence
                    sentences = re.split(r'[.!?]\s+', text)
                    for sentence in sentences:
                        sentence = sentence.strip()
                        if len(sentence) < 30:
                            continue

                        sentence_lower = sentence.lower()
                        # Score this sentence
                        score = 0

                        if vendor_lower in sentence_lower:
                            score += 5

                        if any(verb in sentence_lower for verb in [' is a ', ' is an ', ' provides ', ' offers ']):
                            score += 3

                        if any(word in sentence_lower for word in ['platform', 'software', 'solution', 'saas']):
                            score += 2

                        # Descriptive phrases
                        if any(phrase in sentence_lower for phrase in [
                            'designed to', 'helps companies', 'helps organizations',
                            'enables users', 'allows teams', 'specializes in'
                        ]):
                            score += 2

                        if score >= 5:
                            candidate_sentences.append((score, sentence))

        # Sort by score and return the best one
        if candidate_sentences:
            candidate_sentences.sort(reverse=True, key=lambda x: x[0])
            best_sentence = candidate_sentences[0][1]

            # Clean up the sentence
            best_sentence = best_sentence.strip()
            if not best_sentence.endswith('.'):
                best_sentence += '.'

            return best_sentence

        return ""

    def _synthesize_description(self, vendor_name: str, vendor_metadata: Dict[str, Any] = None) -> str:
        """Synthesize description from extracted services, integrations, and data"""

        description_parts = []

        # Start with vendor type
        vendor_type = self._determine_vendor_type()
        services = self.overview.get('services', [])

        if vendor_type:
            description_parts.append(f"{vendor_name} is {vendor_type}")
        elif services:
            description_parts.append(f"{vendor_name} is a software solution")
        else:
            description_parts.append(f"{vendor_name} is a technology platform")

        # Add main function/service
        if services:
            # Find the most descriptive service
            main_service = self._find_most_descriptive_service(services)
            if main_service:
                # Format it properly
                main_service_lower = main_service.lower()
                if any(word in main_service_lower for word in ['for ', 'that ', 'which ']):
                    description_parts.append(main_service_lower)
                elif any(word in main_service_lower for word in ['platform', 'solution', 'software', 'service']):
                    description_parts.append(f"that offers {main_service_lower}")
                else:
                    description_parts.append(f"for {main_service_lower}")

        # Add capabilities
        capabilities = self._get_key_capabilities()
        if capabilities:
            description_parts.append(f"The solution {capabilities}")

        # Combine parts
        if len(description_parts) == 0:
            return ""

        description = description_parts[0]

        if len(description_parts) > 1:
            description += " " + description_parts[1]

        if len(description_parts) > 2:
            description += ". " + description_parts[2]

        if not description.endswith('.'):
            description += '.'

        return description

    def _find_most_descriptive_service(self, services: List[str]) -> str:
        """Find the most descriptive service from the list"""

        if not services:
            return ""

        best_service = services[0]
        best_score = 0

        for service in services[:10]:
            score = len(service.split())  # Prefer longer descriptions

            service_lower = service.lower()

            # Boost score for descriptive keywords
            if any(word in service_lower for word in [
                'management', 'monitoring', 'analytics', 'security',
                'collaboration', 'communication', 'automation',
                'integration', 'customer', 'data', 'cloud'
            ]):
                score += 3

            # Boost for descriptive structure
            if ' for ' in service_lower or ' that ' in service_lower:
                score += 2

            if score > best_score:
                best_score = score
                best_service = service

        return best_service

    def _determine_vendor_type(self) -> str:
        """Determine the type of vendor (SaaS, platform, etc.)"""

        services_text = ' '.join(self.overview.get('services', [])).lower()

        # Check for specific types
        if 'saas' in services_text or 'software as a service' in services_text:
            return "a SaaS"
        elif any(word in services_text for word in ['cloud platform', 'cloud service']):
            return "a cloud platform"
        elif 'platform' in services_text:
            return "a platform"
        elif any(word in services_text for word in ['solution', 'software']):
            return "a software solution"
        elif 'api' in services_text:
            return "an API service"
        elif 'tool' in services_text:
            return "a tool"

        return ""

    def _get_primary_service(self) -> str:
        """Extract the primary service or function"""

        services = self.overview.get('services', [])
        if not services:
            return ""

        # Look for the most descriptive service (usually longer and more specific)
        primary = None
        max_score = 0

        for service in services[:5]:
            service_lower = service.lower()
            score = 0

            # Score based on keywords that indicate primary function
            if any(word in service_lower for word in ['management', 'monitoring', 'analytics',
                                                       'security', 'collaboration', 'communication',
                                                       'crm', 'customer', 'sales', 'marketing',
                                                       'data', 'automation', 'integration']):
                score += 3

            # Prefer longer, more descriptive services
            score += min(len(service.split()), 5)

            # Look for "for" or "that" which often indicate purpose
            if ' for ' in service_lower or ' that ' in service_lower:
                score += 2

            if score > max_score:
                max_score = score
                primary = service

        if primary:
            # Clean up the service description
            primary_lower = primary.lower()

            # If it already starts with "that" or "for", use it as is
            if primary_lower.startswith(('that ', 'for ', 'which ')):
                return primary_lower

            # Otherwise, format it nicely
            if any(word in primary_lower for word in ['platform', 'solution', 'service', 'tool', 'software', 'system']):
                return f"that offers {primary.lower()}"
            else:
                return f"for {primary.lower()}"

        return ""

    def _get_key_capabilities(self) -> str:
        """Extract key capabilities or technologies"""

        services_text = ' '.join(self.overview.get('services', [])).lower()
        capabilities = []

        # Look for key technology or capability keywords
        tech_keywords = {
            'ai': 'uses AI',
            'machine learning': 'uses machine learning',
            'artificial intelligence': 'uses artificial intelligence',
            'automation': 'provides automation',
            'real-time': 'offers real-time monitoring',
            'analytics': 'provides analytics',
            'encryption': 'uses encryption',
            'cloud-based': 'is cloud-based',
            'api': 'offers API access'
        }

        for keyword, description in tech_keywords.items():
            if keyword in services_text:
                capabilities.append(description)

        if capabilities:
            if len(capabilities) == 1:
                return capabilities[0]
            elif len(capabilities) == 2:
                return f"{capabilities[0]} and {capabilities[1]}"
            else:
                return f"{capabilities[0]}, {capabilities[1]}, and more"

        return ""

    def get_formatted_overview(self) -> str:
        """Get formatted text overview"""
        lines = []

        lines.append(f"**Vendor:** {self.overview['vendor_name']}")
        lines.append("")

        if self.overview['description']:
            lines.append(f"**Description:** {self.overview['description']}")
            lines.append("")

        if self.overview['services']:
            lines.append("**Services Provided:**")
            for service in self.overview['services'][:8]:
                lines.append(f"- {service}")
            lines.append("")

        if self.overview['integrations']:
            lines.append("**Integrations:**")
            for integration in self.overview['integrations'][:10]:
                lines.append(f"- {integration}")
            lines.append("")

        if self.overview['data_processed']:
            lines.append("**Data Processed:**")
            for data_type in self.overview['data_processed'][:10]:
                lines.append(f"- {data_type}")
            lines.append("")

        return "\n".join(lines)
