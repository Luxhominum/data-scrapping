"""
High-Fidelity Seed Dataset for Indonesian UMKM & Product Mapping
"""
from database.db_manager import DatabaseManager
from database.models import UMKM, Product

SAMPLE_UMKMS = [
    {
        "name": "Batik Danar Hadi Solo",
        "category": "Fashion & Batik",
        "address": "Jl. Slamet Riyadi No. 261, Sriwedari, Laweyan",
        "city": "Solo",
        "province": "Jawa Tengah",
        "latitude": -7.5666,
        "longitude": 110.8166,
        "phone": "+62 271-714326",
        "whatsapp": "628112658990",
        "instagram_handle": "danarhadi_id",
        "tokopedia_url": "https://tokopedia.com/danarhadi",
        "shopee_url": "https://shopee.co.id/danarhadi_official",
        "rating": 4.9,
        "reviews_count": 840,
        "source": "verified_umkm",
        "products": [
            {
                "title": "Kemeja Batik Pria Katun Primisima Parang Kusumo",
                "price": 285000,
                "original_price": 320000,
                "rating": 4.9,
                "sold_count": 1420,
                "platform": "tokopedia",
                "image_url": "https://images.unsplash.com/photo-1598033129183-c4f50c736f10?w=500&auto=format&fit=crop&q=60",
                "description": "Batik cap handmade halus motif Parang Kusumo khas Solo dengan lapisan furing katun adem."
            },
            {
                "title": "Outer Tunik Batik Wanita Motif Sekar Jagad",
                "price": 345000,
                "original_price": 395000,
                "rating": 4.8,
                "sold_count": 890,
                "platform": "shopee",
                "image_url": "https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=500&auto=format&fit=crop&q=60",
                "description": "Outerwear batik modern kasual cocok untuk kerja dan acara semi formal."
            }
        ]
    },
    {
        "name": "Kopi Aroma Bandung 1930",
        "category": "Kopi & Minuman",
        "address": "Jl. Banceuy No. 51, Braga, Sumur Bandung",
        "city": "Bandung",
        "province": "Jawa Barat",
        "latitude": -6.9192,
        "longitude": 107.6067,
        "phone": "+62 22-4230473",
        "whatsapp": "628122019300",
        "instagram_handle": "kopiaroma_bdg",
        "tokopedia_url": "https://tokopedia.com/kopiaroma",
        "shopee_url": "https://shopee.co.id/kopiaroma_bdg",
        "rating": 4.9,
        "reviews_count": 2150,
        "source": "verified_umkm",
        "products": [
            {
                "title": "Kopi Mokka Arabika Biji/Bubuk Aged 8 Years 250g",
                "price": 55000,
                "original_price": 60000,
                "rating": 4.9,
                "sold_count": 5200,
                "platform": "tokopedia",
                "image_url": "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=500&auto=format&fit=crop&q=60",
                "description": "Kopi arabika legendaris Bandung yang disimpan selama 8 tahun sebelum disangrai kayu karet."
            },
            {
                "title": "Kopi Robusta Tradisional Aged 5 Years 250g",
                "price": 45000,
                "original_price": 50000,
                "rating": 4.8,
                "sold_count": 3400,
                "platform": "shopee",
                "image_url": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=500&auto=format&fit=crop&q=60",
                "description": "Robusta murni minim keasaman dengan aroma pekat otentik 1930."
            }
        ]
    },
    {
        "name": "Bakpia Kukus Tugu Jogja",
        "category": "Kuliner & Snack",
        "address": "Jl. Solo KM 9, Maguwoharjo, Sleman",
        "city": "Yogyakarta",
        "province": "D.I. Yogyakarta",
        "latitude": -7.7828,
        "longitude": 110.4285,
        "phone": "+62 274-488999",
        "whatsapp": "628112933800",
        "instagram_handle": "bakpiatugujogja",
        "tokopedia_url": "https://tokopedia.com/bakpiakukustugu",
        "shopee_url": "https://shopee.co.id/bakpiakukustuguofficial",
        "rating": 4.8,
        "reviews_count": 3400,
        "source": "verified_umkm",
        "products": [
            {
                "title": "Bakpia Kukus Tugu Original Cokelat Isi 10 Pcs",
                "price": 42000,
                "original_price": 45000,
                "rating": 4.9,
                "sold_count": 12800,
                "platform": "shopee",
                "image_url": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=500&auto=format&fit=crop&q=60",
                "description": "Bakpia kukus lembut dengan lelehan pasta cokelat lumer premium."
            },
            {
                "title": "Bakpia Kukus Brownies Keju Isi 10 Pcs",
                "price": 45000,
                "original_price": 48000,
                "rating": 4.8,
                "sold_count": 9100,
                "platform": "tokopedia",
                "image_url": "https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=500&auto=format&fit=crop&q=60",
                "description": "Kombinasi cake brownies lembut berpadu gurihnya keju kraft."
            }
        ]
    },
    {
        "name": "Sambal Bu Rudy Surabaya",
        "category": "Kuliner & Snack",
        "address": "Jl. Dharmahusada No. 140, Mojo, Gubeng",
        "city": "Surabaya",
        "province": "Jawa Timur",
        "latitude": -7.2681,
        "longitude": 112.7663,
        "phone": "+62 31-5923485",
        "whatsapp": "6281330008899",
        "instagram_handle": "sambalburudy_sby",
        "tokopedia_url": "https://tokopedia.com/burudy",
        "shopee_url": "https://shopee.co.id/burudyofficial",
        "rating": 4.9,
        "reviews_count": 4120,
        "source": "verified_umkm",
        "products": [
            {
                "title": "Sambal Bawang Bu Rudy Khas Surabaya 130g",
                "price": 32000,
                "original_price": 35000,
                "rating": 4.9,
                "sold_count": 28400,
                "platform": "tokopedia",
                "image_url": "https://images.unsplash.com/photo-1563245372-f21724e3856d?w=500&auto=format&fit=crop&q=60",
                "description": "Sambal bawang ikonik Surabaya dengan cita rasa pedas mantap dan rempah pilihan."
            },
            {
                "title": "Udang Crispy Gurih Bu Rudy 100g",
                "price": 40000,
                "original_price": 45000,
                "rating": 4.8,
                "sold_count": 15200,
                "platform": "shopee",
                "image_url": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=500&auto=format&fit=crop&q=60",
                "description": "Udang laut renyah gurih pelengkap sambal bu rudy."
            }
        ]
    },
    {
        "name": "Karya Rotan Artisan Cirebon",
        "category": "Kriya & Kerajinan",
        "address": "Jl. Tegalwangi No. 88, Weru",
        "city": "Cirebon",
        "province": "Jawa Barat",
        "latitude": -6.7118,
        "longitude": 108.5142,
        "phone": "+62 231-321789",
        "whatsapp": "6281788992211",
        "instagram_handle": "karyarotancrb",
        "tokopedia_url": "https://tokopedia.com/karyarotan",
        "shopee_url": "https://shopee.co.id/karyarotan",
        "rating": 4.7,
        "reviews_count": 310,
        "source": "verified_umkm",
        "products": [
            {
                "title": "Keranjang Anyaman Rotan Alami Multipurpose Boho",
                "price": 115000,
                "original_price": 145000,
                "rating": 4.8,
                "sold_count": 780,
                "platform": "tokopedia",
                "image_url": "https://images.unsplash.com/photo-1544816155-12df9643f363?w=500&auto=format&fit=crop&q=60",
                "description": "Keranjang penyimpanan estetis berbahan rotan alam grade A finishing eco-friendly."
            },
            {
                "title": "Lampu Gantung Anyaman Bambu & Rotan Minimalis",
                "price": 185000,
                "original_price": 220000,
                "rating": 4.7,
                "sold_count": 420,
                "platform": "shopee",
                "image_url": "https://images.unsplash.com/photo-1513519245088-0e12902e5a38?w=500&auto=format&fit=crop&q=60",
                "description": "Kap lampu gantung estetik tema Scandinavian dan Japandi."
            }
        ]
    },
    {
        "name": "Bali Pure Coconut & Organic Spa",
        "category": "Herbal & Kosmetik",
        "address": "Jl. Raya Seminyak No. 17, Kuta",
        "city": "Denpasar",
        "province": "Bali",
        "latitude": -8.6913,
        "longitude": 115.1682,
        "phone": "+62 361-734567",
        "whatsapp": "6281999234888",
        "instagram_handle": "balipure_organic",
        "tokopedia_url": "https://tokopedia.com/balipure",
        "shopee_url": "https://shopee.co.id/balipure_organics",
        "rating": 4.9,
        "reviews_count": 1200,
        "source": "verified_umkm",
        "products": [
            {
                "title": "Cold-Pressed Extra Virgin Coconut Oil (VCO) 500ml",
                "price": 68000,
                "original_price": 80000,
                "rating": 4.9,
                "sold_count": 3100,
                "platform": "tokopedia",
                "image_url": "https://images.unsplash.com/photo-1608248597359-32219747514a?w=500&auto=format&fit=crop&q=60",
                "description": "Minyak kelapa murni diproses dingin tanpa bahan kimia untuk perawatan kulit dan diet."
            },
            {
                "title": "Body Scrub Lulur Bali Frangipani Essential Oil 250g",
                "price": 52000,
                "original_price": 65000,
                "rating": 4.8,
                "sold_count": 1800,
                "platform": "shopee",
                "image_url": "https://images.unsplash.com/photo-1540555700478-4be289fbecef?w=500&auto=format&fit=crop&q=60",
                "description": "Lulur tradisional Bali dengan aroma bunga kamboja alami merelaksasi tubuh."
            }
        ]
    },
    {
        "name": "Bolu Gulung Meranti Medan",
        "category": "Kuliner & Snack",
        "address": "Jl. Kruing No. 2K, Sekip, Medan Petisah",
        "city": "Medan",
        "province": "Sumatera Utara",
        "latitude": 3.5952,
        "longitude": 98.6722,
        "phone": "+62 61-4538212",
        "whatsapp": "628116088212",
        "instagram_handle": "bolumeranti_official",
        "tokopedia_url": "https://tokopedia.com/merantiofficial",
        "shopee_url": "https://shopee.co.id/merantimedan",
        "rating": 4.9,
        "reviews_count": 5300,
        "source": "verified_umkm",
        "products": [
            {
                "title": "Bolu Gulung Spesial Keju Kraft Lumer Medan",
                "price": 85000,
                "original_price": 95000,
                "rating": 4.9,
                "sold_count": 18900,
                "platform": "tokopedia",
                "image_url": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=500&auto=format&fit=crop&q=60",
                "description": "Oleh-oleh nomor 1 Kota Medan dengan parutan keju melimpah luar dan dalam."
            }
        ]
    },
    {
        "name": "Keripik Apel Batu Mandiri",
        "category": "Kuliner & Snack",
        "address": "Jl. Diponegoro No. 45, Sisir, Batu",
        "city": "Malang",
        "province": "Jawa Timur",
        "latitude": -7.8712,
        "longitude": 112.5271,
        "phone": "+62 341-591234",
        "whatsapp": "6281234889911",
        "instagram_handle": "keripikapel_batu",
        "tokopedia_url": "https://tokopedia.com/apelbatumandiri",
        "shopee_url": "https://shopee.co.id/keripikbatu",
        "rating": 4.8,
        "reviews_count": 920,
        "source": "verified_umkm",
        "products": [
            {
                "title": "Keripik Buah Apel Manalagi Asli Batu Vacuum Frying 100g",
                "price": 18000,
                "original_price": 22000,
                "rating": 4.8,
                "sold_count": 8700,
                "platform": "tokopedia",
                "image_url": "https://images.unsplash.com/photo-1568702846914-96b305d2aaeb?w=500&auto=format&fit=crop&q=60",
                "description": "Diproduksi dengan metode vacuum frying menjaga vitamin dan rasa manis alami buah apel."
            }
        ]
    },
    {
        "name": "Tenun Ikat Toraja Heritage",
        "category": "Kriya & Kerajinan",
        "address": "Jl. Poros Rantepao No. 12, Rantepao",
        "city": "Makassar",
        "province": "Sulawesi Selatan",
        "latitude": -5.1477,
        "longitude": 119.4327,
        "phone": "+62 423-21456",
        "whatsapp": "6285242338877",
        "instagram_handle": "torajaheritage_ikat",
        "tokopedia_url": "https://tokopedia.com/torajatenun",
        "shopee_url": "https://shopee.co.id/tenuntoraja",
        "rating": 4.9,
        "reviews_count": 480,
        "source": "verified_umkm",
        "products": [
            {
                "title": "Kain Tenun Ikat Asli Toraja Pewarna Alam 200x100cm",
                "price": 450000,
                "original_price": 520000,
                "rating": 4.9,
                "sold_count": 390,
                "platform": "tokopedia",
                "image_url": "https://images.unsplash.com/photo-1607344645866-009c320c5ab8?w=500&auto=format&fit=crop&q=60",
                "description": "Tenun tangan tradisional motif Pa'sekong Kandaure dengan benang katun dan pewarna dedaunan hutan."
            }
        ]
    },
    {
        "name": "Sepatu Kulit Cibaduyut Mastercraft",
        "category": "Fashion & Sepatu",
        "address": "Jl. Cibaduyut Raya No. 112, Bojongloa Kidul",
        "city": "Bandung",
        "province": "Jawa Barat",
        "latitude": -6.9538,
        "longitude": 107.5925,
        "phone": "+62 22-5401289",
        "whatsapp": "6282119882200",
        "instagram_handle": "cibaduyut_mastercraft",
        "tokopedia_url": "https://tokopedia.com/cibaduyutcraft",
        "shopee_url": "https://shopee.co.id/cibaduyut_boots",
        "rating": 4.8,
        "reviews_count": 1650,
        "source": "verified_umkm",
        "products": [
            {
                "title": "Sepatu Boots Pria Kulit Sapi Asli Goodyear Welted",
                "price": 490000,
                "original_price": 580000,
                "rating": 4.8,
                "sold_count": 2100,
                "platform": "shopee",
                "image_url": "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=500&auto=format&fit=crop&q=60",
                "description": "Handmade leather boots pengrajin legendaris Cibaduyut dengan sol karet anti slip."
            },
            {
                "title": "Sepatu Pantofel Formal Kulit Kilap Derby Oxford",
                "price": 375000,
                "original_price": 430000,
                "rating": 4.9,
                "sold_count": 1450,
                "platform": "tokopedia",
                "image_url": "https://images.unsplash.com/photo-1533867617858-e7b97e060509?w=500&auto=format&fit=crop&q=60",
                "description": "Sepatu formal kantor kulit sapi asli dengan insole empuk memory foam."
            }
        ]
    },
    {
        "name": "Madu Hutan Uray Jakarta Hub",
        "category": "Herbal & Organik",
        "address": "Jl. Senopati No. 64, Kebayoran Baru",
        "city": "Jakarta",
        "province": "DKI Jakarta",
        "latitude": -6.2341,
        "longitude": 106.8115,
        "phone": "+62 21-7278910",
        "whatsapp": "628118080999",
        "instagram_handle": "maduray_id",
        "tokopedia_url": "https://tokopedia.com/maduuray",
        "shopee_url": "https://shopee.co.id/maduurayofficial",
        "rating": 4.9,
        "reviews_count": 8900,
        "source": "verified_umkm",
        "products": [
            {
                "title": "Madu Hutan Murni Grade A Raw Wild Honey 875g",
                "price": 145000,
                "original_price": 160000,
                "rating": 4.9,
                "sold_count": 14500,
                "platform": "tokopedia",
                "image_url": "https://images.unsplash.com/photo-1587049352846-4a222e784d38?w=500&auto=format&fit=crop&q=60",
                "description": "Madu mentah lebah hutan liar Apis Dorsata tanpa pemanasan dan pemanis buatan."
            }
        ]
    },
    {
        "name": "Gudeg Yu Djum Wijilan",
        "category": "Kuliner & Snack",
        "address": "Jl. Wijilan No. 167, Panembahan, Kraton",
        "city": "Yogyakarta",
        "province": "D.I. Yogyakarta",
        "latitude": -7.8052,
        "longitude": 110.3668,
        "phone": "+62 274-375924",
        "whatsapp": "628122756889",
        "instagram_handle": "gudegyudjumwijilan",
        "tokopedia_url": "https://tokopedia.com/gudegyudjum",
        "shopee_url": "https://shopee.co.id/yudjumwijilan",
        "rating": 4.9,
        "reviews_count": 6700,
        "source": "verified_umkm",
        "products": [
            {
                "title": "Gudeg Kaleng Yu Djum Komplit Telur & Ayam Suwir 210g",
                "price": 48000,
                "original_price": 55000,
                "rating": 4.9,
                "sold_count": 11200,
                "platform": "tokopedia",
                "image_url": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500&auto=format&fit=crop&q=60",
                "description": "Gudeg kering khas Wijilan Jogja dalam kemasan kaleng steril tahan 1 tahun tanpa pengawet."
            }
        ]
    }
]

def seed_database():
    db = DatabaseManager()
    print("Populating database with realistic Indonesian UMKM dataset...")
    
    total_added_umkm = 0
    total_added_prods = 0
    
    for item in SAMPLE_UMKMS:
        prods = item.pop("products", [])
        umkm = UMKM(**item)
        umkm_id = db.add_or_update_umkm(umkm)
        total_added_umkm += 1
        
        for p in prods:
            prod = Product(umkm_id=umkm_id, **p)
            db.add_product(prod)
            total_added_prods += 1

    print(f"Successfully seeded {total_added_umkm} UMKMs and {total_added_prods} products.")

if __name__ == "__main__":
    seed_database()
