from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
from typing import Dict, Any
import os

class ReportGenerator:
    def __init__(self, report_dir: str = 'reports'):
        self.report_dir = report_dir
        os.makedirs(report_dir, exist_ok=True)

    def generate_pdf(self, scan_results: Dict[str, Any]) -> str:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.report_dir}/vulnscan_{scan_results['host']}_{timestamp}.pdf"

        doc = SimpleDocTemplate(filename, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )

        story.append(Paragraph("Security Vulnerability Assessment Report", title_style))
        story.append(Spacer(1, 0.2*inch))

        summary_data = [
            ['Target URL', scan_results['url']],
            ['Hostname', scan_results['host']],
            ['IP Address', scan_results['ip']],
            ['Scan Date', scan_results['timestamp']],
            ['Risk Score', f"{scan_results['risk_score']}/100"]
        ]

        summary_table = Table(summary_data, colWidths=[2*inch, 4*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))

        if scan_results['ports']:
            story.append(Paragraph("Open Ports", heading_style))

            port_data = [['Port', 'State', 'Service', 'Version']]
            for port in scan_results['ports']:
                port_data.append([
                    str(port['port']),
                    port['state'],
                    port['service'],
                    f"{port.get('product', '')} {port.get('version', '')}".strip()
                ])

            port_table = Table(port_data, colWidths=[1*inch, 1*inch, 1.5*inch, 2.5*inch])
            port_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecf0f1')]),
            ]))

            story.append(port_table)
            story.append(Spacer(1, 0.2*inch))

        if scan_results['security_headers']:
            story.append(Paragraph("Security Headers", heading_style))

            header_data = [['Header', 'Status']]
            for header, value in scan_results['security_headers'].items():
                status = value if value == 'Missing' else 'Present'
                header_data.append([header, status])

            header_table = Table(header_data, colWidths=[3.5*inch, 2.5*inch])
            header_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ecc71')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecf0f1')]),
            ]))

            story.append(header_table)
            story.append(Spacer(1, 0.2*inch))

        if scan_results['ssl_info'] and 'error' not in scan_results['ssl_info']:
            story.append(Paragraph("SSL/TLS Information", heading_style))

            ssl_data = []
            for key, value in scan_results['ssl_info'].items():
                if key != 'cipher':
                    ssl_data.append([key.replace('_', ' ').title(), str(value)])

            if ssl_data:
                ssl_table = Table(ssl_data, colWidths=[2*inch, 4*inch])
                ssl_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#9b59b6')),
                    ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ]))

                story.append(ssl_table)
                story.append(Spacer(1, 0.2*inch))

        if scan_results['vulnerabilities']:
            story.append(Paragraph("Identified Vulnerabilities", heading_style))

            vuln_data = [['Severity', 'Type', 'Description', 'Recommendation']]
            for vuln in scan_results['vulnerabilities']:
                vuln_data.append([
                    vuln['severity'],
                    vuln['type'],
                    vuln['description'],
                    vuln['recommendation']
                ])

            vuln_table = Table(vuln_data, colWidths=[0.8*inch, 1.5*inch, 2*inch, 1.7*inch])
            vuln_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fadbd8')]),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))

            story.append(vuln_table)
            story.append(Spacer(1, 0.3*inch))

        story.append(Paragraph("General Security Best Practices", heading_style))
        best_practices = [
            "1. Keep all software and dependencies up to date",
            "2. Implement strong authentication mechanisms",
            "3. Use HTTPS with valid SSL/TLS certificates",
            "4. Configure proper security headers",
            "5. Regularly monitor and audit security logs",
            "6. Implement rate limiting and DDoS protection",
            "7. Use a Web Application Firewall (WAF)",
            "8. Conduct regular security assessments",
            "9. Follow the principle of least privilege",
            "10. Implement proper input validation and sanitization"
        ]

        for practice in best_practices:
            story.append(Paragraph(practice, styles['Normal']))
            story.append(Spacer(1, 0.1*inch))

        story.append(Spacer(1, 0.3*inch))
        disclaimer = """
        <b>DISCLAIMER:</b> This report is generated for educational and defensive security purposes only.
        Vulnerability scanning should only be performed on systems you own or have explicit authorization to test.
        Unauthorized scanning may be illegal. The findings in this report are informational and should be
        verified by security professionals before taking action.
        """
        story.append(Paragraph(disclaimer, styles['Normal']))

        doc.build(story)
        return filename
