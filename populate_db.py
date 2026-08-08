import asyncio
from datetime import UTC, datetime, timedelta

import httpx
from sqlalchemy import delete, select, update

import models
from database import local_session, Base, engine
from main import app


USERS = [
    {
        "username": "CanSahin",
        "email": "cansahin@gmail.com",
        "password": "TestPassword1!",
    },
    {
        "username": "DenemeKullanici",
        "email": "testemail2@test.com",
        "password": "TestPassword2!",
    },
    {
        "username": "KediPamuk",
        "email": "testemail3@test.com",
        "password": "TestPassword3!",
    },
    {
        "username": "CiftlikKopekleri",
        "email": "testemail4@test.com",
        "password": "TestPassword4!",
    },
    {
        "username": "KodcuZeynep",
        "email": "testemail5@test.com",
        "password": "TestPassword5!",
    },
    {
        "username": "DostumKarabas",
        "email": "testemail6@test.com",
        "password": "TestPassword6!",
    },
]


POSTS = [
    {
        "title": "FastAPI'yi Neden Çok Seviyorum?",
        "content": "FastAPI modern API geliştirme sürecimi tamamen değiştirdi. Otomatik dokümantasyon, tip ipuçları ve yerleşik async desteği geliştirme hızını inanılmaz artırıyor. Ayrıca performansı gerçekten harika!",
    },
    {
        "title": "Can Şahin En İyi Python İçeriklerine Sahip!",
        "content": "Bu yazı kesinlikle başka bir takipçi tarafından yazıldı... Yani kendisi yazmadı. Tamamen tarafsız bir takipçi yazısıdır... Şaka bir yana, harika Python ve backend içerikleri için projelerini inceleyin.",
    },
    {
        "title": "Async/Await Mantığı Nihayet Oturdu",
        "content": "Aylardır asenkron programlamayla mücadele ediyordum ama FastAPI yaklaşımı sayesinde taşlar yerine oturdu. Endpoint'lerde 'async def' ve veritabanı çağrılarında 'await' kullanmak mükemmel bir akış sağlıyor.",
    },
    {
        "title": "Şahin mi? Şahane Bir Mimari!",
        "content": "Bu blog yazılarını gerçekten kimse okuyor mu? İçeride derin mimari anlatımlar olması şart mı? İstersem akşama kadar yazabilirim... Ya da yapay zeka yazsın, lütfen devam et Claude.",
    },
    {
        "title": "Pydantic Doğrulaması Adeta Büyü Gibi",
        "content": "FastAPI içinde Pydantic veri doğrulama işleme yöntemi muazzam. Modeli tip belirteçleriyle tanımlıyorsunuz ve bitti: Otomatik doğrulama, serileştirme ve dokümantasyon hazır!",
    },
    {
        "title": "Flask'ten FastAPI Geçiş Süreci",
        "content": "Geçen ay Flask projelerimi FastAPI'ye taşımaya başladım. Öğrenme eğrisi oldukça düşüktü ve kazançlar devasa: Otomatik OpenAPI dokümanları, yüksek performans ve yerel async desteği.",
    },
    {
        "title": "Favori Korku ve Gerilim Filmlerim",
        "content": "Korku filmlerine ve pratik efektlere bayılırım. Tüm zamanların en iyilerinden biri 'The Thing'. Modern tarafta 'Hereditary' harika ama 'The Night House' psikolojik gerilim sevenler için gizli bir cevherdir.",
    },
    {
        "title": "Tip İpuçları (Type Hints) Hayat Kurtarır",
        "content": "Eskiden type hint yazmayı fazladan yük olarak görürdüm. Ancak FastAPI kullandıktan sonra otomatik tamamlama, hızlı doğrulama ve kendi kendini dokümante eden kodun gücünü anladım.",
    },
    {
        "title": "Bağımlılık Enjeksiyonunun (Dependency Injection) Gücü",
        "content": "FastAPI'nin DI sistemi çok zarif. Veritabanı oturumuna mı ihtiyacınız var? Parametre olarak ekleyin. Mevcut kullanıcı mı lazım? Yine aynı şekilde. Kod inanılmaz temiz ve test edilebilir kalıyor.",
    },
    {
        "title": "SQLAlchemy 2.0 Geçişine Değer",
        "content": "Hala SQLAlchemy 1.x kalıplarını kullanıyorsanız yükseltme vakti geldi. select() ve mapped_column() içeren yeni 2.0 stili çok daha net ve async mimariyle kusursuz çalışıyor.",
    },
    {
        "title": "Sıcak Gelişme: API'ler İçin Python > JavaScript",
        "content": "Evet, söyledim gitti. Backend API geliştirmede FastAPI ile Python, Node.js ekosistemini geçer. Yorumlarda tartışabiliriz. (Şaka yapıyorum, bu blogda henüz yorum sistemi yok...)",
    },
    {
        "title": "HTTP Durum Kodlarını Doğru Anlamak",
        "content": "200 OK, 201 Created, 400 Bad Request, 404 Not Found, 500 Internal Server Error. Bu kodları iyi öğrenin; API'nizin dış dünyayla iletişim dilidir.",
    },
    {
        "title": "Favori Oyunlarım ve RPG Tutkusu",
        "content": "En çok vakit geçirdiğim oyun League of Legends olabilir ama favorim izometrik RPG'lerdir. Baldur's Gate 3, Pillars of Eternity ve Pathfinder serisi (Kingmaker / Wrath of the Righteous) harika yapımlardır.",
    },
    {
        "title": "JWT Kimlik Doğrulama Mantığı",
        "content": "JSON Web Token'lar başta karmaşık gelebilir ama mantığı basittir: Kullanıcı verisini kodla, gizli bir anahtarla imzala ve istekleri doğrula. FastAPI ile JWT entegrasyonu oldukça pratik.",
    },
    {
        "title": "API Tasarımı İçin İpuçları",
        "content": "Kaynaklar için isimler (/users, /posts), eylemler için HTTP fiilleri (GET, POST, PUT, DELETE) kullanın ve tutarlı yanıtlar döndürün. FastAPI response_model bu tutarlılığı zorunlu kılar.",
    },
    {
        "title": "Path Parametreleri mi Query Parametreleri mi?",
        "content": "Zorunlu kaynak kimlikleri için Path parametreleri (/users/123), isteğe bağlı filtrelemeler için Query parametreleri (/posts?author=can&limit=10) tercih edilmelidir.",
    },
    {
        "title": "Hata Yönetimini Doğru Yapmak",
        "content": "Her istisna için 500 döndürmeyin! Anlamlı durum kodları ve mesajlar sunmak için HTTPException kullanın. API'nizi tüketen istemciler size teşekkür edecektir.",
    },
    {
        "title": "Neden Paket Yöneticisi Olarak UV Kullanıyorum?",
        "content": "UV, Python paket yönetimi için inanılmaz hızlı. Dakikalar süren bağımlılık kurulumlarını milisaniyeler seviyesine indiriyor. Henüz denemediyseniz mutlaka göz atın.",
    },
    {
        "title": "Kitap Tavsiyeleri ve Okuma Listem",
        "content": "Genelde kurgu dışı okumayı severim. Marcus Aurelius'tan 'Kendime Düşünceler', Seneca'dan 'Bilinç' tarzı felsefi eserler başucumdadır. Kurgu tarafında ise 'House of Leaves' ve 'Martian' harikadır.",
    },
    {
        "title": "FastAPI Uygulamalarını Test Etmek",
        "content": "FastAPI'nin TestClient altyapısı birim ve entegrasyon testlerini çok kolaylaştırır. Endpoint'leri test edin, bağımlılıkları mock'layın ve hataları canlıya çıkmadan yakalayın.",
    },
    {
        "title": "Ortam Değişkenleri ve Güvenlik",
        "content": "Gizli anahtarları asla koda gömmeyin! API anahtarlarınızı, veritabanı URL'lerinizi ve JWT sırlarınızı korumak için ortam değişkenleri ve pydantic-settings kullanın.",
    },
    {
        "title": "CORS Hataları ve Çözüm Yolları",
        "content": "Frontend geliştiricilerin korkulu rüyası CORS! FastAPI CORSMiddleware bu sorunu çözer. Üretim ortamında 'allow_origins' listesini spesifik tutmayı unutmayın.",
    },
    {
        "title": "Asenkron Veritabanı Sorguları",
        "content": "Async kodun içinde bloklayıcı veritabanı çağrıları yapmak performansı öldürür. Event loop'u rahat ettirmek için asyncpg veya aiosqlite gibi async sürücüler kullanın.",
    },
    {
        "title": "Response Model Kullanmanın Avantajları",
        "content": "Yanıt modelleri sadece dokümantasyon için değildir; hassas alanları (parola gibi) otomatik filtreler. Neyin dışarı çıkacağını tanımlayın, gerisini Pydantic halletsin.",
    },
    {
        "title": "Kutu Oyunları ve Hobiler",
        "content": "Catan klasik bir favoridir. Ayrıca ahşap atölyesinde kendi imkanlarımla şeyler üretmeyi çok severim. Doğal ahşaptan yapılmış bir nesnenin hikayesi her zaman daha değerlidir.",
    },
    {
        "title": "API Sürümleme (Versioning) Stratejileri",
        "content": "API'ler zamanla gelişir. İlk günden sürümleme planı yapın! İster URL ön eki (/v1/users) ister header kullanın, mevcut istemcileri kırmadan ilerlemek kritiktir.",
    },
    {
        "title": "FastAPI'de Arka Plan Görevleri (Background Tasks)",
        "content": "E-posta gönderimi veya dosya işleme için kullanıcıyı bekletmeyin. FastAPI BackgroundTasks ile hemen yanıt dönüp işlemi arka planda sürdürebilirsiniz.",
    },
    {
        "title": "Rate Limiting ile API Koruma",
        "content": "API'nizi kötüye kullanımlardan korumak için istek sınırlandırma (rate limiting) uygulayın. Aşırı istek durumunda 429 Too Many Requests dönmek sunucunuzu korur.",
    },
    {
        "title": "Kendi Kendini Yazan Dokümantasyon",
        "content": "Endpoint'lerinize docstring ekleyin, Swagger UI üzerinde anında görünsün. Pydantic modellerine örnekler ekleyin, dokümantasyon çaba sarf etmeden tamamlansın.",
    },
    {
        "title": "FastAPI ile WebSockets Kullanımı",
        "content": "Sadece REST API ile sınırlı kalmayın. FastAPI, gerçek zamanlı iletişim için WebSockets yapısını destekler. Canlı bildirimler ve sohbet uygulamaları için idealdir.",
    },
    {
        "title": "Ahşap İşçiliği ve Üretim Tutkusu",
        "content": "Ağaçla çalışmak, kendi ellerinizle somut bir şey üretmek harika bir duygu. Kendin yap projeleri ve marangozluk teknikleri zihni dinlendirmek için birebir.",
    },
    {
        "title": "Pydantic Özel Doğrulayıcılar (Validators)",
        "content": "Tip kontrolünün ötesinde mantıksal doğrulamalar gerektiğinde @field_validator ve @model_validator dekoratörleri imdadınıza yetişir.",
    },
    {
        "title": "ORM vs Ham SQL Tartışması",
        "content": "SQLAlchemy gibi ORM'ler soyutlama sağlar ama bazen karmaşık sorgularda performansı gizleyebilir. Nerede ORM, nerede ham SQL yazacağınızı bilmek önemlidir.",
    },
    {
        "title": "Async Kodlarda Hata Ayıklama",
        "content": "Asenkron hataları yakalamak bazen zorlaşabilir. Detaylı loglama kullanın, event loop mantığını kavramadan senkron ve asenkron kodları karıştırmayın.",
    },
    {
        "title": "FastAPI Uygulamalarını Dockerize Etmek",
        "content": "Docker + FastAPI = Kolay Dağıtım. Temiz bir Dockerfile hazırlayın, imajınızı derleyin ve istediğiniz sunucuda ortam bağımsız çalıştırın.",
    },
    {
        "title": "Sağlık Kontrolü (Health Check) Endpoint'leri",
        "content": "Sisteminize mutlaka bir /health endpoint'i ekleyin. Load balancer veya orchestrator yapılar sunucunuzun ayakta olup olmadığını bu yolla kontrol eder.",
    },
    {
        "title": "Sıradaki Konu Ne Olmalı?",
        "content": "Blog konuları tükenmek üzere! Belki de tekrar FastAPI'nin ne kadar harika olduğunu yazmalıyım... Buraya kadar okuduysanız harikasınız, teşekkürler!",
    },
    {
        "title": "Sayfalama (Pagination): Tüm Veriyi Tekte Dönmeyin",
        "content": "10.000 kaydı tek bir yanıtta döndürmek veritabanını yorar. Limit ve offset ile sayfalama altyapısı kurun, istemci ve sunucu rahat etsin.",
    },
    {
        "title": "OpenAPI Şemasını Özelleştirme",
        "content": "Otomatik oluşturulan OpenAPI şemasını varsayılan haliyle bırakmayın. Başlıklar, açıklamalar ve etiketler ekleyerek dokümantasyonu özelleştirin.",
    },
    {
        "title": "Güvenlik Başlıkları (Security Headers)",
        "content": "Yanıtlarınıza güvenlik başlıkları ekleyin: X-Content-Type-Options, X-Frame-Options, Content-Security-Policy. Küçük bir dokunuşla büyük güvenlik artışı sağlayın.",
    },
    {
        "title": "Önbellekleme Stratejileri (Caching)",
        "content": "Her isteğin veritabanına gitmesine gerek yok. Sık erişilen veriler için Redis veya bellek içi önbellekleme kullanarak yanıt sürelerini düşürün.",
    },
    {
        "title": "GraphQL mi REST mi?",
        "content": "GraphQL esneklik sağlar ama REST rüştünü ispatlamıştır. İhtiyacınıza göre seçin. FastAPI REST mimarisinde mükemmeldir ama Strawberry ile GraphQL de destekler.",
    },
    {
        "title": "İlham Veren Film Replikleri",
        "content": "Gattaca filminden ilham veren bir sahne, azim ve kararlılık üzerine düşünmek için güzel bir örnektir. Bu gönderi örnek veri oluşturmak için kullanılmaktadır.",
    },
]


