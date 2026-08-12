# FastAPI ile Modern Backend Geliştirme

*[English version below / İngilizce versiyon aşağıdadır](#modern-backend-development-with-fastapi)*

Modern backend geliştirme prensiplerini, RESTful API tasarımını, asenkron programlamayı, veritabanı yönetimini, kimlik doğrulamayı, test yazmayı, konteynerleştirmeyi ve bulut ortamına dağıtımı uygulamak ve göstermek amacıyla geliştirilmiş, üretime yönelik bir FastAPI backend projesi.

Proje aşamalı olarak geliştirildi; yerel bir FastAPI uygulaması olarak başlayıp, Neon üzerinde barındırılan PostgreSQL veritabanı ile Google Cloud Run üzerinde çalışan konteynerleştirilmiş bir uygulamaya dönüştü.

---

## 🌐 Canlı Demo

**Uygulama:**  
https://fastapi-service-891132588768.us-central1.run.app

**API Dokümantasyonu:**  
https://fastapi-service-891132588768.us-central1.run.app/docs

**Sağlık Kontrolü (Health Check):**  
https://fastapi-service-891132588768.us-central1.run.app/health

> Uygulama, Google Cloud Run üzerinde Docker konteyneri olarak dağıtılmıştır ve üretim veritabanı olarak Neon PostgreSQL kullanmaktadır.

---

## 📌 Proje Genel Bakış

Bu proje, modern bir backend uygulamasının tüm yaşam döngüsüne odaklanır:

```text
FastAPI
   ↓
RESTful API
   ↓
Pydantic Doğrulama
   ↓
SQLAlchemy ORM
   ↓
Asenkron Veritabanı İşlemleri
   ↓
JWT Kimlik Doğrulama
   ↓
Alembic Migrasyonları
   ↓
Otomatik Testler
   ↓
Docker
   ↓
PostgreSQL / Neon
   ↓
Google Artifact Registry
   ↓
Google Cloud Run
```

Amaç yalnızca API uç noktaları oluşturmak değil, bir backend uygulamasının farklı katmanlarının nasıl birlikte çalıştığını ve yerel bir uygulamanın bulut ortamına dağıtım için nasıl hazırlandığını anlamaktır.

---

# 🚀 Özellikler

## RESTful API

Uygulama, kullanıcılar ve gönderiler (posts) için RESTful API uç noktaları sağlar.

Ana API grupları:

```text
/api/users
/api/posts
```

Farklı sorumlulukları ayırmak ve kod tabanını modüler tutmak için FastAPI'nin `APIRouter` yapısı kullanılmaktadır.

---

## 🔐 Kimlik Doğrulama ve Yetkilendirme

Uygulama, JWT tabanlı kimlik doğrulama uygular.

Kullanıcılar şunları yapabilir:

- Kayıt olma
- Giriş yapma
- Erişim (access) token'ı alma
- Korumalı uç noktalara erişme
- Gönderi oluşturma ve güncelleme
- Sahiplik izinlerine göre kaynakları değiştirme

Şifreler, veritabanında saklanmadan önce güvenli bir şekilde hashlenir.

Korumalı uç noktalara yapılan istekleri doğrulamak için JWT token'ları kullanılır.

---

## 🧩 Pydantic Doğrulama

Pydantic v2 şunlar için kullanılır:

- İstek doğrulama
- Yanıt şemaları
- Veri serileştirme
- Tip doğrulama
- Yapılandırılmış API sözleşmeleri

Bu, gelen API verilerinin iş mantığına ulaşmadan önce doğrulanmasını sağlar.

Örnek:

```python
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
```

Geçersiz istekler, FastAPI'nin doğrulama sistemi aracılığıyla otomatik olarak tespit edilir ve işlenir.

---

# 🗄️ Veritabanı Mimarisi

Proje, ORM katmanı olarak **SQLAlchemy 2.0** kullanır.

Geliştirme sırasında, yerel veritabanı işlemleri için SQLite kullanıldı. Uygulama daha sonra dağıtılan ortamda PostgreSQL kullanacak şekilde yapılandırıldı.

Üretim veritabanı **Neon PostgreSQL** üzerinde barındırılmaktadır.

```text
FastAPI
   │
   ▼
SQLAlchemy
   │
   ▼
psycopg
   │
   ▼
PostgreSQL
   │
   ▼
Neon
```

---

## ⚡ Asenkron Veritabanı İşlemleri

Uygulama, SQLAlchemy'nin asenkron API'sini kullanır.

Veritabanı oturumları şu şekilde yönetilir:

```python
AsyncSession
```

Bu nedenle veritabanı işlemleri asenkron çağrılar kullanır, örneğin:

```python
await db.execute(...)
await db.commit()
await db.refresh(...)
```

Bu sayede veritabanı işlemleri, FastAPI'nin asenkron istek işleme yapısıyla doğal bir şekilde çalışır.

---

# 🔄 Veritabanı Migrasyonları

Veritabanı şema değişikliklerini yönetmek için **Alembic** kullanılır.

Migrasyon oluşturma:

```bash
alembic revision --autogenerate -m "migrasyon mesajı"
```

Migrasyonları uygulama:

```bash
alembic upgrade head
```

Mevcut migrasyonu kontrol etme:

```bash
alembic current
```

Bu, veritabanı şema değişikliklerinin veritabanını manuel olarak değiştirmek yerine sürüm kontrolüne tabi tutulmasını sağlar.

---

# 📄 Sayfalama (Pagination)

Posts API'si, tek bir istekte gereğinden fazla kayıt döndürmemek için sayfalama uygular.

Sayfalama bilgileri şunları içerir:

```json
{
    "limit": 10,
    "skip": 0,
    "total": 50,
    "has_more": true
}
```

Burada:

- `limit` → İstenen kayıt sayısı
- `skip` → Atlanan kayıt sayısı
- `total` → Mevcut toplam kayıt sayısı
- `has_more` → Ek kayıtların olup olmadığını belirtir

Gerçekçi veri setleriyle sayfalama davranışını üretmek ve test etmek için bir veritabanı doldurma (populate) betiği de dahil edilmiştir.

---

# 🧪 Otomatik Testler

Proje, **Pytest** kullanan otomatik bir test paketi içerir.

Testler şunları kapsar:

- Ana sayfa
- Boş gönderi yanıtları
- Gönderi alma
- Bulunamadı (not-found) yanıtları
- Gönderi oluşturma
- Yetkisiz istekler
- Gönderi güncellemeleri
- Sahiplik yetkilendirmesi
- Sayfalama
- Kullanıcı doğrulama
- Yinelenen e-posta doğrulama
- Kullanıcı oluşturma

Testleri çalıştırma:

```bash
pytest tests/ -v
```

Mevcut test paketi:

```text
11 passed
```

Uygulamayı dağıtımdan önce test etmek, yerel geliştirmeden Docker'a ve bulut dağıtımına geçiş sırasında ana API işlevselliğinin kararlı kaldığını doğrulamaya yardımcı oldu.

---

# 🛡️ Güvenlik

Uygulama, çeşitli güvenlikle ilgili mekanizmalar içerir.

## Şifre Hashleme

Şifreler, veritabanında saklanmadan önce hashlenir.

## JWT Kimlik Doğrulama

Kimlik doğrulama, imzalanmış JWT erişim token'ları kullanılarak uygulanır.




---

# 🐳 Docker

Uygulama Docker kullanılarak konteynerleştirilmiştir.

Dockerfile, hafif bir Python imajı kullanır:

```dockerfile
FROM python:3.13.5-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8080

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT --proxy-headers --forwarded-allow-ips=*"]
```

### Neden Docker?

Docker, aşağıdakileri içeren tutarlı bir çalışma zamanı ortamı sağlar:

- Python
- Uygulama bağımlılıkları
- FastAPI
- Uvicorn
- Uygulama kaynak kodu

Her ortamın uygulama kurulumunu manuel olarak yeniden oluşturmasını gerektirmek yerine, uygulama bir Docker imajına paketlenebilir ve tutarlı bir şekilde çalıştırılabilir.

---

## Docker İmajını Oluşturma

Proje kök dizininden:

```bash
docker build -t fastapi-app .
```

Bu komut:

1. Dockerfile'ı okur
2. Python temel imajını indirir
3. `requirements.txt` dosyasından bağımlılıkları yükler
4. Uygulamayı imaja kopyalar
5. `fastapi-app` imajını oluşturur

---

## Konteyneri Yerel Olarak Çalıştırma

```bash
docker run -p 8080:8080 --env-file .env fastapi-app
```

Uygulama şu adreste erişilebilir olacaktır:

```text
http://localhost:8080
```

---

# ☁️ Bulut Dağıtımı

Uygulama, **Google Cloud Run** kullanılarak dağıtılmıştır.

Dağıtım mimarisi şu şekildedir:

```text
                    Docker Build
                         │
                         ▼
                    Docker İmajı
                         │
                         ▼
              Google Artifact Registry
                         │
                         ▼
                  Google Cloud Run
                         │
              ┌──────────┴──────────┐
              │                     │
              ▼                     ▼
          FastAPI                Uvicorn
              │
              ▼
       Neon PostgreSQL
```

---

# 📦 Google Artifact Registry

Docker imajını dağıtımdan önce depolamak için Google Artifact Registry kullanılır.

İmaj şu yapıyı takip eder:

```text
REGION-docker.pkg.dev/PROJECT_ID/REPOSITORY/IMAGE
```

Örneğin:

```text
us-central1-docker.pkg.dev/PROJECT_ID/fastapi-repo/fastapi-app
```

Registry, Cloud Run'ın konteyner imajını aldığı konum olarak işlev görür.

---

# 🚀 Google Cloud Run

Google Cloud Run, Docker konteynerini yönetilen bir bulut hizmeti olarak çalıştırır.

Bir dağıtım genel olarak şu iş akışını izler:

```text
Yerel Uygulama
       ↓
Docker Build
       ↓
Docker İmajı
       ↓
Artifact Registry
       ↓
Cloud Run

```



---

# 🔒 Ortam Değişkenleri

Hassas yapılandırma, ortam değişkenlerinde saklanır.

Örnek:

```env
DATABASE_URL=postgresql+psycopg://user:password@host/database
SECRET_KEY=your-secret-key
```

Gerçek `.env` dosyası kasıtlı olarak Git'ten hariç tutulmuştur.

Depo (repository) asla şunları içermemelidir:

- Veritabanı şifreleri
- Gizli anahtarlar (secret keys)
- API anahtarları
- Kimlik doğrulama bilgileri

Yerel Docker geliştirmesi için:

```bash
docker run -p 8080:8080 --env-file .env fastapi-app
```

---

# 📁 Proje Yapısı

```text
FAST_API/
│
├── alembic/
│   └── versions/
│
├── routers/
│   ├── user.py
│   └── post.py
│
├── tests/
│   ├── test_demo.py
│   ├── test_posts.py
│   └── test_users.py
│
├── static/
│   ├── css/
│   ├── js/
│   └── icons/
│
├── templates/
│   ├── home.html
│   ├── login.html
│   ├── register.html
│   └── ...
│
├── media/
│
├── main.py
├── models.py
├── schemas.py
├── database.py
├── auth.py
├── config.py
├── image_utils.py
├── populate_db.py
│
├── alembic.ini
├── Dockerfile
├── .dockerignore
├── .gitignore
├── requirements.txt
└── README.md
```

---

# ⚙️ Yerel Geliştirme

## 1. Depoyu klonlayın

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd FAST_API
```

## 2. Sanal ortam oluşturun

```bash
python3 -m venv .venv
```

Etkinleştirin:

```bash
source .venv/bin/activate
```

## 3. Bağımlılıkları yükleyin

```bash
pip install -r requirements.txt
```

## 4. Ortam değişkenlerini yapılandırın

Bir `.env` dosyası oluşturun:

```env
DATABASE_URL=your-database-url
SECRET_KEY=your-secret-key
```

## 5. Uygulamayı çalıştırın

```bash
uvicorn main:app --reload
```

Uygulama şu adreste erişilebilir olacaktır:

```text
http://127.0.0.1:8000
```

---

# 🧪 Testleri Çalıştırma

```bash
pytest tests/ -v
```

---

# 🐳 Docker ile Çalıştırma

Oluşturma:

```bash
docker build -t fastapi-app .
```

Çalıştırma:

```bash
docker run -p 8080:8080 --env-file .env fastapi-app
```

Açma:

```text
http://localhost:8080
```

---

# 🗺️ Geliştirme Yolculuğu

Proje aşamalı olarak geliştirildi; her aşama modern bir backend mimarisinin başka bir parçasını tanıttı.

```text
FastAPI Temelleri
        ↓
RESTful API Tasarımı
        ↓
Pydantic Doğrulama
        ↓
SQLAlchemy ORM
        ↓
CRUD İşlemleri
        ↓
Async/Await
        ↓
AsyncSession
        ↓
APIRouter Mimarisi
        ↓
JWT Kimlik Doğrulama
        ↓
Yetkilendirme
        ↓
Alembic Migrasyonları
        ↓
Sayfalama
        ↓
Veritabanı Doldurma
        ↓
Pytest
        ↓
Docker
        ↓
PostgreSQL / Neon
        ↓
Artifact Registry
        ↓
Google Cloud Run
```

Bu nedenle proje, yalnızca backend geliştirmeyi değil, aynı zamanda bir uygulamayı yerel geliştirmeden dağıtılmış bir bulut ortamına taşıma sürecini de kapsar.

---

# 📊 Mevcut Proje Durumu

| Bileşen | Durum |
|---|---|
| FastAPI REST API | ✅ Tamamlandı |
| Pydantic Doğrulama | ✅ Tamamlandı |
| SQLAlchemy ORM | ✅ Tamamlandı |
| Asenkron Veritabanı İşlemleri | ✅ Tamamlandı |
| APIRouter Mimarisi | ✅ Tamamlandı |
| JWT Kimlik Doğrulama | ✅ Tamamlandı |
| Yetkilendirme | ✅ Tamamlandı |
| Alembic Migrasyonları | ✅ Tamamlandı |
| Sayfalama | ✅ Tamamlandı |
| Veritabanı Doldurma | ✅ Tamamlandı |
| Pytest Testleri | ✅ Tamamlandı |
| Docker Konteynerleştirme | ✅ Tamamlandı |
| PostgreSQL / Neon | ✅ Tamamlandı |
| Artifact Registry | ✅ Tamamlandı |
| Google Cloud Run | ✅ Tamamlandı |


---



## 👨‍💻 Proje Amacı

Bu proje, modern backend sistemlerinin nasıl tasarlandığını, test edildiğini, konteynerleştirildiğini ve dağıtıldığını anlamaya odaklanan pratik bir backend mühendisliği yolculuğu olarak geliştirilmiştir.

Yalnızca bireysel API uç noktalarına odaklanmak yerine, proje tam geliştirme yaşam döngüsünü kapsar:

**Geliştirme → Veritabanı → Kimlik Doğrulama → Test → Docker → Bulut Dağıtımı**

---
---

# Modern Backend Development with FastAPI

*[Türkçe versiyon yukarıda / Turkish version above](#fastapi-ile-modern-backend-geliştirme)*

A production-oriented FastAPI backend project built to practice and demonstrate modern backend development principles, RESTful API design, asynchronous programming, database management, authentication, testing, containerization, and cloud deployment.

The project was developed incrementally, starting from a local FastAPI application and evolving into a containerized application deployed on Google Cloud Run with PostgreSQL hosted on Neon.

---

## 🌐 Live Demo

**Application:**  
https://fastapi-service-891132588768.us-central1.run.app

**API Documentation:**  
https://fastapi-service-891132588768.us-central1.run.app/docs

**Health Check:**  
https://fastapi-service-891132588768.us-central1.run.app/health

> The application is deployed as a Docker container on Google Cloud Run and uses Neon PostgreSQL as its production database.

---

## 📌 Project Overview

This project focuses on the complete lifecycle of a modern backend application:

```text
FastAPI
   ↓
RESTful API
   ↓
Pydantic Validation
   ↓
SQLAlchemy ORM
   ↓
Async Database Operations
   ↓
JWT Authentication
   ↓
Alembic Migrations
   ↓
Automated Testing
   ↓
Docker
   ↓
PostgreSQL / Neon
   ↓
Google Artifact Registry
   ↓
Google Cloud Run
```

The goal is not only to create API endpoints, but to understand how the different layers of a backend application work together and how a local application can be prepared for cloud deployment.

---

# 🚀 Features

## RESTful API

The application provides RESTful API endpoints for users and posts.

Main API groups:

```text
/api/users
/api/posts
```

FastAPI's `APIRouter` structure is used to separate different responsibilities and keep the codebase modular.

---

## 🔐 Authentication & Authorization

The application implements JWT-based authentication.

Users can:

- Register
- Log in
- Obtain an access token
- Access protected endpoints
- Create and update posts
- Modify resources according to ownership permissions

Passwords are securely hashed before being stored in the database.

JWT tokens are used to authenticate requests to protected endpoints.

---

## 🧩 Pydantic Validation

Pydantic v2 is used for:

- Request validation
- Response schemas
- Data serialization
- Type validation
- Structured API contracts

This allows incoming API data to be validated before reaching the business logic.

Example:

```python
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
```

Invalid requests are automatically detected and handled through FastAPI's validation system.

---

# 🗄️ Database Architecture

The project uses **SQLAlchemy 2.0** as its ORM layer.

During development, SQLite was used for local database operations. The application was later configured to use PostgreSQL for the deployed environment.

The production database is hosted on **Neon PostgreSQL**.

```text
FastAPI
   │
   ▼
SQLAlchemy
   │
   ▼
psycopg
   │
   ▼
PostgreSQL
   │
   ▼
Neon
```

---

## ⚡ Asynchronous Database Operations

The application uses SQLAlchemy's asynchronous API.

Database sessions are handled using:

```python
AsyncSession
```

Database operations therefore use asynchronous calls such as:

```python
await db.execute(...)
await db.commit()
await db.refresh(...)
```

This allows database operations to work naturally with FastAPI's asynchronous request handling.

---

# 🔄 Database Migrations

**Alembic** is used to manage database schema changes.

Create a migration:

```bash
alembic revision --autogenerate -m "migration message"
```

Apply migrations:

```bash
alembic upgrade head
```

Check the current migration:

```bash
alembic current
```

This allows database schema changes to be version-controlled instead of manually modifying the database.

---

# 📄 Pagination

The posts API implements pagination to avoid returning an unnecessarily large number of records in a single request.

Pagination information includes:

```json
{
    "limit": 10,
    "skip": 0,
    "total": 50,
    "has_more": true
}
```

Where:

- `limit` → Number of records requested
- `skip` → Number of records skipped
- `total` → Total number of available records
- `has_more` → Indicates whether additional records are available

A database population script is also included to generate sample data and test pagination behavior with realistic datasets.

---

# 🧪 Automated Testing

The project includes an automated test suite using **Pytest**.

The tests cover:

- Homepage
- Empty post responses
- Post retrieval
- Not-found responses
- Post creation
- Unauthorized requests
- Post updates
- Ownership authorization
- Pagination
- User validation
- Duplicate email validation
- User creation

Run the tests:

```bash
pytest tests/ -v
```

Current test suite:

```text
11 passed
```

Testing the application before deployment helped verify that the main API functionality remained stable during the transition from local development to Docker and cloud deployment.

---

# 🛡️ Security

The application includes several security-related mechanisms.

## Password Hashing

Passwords are hashed before being stored in the database.

## JWT Authentication

Authentication is implemented using signed JWT access tokens.

---
# 🐳 Docker

The application is containerized using Docker.

The Dockerfile uses a lightweight Python image:

```dockerfile
FROM python:3.13.5-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8080

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT --proxy-headers --forwarded-allow-ips=*"]
```

### Why Docker?

Docker provides a consistent runtime environment containing:

- Python
- Application dependencies
- FastAPI
- Uvicorn
- Application source code

Instead of requiring every environment to manually reproduce the application setup, the application can be packaged into a Docker image and run consistently.

---

## Build the Docker Image

From the project root:

```bash
docker build -t fastapi-app .
```

This command:

1. Reads the Dockerfile
2. Downloads the Python base image
3. Installs dependencies from `requirements.txt`
4. Copies the application into the image
5. Creates the `fastapi-app` image

---

## Run the Container Locally

```bash
docker run -p 8080:8080 --env-file .env fastapi-app
```

The application will then be available at:

```text
http://localhost:8080
```

---

# ☁️ Cloud Deployment

The application is deployed using **Google Cloud Run**.

The deployment architecture is:

```text
                    Docker Build
                         │
                         ▼
                    Docker Image
                         │
                         ▼
              Google Artifact Registry
                         │
                         ▼
                  Google Cloud Run
                         │
              ┌──────────┴──────────┐
              │                     │
              ▼                     ▼
          FastAPI                Uvicorn
              │
              ▼
       Neon PostgreSQL
```

---

# 📦 Google Artifact Registry

Google Artifact Registry is used to store the Docker image before deployment.

The image follows the structure:

```text
REGION-docker.pkg.dev/PROJECT_ID/REPOSITORY/IMAGE
```

For example:

```text
us-central1-docker.pkg.dev/PROJECT_ID/fastapi-repo/fastapi-app
```

The registry acts as the location from which Cloud Run retrieves the container image.

---

# 🚀 Google Cloud Run

Google Cloud Run runs the Docker container as a managed cloud service.

A deployment follows this general workflow:

```text
Local Application
       ↓
Docker Build
       ↓
Docker Image
       ↓
Artifact Registry
       ↓
Cloud Run

```



---

# 🔒 Environment Variables

Sensitive configuration is stored in environment variables.

Example:

```env
DATABASE_URL=postgresql+psycopg://user:password@host/database
SECRET_KEY=your-secret-key
```

The actual `.env` file is intentionally excluded from Git.

The repository should never contain:

- Database passwords
- Secret keys
- API keys
- Authentication credentials

For local Docker development:

```bash
docker run -p 8080:8080 --env-file .env fastapi-app
```

---

# 📁 Project Structure

```text
FAST_API/
│
├── alembic/
│   └── versions/
│
├── routers/
│   ├── user.py
│   └── post.py
│
├── tests/
│   ├── test_demo.py
│   ├── test_posts.py
│   └── test_users.py
│
├── static/
│   ├── css/
│   ├── js/
│   └── icons/
│
├── templates/
│   ├── home.html
│   ├── login.html
│   ├── register.html
│   └── ...
│
├── media/
│
├── main.py
├── models.py
├── schemas.py
├── database.py
├── auth.py
├── config.py
├── image_utils.py
├── populate_db.py
│
├── alembic.ini
├── Dockerfile
├── .dockerignore
├── .gitignore
├── requirements.txt
└── README.md
```

---

# ⚙️ Local Development

## 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd FAST_API
```

## 2. Create a virtual environment

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure environment variables

Create a `.env` file:

```env
DATABASE_URL=your-database-url
SECRET_KEY=your-secret-key
```

## 5. Run the application

```bash
uvicorn main:app --reload
```

The application will be available at:

```text
http://127.0.0.1:8000
```

---

# 🧪 Run Tests

```bash
pytest tests/ -v
```

---

# 🐳 Run with Docker

Build:

```bash
docker build -t fastapi-app .
```

Run:

```bash
docker run -p 8080:8080 --env-file .env fastapi-app
```

Open:

```text
http://localhost:8080
```
---
# 🗺️ Development Journey

The project was developed incrementally, with each stage introducing another part of a modern backend architecture.

```text
FastAPI Fundamentals
        ↓
RESTful API Design
        ↓
Pydantic Validation
        ↓
SQLAlchemy ORM
        ↓
CRUD Operations
        ↓
Async/Await
        ↓
AsyncSession
        ↓
APIRouter Architecture
        ↓
JWT Authentication
        ↓
Authorization
        ↓
Alembic Migrations
        ↓
Pagination
        ↓
Database Population
        ↓
Pytest
        ↓
Docker
        ↓
PostgreSQL / Neon
        ↓
Artifact Registry
        ↓
Google Cloud Run

```
The project therefore covers not only backend development, but also the process of taking an application from local development to a deployed cloud environment.

---
# 📊 Current Project Status
| Component | Status |
|---|---|
| FastAPI REST API | ✅ Complete |
| Pydantic Validation | ✅ Complete |
| SQLAlchemy ORM | ✅ Complete |
| Async Database Operations | ✅ Complete |
| APIRouter Architecture | ✅ Complete |
| JWT Authentication | ✅ Complete |
| Authorization | ✅ Complete |
| Alembic Migrations | ✅ Complete |
| Pagination | ✅ Complete |
| Database Population | ✅ Complete |
| Pytest Testing | ✅ Complete |
| Docker Containerization | ✅ Complete |
| PostgreSQL / Neon | ✅ Complete |
| Artifact Registry | ✅ Complete |
| Google Cloud Run | ✅ Complete |
---
## 👨‍💻 Project Purpose

This project was developed as a practical backend engineering journey focused on understanding how modern backend systems are designed, tested, containerized, and deployed.

Rather than focusing only on individual API endpoints, the project covers the complete development lifecycle:

**Development → Database → Authentication → Testing → Docker → Cloud Deployment**