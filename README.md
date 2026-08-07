# Modern Backend Development with FastAPI

Bu repository, modern backend geliştirme pratikleri, RESTful API tasarımı ve kurumsal mimari standartlarını öğrenmek ve uygulamak amacıyla geliştirilmekte olan kapsamlı bir FastAPI projesidir.

---

## Proje Durumu (Work in Progress)

Proje aktif olarak geliştirilmektedir. Temel katmanlar tamamlanmış olup, güvenlik, veritabanı migrasyonları ve konteynerizasyon süreçleri aşama aşama eklenmektedir.

*   **Temel API ve Rotalama:** Tamamlandı ✅
*   **Pydantic Veri Doğrulama:** Tamamlandı ✅
*   **SQLAlchemy ORM ve CRUD Operasyonları:** Tamamlandı ✅
*   **Asenkron Programlama (Async/Await):** Tamamlandı ✅
*   **Modüler Mimari (APIRouter):** Tamamlandı ✅
*   **Kimlik Doğrulama ve Yetkilendirme (JWT):** Tamamlandı ✅
*   **Veritabanı Migrasyonları (Alembic):** Planlanıyor ⏳
*   **Test Süreçleri (Pytest):** Planlanıyor ⏳
*   **Docker & Docker Compose Entegrasyonu:** Planlanıyor ⏳

---

## 🛠️ Kullanılan Teknolojiler ve Kütüphaneler

*   **Python** (Asenkron ve modern dil özellikleri)
*   **FastAPI** (Yüksek performanslı web framework)
*   **Pydantic v2** (Veri doğrulama ve şema yönetimi)
*   **SQLAlchemy** (İlişkisel veritabanı yönetimi ve ORM)
*   **SQLite / PostgreSQL** (Veritabanı altyapısı)

---

## 📂 Mimari ve Modüller

Proje, kodun sürdürülebilirliği ve ölçeklenebilirliği göz önünde bulundurularak modüler bir yapıda (`APIRouter`) tasarlanmaktadır. Temel olarak şu yapıları barındırır:
*   `routers/`: Farklı iş mantıklarına ait API uç noktaları (Endpoints)
*   `models/`: SQLAlchemy veritabanı tabloları
*   `schemas/`: Pydantic istek ve yanıt doğrulama sınıfları
*   `database.py`: Veritabanı bağlantı yönetimi

---
