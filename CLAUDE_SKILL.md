# Vendor Security Assessment Tool - Claude Code Guide

## Quick Start

```bash
# Clone the repository
git clone https://github.com/niana0/vendor-security-assessment-tool-.git
cd vendor-security-assessment-tool-

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

## What This Tool Does

Automated vendor security assessment tool that:
- Extracts vendor information from web searches and documents
- Generates comprehensive vendor overviews with intelligent description synthesis
- Detects 100+ data types across 15 categories
- Performs risk assessment using STRIDE threat modeling
- Maps evidence to security questionnaires
- Generates detailed assessment reports

## Key Features

### 1. Vendor Overview Extraction
- **Location:** `src/vendor_overview_extractor.py`
- **Extracts:** Vendor name, services, integrations, data processed
- **Sources:** Web search results, uploaded documents, user input
- **Intelligence:** 3-tier description strategy (user input → web extraction → synthesis)

### 2. Enhanced Web Search
- **Location:** `src/web_search_agent.py`
- **Engine:** DuckDuckGo (with Google/Bing fallback)
- **Strategy:** 5 targeted searches for comprehensive results
- **Filtering:** Vendor-specific filtering to eliminate generic content

### 3. Data Type Detection
- **Comprehensive:** 100+ data types across 15 categories
- **Categories:** Identity, financial, health, business, technical, location, etc.
- **Patterns:** 7 different extraction patterns for maximum coverage

### 4. Risk Assessment
- **Location:** `src/risk_assessor.py`
- **Framework:** STRIDE threat modeling
- **Output:** Risk scores, recommendations, gaps analysis

## Usage

### Basic Assessment
1. Enter vendor name
2. Provide optional context (services, integrations, data)
3. Upload documents (optional)
4. Upload questionnaire (optional)
5. Run assessment

### Web Search Only Mode
- No documents required
- Searches public information about vendor
- Generates risk assessment from web findings

### Hybrid Mode
- Upload vendor documents + questionnaire
- Combines document analysis with web search
- Most comprehensive assessment

## Key Components

### `app.py`
- Streamlit UI
- Main processing pipeline
- Results display

### `src/vendor_overview_extractor.py`
- Vendor overview extraction
- Description synthesis
- Data type detection (100+ types)
- Service and integration extraction

### `src/web_search_agent.py`
- Web search orchestration
- 5 targeted searches (trust pages, certifications, features, breaches, vulnerabilities)
- Vendor-specific filtering
- Result deduplication

### `src/document_parser.py`
- PDF, DOCX, XLSX parsing
- Text extraction
- Content normalization

### `src/evidence_extractor.py`
- Security control extraction
- Evidence scoring
- Keyword matching

### `src/questionnaire_mapper.py`
- Question parsing
- Evidence mapping
- Gap identification

### `src/risk_assessor.py`
- Risk scoring
- STRIDE analysis
- Recommendations generation

## Configuration

### Environment Variables (optional)
Create `.env` file:
```bash
# Google Custom Search (optional)
GOOGLE_API_KEY=your_key
GOOGLE_SEARCH_ENGINE_ID=your_id

# Bing Search (optional)
BING_API_KEY=your_key
```

### Default Search Engine
- Primary: DuckDuckGo (no API key needed)
- Fallback: Google Custom Search, Bing

## Output

### Vendor Overview
- Vendor name and description
- Services provided
- Integrations
- Data processed

### Risk Assessment
- Overall risk score
- Critical/high/medium/low risks
- STRIDE threat analysis
- Recommendations

### Reports
- Markdown report (`output/[vendor]_assessment.md`)
- Excel report with detailed findings

## Advanced Features

### Data Type Detection
Detects 100+ data types including:
- **Regulatory:** PII, PHI, PCI
- **Identity:** credentials, biometric, SSN
- **Financial:** payment info, banking data, transactions
- **Health:** medical records, diagnosis
- **Business:** CRM, sales, contracts
- **Technical:** logs, analytics, IP addresses
- And many more...

### Web Search Strategy
1. **Trust/security pages:** Official vendor security info
2. **Certifications:** SOC 2, ISO 27001, etc.
3. **Security features:** Encryption, data protection
4. **Breaches:** Recent security incidents (2020-2026)
5. **Vulnerabilities:** CVEs and security flaws

### Description Synthesis
Three-tier strategy:
1. **User input:** Uses your description if comprehensive (>50 chars)
2. **Web extraction:** Finds best descriptive sentence from search results
3. **Synthesis:** Combines extracted info into coherent description

## Tips

1. **Provide context:** Fill in vendor services/integrations for better results
2. **Use documents:** Upload vendor docs for deeper analysis
3. **Check web search:** Results show what was found online
4. **Review overview:** Vendor overview appears at top of results
5. **Export reports:** Download Markdown or Excel reports

## Repository
https://github.com/niana0/vendor-security-assessment-tool-

## Created With
- Python 3.10+
- Streamlit
- DuckDuckGo Search
- Sentence Transformers
- Multiple document parsers
