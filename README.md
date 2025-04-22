# TechStore - Electronics Store Management System

A comprehensive Django-based management system for electronics stores, featuring product management, inventory tracking, sales analytics, and user management.

## Features

- **Product Management**
  - Add, edit, and delete products
  - Categorize products by brand and category
  - Upload product images
  - Track stock levels
  - Set prices and discounts

- **Inventory Management**
  - Real-time stock tracking
  - Low stock alerts
  - Stock history
  - Inventory reports

- **Sales Management**
  - Process sales transactions
  - Track sales history
  - Generate invoices
  - Calculate profits

- **User Management**
  - Role-based access control
  - Staff accounts
  - Activity logging

- **Analytics & Reporting**
  - Sales reports
  - Inventory reports
  - Revenue analytics
  - Product performance metrics

## Technology Stack

- **Backend**: Django 5.2
- **Frontend**: Bootstrap 5
- **Database**: SQLite (default)
- **Additional Libraries**:
  - Pillow (for image processing)
  - Crispy Forms (for form rendering)
  - Widget Tweaks (for form customization)
  - Import/Export (for data management)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd techstore
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create necessary directories:
   ```bash
   mkdir static\images
   mkdir media\products
   ```

5. Apply database migrations:
   ```bash
   python manage.py migrate
   ```

6. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```bash
   python manage.py runserver
   ```

8. Visit http://127.0.0.1:8000/ in your browser

## Project Structure

```
techstore/
├── analytics/        # Analytics and reporting
├── inventory/        # Inventory management
├── media/           # User-uploaded files
│   └── products/    # Product images
├── products/        # Product management
├── reports/         # Report generation
├── sales/          # Sales management
├── static/         # Static files
│   └── images/     # Static images
├── templates/      # HTML templates
├── users/         # User management
└── techstore/     # Project settings
```

## Usage

1. **Admin Interface**
   - Access at `/admin/`
   - Manage all aspects of the system
   - Create/edit users, products, etc.

2. **Product Management**
   - Add products with images
   - Set prices and stock levels
   - Manage categories and brands

3. **Sales Processing**
   - Create new sales
   - Process payments
   - Generate receipts

4. **Inventory Control**
   - Track stock levels
   - Receive notifications for low stock
   - Update inventory

5. **Reports & Analytics**
   - View sales reports
   - Track inventory movement
   - Monitor business performance

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please email [shapon1408@gmail.com] or open an issue in the repository.

## Acknowledgments

- Bootstrap for the UI components
- Django community for the excellent framework
- All contributors who have helped with the project 