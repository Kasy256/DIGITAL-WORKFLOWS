# 🧾 EReceipt Backend API

A Flask-based REST API for digital receipt generation with JWT authentication, MongoDB storage, and free Email/SMS delivery.

## 🚀 Features

- **JWT Authentication** - Secure token-based auth with refresh tokens
- **MongoDB Database** - Persistent storage for users and receipts
- **Email Notifications** - Send receipts via Gmail SMTP (free)
- **SMS Notifications** - Send receipts via Twilio/Vonage/TextBelt (free tiers)
- **Receipt Management** - Full CRUD operations for receipts
- **Statistics** - Track total receipts, revenue, and delivery status

## 📁 Project Structure

```
backend/
├── app/
│   ├── __init__.py          # App factory & extensions
│   ├── config.py             # Configuration classes
│   ├── models/
│   │   ├── user.py           # User model
│   │   └── receipt.py        # Receipt model
│   ├── routes/
│   │   ├── auth.py           # Authentication endpoints
│   │   ├── receipts.py       # Receipt CRUD endpoints
│   │   └── notifications.py  # Email/SMS endpoints
│   └── services/
│       ├── email_service.py  # Email sending service
│       └── sms_service.py    # SMS sending service
├── requirements.txt
├── run.py                    # Entry point
└── env_example.txt           # Environment variables template
```

## 🛠️ Setup Instructions

### 1. Prerequisites

- Python 3.8+
- MongoDB (local or Atlas)
- pip

### 2. Install MongoDB

**Option A: Local MongoDB**
```bash
# Windows (using Chocolatey)
choco install mongodb

# macOS
brew tap mongodb/brew
brew install mongodb-community

# Start MongoDB
mongod
```

**Option B: MongoDB Atlas (Cloud - Free Tier)**
1. Go to https://www.mongodb.com/atlas
2. Create free cluster
3. Get connection string

### 3. Create Virtual Environment

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Copy `env_example.txt` to `.env` and fill in your values:

```bash
# Windows
copy env_example.txt .env

# macOS/Linux
cp env_example.txt .env
```

Edit `.env` with your credentials.

### 6. Run the Server

```bash
python run.py
```

Server will start at `http://localhost:5000`

## 📧 Email Setup (Gmail - Free)

1. **Enable 2-Factor Auth** on your Google Account
2. Go to: Google Account → Security → App Passwords
3. Generate new app password for "Mail"
4. Use this password in `MAIL_PASSWORD`

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-16-char-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

## 📱 SMS Setup (Free Options)

### Option 1: Twilio (Recommended - $15 Free Credit)
1. Sign up at https://www.twilio.com/try-twilio
2. Get your Account SID, Auth Token
3. Get a free phone number

```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_NUMBER=+1234567890
```

### Option 2: Vonage (€2 Free Credit)
1. Sign up at https://dashboard.nexmo.com/sign-up
2. Get API Key and Secret

```env
VONAGE_API_KEY=your-api-key
VONAGE_API_SECRET=your-api-secret
VONAGE_PHONE_NUMBER=EReceipt
```

### Option 3: TextBelt (1 Free SMS/Day - Testing Only)
No setup needed! It's the fallback option.

## 🔌 API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login & get tokens |
| POST | `/api/auth/refresh` | Refresh access token |
| GET | `/api/auth/profile` | Get user profile |
| PUT | `/api/auth/profile` | Update profile |
| POST | `/api/auth/change-password` | Change password |

### Receipts

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/receipts` | Create receipt |
| GET | `/api/receipts` | List receipts (paginated) |
| GET | `/api/receipts/<id>` | Get single receipt |
| PUT | `/api/receipts/<id>` | Update receipt |
| DELETE | `/api/receipts/<id>` | Delete receipt |
| GET | `/api/receipts/stats` | Get statistics |

### Notifications

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/notifications/send-email/<id>` | Send receipt via email |
| POST | `/api/notifications/send-sms/<id>` | Send receipt via SMS |
| POST | `/api/notifications/send-both/<id>` | Send via email & SMS |
| POST | `/api/notifications/test-email` | Test email config |
| POST | `/api/notifications/test-sms` | Test SMS config |
| GET | `/api/notifications/config` | Check service status |

## 📝 Example API Requests

### Register User
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword",
    "business_name": "My Store"
  }'
```

### Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword"
  }'
```

### Create Receipt
```bash
curl -X POST http://localhost:5000/api/receipts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "customer_name": "John Doe",
    "customer_email": "john@example.com",
    "customer_phone": "+1234567890",
    "transaction_date": "2025-12-03",
    "items": [
      {"name": "Product A", "quantity": 2, "price": 29.99}
    ],
    "subtotal": 59.98,
    "tax_rate": 10,
    "tax": 5.99,
    "total": 65.97
  }'
```

### Send Receipt via Email
```bash
curl -X POST http://localhost:5000/api/notifications/send-email/RECEIPT_ID \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Send Receipt via SMS
```bash
curl -X POST http://localhost:5000/api/notifications/send-sms/RECEIPT_ID \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 🔒 Security Notes

1. Change `SECRET_KEY` and `JWT_SECRET_KEY` in production
2. Use HTTPS in production
3. Store sensitive data in environment variables
4. Use strong passwords (min 6 characters required)

## 🐛 Troubleshooting

### MongoDB Connection Error
- Ensure MongoDB is running: `mongod`
- Check `MONGO_URI` in `.env`

### Email Not Sending
- Verify Gmail app password (not your regular password)
- Check less secure apps settings
- Try with TLS enabled

### SMS Not Sending
- Verify Twilio credentials
- Check phone number format (+1234567890)
- TextBelt has 1 SMS/day limit on free tier

## 📄 License

MIT License - Free to use and modify.

