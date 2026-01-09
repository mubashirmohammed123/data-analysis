from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import os
from django.conf import settings

# NEW IMPORTS FOR PDF
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from datetime import datetime
from django.http import FileResponse

def home(request):
    return render(request, 'first_screen/home.html')

def upload_view(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get('csv_file_input')

        if uploaded_file:
            
            try:
                df = pd.read_csv(uploaded_file)
            except UnicodeDecodeError:
                uploaded_file.seek(0) 
                df = pd.read_csv(uploaded_file, encoding='latin-1')

            # ----- CREATE TIME PERIOD COLUMN -----
            def time_period(t):
                h = int(str(t).split(" ")[0])
                if 5 <= h <= 11:
                    return "Morning"
                elif 12 <= h <= 15:
                    return "Noon"
                elif 16 <= h <= 19:
                    return "Evening"
                else:
                    return "Night"

            df["time_period"] = df["time"].apply(time_period)

            # ----- FIX DAY AND TIME PERIOD ORDERING -----
            # Define correct day order
            day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            df["day"] = pd.Categorical(df["day"], categories=day_order, ordered=True)

            # Define correct time period order
            time_order = ["Morning", "Noon", "Evening", "Night"]
            df["time_period"] = pd.Categorical(df["time_period"], categories=time_order, ordered=True)

            # =========================
            #        GENERAL
            # =========================
            shape = df.shape
            price_describe = df["price"].describe()

            # print("=" * 60)
            # print("GENERAL INFORMATION")
            # print("=" * 60)
            # print("SHAPE:", shape)
            # print("\nPRICE DESCRIPTION:\n", price_describe)

            # =========================
            #        CASHIER
            # =========================
            cash_per_cashier = df.groupby("cashier_id")["price"].sum()
            cashier_max = cash_per_cashier.idxmax()

            # print("\n" + "=" * 60)
            # print("CASHIER ANALYSIS")
            # print("=" * 60)
            # print("\nCASH PER CASHIER:\n", cash_per_cashier)
            # print("\nMAX CASHIER:", cashier_max)

            # =========================
            #        TYPE
            # =========================
            price_per_type = df.groupby("type")["price"].sum()
            top3_types = price_per_type.sort_values(ascending=False).head(3)

            # print("\n" + "=" * 60)
            # print("PRODUCT TYPE ANALYSIS")
            # print("=" * 60)
            # print("\nPRICE PER TYPE:\n", price_per_type)
            # print("\nTOP 3 TYPES:\n", top3_types)

            # =========================
            #        TIME
            # =========================
            price_per_time = df.groupby("time_period")["price"].sum()
            max_time_period = price_per_time.idxmax()

            # print("\n" + "=" * 60)
            # print("TIME PERIOD ANALYSIS")
            # print("=" * 60)
            # print("\nPRICE PER TIME PERIOD:\n", price_per_time)
            # print("\nMAX TIME PERIOD:", max_time_period)

            # =========================
            #        DAY
            # =========================
            sales_per_day = df.groupby("day")["price"].sum()
            top3_days = sales_per_day.sort_values(ascending=False).head(3)

            # print("\n" + "=" * 60)
            # print("DAY ANALYSIS")
            # print("=" * 60)
            # print("\nSALES PER DAY:\n", sales_per_day)
            # print("\nTOP 3 DAYS:\n", top3_days)

            # =========================
            #        PAYMENT TYPE
            # =========================
            sales_per_payment = df.groupby("payment_type")["price"].sum()
            top_payment_method = sales_per_payment.idxmax()

            # print("\n" + "=" * 60)
            # print("PAYMENT METHOD ANALYSIS")
            # print("=" * 60)
            # print("\nSALES PER PAYMENT METHOD:\n", sales_per_payment)
            # print("\nTOP PAYMENT METHOD:", top_payment_method)

            # =========================
            #        PRICE STATS
            # =========================
            mean_price = df["price"].mean()
            median_price = df["price"].median()
            mode_price = df["price"].mode()

            # print("\n" + "=" * 60)
            # print("PRICE STATISTICS")
            # print("=" * 60)
            # print("\nMEAN PRICE:", mean_price)
            # print("MEDIAN PRICE:", median_price)
            # print("MODE PRICE:\n", mode_price)
            # print("=" * 60)

            # =========================
            #     CREATE CHARTS
            # =========================
            
            # Create media directory if it doesn't exist
            charts_dir = os.path.join(settings.MEDIA_ROOT, 'charts')
            os.makedirs(charts_dir, exist_ok=True)

            # 1. Sales by Cashier - Bar Chart
            plt.figure(figsize=(10, 6))
            cash_per_cashier.plot(kind='bar', color='steelblue')
            plt.title('Sales by Cashier', fontsize=16, fontweight='bold')
            plt.xlabel('Cashier ID', fontsize=12)
            plt.ylabel('Total Sales (₹)', fontsize=12)
            plt.xticks(rotation=0)
            plt.tight_layout()
            cashier_chart_path = os.path.join(charts_dir, 'cashier_sales.png')
            plt.savefig(cashier_chart_path)
            plt.close()

            # 2. Sales by Product Type - Bar Chart
            plt.figure(figsize=(12, 6))
            price_per_type.sort_values(ascending=False).plot(kind='bar', color='green')
            plt.title('Sales by Product Type', fontsize=16, fontweight='bold')
            plt.xlabel('Product Type', fontsize=12)
            plt.ylabel('Total Sales (₹)', fontsize=12)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            type_chart_path = os.path.join(charts_dir, 'product_type_sales.png')
            plt.savefig(type_chart_path)
            plt.close()

            # 3. Top 5 Product Types - Horizontal Bar Chart
            plt.figure(figsize=(10, 6))
            price_per_type.sort_values(ascending=True).tail(5).plot(kind='barh', color='coral')
            plt.title('Top 5 Product Types by Sales', fontsize=16, fontweight='bold')
            plt.xlabel('Total Sales (₹)', fontsize=12)
            plt.ylabel('Product Type', fontsize=12)
            plt.tight_layout()
            top5_chart_path = os.path.join(charts_dir, 'top5_product_types.png')
            plt.savefig(top5_chart_path)
            plt.close()

            # 4. Sales by Time Period - Pie Chart
            plt.figure(figsize=(10, 8))
            plt.pie(price_per_time, labels=price_per_time.index, autopct='%1.1f%%', 
                    startangle=90, colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A'])
            plt.title('Sales Distribution by Time Period', fontsize=16, fontweight='bold')
            plt.axis('equal')
            plt.tight_layout()
            time_pie_path = os.path.join(charts_dir, 'time_period_pie.png')
            plt.savefig(time_pie_path)
            plt.close()

            # 5. Sales by Day of Week - Bar Chart
            plt.figure(figsize=(12, 6))
            sales_per_day.plot(kind='bar', color='orange')
            plt.title('Sales by Day of Week', fontsize=16, fontweight='bold')
            plt.xlabel('Day', fontsize=12)
            plt.ylabel('Total Sales (₹)', fontsize=12)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            day_chart_path = os.path.join(charts_dir, 'day_sales.png')
            plt.savefig(day_chart_path)
            plt.close()

            # 6. Payment Method Distribution - Pie Chart
            plt.figure(figsize=(10, 8))
            plt.pie(sales_per_payment, labels=sales_per_payment.index, autopct='%1.1f%%',
                    startangle=90, colors=['#9B59B6', '#3498DB', '#E74C3C'])
            plt.title('Sales Distribution by Payment Method', fontsize=16, fontweight='bold')
            plt.axis('equal')
            plt.tight_layout()
            payment_pie_path = os.path.join(charts_dir, 'payment_method_pie.png')
            plt.savefig(payment_pie_path)
            plt.close()

            # 7. Cashier Performance - Pie Chart
            plt.figure(figsize=(10, 8))
            plt.pie(cash_per_cashier, labels=[f'Cashier {i}' for i in cash_per_cashier.index], 
                    autopct='%1.1f%%', startangle=90)
            plt.title('Cashier Sales Distribution', fontsize=16, fontweight='bold')
            plt.axis('equal')
            plt.tight_layout()
            cashier_pie_path = os.path.join(charts_dir, 'cashier_pie.png')
            plt.savefig(cashier_pie_path)
            plt.close()

            # 8. Combined Time Period and Payment Method
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

            # Time Period
            ax1.bar(price_per_time.index, price_per_time.values, color='teal')
            ax1.set_title('Sales by Time Period', fontsize=14, fontweight='bold')
            ax1.set_xlabel('Time Period', fontsize=11)
            ax1.set_ylabel('Total Sales (₹)', fontsize=11)
            ax1.tick_params(axis='x', rotation=0)

            # Payment Method
            ax2.bar(sales_per_payment.index, sales_per_payment.values, color='purple')
            ax2.set_title('Sales by Payment Method', fontsize=14, fontweight='bold')
            ax2.set_xlabel('Payment Method', fontsize=11)
            ax2.set_ylabel('Total Sales (₹)', fontsize=11)
            ax2.tick_params(axis='x', rotation=0)

            plt.tight_layout()
            combined_chart_path = os.path.join(charts_dir, 'combined_time_payment.png')
            plt.savefig(combined_chart_path)
            plt.close()

            # print("\n📊 ALL CHARTS GENERATED AND SAVED!")
            # print("=" * 60)

            # Store all variables in context dictionary
            context = {
                'shape': shape,
                'row_count': shape[0],
                'column_count': shape[1],
                'price_describe': price_describe.to_dict(),
                'cash_per_cashier': cash_per_cashier.to_dict(),
                'cashier_max': int(cashier_max),
                'price_per_type': price_per_type.to_dict(),
                'top3_types': top3_types.to_dict(),
                'price_per_time': price_per_time.to_dict(),
                'max_time_period': str(max_time_period),
                'sales_per_day': sales_per_day.to_dict(),
                'top3_days': top3_days.to_dict(),
                'sales_per_payment': sales_per_payment.to_dict(),
                'top_payment_method': top_payment_method,
                'mean_price': float(mean_price),
                'median_price': float(median_price),
                'mode_price': mode_price.tolist() if len(mode_price) > 0 else None,
                
                # Chart image paths (relative to MEDIA_URL)
                'cashier_chart': 'charts/cashier_sales.png',
                'type_chart': 'charts/product_type_sales.png',
                'top5_chart': 'charts/top5_product_types.png',
                'time_pie': 'charts/time_period_pie.png',
                'day_chart': 'charts/day_sales.png',
                'payment_pie': 'charts/payment_method_pie.png',
                'cashier_pie': 'charts/cashier_pie.png',
                'combined_chart': 'charts/combined_time_payment.png',
            }
            
            # print("\n✅ ALL VARIABLES STORED IN CONTEXT SUCCESSFULLY!")
            # print("=" * 60)
            
            request.session['analysis_data'] = context
            
            return render(request, 'first_screen/home.html', context)

    return render(request, 'first_screen/home.html')

def generate_pdf(request):
    """
    This function generates a PDF report with all analysis data and charts
    """
    
    # Check if we have the data in session (we'll store it there)
    context = request.session.get('analysis_data', None)
    
    if not context:
        return HttpResponse("No data available. Please upload a CSV first.", status=400)
    
    # Create a buffer to hold PDF data in memory
    buffer = BytesIO()
    
    # Create the PDF document
    # letter = page size (8.5 x 11 inches, standard US letter)
    doc = SimpleDocTemplate(buffer, pagesize=letter, 
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects (elements of the PDF)
    elements = []
    
    # Get pre-defined styles for text formatting
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2C3E50'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#3498DB'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # =========================
    # ADD TITLE
    # =========================
    title = Paragraph("Supermarket Sales Analysis Report", title_style)
    elements.append(title)
    
    # Add generation date
    date_text = Paragraph(f"<b>Generated on:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", 
                         styles['Normal'])
    elements.append(date_text)
    elements.append(Spacer(1, 20))  # Add 20 pixels of space
    
    # =========================
    # GENERAL INFORMATION
    # =========================
    elements.append(Paragraph("General Information", heading_style))
    
    general_data = [
        ['Metric', 'Value'],
        ['Total Rows', f"{context['row_count']:,}"],
        ['Total Columns', str(context['column_count'])],
        ['Mean Price', f"₹{context['mean_price']:,.2f}"],
        ['Median Price', f"₹{context['median_price']:,.2f}"],
    ]
    
    general_table = Table(general_data, colWidths=[3*inch, 3*inch])
    general_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(general_table)
    elements.append(Spacer(1, 20))
    
    # =========================
    # CASHIER ANALYSIS
    # =========================
    elements.append(Paragraph("Cashier Analysis", heading_style))
    
    cashier_data = [['Cashier ID', 'Total Sales']]
    for cashier_id, sales in context['cash_per_cashier'].items():
        cashier_data.append([f"Cashier {cashier_id}", f"₹{sales:,.2f}"])
    
    # Add best cashier info
    elements.append(Paragraph(f"<b>Best Performing Cashier:</b> Cashier {context['cashier_max']}", 
                             styles['Normal']))
    elements.append(Spacer(1, 10))
    
    cashier_table = Table(cashier_data, colWidths=[3*inch, 3*inch])
    cashier_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(cashier_table)
    elements.append(Spacer(1, 15))
    
    # Add cashier chart
    cashier_chart_path = os.path.join(settings.MEDIA_ROOT, 'charts', 'cashier_sales.png')
    if os.path.exists(cashier_chart_path):
        img = Image(cashier_chart_path, width=5*inch, height=3*inch)
        elements.append(img)
        elements.append(Spacer(1, 20))
    
    # =========================
    # PRODUCT TYPE ANALYSIS
    # =========================
    elements.append(PageBreak())  # Start new page
    elements.append(Paragraph("Product Type Analysis", heading_style))
    
    # Top 3 Types
    elements.append(Paragraph("<b>Top 3 Product Types:</b>", styles['Normal']))
    elements.append(Spacer(1, 10))
    
    top3_data = [['Product Type', 'Total Sales']]
    for product_type, sales in context['top3_types'].items():
        top3_data.append([product_type, f"₹{sales:,.2f}"])
    
    top3_table = Table(top3_data, colWidths=[3*inch, 3*inch])
    top3_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27AE60')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(top3_table)
    elements.append(Spacer(1, 20))
    
    # Add product type chart
    type_chart_path = os.path.join(settings.MEDIA_ROOT, 'charts', 'product_type_sales.png')
    if os.path.exists(type_chart_path):
        img = Image(type_chart_path, width=5.5*inch, height=3.3*inch)
        elements.append(img)
    
    # =========================
    # TIME PERIOD ANALYSIS
    # =========================
    elements.append(PageBreak())
    elements.append(Paragraph("Time Period Analysis", heading_style))
    
    elements.append(Paragraph(f"<b>Peak Sales Period:</b> {context['max_time_period']}", 
                             styles['Normal']))
    elements.append(Spacer(1, 10))
    
    time_data = [['Time Period', 'Total Sales']]
    for period, sales in context['price_per_time'].items():
        time_data.append([period, f"₹{sales:,.2f}"])
    
    time_table = Table(time_data, colWidths=[3*inch, 3*inch])
    time_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E74C3C')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.pink),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(time_table)
    elements.append(Spacer(1, 20))
    
    # Add time period pie chart
    time_pie_path = os.path.join(settings.MEDIA_ROOT, 'charts', 'time_period_pie.png')
    if os.path.exists(time_pie_path):
        img = Image(time_pie_path, width=4.5*inch, height=3.6*inch)
        elements.append(img)
    
    # =========================
    # DAY ANALYSIS
    # =========================
    elements.append(PageBreak())
    elements.append(Paragraph("Day of Week Analysis", heading_style))
    
    elements.append(Paragraph("<b>Top 3 Sales Days:</b>", styles['Normal']))
    elements.append(Spacer(1, 10))
    
    day_data = [['Day', 'Total Sales']]
    for day, sales in context['top3_days'].items():
        day_data.append([day, f"₹{sales:,.2f}"])
    
    day_table = Table(day_data, colWidths=[3*inch, 3*inch])
    day_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F39C12')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightyellow),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(day_table)
    elements.append(Spacer(1, 20))
    
    # Add day chart
    day_chart_path = os.path.join(settings.MEDIA_ROOT, 'charts', 'day_sales.png')
    if os.path.exists(day_chart_path):
        img = Image(day_chart_path, width=5.5*inch, height=3.3*inch)
        elements.append(img)
    
    # =========================
    # PAYMENT METHOD ANALYSIS
    # =========================
    elements.append(PageBreak())
    elements.append(Paragraph("Payment Method Analysis", heading_style))
    
    elements.append(Paragraph(f"<b>Most Used Payment Method:</b> {context['top_payment_method']}", 
                             styles['Normal']))
    elements.append(Spacer(1, 10))
    
    payment_data = [['Payment Method', 'Total Sales']]
    for method, sales in context['sales_per_payment'].items():
        payment_data.append([method, f"₹{sales:,.2f}"])
    
    payment_table = Table(payment_data, colWidths=[3*inch, 3*inch])
    payment_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9B59B6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lavender),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(payment_table)
    elements.append(Spacer(1, 20))
    
    # Add payment pie chart
    payment_pie_path = os.path.join(settings.MEDIA_ROOT, 'charts', 'payment_method_pie.png')
    if os.path.exists(payment_pie_path):
        img = Image(payment_pie_path, width=4.5*inch, height=3.6*inch)
        elements.append(img)
    
    # =========================
    # BUILD PDF
    # =========================
    doc.build(elements)
    
    # Get the PDF from buffer
    buffer.seek(0)
    
    # Return PDF as downloadable file
    response = FileResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="sales_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    
    return response