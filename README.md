# AGENTTA - Agents Enhancing Natural Task Technology Automation

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**AGENTTA** is an innovative multi-agent AI system designed to augment and automate digital workflows in legal practice management. Built on a philosophy of intelligent collaboration, AGENTTA employs specialized AI agents that work together to enhance productivity, streamline processes, and enable new possibilities.

## 🌟 Philosophy

At AGENTTA, we believe in a **whole-to-part approach** to technology. Before diving into technical details, we consider the broader implications and philosophical underpinnings of our work. By grounding our efforts in a thoughtful, human-centric perspective, we aim to build AI systems that are not only effective but also ethical and aligned with human values.

As a team with diverse backgrounds spanning the arts, finance, and technology, we bring a unique multidisciplinary lens to the challenges of AI development. We are product designers at heart, striving to craft elegant, intuitive solutions that empower users and push the boundaries of what's possible.

## 🤖 The Four Agents

AGENTTA is powered by four specialized AI agents, each with unique capabilities:

### 1. **La Secretaria** - Email Intelligence Agent
- Intelligent email triage and routing
- Priority assessment and urgency detection
- Action item extraction
- Email categorization
- Response requirement analysis

### 2. **El Calendista** - Deadline Management Agent
- Jurisdiction-specific deadline tracking
- Intelligent deadline extraction
- Calendar event management
- Reminder scheduling
- Conflict detection

### 3. **La Archivista** - Document Organization Agent
- Intelligent document classification
- Metadata extraction
- Smart filing and organization
- Full-text search capabilities
- Duplicate detection

### 4. **El Estratega** - Process Learning Agent
- Workflow pattern analysis
- Optimization opportunity detection
- Continuous learning from usage
- Strategic insights generation
- Performance metrics tracking

## 🏗️ Architecture

AGENTTA is built on a modern, scalable architecture:

```
┌─────────────────────────────────────────────────┐
│         Master Control Program (MCP)            │
│    Orchestrates agents & manages workflow       │
└─────────────────┬───────────────────────────────┘
                  │
        ┌─────────┴─────────┐
        │    Event Bus      │
        │  Pub/Sub System   │
        └─────────┬─────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
┌───▼───┐   ┌────▼────┐   ┌───▼───┐
│Agent 1│   │ Agent 2 │   │Agent 3│
└───────┘   └─────────┘   └───────┘
    │             │             │
    └─────────────┼─────────────┘
                  │
        ┌─────────▼─────────┐
        │ Shared Context    │
        │  State Manager    │
        └───────────────────┘
```

### Key Technologies

- **Language**: Python 3.11+
- **Web Framework**: FastAPI
- **Async Processing**: Celery with Redis
- **AI Integration**: Anthropic Claude API
- **Database**: PostgreSQL with SQLAlchemy
- **ORM**: SQLAlchemy + Alembic migrations
- **Testing**: pytest
- **Security**: Cryptography (zero-knowledge encryption)

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose
- PostgreSQL (or use Docker)
- Redis (or use Docker)
- Anthropic API key

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/agentta.git
cd agentta
```

2. **Create virtual environment**

```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment**

```bash
cp .env.example .env
# Edit .env and add your API keys and configuration
```

5. **Start infrastructure with Docker**

```bash
docker-compose up -d postgres redis
```

6. **Run database migrations**

```bash
alembic upgrade head
```

7. **Start the API server**

```bash
uvicorn src.api.main:app --reload
```

8. **Start Celery worker** (in another terminal)

```bash
celery -A src.api.tasks.celery_app worker --loglevel=info
```

The API will be available at `http://localhost:8000`

## 🐳 Docker Deployment

For a complete containerized deployment:

```bash
# Set your API keys in .env first
docker-compose up -d
```

This will start:
- PostgreSQL database
- Redis
- FastAPI application
- Celery worker
- Celery beat (scheduler)
- Flower (Celery monitoring UI at http://localhost:5555)

## 📚 API Documentation

Once the server is running, visit:

- **Interactive API docs**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc

### Example API Calls

**Process an email:**

```bash
curl -X POST "http://localhost:8000/events/email" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "client@example.com",
    "to": ["lawyer@firm.com"],
    "subject": "Contract Review Needed",
    "body": "Please review the attached contract by Friday."
  }'
```

**Upload a document:**

```bash
curl -X POST "http://localhost:8000/events/document" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "contract.pdf",
    "file_type": "PDF Document",
    "source": "upload"
  }'
```

**Get system statistics:**

```bash
curl "http://localhost:8000/system/stats"
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_agents.py

# Run with verbose output
pytest -v
```

## 📁 Project Structure

```
agentta/
├── src/
│   ├── agents/              # AI Agent implementations
│   │   ├── base_agent.py    # Base agent class
│   │   ├── la_secretaria.py # Email intelligence
│   │   ├── el_calendista.py # Deadline management
│   │   ├── la_archivista.py # Document organization
│   │   └── el_estratega.py  # Process learning
│   ├── api/                 # FastAPI application
│   │   ├── main.py          # API endpoints
│   │   └── tasks.py         # Celery tasks
│   ├── core/                # Core infrastructure
│   │   ├── mcp.py           # Master Control Program
│   │   ├── event_bus.py     # Event distribution
│   │   └── shared_context.py # State management
│   ├── ai/                  # AI integrations
│   │   └── claude_integration.py
│   ├── security/            # Security & encryption
│   │   └── encryption.py
│   ├── database/            # Database models
│   │   ├── models.py
│   │   └── connection.py
│   └── config.py            # Configuration
├── tests/                   # Test suite
│   ├── unit/               # Unit tests
│   └── integration/        # Integration tests
├── alembic/                # Database migrations
├── docs/                   # Documentation
├── scripts/                # Utility scripts
├── docker-compose.yml      # Docker configuration
├── Dockerfile
├── requirements.txt        # Python dependencies
└── README.md
```

## 🔒 Security

AGENTTA implements zero-knowledge encryption for sensitive data:

- **Client-side encryption**: Data is encrypted before transmission
- **Field-level encryption**: Sensitive fields are automatically encrypted
- **Secure key management**: PBKDF2 key derivation
- **No plaintext storage**: Sensitive data never stored unencrypted

## 🛣️ Roadmap

### Phase 1: Core Infrastructure ✅
- [x] MCP base implementation
- [x] Agent base classes
- [x] Event bus
- [x] Shared context management

### Phase 2: AI Integration ✅
- [x] Claude metadata extraction
- [x] Intelligent routing
- [x] Training mechanisms

### Phase 3: Async Processing ✅
- [x] Celery task queue
- [x] Background processing
- [x] Performance optimization

### Phase 4: Frontend (Upcoming)
- [ ] React/Vue.js web interface
- [ ] Real-time updates via WebSockets
- [ ] Dashboard and analytics
- [ ] Mobile-responsive design

### Phase 5: Advanced Features (Planned)
- [ ] OCR for scanned documents
- [ ] Email provider integrations (Gmail, Outlook)
- [ ] Calendar sync (Google Calendar, Outlook)
- [ ] Advanced pattern recognition
- [ ] Multi-language support

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Powered by [Anthropic Claude](https://www.anthropic.com/)
- Inspired by the philosophy of human-centered AI

## 📞 Contact

For questions, feedback, or collaboration opportunities:

- **Email**: contact@agentta.com
- **GitHub Issues**: [Create an issue](https://github.com/yourusername/agentta/issues)

---

**"Building intelligent systems that learn, adapt, and transform legal practice through code."**

Made with ❤️ by the AGENTTA team
