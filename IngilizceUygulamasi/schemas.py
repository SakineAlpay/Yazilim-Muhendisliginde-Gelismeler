# schemas.py
# Bu dosya Swagger dokümantasyonu için veri yapılarını tanımlar

user_schema = {
    "type": "object",
    "properties": {
        "username": {"type": "string", "example": "ogrenci1"},
        "password": {"type": "string", "example": "sifre123"}
    }
}

word_schema = {
    "type": "object",
    "properties": {
        "word": {"type": "string"},
        "meaning": {"type": "string"},
        "level": {"type": "string"}
    }
}