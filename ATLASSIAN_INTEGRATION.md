# Atlassian Rovo/Jira Integration Guide

This guide explains how to integrate your Atlassian Rovo agent and Jira tickets with the Vendor Review Tool.

## Overview

The integration allows you to:
- ✅ Fetch vendor information from Jira tickets
- ✅ Query your Rovo agent for risk summaries
- ✅ Automatically populate vendor data from existing assessments
- ✅ Create new Jira tickets with assessment results
- ✅ Merge Jira data with web search and document analysis

## Architecture

```
┌─────────────────┐
│  Rovo Agent     │ ← Your AI agent for vendor risk
│  (Jira)         │
└────────┬────────┘
         │
         ↓ Atlassian API
┌─────────────────┐
│ Atlassian MCP   │ ← Official MCP Server
│ Server          │
└────────┬────────┘
         │
         ↓ Python Integration
┌─────────────────┐
│ Vendor Review   │ ← Our Tool
│ Tool v3         │
└─────────────────┘
```

## Prerequisites

### 1. Atlassian Account & Permissions
- Jira Cloud instance
- API token (see setup below)
- Permission to access vendor-related projects

### 2. Node.js (for MCP Server) - **Optional**
The official Atlassian MCP server requires Node.js, but our integration works directly with the Atlassian API, so Node.js is optional.

If you want to use the official MCP server:
```bash
# Install Node.js 18+
# Then install Atlassian MCP server
npm install -g @atlassian/mcp-server
```

## Setup Instructions

### Step 1: Get Atlassian API Token

