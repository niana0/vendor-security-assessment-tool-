# Vendor Security Assessment Tool

Automate vendor security reviews by extracting answers from vendor artifacts and producing risk summaries + recommendations.

## Features

- 📄 **Document Parsing**: Automatically extract text and tables from PDF and Excel files
- 🔍 **Evidence Extraction**: Identify security controls, certifications, and compliance statements
- 🌐 **Live Web Search**: Automatically search for public security information (certifications, incidents)
- 📋 **Questionnaire Mapping**: Map evidence to questionnaire questions with confidence levels
- ⚠️ **Risk Assessment**: Generate ranked risks and prioritized recommendations
- 📊 **Reports**: Create executive-ready reports and completed questionnaires
- 🖥️ **Web UI**: User-friendly interface for uploading files and viewing results

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.8 or higher installed on your system
- A modern web browser (Chrome, Firefox, Safari, or Edge)
- At least 2GB of free RAM

### Step 1: Open Terminal and Navigate to Project Directory

```bash
cd "[directory where you've saved this project]"
```

### Step 2: Create a Virtual Environment

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` appear at the start of your terminal prompt.

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

⏱️ This will take 2-3 minutes. You'll see packages being downloaded and installed.

### Step 4: Run the Application

```bash
streamlit run app.py
```

**What happens next:**
- Streamlit will start the web server
- Your default browser will automatically open
- You'll see the URL: `http://localhost:8501`
- The Vendor Security Assessment Tool interface will load

If the browser doesn't open automatically, manually go to: **http://localhost:8501**

### Step 5: Use the Application

1. **Fill in Vendor Information**:
   - Enter the vendor name (required)
   - Optionally add details about services, integrations, and data stored

2. **Upload Documents** (Optional):
   - **Vendor Documents** (left side): PDF or Excel files (SOC 2 reports, security docs)
   - **Questionnaire** (right side): Your vendor questionnaire (Excel format)
   - Documents are optional - the tool can work with just vendor name + web search

3. **Click "🎯 Generate Risk Assessment"**:
   - A progress bar will show the processing stages
   - The tool will automatically:
     - Parse any uploaded documents
     - **Search the web for public security information**
     - Extract certifications (SOC 2, ISO 27001, etc.)
     - Find security incidents and breaches
     - Combine all evidence sources
   - Takes 1-2 minutes depending on document size and search results

4. **View Results**:
   - Overall risk level and score
   - **Web search results** (incidents found, certifications)
   - Confidence distribution chart
   - Key risks (expandable cards)
   - Prioritized recommendations
   - Detailed question-by-question analysis

5. **Download Reports**:
   - Click "📊 Download Completed Questionnaire (Excel)"
   - Click "📄 Download Risk Assessment Report (Markdown)"
   - Files will save to your `output/` directory

### Step 6: Process Another Vendor

Click "🔄 Process New Documents" to start over with different files.

### Step 7: Stop the Application

When you're done, return to your terminal and press:
```
Ctrl + C
```

This will stop the web server.

---

## 💡 Complete Example Run

Here's a complete example from start to finish:

```bash
# 1. Navigate to project
cd "/Users/ana.ni/Documents/Obsidian Vault/Claude Code projects/Heydar's version (vendor reviews)"

# 2. Activate virtual environment
source venv/bin/activate

# 3. Run the app
streamlit run app.py

# Browser opens automatically to http://localhost:8501

# 4. Upload files in the UI
# 5. Click Process
# 6. View results
# 7. Download reports

# 8. Stop the server when done
# Press Ctrl + C in terminal
```

---

## 🎯 What You Need Before Starting

**Minimum Required:**
- **Vendor Name**: Just the vendor's name is enough to get started!

**Optional (for deeper analysis):**
1. **Vendor Documentation**:
   - SOC 2 Type 2 reports (PDF)
   - Security questionnaires like CAIQ (Excel)
   - Compliance documentation (PDF or Excel)
   - Security policies and procedures (PDF)

2. **Questionnaire Template**:
   - Your Datadog vendor risk assessment questionnaire (Excel)
   - Should contain questions in a sheet with "?" characters
   - Questions should be in clear cells (>20 characters)

**Supported File Formats:**
- PDF files (`.pdf`)
- Excel files (`.xlsx`, `.xls`)

