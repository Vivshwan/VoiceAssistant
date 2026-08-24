# 🛒 Voice Shopping Assistant

A powerful, voice-controlled shopping list manager with AI-powered smart suggestions, multi-language support, and a complete REST API.

![Voice Shopping Assistant](https://img.shields.io/badge/Version-1.0.0-blue)
![Django](https://img.shields.io/badge/Django-5.0-green)
![License](https://img.shields.io/badge/License-MIT-orange)

---

## 🌟 Features

### 🎤 Voice Input
- **Voice Command Recognition**: Add items using natural voice commands
- **NLP Processing**: Understands varied phrases like "I need milk" or "Add milk to my list"
- **Multilingual Support**: Supports multiple languages

### 💡 Smart Suggestions
- **Product Recommendations**: Based on shopping history
- **Seasonal Recommendations**: Suggests items in season
- **Substitutes**: Offers alternatives for products

### 📋 Shopping List Management
- **Add/Remove Items**: Voice-controlled CRUD operations
- **Auto-Categorization**: Automatically categorizes items (dairy, produce, etc.)
- **Quantity Management**: Specify quantities like "2 bottles of water"

### 🔍 Voice-Activated Search
- **Item Search**: Search by voice with brand, size, or price filters
- **Price Range Filtering**: "Find toothpaste under $5"

### 🎨 UI/UX
- **Minimalist Interface**: Clean, modern design
- **Visual Feedback**: Real-time item recognition and confirmations
- **Mobile Optimized**: Responsive design for all devices

### 🔗 API
- **REST API**: Complete API with JWT authentication
- **Third-party Integration**: Connect with mobile apps or external services

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip
- Virtual environment (recommended)

### Installation

```bash
# Clone the repository
git clone https://github.com/Vivshwan/VoiceCommanding.git
cd VoiceCommanding

# Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download textblob corpora
python -m textblob.download_corpora

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run the development server
python manage.py runserver