1. Go to: https://id.atlassian.com/manage-profile/security/api-tokens
2. Click **"Create API token"**
3. Give it a name (e.g., "Vendor Review Tool")
4. Copy the token (you'll need it for .env)

### Step 2: Configure Environment Variables

Create or update your `.env` file:

```bash
# Atlassian Configuration
ATLASSIAN_URL=https://your-domain.atlassian.net
ATLASSIAN_EMAIL=your.email@datadoghq.com
ATLASSIAN_API_TOKEN=your_api_token_here

# Optional: Jira Project Configuration
JIRA_VENDOR_PROJECT_KEY=VEN  # Your vendor management project key
```

### Step 3: Install Python Dependencies

The integration is already included in requirements.txt. If you need to install manually:

```bash
pip install requests python-dotenv
```

### Step 4: Test the Integration

Run the Streamlit app and try the Jira integration:

```bash
streamlit run app.py
```

In the UI:
1. Enter a vendor name
2. Check the box: **"🔗 Fetch data from Jira/Rovo Agent"**
3. The tool will search Jira for relevant tickets

## How It Works

### 1. Jira Ticket Search

When you enable Jira integration, the tool searches for tickets using JQL:

```sql
text ~ "VendorName"
AND (
  labels in (vendor, security, privacy, risk-assessment)
  OR component in (vendor-management, security-review)
  OR type in (Vendor, "Security Review", "Privacy Review")
)
```

### 2. Data Extraction

From Jira tickets, the tool extracts:
- **Risk summaries** from ticket descriptions
- **Security issues** (vulnerabilities, breaches, CVEs)
- **Privacy concerns** (PII, PHI, GDPR, CCPA mentions)
- **Compliance status** (SOC 2, ISO 27001, etc.)
- **Services mentioned** in labels/descriptions
- **Overall risk level** from ticket priorities

### 3. Rovo Agent Query

The tool can query your Rovo agent by:
- Analyzing Rovo-generated tickets
- Extracting AI-generated risk summaries
- Pulling structured vendor data from Rovo's analysis

### 4. Data Merging

Jira data is merged with:
- Web search results
- Uploaded documents
- User-provided information

To create a comprehensive vendor overview.

## Jira Ticket Structure (Recommended)

For best results, structure your vendor Jira tickets like this:

### Ticket Type
- **"Vendor"** or **"Security Review"** or **"Privacy Review"**

### Required Fields
- **Summary:** "Vendor Assessment: [Vendor Name]"
- **Labels:** `vendor`, `security`, `privacy`, `risk-assessment`
- **Component:** `vendor-management` or `security-review`

### Description Template
```
h2. Vendor Information
* Vendor Name: [Name]
* Services: [List services]
* Data Types: PII, Payment Info, etc.

h2. Risk Assessment
* Overall Risk: HIGH/MEDIUM/LOW
* Security Issues: [List issues]

h2. Compliance Status
* SOC 2: [Status]
* ISO 27001: [Status]
```

## Rovo Agent Setup

### Option 1: Rovo Creates/Updates Tickets
Configure your Rovo agent to create or update Jira tickets with vendor assessments. The tool will automatically find and parse them.

### Option 2: Direct API Integration
If your Rovo agent has an API endpoint:

```python
# Customize in src/atlassian_mcp_integration.py
def query_rovo_agent(self, vendor_name: str):
    url = f"{self.atlassian_url}/rest/rovo/1.0/query"
    response = self.session.post(url, json={
        'agent': 'vendor-risk-agent',
        'vendor': vendor_name,
        'query_type': 'risk_summary'
    })
    return response.json()
```

## Features

### ✅ Auto-populate Vendor Information
- Services, integrations, and data types from Jira
- Risk level indicators from ticket priorities
- Historical assessment data

### ✅ Risk Context from Jira
- Past security issues
- Privacy concerns
- Compliance status updates
- Remediation tracking

### ✅ Create Assessment Tickets
After completing an assessment, create a new Jira ticket:

```python
jira_integration = AtlassianMCPIntegration()
ticket_key = jira_integration.create_assessment_ticket(
    vendor_name="CloudSecure Inc.",
    assessment_results=results,
    project_key="VEN"
)
```

## Troubleshooting

### Error: "Atlassian credentials not fully configured"
**Solution:** Check your `.env` file has all three variables:
- `ATLASSIAN_URL`
- `ATLASSIAN_EMAIL`
- `ATLASSIAN_API_TOKEN`

### Error: "401 Unauthorized"
**Solution:**
1. Verify your API token is correct
2. Check your email matches your Atlassian account
3. Ensure the token hasn't expired

### No Jira tickets found
**Solution:**
1. Check your JQL query matches your ticket structure
2. Verify vendor name spelling
3. Check you have permission to view the tickets
4. Customize the search in `src/atlassian_mcp_integration.py`

### Rovo agent not responding
**Solution:**
1. Check if Rovo has an API endpoint
2. Verify Rovo has analyzed this vendor
3. Look for Rovo-generated tickets in Jira

## Advanced Configuration

### Custom JQL Query

Edit `src/atlassian_mcp_integration.py`:

```python
def search_vendor_tickets(self, vendor_name: str, project_key: str = None):
    # Customize your JQL here
    jql = f'project = {project_key} AND text ~ "{vendor_name}" AND labels = custom-label'
    # ... rest of the function
```

### Custom Field Extraction

Add custom field extraction in `_extract_rovo_data_from_tickets`:

```python
# Extract custom fields
custom_field = fields.get('customfield_10001', '')
vendor_data['custom_data'] = custom_field
```

## Using with Official Atlassian MCP Server

If you want to use the official Atlassian MCP Server with Claude Desktop:

1. Install the server:
```bash
npm install -g @atlassian/mcp-server
```

2. Configure Claude Desktop (`~/Library/Application Support/Claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "atlassian": {
      "command": "npx",
      "args": ["-y", "@atlassian/mcp-server"],
      "env": {
        "ATLASSIAN_URL": "https://your-domain.atlassian.net",
        "ATLASSIAN_EMAIL": "your.email@datadoghq.com",
        "ATLASSIAN_API_TOKEN": "your_token"
      }
    }
  }
}
```

3. Restart Claude Desktop

The official MCP server provides additional features like:
- Direct Claude.ai integration
- Enhanced search capabilities
- Real-time Jira updates

## Security Best Practices

1. **Never commit API tokens** to version control
2. Use environment variables (`.env` file)
3. Limit API token permissions to necessary scopes
4. Rotate API tokens regularly
5. Use project-specific tokens when possible

## Examples

### Example 1: Fetch and Display Jira Data

```python
from src.atlassian_mcp_integration import AtlassianMCPIntegration

# Initialize
jira = AtlassianMCPIntegration()

# Search for vendor
vendor_data = jira.get_vendor_overview_from_jira("Salesforce")

# Display results
print(f"Found {len(vendor_data['security_issues'])} security issues")
print(f"Risk Level: {vendor_data['overall_risk_level']}")
```

### Example 2: Create Assessment Ticket

```python
# After running assessment
results = {
    'risk_assessment': {...},
    'vendor_overview': {...}
}

# Create Jira ticket
ticket_key = jira.create_assessment_ticket(
    vendor_name="CloudSecure",
    assessment_results=results,
    project_key="VEN"
)

print(f"Created ticket: {ticket_key}")
```

## Resources

- **Atlassian MCP Server:** https://github.com/atlassian/atlassian-mcp-server
- **Atlassian API Docs:** https://developer.atlassian.com/cloud/jira/platform/rest/v3/
- **MCP Protocol:** https://modelcontextprotocol.io/
- **Rovo Documentation:** https://www.atlassian.com/software/rovo

## Support

For issues with:
- **This integration:** Create an issue on GitHub
- **Atlassian MCP Server:** https://github.com/atlassian/atlassian-mcp-server/issues
- **Jira API:** https://community.atlassian.com/

---

**Next Steps:**
1. Set up your `.env` file with Atlassian credentials
2. Test the integration with a known vendor
3. Customize the JQL query for your Jira structure
4. Configure your Rovo agent to work with the tool