**Assessment Modes:**
- **Web Search Only**: Just vendor name → searches public information
- **Documents Only**: Vendor docs + questionnaire → analyzes provided materials
- **Hybrid Mode**: Combines both for comprehensive assessment

---

## 📱 Accessing the Application

Once running, you can access the application from:

- **Same Computer**: http://localhost:8501
- **Other Devices on Same Network**: http://192.168.1.206:8501 (or your computer's IP)

To find your computer's IP address:
```bash
# macOS/Linux
ifconfig | grep "inet "

# Windows
ipconfig
```

## Output Files

The tool generates three main outputs:

1. **completed_questionnaire.xlsx**: Excel file with questions, answers, evidence references, confidence levels, and gaps
2. **risk_assessment_report.md**: Markdown report with risk summary, key findings, and recommendations
3. **Interactive UI**: Real-time results displayed in the web interface

## Project Structure

```
vendor_security_assessment/
├── app.py                          # Streamlit web UI (main entry point)
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── .env.example                    # Environment variables template
│
├── src/                            # Core modules
│   ├── __init__.py
│   ├── document_parser.py          # PDF/Excel parsing
│   ├── evidence_extractor.py       # Security evidence extraction
│   ├── questionnaire_mapper.py     # Evidence-to-question mapping
│   └── risk_assessor.py            # Risk assessment & reporting
│
├── uploads/                        # Temporary uploaded files
├── output/                         # Generated reports
└── vendor_security_assessment.md   # Project planning document
```

## 🌐 Web Search Configuration

The tool performs **automatic web searches** to gather public security information about vendors.

### Default: DuckDuckGo (Free, No Setup)

By default, the tool uses **DuckDuckGo** search which:
- ✅ **Free** - No API keys required
- ✅ **No registration** - Works immediately
- ✅ **Privacy-friendly** - No tracking
- ⚠️ Rate limited - May slow down with many searches

**No configuration needed!** Just run the app and it works.

### Optional: Google Custom Search API

For higher quality and faster results, configure Google Custom Search:

1. **Get a Google API Key**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable "Custom Search API"
   - Create credentials → API Key
   - Copy your API key