POST_44 = {
    "title": "Eğlenceli Bilgi: Forma Numaram #44",
    "content": "En eski gönderiye, yani 44. gönderiye kadar sayfalamayı başardıysanız bu detay tam size göre: Forma numaram 44'tü. 44 numarayı giyen diğer efsaneler arasında Jerry West (NBA), Hank Aaron (MLB) ve Floyd Little (NFL) yer alır.",
}


async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("Database tables are ready")


async def clear_existing_data() -> None:
    async with local_session() as db:
        await db.execute(delete(models.Post))
        await db.execute(delete(models.User))
        await db.commit()

    print("Cleared existing data")


async def update_post_dates() -> None:
    now = datetime.now(UTC)

    async with local_session() as db:
        result = await db.execute(
            select(models.Post).order_by(models.Post.id)
        )

        posts = result.scalars().all()

        if not posts:
            return

        # İlk post en eski post olacak
        await db.execute(
            update(models.Post)
            .where(models.Post.id == posts[0].id)
            .values(date_posted=now - timedelta(days=90))
        )

        # Diğer postlar
        for i, post in enumerate(posts[1:], start=1):
            days_ago = (len(posts) - i) * 1.5
            hours_offset = (i * 7) % 24

            post_date = now - timedelta(
                days=days_ago,
                hours=hours_offset,
            )

            await db.execute(
                update(models.Post)
                .where(models.Post.id == post.id)
                .values(date_posted=post_date)
            )

        await db.commit()

    print("Updated post dates")


