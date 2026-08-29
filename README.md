# VulnShop Realistic Cybersecurity Lab

## Features
- E-commerce home page, catalog, categories, product details
- Cart and demo checkout
- Customer login and admin dashboard
- SQLite backend
- Security Lab page
- Intentional SQL injection, reflected XSS and file-inclusion-style vulnerabilities

## Run
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Open https://vulnshop-ecommerce-by-alok.onrender.com/

Demo accounts:
- Customer: student / labpass
- Admin: admin / admin123

## Important
This version is intentionally insecure and must be run only on localhost or an isolated VM. Never expose it to the public internet.

## Learning path
1. Map the application routes.
2. Identify vulnerable data flows.
3. Test the flaws only in this lab.
4. Patch them using parameterized queries, output encoding/safe templating, allowlists and proper authentication.
5. Retest.
