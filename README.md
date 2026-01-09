Super-Market Data Analysis – Report Creator

A simple web-based tool to upload supermarket sales data in CSV format
and generate a professional PDF report.


FEATURES
--------
- CSV file upload
- Data validation using predefined rules
- PDF report generation
- Clean and user-friendly interface


CSV FILE RULES
--------------
Your uploaded file must follow these rules:

- File format must be .csv only
- No special symbols allowed:
  $  ₹  &  :  ;
- Exactly 7 columns required
- Unlimited rows supported


REQUIRED COLUMNS (ORDER MATTERS)
--------------------------------
1. customer_id
2. cashier_id (allowed values: 1 to 6)
3. product_type (Food, Grocery, Fashion, Electronics, etc.)
4. time (24-hour format HH:MM)
5. day (Sunday to Saturday)
6. price (numbers only)
7. payment_type (UPI / CARD / CASH)


SAMPLE CSV FORMAT
-----------------
customer_id,cashier_id,product_type,time,day,price,payment_type
C001,1,Food,14:30,Monday,250,CASH
C002,3,Fashion,18:45,Wednesday,1200,CARD
C003,2,Grocery,09:15,Sunday,540,UPI
C004,5,Electronics,20:10,Friday,3500,CARD


TECH STACK
----------
- HTML5
- CSS3
- Django (Backend)
- Python (Data Processing & PDF Generation)


HOW IT WORKS
------------
1. Upload a valid CSV file
2. System validates the file structure
3. Data is analyzed
4. Download the generated PDF report


BEST PRACTICES
--------------
- Keep data clean and consistent
- Follow column order strictly
- Use valid cashier IDs and payment types


AUTHOR
------
Built for learning, data analysis, and real-world project practice.
