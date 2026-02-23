"""
Atlassian MCP Integration - Connect to Rovo agent and Jira for vendor information
"""
from typing import Dict, List, Any, Optional
import os
import json
import requests
from datetime import datetime


class AtlassianMCPIntegration:
    """Integration with Atlassian MCP server to fetch vendor data from Jira/Rovo"""

    def __init__(self,
                 atlassian_url: str = None,
                 email: str = None,
                 api_token: str = None):
        """
        Initialize Atlassian integration

        Args:
            atlassian_url: Your Atlassian instance URL (e.g., https://your-domain.atlassian.net)
            email: Your Atlassian email
            api_token: Your Atlassian API token
        """
        self.atlassian_url = atlassian_url or os.getenv('ATLASSIAN_URL')
        self.email = email or os.getenv('ATLASSIAN_EMAIL')
        self.api_token = api_token or os.getenv('ATLASSIAN_API_TOKEN')

        if not all([self.atlassian_url, self.email, self.api_token]):
            print("⚠️ Atlassian credentials not fully configured. Some features may not work.")

        self.session = requests.Session()
        if self.email and self.api_token:
            self.session.auth = (self.email, self.api_token)

    def search_vendor_tickets(self, vendor_name: str,
                             project_key: str = None) -> List[Dict[str, Any]]:
        """
        Search Jira tickets related to a vendor

        Args:
            vendor_name: Name of the vendor to search for
            project_key: Optional Jira project key to limit search

        Returns:
            List of Jira tickets with vendor information
        """
        if not self.atlassian_url:
            return []

        try:
            # Build JQL query
            jql_parts = [f'text ~ "{vendor_name}"']

            if project_key:
                jql_parts.append(f'project = {project_key}')

            # Add common vendor-related labels/components
            vendor_filters = ' OR '.join([
                'labels in (vendor, security, privacy, risk-assessment)',
                'component in (vendor-management, security-review)',
                'type in (Vendor, "Security Review", "Privacy Review")'
            ])
            jql_parts.append(f'({vendor_filters})')

            jql = ' AND '.join(jql_parts)

            # Search Jira
            url = f"{self.atlassian_url}/rest/api/3/search"
            params = {
                'jql': jql,
                'maxResults': 50,
                'fields': 'summary,description,status,priority,labels,customfield_*'
            }

            response = self.session.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            issues = data.get('issues', [])

            print(f"✅ Found {len(issues)} Jira tickets for {vendor_name}")
            return issues

        except Exception as e:
            print(f"❌ Error searching Jira: {e}")
            return []

    def query_rovo_agent(self, vendor_name: str,
                        query_type: str = "risk_summary") -> Dict[str, Any]:
        """
        Query the Rovo agent for vendor information

        Args:
            vendor_name: Name of the vendor
            query_type: Type of query (risk_summary, security_review, privacy_review)

        Returns:
            Dictionary with Rovo agent response
        """
        # Note: This is a placeholder for Rovo integration
        # The actual implementation will depend on how your Rovo agent is exposed

        try:
            # Option 1: If Rovo has an API endpoint
            # url = f"{self.atlassian_url}/rest/rovo/1.0/query"
            # response = self.session.post(url, json={
            #     'agent': 'vendor-risk-agent',
            #     'vendor': vendor_name,
            #     'query_type': query_type
            # })

            # Option 2: Query via Jira tickets that Rovo has created/updated
            tickets = self.search_vendor_tickets(vendor_name)
            rovo_data = self._extract_rovo_data_from_tickets(tickets)

            return rovo_data

        except Exception as e:
            print(f"❌ Error querying Rovo: {e}")
            return {}

    def _extract_rovo_data_from_tickets(self, tickets: List[Dict]) -> Dict[str, Any]:
        """
        Extract vendor risk information from Jira tickets

        Args:
            tickets: List of Jira tickets

        Returns:
            Aggregated vendor risk data
        """
        vendor_data = {
            'vendor_name': '',
            'risk_summary': [],
            'security_issues': [],
            'privacy_concerns': [],
            'compliance_status': [],
            'services_mentioned': [],
            'data_types_mentioned': [],
            'last_review_date': None,
            'overall_risk_level': 'UNKNOWN'
        }

        for ticket in tickets:
            fields = ticket.get('fields', {})

            # Extract summary and description
            summary = fields.get('summary', '')
            description = fields.get('description', '')

            # Combine text for analysis
            text = f"{summary} {description}"

            # Extract risk information
            if 'risk' in text.lower():
                vendor_data['risk_summary'].append({
                    'ticket': ticket.get('key'),
                    'summary': summary,
                    'status': fields.get('status', {}).get('name', ''),
                    'priority': fields.get('priority', {}).get('name', '')
                })

            # Extract security issues
            security_keywords = ['vulnerability', 'breach', 'security', 'exploit', 'cve']
            if any(kw in text.lower() for kw in security_keywords):
                vendor_data['security_issues'].append({
                    'ticket': ticket.get('key'),
                    'issue': summary,
                    'status': fields.get('status', {}).get('name', '')
                })

            # Extract privacy concerns
            privacy_keywords = ['privacy', 'pii', 'phi', 'gdpr', 'ccpa', 'personal data']
            if any(kw in text.lower() for kw in privacy_keywords):
                vendor_data['privacy_concerns'].append({
                    'ticket': ticket.get('key'),
                    'concern': summary
                })

            # Extract compliance status
            compliance_keywords = ['soc 2', 'iso 27001', 'hipaa', 'pci', 'compliance']
            if any(kw in text.lower() for kw in compliance_keywords):
                vendor_data['compliance_status'].append({
                    'ticket': ticket.get('key'),
                    'status': summary
                })

            # Extract labels for additional context
            labels = fields.get('labels', [])
            vendor_data['services_mentioned'].extend([
                label for label in labels
                if any(svc in label.lower() for svc in ['saas', 'cloud', 'api', 'platform'])
            ])

            # Check for risk level indicators
            priority = fields.get('priority', {}).get('name', '').upper()
            if priority in ['HIGHEST', 'HIGH', 'CRITICAL']:
                vendor_data['overall_risk_level'] = 'HIGH'
            elif priority in ['MEDIUM'] and vendor_data['overall_risk_level'] == 'UNKNOWN':
                vendor_data['overall_risk_level'] = 'MEDIUM'

        # Deduplicate lists
        vendor_data['services_mentioned'] = list(set(vendor_data['services_mentioned']))

        return vendor_data

    def get_vendor_overview_from_jira(self, vendor_name: str) -> Dict[str, Any]:
        """
        Get comprehensive vendor overview from Jira/Rovo

        Args:
            vendor_name: Name of the vendor

        Returns:
            Dictionary with vendor overview data that can be merged with VendorOverviewExtractor
        """
        print(f"🔍 Fetching vendor data from Jira for {vendor_name}...")

        # Search Jira tickets
        tickets = self.search_vendor_tickets(vendor_name)

        # Extract Rovo/vendor data
        vendor_data = self._extract_rovo_data_from_tickets(tickets)
        vendor_data['vendor_name'] = vendor_name

        # Query Rovo agent if available
        rovo_data = self.query_rovo_agent(vendor_name)
        vendor_data.update(rovo_data)

        print(f"✅ Extracted data from {len(tickets)} Jira tickets")
        return vendor_data

    def create_assessment_ticket(self,
                                vendor_name: str,
                                assessment_results: Dict[str, Any],
                                project_key: str) -> Optional[str]:
        """
        Create a Jira ticket with assessment results

        Args:
            vendor_name: Name of the vendor
            assessment_results: Results from vendor assessment
            project_key: Jira project key to create ticket in

        Returns:
            Ticket key if successful, None otherwise
        """
        if not all([self.atlassian_url, project_key]):
            print("❌ Cannot create Jira ticket: Missing configuration")
            return None

        try:
            url = f"{self.atlassian_url}/rest/api/3/issue"

            # Build ticket description
            risk = assessment_results.get('risk_assessment', {})
            overview = assessment_results.get('vendor_overview', {})

            description_parts = [
                f"h2. Vendor Assessment: {vendor_name}",
                f"*Date:* {datetime.now().strftime('%Y-%m-%d')}",
                "",
                "h3. Overview",
                f"*Description:* {overview.get('description', 'N/A')}",
                "",
                "h3. Risk Assessment",
                f"*Overall Risk:* {risk.get('overall_risk', 'N/A')}",
                f"*Risk Score:* {risk.get('risk_score', 'N/A')}/100",
                f"*Critical Risks:* {risk.get('summary', {}).get('critical_risks', 0)}",
                "",
                "h3. Data Processed",
            ]

            data_types = overview.get('data_processed', [])[:5]
            for dt in data_types:
                description_parts.append(f"* {dt}")

            description = "\n".join(description_parts)

            # Create ticket
            payload = {
                "fields": {
                    "project": {"key": project_key},
                    "summary": f"Vendor Security Assessment: {vendor_name}",
                    "description": {
                        "type": "doc",
                        "version": 1,
                        "content": [
                            {
                                "type": "paragraph",
                                "content": [
                                    {"type": "text", "text": description}
                                ]
                            }
                        ]
                    },
                    "issuetype": {"name": "Task"},
                    "labels": ["vendor-assessment", "security", "automated"]
                }
            }

            response = self.session.post(url, json=payload)
            response.raise_for_status()

            ticket_key = response.json().get('key')
            print(f"✅ Created Jira ticket: {ticket_key}")
            return ticket_key

        except Exception as e:
            print(f"❌ Error creating Jira ticket: {e}")
            return None

    def update_vendor_metadata(self, vendor_metadata: Dict[str, Any],
                              jira_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge Jira/Rovo data with vendor metadata

        Args:
            vendor_metadata: Existing vendor metadata
            jira_data: Data from Jira/Rovo

        Returns:
            Updated vendor metadata
        """
        # Merge services
        if jira_data.get('services_mentioned'):
            existing_services = vendor_metadata.get('services', '')
            new_services = ', '.join(jira_data['services_mentioned'])
            vendor_metadata['services'] = f"{existing_services}, {new_services}".strip(', ')

        # Add Jira-specific fields
        vendor_metadata['jira_risk_level'] = jira_data.get('overall_risk_level', 'UNKNOWN')
        vendor_metadata['jira_tickets_found'] = len(jira_data.get('risk_summary', []))
        vendor_metadata['security_issues_count'] = len(jira_data.get('security_issues', []))
        vendor_metadata['privacy_concerns_count'] = len(jira_data.get('privacy_concerns', []))

        return vendor_metadata