2. **Create Custom Search Engine**:
   - Go to [Programmable Search Engine](https://programmablesearchengine.google.com/)
   - Click "Add" to create new search engine
   - Search settings: "Search the entire web"
   - Copy your Search Engine ID

3. **Configure the app**:
   - Copy `.env.example` to `.env`
   - Add your keys:
     ```
     GOOGLE_API_KEY=your_api_key_here
     GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here
     ```

**Limits**: Google provides 100 free searches/day, then charges $5 per 1,000 queries.

### Optional: Bing Search API

Alternative to Google:

1. **Get Bing API Key**:
   - Go to [Azure Portal](https://portal.azure.com/)
   - Create "Bing Search v7" resource
   - Copy your API key

2. **Configure the app**:
   - Add to `.env`:
     ```
     BING_API_KEY=your_bing_api_key_here
     ```

**Limits**: Bing provides 1,000 free searches/month on free tier.

### Search Priority

The tool tries search providers in this order:
1. DuckDuckGo (always attempted first)
2. Google Custom Search (if API key configured)
3. Bing Search (if API key configured)

If DuckDuckGo succeeds, other providers aren't used (saves your API quota).

## How It Works

### Pipeline

1. **Document Parsing**: Extract text, tables, and metadata from vendor documents
2. **Web Search**: Automatically search for certifications, security incidents, and public information
3. **Evidence Extraction**: Identify security controls, certifications, and policies using keyword matching and NLP
4. **Evidence Merging**: Combine document evidence with web search findings
5. **Semantic Mapping**: Use sentence transformers to match evidence to questionnaire questions
6. **Gap Analysis**: Identify missing evidence and contradictions
7. **Risk Scoring**: Calculate risk levels based on confidence and evidence quality
8. **Report Generation**: Create structured outputs for review

### Web Search Process

The tool searches for:
1. **Security Certifications**: SOC 2, ISO 27001, FedRAMP, HIPAA, PCI DSS
2. **Security Controls**: Encryption, MFA, access controls, monitoring
3. **Compliance**: GDPR, CCPA, industry-specific frameworks
4. **Security Incidents**: Breaches, vulnerabilities, past issues
5. **Public Reviews**: Security ratings and customer feedback

Search results are:
- Categorized by type (controls vs. incidents)
- Assigned confidence levels based on source quality
- Converted to standard evidence format
- Merged with document-based evidence

### Confidence Levels

- **HIGH**: Direct evidence found with strong semantic match (>0.6 similarity)
- **MEDIUM**: Indirect or partial evidence (0.4-0.6 similarity)
- **LOW**: Weak evidence (<0.4 similarity)
- **NOT_FOUND**: No relevant evidence in documentation

### Risk Levels

- **LOW RISK**: >70% questions answered with high confidence
- **MEDIUM RISK**: 50-70% coverage
- **HIGH RISK**: 30-50% coverage
- **CRITICAL RISK**: <30% coverage

## 📋 System Requirements

**Minimum Requirements:**
- **OS**: macOS, Windows, or Linux
- **Python**: 3.8 or higher
- **RAM**: 2GB free (4GB recommended)
- **Disk Space**: 500MB for application + models
- **Browser**: Chrome, Firefox, Safari, or Edge (latest version)
- **Internet**: Required for first-time model download (~80MB)

**Recommended:**
- Python 3.10+
- 8GB total RAM
- SSD for faster file processing

## 🔧 Troubleshooting

### Issue: "No questions found in questionnaire"

**Solution:**
- Ensure the Excel file contains actual questions
- Questions should have "?" and be longer than 20 characters
- Questions should be in the first or second sheet
- The tool looks for sheets named: "Questions", "Questionnaire", "Assessment"
- Make sure cells aren't merged or formatted strangely

### Issue: Application won't start / Port already in use

**Solution:**
```bash
# Kill any existing Streamlit processes
lsof -ti:8501 | xargs kill -9

# Then restart
streamlit run app.py
```

### Issue: Slow processing

**Causes:**
- First run downloads the sentence transformer model (~80MB) - this is normal
- Large PDFs with many pages take longer to parse
- Multiple large files increase processing time

**Solutions:**
- Be patient on first run (model download)
- Process fewer documents at once
- Break large PDFs into smaller sections if possible

### Issue: Memory errors

**Solutions:**
- Close other applications to free up RAM
- Process fewer documents at once (try 2-3 files instead of 10+)
- Use compressed/optimized PDF files when possible
- Restart your computer if memory is very low

### Issue: Browser doesn't open automatically

**Solution:**
- Manually open your browser
- Go to: http://localhost:8501
- Check terminal output for the correct URL

### Issue: Module not found errors

**Solution:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "Connection refused" or can't access the page

**Solution:**
- Check if Streamlit is actually running (look at terminal)
- Make sure no firewall is blocking port 8501
- Try http://127.0.0.1:8501 instead of localhost
- Restart the application

### Issue: Files won't upload

**Solution:**
- Check file formats (must be .pdf, .xlsx, or .xls)
- Ensure files aren't corrupted
- Try uploading one file at a time
- Check file permissions (make sure they're readable)

### Issue: Results look incorrect or incomplete

**Possible Causes:**
- Vendor documents don't contain relevant security information
- Documents are scanned images (not text-searchable PDFs)
- Questions in questionnaire are too vague or generic

**Solutions:**
- Use text-searchable PDFs (run OCR if needed)
- Ensure vendor documentation is comprehensive
- Review the confidence levels - LOW means weak evidence
- Check the "Evidence" section to see what was found

---

## 🛑 How to Stop the Application

**Method 1: From Terminal**
1. Go to the terminal where Streamlit is running
2. Press `Ctrl + C`
3. Wait for "Stopping..." message

**Method 2: Force Kill**
```bash
# Find and kill the process
lsof -ti:8501 | xargs kill -9
```

**Method 3: Close Terminal**
- Simply close the terminal window
- The process will stop automatically

## Future Enhancements

- [ ] Support for Word documents (.docx)
- [ ] Advanced contradiction detection
- [ ] Custom questionnaire templates
- [ ] Batch processing multiple vendors
- [ ] API integration for automated workflows
- [ ] PDF report generation

## License

Internal tool - Not for public distribution

## Support

For issues or questions, contact the development team.
