from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from io import BytesIO
from datetime import datetime
import pandas as pd

class DashboardPDFGenerator:
    """Generate PDF reports for dashboard analytics"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=12,
            spaceBefore=12
        )
    
    def generate_report(self, kpis, daily_metrics, forecast_summary, period_days=30):
        """
        Generate comprehensive PDF report
        
        Args:
            kpis: KPI data dictionary
            daily_metrics: List of daily metrics
            forecast_summary: Forecast data dictionary
            period_days: Number of days in the report
        
        Returns:
            BytesIO buffer containing PDF
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch)
        story = []
        
        # Title
        title = Paragraph("📊 AI Analytics Dashboard Report", self.title_style)
        story.append(title)
        
        # Report metadata
        meta_style = ParagraphStyle('meta', parent=self.styles['Normal'], fontSize=10, textColor=colors.grey)
        report_date = Paragraph(
            f"<b>Generated:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br/>"
            f"<b>Period:</b> Last {period_days} days",
            meta_style
        )
        story.append(report_date)
        story.append(Spacer(1, 0.3*inch))
        
        # KPI Summary Section
        story.append(Paragraph("Key Performance Indicators", self.heading_style))
        kpi_data = [
            ['Metric', 'Current Value', 'Change', 'Previous Value'],
            [
                'Total Revenue',
                f"${kpis['total_revenue']['value']:,.2f}",
                f"{kpis['total_revenue']['change_percent']:+.1f}%",
                f"${kpis['total_revenue']['previous_value']:,.2f}"
            ],
            [
                'Total Orders',
                f"{kpis['total_orders']['value']:,}",
                f"{kpis['total_orders']['change_percent']:+.1f}%",
                f"{kpis['total_orders']['previous_value']:,}"
            ],
            [
                'Active Customers',
                f"{kpis['active_customers']['value']:,}",
                f"{kpis['active_customers']['change_percent']:+.1f}%",
                f"{kpis['active_customers']['previous_value']:,}"
            ],
            [
                'Avg Order Value',
                f"${kpis['avg_order_value']['value']:.2f}",
                f"{kpis['avg_order_value']['change_percent']:+.1f}%",
                f"${kpis['avg_order_value']['previous_value']:.2f}"
            ],
            [
                'Churn Rate',
                f"{kpis['churn_rate']['value']:.2f}%",
                f"{kpis['churn_rate']['change_percent']:+.1f}%",
                f"{kpis['churn_rate']['previous_value']:.2f}%"
            ]
        ]
        
        kpi_table = Table(kpi_data, colWidths=[2*inch, 1.5*inch, 1*inch, 1.5*inch])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        story.append(kpi_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Recent Performance Section
        story.append(Paragraph("Recent Daily Performance (Last 7 Days)", self.heading_style))
        
        recent_data = daily_metrics[-7:]
        daily_table_data = [['Date', 'Revenue', 'Orders', 'Customers', 'Churn %']]
        
        for day in recent_data:
            daily_table_data.append([
                day['date'],
                f"${day['daily_revenue']:,.0f}",
                str(day['orders']),
                str(day['active_customers']),
                f"{day['churn_rate']:.2f}%"
            ])
        
        daily_table = Table(daily_table_data, colWidths=[1.2*inch, 1.3*inch, 1*inch, 1.2*inch, 1*inch])
        daily_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        story.append(daily_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Forecast Section
        if forecast_summary:
            story.append(Paragraph(
                f"30-Day Forecast Summary",
                self.heading_style
            ))
            
            forecast_data = [
                ['Metric', 'Forecasted Value'],
                ['Projected Revenue', f"${forecast_summary['total_revenue']:,.2f}"],
                ['Expected Orders', f"{forecast_summary['total_orders']:,}"],
                ['Avg Customers', f"{forecast_summary['avg_customers']:,}"],
                ['Avg Churn Rate', f"{forecast_summary['avg_churn_rate']:.2f}%"]
            ]
            
            forecast_table = Table(forecast_data, colWidths=[3*inch, 3*inch])
            forecast_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
            ]))
            story.append(forecast_table)
        
        # Footer
        story.append(Spacer(1, 0.5*inch))
        footer_style = ParagraphStyle('footer', parent=self.styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
        footer = Paragraph(
            "Generated by AI Analytics Dashboard • Powered by FastAPI & Prophet ML",
            footer_style
        )
        story.append(footer)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer

# Create global instance
pdf_generator = DashboardPDFGenerator()