async def populate() -> None:
    # Önce tabloları oluştur
    await create_tables()

    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://localhost",
    ) as client:


        await clear_existing_data()

        users: list[dict] = []

        # -------------------------
        # USERS
        # -------------------------

        print(f"\nCreating {len(USERS)} users...")

        for user_data in USERS:

            response = await client.post(
                "/api/users",
                json={
                    "username": user_data["username"],
                    "email": user_data["email"],
                    "password": user_data["password"],
                },
            )

            response.raise_for_status()

            user = response.json()

            print(f"Created: {user['username']}")

            # Login
            response = await client.post(
                "/api/users/token",
                data={
                    "username": user_data["email"],
                    "password": user_data["password"],
                },
            )

            response.raise_for_status()

            token = response.json()["access_token"]

            users.append(
                {
                    "id": user["id"],
                    "username": user["username"],
                    "token": token,
                }
            )

        # -------------------------
        # POSTS
        # -------------------------

        print(f"\nCreating {len(POSTS) + 1} posts...")

        # Önce POST_44
        response = await client.post(
            "/api/posts",
            json={
                "title": POST_44["title"],
                "content": POST_44["content"],
            },
            headers={
                "Authorization": f"Bearer {users[0]['token']}"
            },
        )

        response.raise_for_status()

        print(f"Created: '{POST_44['title']}'")

        # Diğer postlar
        for i, post_data in enumerate(reversed(POSTS)):

            user = users[i % len(users)]

            response = await client.post(
                "/api/posts",
                json={
                    "title": post_data["title"],
                    "content": post_data["content"],
                },
                headers={
                    "Authorization": f"Bearer {user['token']}"
                },
            )

            response.raise_for_status()

            title = post_data["title"]

            if len(title) > 50:
                print(f"Created: '{title[:50]}...'")
            else:
                print(f"Created: '{title}'")

        # -------------------------
        # UPDATE DATES
        # -------------------------

        print("\nUpdating post dates...")

        await update_post_dates()

    await engine.dispose()

    print("\nDone!")
    print(f"  {len(USERS)} users")
    print(f"  {len(POSTS) + 1} posts")
    print("  Default profile pictures will be used")


if __name__ == "__main__":
    asyncio.run(populate())