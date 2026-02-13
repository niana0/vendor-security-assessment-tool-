"""
Risk Assessor - Analyzes completed questionnaire and generates risk assessment
"""
from typing import Dict, List, Any
import json


class RiskAssessor:
    """Assess risks based on questionnaire responses"""

    RISK_CATEGORIES = {
        'data_protection': ['encryption', 'data protection', 'privacy', 'gdpr', 'confidentiality'],
        'access_control': ['authentication', 'authorization', 'access control', 'mfa', 'password'],
        'monitoring': ['logging', 'monitoring', 'audit', 'siem', 'detection'],
        'incident_response': ['incident', 'response', 'breach', 'disaster recovery', 'backup'],
        'compliance': ['compliance', 'certification', 'soc 2', 'iso 27001', 'audit'],
        'vulnerability_management': ['vulnerability', 'patch', 'scanning', 'penetration test'],
        'vendor_management': ['vendor', 'third party', 'supplier', 'subprocessor']
    }

    def __init__(self):
        self.risk_assessment = {
            "risks": [],
            "recommendations": [],
            "summary": {}
        }

    def assess(self, question_mappings: List[Dict[str, Any]],
               vendor_metadata: Dict[str, Any] = None,
               web_search_results: Dict[str, Any] = None) -> Dict[str, Any]:
        """Perform risk assessment with threat modeling"""

        # Store metadata and web results for use in other methods
        self.vendor_metadata = vendor_metadata or {}
        self.web_search_results = web_search_results or {}

        # Analyze by confidence level
        confidence_stats = self._analyze_confidence(question_mappings)

        # Identify high-risk areas
        risks = self._identify_risks(question_mappings)

        # Generate threat model
        threat_model = self._generate_threat_model(question_mappings, risks)

        # Generate recommendations
        recommendations = self._generate_recommendations(risks, question_mappings)

        # Calculate overall risk score
        risk_score = self._calculate_risk_score(question_mappings)

        # Count public incidents
        public_incidents_count = len(self.web_search_results.get('incidents', []))

        self.risk_assessment = {
            "overall_risk": risk_score['level'],
            "risk_score": risk_score['score'],
            "confidence_distribution": confidence_stats,
            "risks": risks,
            "threat_model": threat_model,
            "recommendations": recommendations,
            "public_incidents_found": public_incidents_count,
            "summary": {
                "total_questions": len(question_mappings),
                "answered_high_confidence": confidence_stats.get('HIGH', 0),
                "answered_medium_confidence": confidence_stats.get('MEDIUM', 0),
                "answered_low_confidence": confidence_stats.get('LOW', 0),
                "insufficient_evidence": confidence_stats.get('NOT_FOUND', 0),
                "critical_risks": len([r for r in risks if r['severity'] == 'HIGH']),
                "medium_risks": len([r for r in risks if r['severity'] == 'MEDIUM']),
                "low_risks": len([r for r in risks if r['severity'] == 'LOW'])
            }
        }

        return self.risk_assessment

    def _analyze_confidence(self, mappings: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze confidence distribution"""
        stats = {}
        for mapping in mappings:
            conf = mapping.get('confidence', 'NOT_FOUND')
            stats[conf] = stats.get(conf, 0) + 1
        return stats

    def _identify_risks(self, mappings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify specific risks"""
        risks = []

        # Group questions by risk category
        for category, keywords in self.RISK_CATEGORIES.items():
            category_questions = []

            for mapping in mappings:
                question_lower = mapping['question'].lower()
                if any(kw in question_lower for kw in keywords):
                    category_questions.append(mapping)

            if not category_questions:
                continue

            # Assess category risk
            low_conf_count = sum(1 for m in category_questions
                                if m['confidence'] in ['LOW', 'NOT_FOUND'])

            if low_conf_count > len(category_questions) * 0.5:
                severity = 'HIGH' if low_conf_count > len(category_questions) * 0.7 else 'MEDIUM'

                risks.append({
                    "category": category.replace('_', ' ').title(),
                    "severity": severity,
                    "description": f"Insufficient evidence for {low_conf_count}/{len(category_questions)} {category.replace('_', ' ')} controls",
                    "affected_questions": [m['question_id'] for m in category_questions if m['confidence'] in ['LOW', 'NOT_FOUND']],
                    "gaps": list(set([gap for m in category_questions for gap in m.get('gaps', [])]))
                })

        # Sort by severity
        severity_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
        risks.sort(key=lambda x: severity_order.get(x['severity'], 3))

        return risks

    def _generate_recommendations(
        self,
        risks: List[Dict[str, Any]],
        mappings: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate prioritized recommendations"""
        recommendations = []

        # Recommendations for high-severity risks
        for risk in risks:
            if risk['severity'] == 'HIGH':
                recommendations.append({
                    "priority": "Critical",
                    "category": risk['category'],
                    "action": f"Request additional documentation for {risk['category']} controls",
                    "rationale": risk['description'],
                    "questions_to_followup": risk['affected_questions'][:5]
                })

        # General recommendations based on confidence levels
        not_found_questions = [m for m in mappings if m['confidence'] == 'NOT_FOUND']
        if len(not_found_questions) > 5:
            recommendations.append({
                "priority": "High",
                "category": "Documentation",
                "action": "Request comprehensive security documentation package",
                "rationale": f"{len(not_found_questions)} questions have no supporting evidence",
                "questions_to_followup": [m['question_id'] for m in not_found_questions[:10]]
            })

        # Recommendations for contradictions
        # (This would require more sophisticated analysis)

        return recommendations

    def _calculate_risk_score(self, mappings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall risk score"""
        total = len(mappings)
        if total == 0:
            return {"score": 0, "level": "UNKNOWN"}

        # Scoring: HIGH=3, MEDIUM=2, LOW=1, NOT_FOUND=0
        score_map = {'HIGH': 3, 'MEDIUM': 2, 'LOW': 1, 'NOT_FOUND': 0}
        total_score = sum(score_map.get(m.get('confidence', 'NOT_FOUND'), 0) for m in mappings)
        normalized_score = (total_score / (total * 3)) * 100  # 0-100 scale

        # Determine risk level
        if normalized_score >= 70:
            level = "LOW RISK"
        elif normalized_score >= 50:
            level = "MEDIUM RISK"
        elif normalized_score >= 30:
            level = "HIGH RISK"
        else:
            level = "CRITICAL RISK"

        return {
            "score": round(normalized_score, 1),
            "level": level
        }

    def _generate_threat_model(self, mappings: List[Dict[str, Any]], risks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate STRIDE-based threat model"""

        threat_model = {
            "framework": "STRIDE",
            "threats": [],
            "attack_surfaces": [],
            "mitigations_needed": []
        }

        # Map risk categories to STRIDE
        stride_mapping = {
            'Data Protection': 'Information Disclosure',
            'Access Control': 'Elevation of Privilege',
            'Monitoring': 'Repudiation',
            'Incident Response': 'Denial of Service',
            'Compliance': 'Tampering',
            'Vulnerability Management': 'Spoofing',
            'Vendor Management': 'Elevation of Privilege'
        }

        # Generate threats from identified risks
        for risk in risks:
            stride_category = stride_mapping.get(risk['category'], 'Information Disclosure')

            threat_model['threats'].append({
                'category': stride_category,
                'severity': risk['severity'],
                'description': risk['description'],
                'affected_questions': len(risk.get('affected_questions', [])),
                'evidence_gaps': risk.get('gaps', [])[:3],
                'potential_impact': self._get_threat_impact(stride_category, risk['severity'])
            })

        # Add historical incidents as threats if found
        incidents = self.web_search_results.get('incidents', [])
        for incident in incidents[:5]:  # Limit to 5 most relevant
            threat_model['threats'].append({
                'category': 'Historical Incident',
                'severity': 'HIGH',
                'description': f"Past security incident: {incident.get('title', 'Unknown incident')}",
                'affected_questions': 0,
                'evidence_gaps': [],
                'potential_impact': 'Historical breach indicates potential vulnerabilities in security posture'
            })

        # Generate attack surfaces based on vendor metadata
        if self.vendor_metadata:
            attack_surfaces = self._analyze_attack_surfaces()
            threat_model['attack_surfaces'] = attack_surfaces

        # Generate mitigations
        for threat in threat_model['threats']:
            if threat['severity'] in ['HIGH', 'CRITICAL']:
                threat_model['mitigations_needed'].append({
                    'threat_category': threat['category'],
                    'priority': 'Critical' if threat['severity'] == 'HIGH' else 'High',
                    'action': f"Address {threat['category']} risks",
                    'specific_controls': self._suggest_controls(threat['category'])
                })

        return threat_model

    def _get_threat_impact(self, stride_category: str, severity: str) -> str:
        """Get potential impact description for threat"""
        impacts = {
            'Spoofing': 'Unauthorized access through identity impersonation',
            'Tampering': 'Unauthorized modification of data or configurations',
            'Repudiation': 'Inability to prove actions occurred or track accountability',
            'Information Disclosure': 'Unauthorized access to sensitive data',
            'Denial of Service': 'Service disruption affecting availability',
            'Elevation of Privilege': 'Unauthorized access to elevated permissions',
            'Historical Incident': 'Repeated security failures based on past incidents'
        }

        base_impact = impacts.get(stride_category, 'Potential security impact')

        if severity == 'HIGH':
            return f"{base_impact} - Critical impact to business operations"
        elif severity == 'MEDIUM':
            return f"{base_impact} - Moderate impact requiring attention"
        else:
            return f"{base_impact} - Low impact but requires monitoring"

    def _suggest_controls(self, threat_category: str) -> List[str]:
        """Suggest specific controls for threat category"""
        controls = {
            'Spoofing': ['Multi-factor authentication', 'Strong password policies', 'Identity verification'],
            'Tampering': ['Data integrity checks', 'Code signing', 'Change management'],
            'Repudiation': ['Comprehensive audit logging', 'Digital signatures', 'Time stamping'],
            'Information Disclosure': ['Encryption at rest and in transit', 'Access controls', 'Data classification'],
            'Denial of Service': ['Rate limiting', 'DDoS protection', 'Redundancy and failover'],
            'Elevation of Privilege': ['Least privilege access', 'Role-based access control', 'Regular access reviews'],
            'Historical Incident': ['Incident response plan review', 'Security control validation', 'Third-party audit']
        }

        return controls.get(threat_category, ['General security hardening', 'Regular security assessments'])

    def _analyze_attack_surfaces(self) -> List[Dict[str, Any]]:
        """Analyze attack surfaces based on vendor metadata"""
        surfaces = []

        # Data storage attack surface
        if self.vendor_metadata.get('data_stored'):
            data_types = self.vendor_metadata['data_stored']
            exposure = 'HIGH' if any(term in data_types.lower() for term in ['pii', 'credential', 'password', 'secret']) else 'MEDIUM'

            surfaces.append({
                'surface': 'Data Storage',
                'description': f"Vendor stores: {data_types[:100]}...",
                'exposure_level': exposure
            })

        # System integration attack surface
        if self.vendor_metadata.get('integrations'):
            integrations = self.vendor_metadata['integrations']
            exposure = 'HIGH' if any(term in integrations.lower() for term in ['production', 'database', 'api']) else 'MEDIUM'

            surfaces.append({
                'surface': 'System Integration',
                'description': f"Integration points: {integrations[:100]}...",
                'exposure_level': exposure
            })

        # Service access attack surface
        if self.vendor_metadata.get('services'):
            services = self.vendor_metadata['services']
            surfaces.append({
                'surface': 'Service Access',
                'description': f"Services provided: {services[:100]}...",
                'exposure_level': 'MEDIUM'
            })

        return surfaces

    def to_json(self, output_path: str = "risk_assessment.json"):
        """Save risk assessment to JSON"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.risk_assessment, f, indent=2, ensure_ascii=False)
        return output_path

    def to_markdown(self, output_path: str = "risk_assessment_report.md") -> str:
        """Generate enhanced markdown report with vendor context and threat modeling"""
        md = f"""# Vendor Risk Assessment Report

## 1. Vendor Overview

"""
        # Add vendor metadata if available
        if self.vendor_metadata:
            vendor_name = self.vendor_metadata.get('vendor_name', 'Not provided')
            md += f"**Vendor Name:** {vendor_name}\n\n"

            if self.vendor_metadata.get('services'):
                md += f"**Services Provided:**\n{self.vendor_metadata['services']}\n\n"
            else:
                md += "**Services Provided:** Not provided\n\n"

        md += "---\n\n## 2. Data in Scope\n\n"

        if self.vendor_metadata:
            if self.vendor_metadata.get('data_stored'):
                md += f"**Data Stored by Vendor:**\n{self.vendor_metadata['data_stored']}\n\n"
            else:
                md += "**Data Stored:** Not provided\n\n"

            if self.vendor_metadata.get('integrations'):
                md += f"**System Integrations:**\n{self.vendor_metadata['integrations']}\n\n"
            else:
                md += "**System Integrations:** Not provided\n\n"

        md += "---\n\n## 3. Executive Summary\n\n"
        md += f"**Overall Risk Level:** {self.risk_assessment['overall_risk']}\n"
        md += f"**Risk Score:** {self.risk_assessment['risk_score']}/100\n"
        md += f"**Assessment Date:** {self._get_date()}\n\n"

        md += "### Assessment Highlights\n\n"
        md += f"- **Total Security Controls Assessed:** {self.risk_assessment['summary']['total_questions']}\n"
        md += f"- **High Confidence Evidence:** {self.risk_assessment['summary']['answered_high_confidence']} controls\n"
        md += f"- **Medium Confidence Evidence:** {self.risk_assessment['summary']['answered_medium_confidence']} controls\n"
        md += f"- **Insufficient Evidence:** {self.risk_assessment['summary']['answered_low_confidence'] + self.risk_assessment['summary']['insufficient_evidence']} controls\n"
        md += f"- **Critical Risks Identified:** {self.risk_assessment['summary']['critical_risks']}\n"
        md += f"- **Public Security Incidents Found:** {self.risk_assessment.get('public_incidents_found', 0)}\n\n"

        # Add public incidents section
        md += "---\n\n## 4. Public Security Incidents\n\n"

        incidents = self.web_search_results.get('incidents', [])
        if incidents:
            md += f"**{len(incidents)} security incident(s) identified from public sources:**\n\n"
            for idx, incident in enumerate(incidents[:5], 1):
                md += f"### Incident {idx}: {incident.get('title', 'Unknown')}\n\n"
                md += f"**Year:** {incident.get('year', 'Unknown')}\n"
                md += f"**Description:** {incident.get('snippet', 'No details available')}\n"
                md += f"**Source:** {incident.get('url', 'N/A')}\n\n"
        else:
            md += "✅ **No public security incidents identified in recent searches.**\n\n"
            md += "Note: This does not guarantee absence of incidents. Limited to publicly available information.\n\n"

        md += "---\n\n## 5. Key Risks\n\n"

        # Add risks
        for idx, risk in enumerate(self.risk_assessment['risks'], 1):
            md += f"### Risk {idx}: {risk['severity']} - {risk['category']}\n\n"
            md += f"**Description:** {risk['description']}\n\n"
            if risk.get('gaps'):
                md += "**Evidence Gaps:**\n"
                for gap in risk['gaps'][:5]:
                    md += f"- {gap}\n"
            md += "\n"

        md += "---\n\n## 6. Threat Modeling\n\n"

        threat_model = self.risk_assessment.get('threat_model', {})

        if threat_model:
            md += f"**Framework:** {threat_model.get('framework', 'STRIDE')}\n\n"

            # Attack surfaces
            attack_surfaces = threat_model.get('attack_surfaces', [])
            if attack_surfaces:
                md += "### Attack Surfaces\n\n"
                for surface in attack_surfaces:
                    exposure_emoji = {'HIGH': '🔴', 'MEDIUM': '🟡', 'LOW': '🟢'}.get(surface['exposure_level'], '⚪')
                    md += f"#### {exposure_emoji} {surface['surface']} (Exposure: {surface['exposure_level']})\n\n"
                    md += f"{surface['description']}\n\n"

            # STRIDE threats
            threats = threat_model.get('threats', [])
            if threats:
                md += "### STRIDE Threat Analysis\n\n"

                # Group by STRIDE category
                stride_categories = {}
                for threat in threats:
                    category = threat['category']
                    if category not in stride_categories:
                        stride_categories[category] = []
                    stride_categories[category].append(threat)

                for category, category_threats in stride_categories.items():
                    md += f"#### {category}\n\n"
                    for threat in category_threats:
                        severity_emoji = {'HIGH': '🔴', 'MEDIUM': '🟡', 'LOW': '🟢'}.get(threat['severity'], '⚪')
                        md += f"- {severity_emoji} **{threat['severity']}:** {threat['description']}\n"
                        md += f"  - **Impact:** {threat['potential_impact']}\n"
                        if threat.get('evidence_gaps'):
                            md += f"  - **Gaps:** {', '.join(threat['evidence_gaps'][:2])}\n"
                    md += "\n"

            # Mitigations
            mitigations = threat_model.get('mitigations_needed', [])
            if mitigations:
                md += "### Recommended Mitigations\n\n"
                for idx, mitigation in enumerate(mitigations[:10], 1):
                    md += f"{idx}. **[{mitigation['priority']}] {mitigation['action']}**\n"
                    md += f"   - Threat: {mitigation['threat_category']}\n"
                    if mitigation.get('specific_controls'):
                        md += f"   - Controls: {', '.join(mitigation['specific_controls'][:3])}\n"
                    md += "\n"

        md += "---\n\n## 7. Recommendations\n\n"

        for idx, rec in enumerate(self.risk_assessment['recommendations'], 1):
            md += f"### {idx}. [{rec['priority']}] {rec['action']}\n\n"
            md += f"**Category:** {rec['category']}  \n"
            md += f"**Rationale:** {rec['rationale']}\n\n"
            if rec.get('questions_to_followup'):
                md += f"**Questions to Follow-up:** {', '.join(rec['questions_to_followup'][:5])}\n\n"

        md += "---\n\n## 8. Confidence Distribution\n\n"
        md += "| Confidence Level | Count | Percentage |\n"
        md += "|-----------------|-------|------------|\n"

        total = self.risk_assessment['summary']['total_questions']
        for level, count in self.risk_assessment['confidence_distribution'].items():
            percentage = (count / total * 100) if total > 0 else 0
            md += f"| {level} | {count} | {percentage:.1f}% |\n"

        md += "\n---\n\n## 9. Appendix: Sources\n\n"

        md += "### Document Evidence\n"
        md += "Evidence extracted from uploaded vendor documentation.\n\n"

        # Web sources
        controls = self.web_search_results.get('controls', [])
        if controls:
            md += "### Public Sources\n"
            md += "The following public sources were consulted:\n\n"
            for idx, control in enumerate(controls[:10], 1):
                md += f"{idx}. [{control.get('title', 'Unknown')}]({control.get('url', '#')})\n"
            md += "\n"

        md += "---\n\n"
        md += "*This report was automatically generated by the Vendor Security Assessment Tool*  \n"
        md += f"*Report includes threat modeling based on STRIDE framework and vendor context analysis*\n"

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md)

        return output_path

    def _get_date(self):
        """Get current date"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d")
