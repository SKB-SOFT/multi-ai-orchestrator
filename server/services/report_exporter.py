"""Report export utilities for multiple formats.

Generates downloadable research matrices in CSV, JSON, and PDF formats.
"""

import json
from pathlib import Path
from typing import Dict, BinaryIO
import pandas as pd
from datetime import datetime


class ReportExporter:
    """Export research matrices in multiple downloadable formats."""
    
    def __init__(self, reports_dir: str = "data/research_reports"):
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def export_as_json(self, matrix: Dict, threshold: int) -> bytes:
        """Export matrix as JSON bytes."""
        return json.dumps(matrix, indent=2).encode('utf-8')
    
    def export_as_csv(self, matrix: Dict, threshold: int) -> bytes:
        """Export matrix as CSV bytes (flattened structure)."""
        # Flatten nested dictionary
        flat_data = self._flatten_dict(matrix)
        df = pd.DataFrame([flat_data])
        
        return df.to_csv(index=False).encode('utf-8')
    
    def export_as_tsv(self, matrix: Dict, threshold: int) -> bytes:
        """Export matrix as TSV bytes (tab-separated)."""
        flat_data = self._flatten_dict(matrix)
        df = pd.DataFrame([flat_data])
        
        return df.to_csv(index=False, sep='\t').encode('utf-8')
    
    def export_as_pdf_report(self, matrix: Dict, threshold: int) -> bytes:
        """Export matrix as formatted PDF report.
        
        Uses reportlab for PDF generation with formatting.
        """
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            
            # Create PDF
            pdf_buffer = BinaryIO
            doc = SimpleDocTemplate(
                filename=None,  # Will write to buffer
                pagesize=letter,
                rightMargin=0.5*inch,
                leftMargin=0.5*inch,
                topMargin=0.75*inch,
                bottomMargin=0.75*inch,
            )
            
            # Build content
            content = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1f4788'),
                spaceAfter=30,
                alignment=1  # Center
            )
            content.append(Paragraph("🌍 World Brain Research Report", title_style))
            content.append(Spacer(1, 0.3*inch))
            
            # Metadata
            metadata = matrix.get("metadata", {})
            meta_text = f"""
            <b>Data Collection Phase:</b> {metadata.get('data_collection_phase', 'Unknown')}<br/>
            <b>Total Queries Collected:</b> {metadata.get('total_queries', 0)}<br/>
            <b>Report Generated:</b> {metadata.get('generated_at', 'Unknown')}<br/>
            <b>Distribution:</b> Open-source community contributions
            """
            content.append(Paragraph(meta_text, styles['Normal']))
            content.append(Spacer(1, 0.3*inch))
            
            # Statistics section
            content.append(Paragraph("Research Statistics", styles['Heading2']))
            stats_data = [
                ["Metric", "Value"],
                ["Success Rate", f"{matrix.get('statistics', {}).get('success_rate', 0)}%"],
                ["Average Confidence Score", str(matrix.get('statistics', {}).get('avg_confidence', 0))],
                ["Average Response Time", f"{matrix.get('statistics', {}).get('avg_response_time_ms', 0)}ms"],
            ]
            
            table = Table(stats_data, colWidths=[3*inch, 2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            content.append(table)
            content.append(Spacer(1, 0.3*inch))
            
            # Quality metrics
            content.append(Paragraph("Quality Analysis", styles['Heading2']))
            quality = matrix.get('quality_analysis', {})
            quality_text = f"""
            <b>Minimum Confidence:</b> {quality.get('min_confidence', 0)}<br/>
            <b>Maximum Confidence:</b> {quality.get('max_confidence', 0)}<br/>
            <b>Confidence Variation (Std Dev):</b> {quality.get('confidence_std_dev', 0)}<br/>
            <b>User Feedback Submitted:</b> {quality.get('queries_with_feedback', 0)} queries
            """
            content.append(Paragraph(quality_text, styles['Normal']))
            content.append(Spacer(1, 0.3*inch))
            
            # Data diversity (emphasis on diversity, not user count)
            content.append(Paragraph("Data Diversity & Coverage", styles['Heading2']))
            diversity = matrix.get('data_diversity', {})
            diversity_text = f"""
            <b>Unique Queries:</b> {diversity.get('unique_queries', 0)}<br/>
            <b>Query Length Range:</b> {diversity.get('query_length_range', [0, 0])[0]} - {diversity.get('query_length_range', [0, 0])[1]} characters<br/>
            <b>Query Complexity Variation:</b> Diverse community contributions from multiple domains
            """
            content.append(Paragraph(diversity_text, styles['Normal']))
            content.append(Spacer(1, 0.3*inch))
            
            # Provider performance
            content.append(Paragraph("AI Provider Performance", styles['Heading2']))
            providers = matrix.get('provider_performance', {})
            provider_data = [["Provider", "Usage Count", "Success Rate", "Avg Confidence"]]
            for provider, stats in sorted(providers.items(), 
                                         key=lambda x: x[1].get('times_used', 0), 
                                         reverse=True):
                provider_data.append([
                    provider,
                    str(stats.get('times_used', 0)),
                    f"{stats.get('success_rate', 0)}%",
                    str(stats.get('avg_confidence', 0))
                ])
            
            if len(provider_data) > 1:
                provider_table = Table(provider_data, colWidths=[1.5*inch, 1.2*inch, 1.2*inch, 1.2*inch])
                provider_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                content.append(provider_table)
            
            content.append(Spacer(1, 0.3*inch))
            
            # Brain strength metrics
            content.append(Paragraph("System Performance Metrics", styles['Heading2']))
            brain = matrix.get('brain_metrics', {})
            brain_text = f"""
            <b>Average Brain Strength:</b> {brain.get('avg_brain_strength', 0)}<br/>
            <b>Peak Brain Strength:</b> {brain.get('max_brain_strength', 0)}<br/>
            <b>Growth Trend:</b> {brain.get('brain_strength_growth', 0)}%
            """
            content.append(Paragraph(brain_text, styles['Normal']))
            content.append(Spacer(1, 0.5*inch))
            
            # Footer
            footer_text = """
            <i>This report represents research data collected from an open-source community platform.
            All data is anonymized and aggregated. No individual user information is tracked or reported.</i>
            """
            content.append(Paragraph(footer_text, styles['Normal']))
            
            # Build PDF (to bytes)
            from io import BytesIO
            pdf_buffer = BytesIO()
            doc.filename = pdf_buffer
            doc.build(content)
            pdf_bytes = pdf_buffer.getvalue()
            pdf_buffer.close()
            
            return pdf_bytes
            
        except ImportError:
            # Fallback: return JSON if reportlab not available
            return json.dumps(matrix, indent=2).encode('utf-8')
    
    def _flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '_') -> Dict:
        """Flatten nested dictionary."""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                items.append((new_key, str(v)))
            else:
                items.append((new_key, v))
        return dict(items)
    
    def save_export(self, matrix: Dict, threshold: int, format: str = 'all') -> Dict:
        """Save reports in specified format(s).
        
        Args:
            matrix: Research matrix dictionary
            threshold: Query threshold for filename
            format: 'json', 'csv', 'tsv', 'pdf', or 'all'
        
        Returns:
            Dictionary with file paths of exported reports
        """
        exports = {}
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        if format in ['json', 'all']:
            filename = f"research_matrix_{threshold}_queries_{timestamp}.json"
            filepath = self.reports_dir / filename
            filepath.write_bytes(self.export_as_json(matrix, threshold))
            exports['json'] = str(filepath)
        
        if format in ['csv', 'all']:
            filename = f"research_matrix_{threshold}_queries_{timestamp}.csv"
            filepath = self.reports_dir / filename
            filepath.write_bytes(self.export_as_csv(matrix, threshold))
            exports['csv'] = str(filepath)
        
        if format in ['tsv', 'all']:
            filename = f"research_matrix_{threshold}_queries_{timestamp}.tsv"
            filepath = self.reports_dir / filename
            filepath.write_bytes(self.export_as_tsv(matrix, threshold))
            exports['tsv'] = str(filepath)
        
        if format in ['pdf', 'all']:
            filename = f"research_report_{threshold}_queries_{timestamp}.pdf"
            filepath = self.reports_dir / filename
            filepath.write_bytes(self.export_as_pdf_report(matrix, threshold))
            exports['pdf'] = str(filepath)
        
        return exports
