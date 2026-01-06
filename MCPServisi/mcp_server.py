from mcp.server.fastmcp import FastMCP
import requests

# 1. MCP Servisini Başlatıyoruz
mcp = FastMCP("IngilizceAsistani")

# 2. Public API'den Veri Çeken Yardımcı Fonksiyon (Ödevdeki 'request' şartı)
def get_dictionary_data(word: str):
    """
    Free Dictionary API kullanarak kelime verisini çeker.
    Bu kısım ödevindeki 'Public API adresindeki uzak bir adresten sorgu atabilmesi' şartını sağlar.
    """
    api_url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        return None

# 3. MCP Tool Tanımlaması (Ödevdeki 'Tool fonksiyonu' şartı)
@mcp.tool()
def kelime_anlami_getir(word: str) -> str:
    """
    Verilen İngilizce kelimenin anlamını ve örneğini getirir.
    Örnek Kullanım: kelime_anlami_getir("serene")
    """
    
    data = get_dictionary_data(word)
    
    if not data:
        return f"'{word}' kelimesi sözlükte bulunamadı veya API hatası oluştu."

    try:
        # API'den gelen karmaşık JSON'u basit bir metne çeviriyoruz
        first_entry = data[0]
        meaning = first_entry['meanings'][0]['definitions'][0]['definition']
        
        # Eğer örnek cümle varsa onu da alalım
        example = first_entry['meanings'][0]['definitions'][0].get('example', 'Örnek cümle bulunamadı.')
        
        result = f"📖 Kelime: {word}\n💡 Anlamı: {meaning}\n📝 Örnek: {example}"
        return result
        
    except (KeyError, IndexError):
        return f"'{word}' kelimesi için detaylı veri ayrıştırılamadı."

# 4. İstersen basit bir toplama işlemi de ekleyebilirsin (Hocanın örneği için opsiyonel)
@mcp.tool()
def puan_hesapla(mevcut_puan: int, eklenen_puan: int) -> int:
    """
    Öğrencinin puanına yeni puan ekler.
    """
    return mevcut_puan + eklenen_puan

if __name__ == "__main__":
    # Servisi çalıştır
    mcp.run()