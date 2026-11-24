# OM SAI AGRO — Django E-commerce Starter

A beginner-friendly starter project for an agricultural product store with:
- Customer registration/login
- Seller registration/login
- Django admin login
- Product listing and product details
- Seller product management (seller sees/edits only their products)
- Simple cart and Cash on Delivery order placement
- Basic order history

This is a learning/MVP starter, not a production-ready marketplace. It does not yet include online payments, shipping APIs, GST invoice generation, seller payouts, image storage service, or marketplace commission settlement.

## Requirements
- Python 3.11+ recommended
- VS Code
- Internet for installing packages

## Windows setup (PowerShell)
```powershell
cd om_sai_agro_project
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open:
- Store: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/

## First use
1. Create an admin user using `createsuperuser`.
2. Open `/admin/` and create a user, or register a seller through `/accounts/register/seller/`.
3. Seller login: `/accounts/login/`
4. Seller dashboard: `/seller/`
5. Add products from the seller dashboard.

## Important
- Set `DEBUG=False`, configure a strong `SECRET_KEY`, allowed hosts, HTTPS, backups and secure email before public deployment.
- Do not store real payment card details.
- Review privacy, refund, shipping, tax and seller policies with qualified professionals before selling.
