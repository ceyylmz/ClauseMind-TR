import http.server
import json

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            try:
                with open('index.html', 'rb') as f:
                    self.wfile.write(f.read())
            except FileNotFoundError:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"index.html dosyasi bulunamadi!")
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        try:
            data = json.loads(post_data)
        except json.JSONDecodeError:
            data = {}
            
        raw_text = data.get('text', '').strip()
        text_lower = raw_text.lower()
        
        # Risk Kuralları Veri Tabanı
        high_risk_map = {
            "süresiz": ("Kullanıcı verisi zaman sınırlaması olmaksızın işlenemez/saklanamaz.", "KVKK Madde 4 (İşlendikleri Amaçla Bağlantılı ve Sınırlı Olma)"),
            "üçüncü taraf": ("Verilerin üçüncü taraflarla paylaşılması açık rıza ve net bilgilendirme gerektirir.", "KVKK Madde 8 (Kişisel Verilerin Aktarılması)"),
            "reklam": ("Kişisel verilerin pazarlama ve reklam amacıyla işlenmesi için ayrı bir açık rıza şarttır.", "6563 sayılı ETK & KVKK Madde 5"),
            "aktar": ("Yurt dışına veya şirketler grup şirketlerine veri aktarımı sıkı yasal şartlara tabidir.", "KVKK Madde 9 (Yurt Dışına Aktarım)"),
            "devredil": ("Fikri mülkiyet ve telif haklarının münhasıran devri kullanıcı aleyhine orantısız bir şarttır.", "6102 sayılı TTK & Tüketici Kanunu Madde 5 (Haksız Şartlar)"),
            "otomatik": ("Otomatik yenileme ve karttan çekim yapılmadan önce açık bilgilendirme yapılmalıdır.", "TKHK Madde 52 (Abonelik Sözleşmeleri)"),
            "feragat": ("Kullanıcı yasal haklarından (tazminat, dava) önceden feragat ettirilemez.", "Türk Borçlar Kanunu Madde 115 (Sorumsuzluk Anlaşması)"),
            "değiştirebilir": ("Tek taraflı sözleşme değiştirme yetkisi haksız şart niteliğindedir.", "Tüketici Sözleşmelerindeki Haksız Şartlar Yönetmeliği")
        }
        
        low_risk_keywords = ["kvkk", "yasal yükümlülük", "silme", "güncelleme", "onay", "6698"]
        
        flagged_words = []
        legal_citations = set()
        detected_risks = []

        # 1. Kırmızı Bayrak ve Mevzuat Tespiti
        for word, (desc, cite) in high_risk_map.items():
            if word in text_lower:
                flagged_words.append(word)
                legal_citations.add(cite)
                detected_risks.append(desc)

        # 2. Risk Karar Motoru & Clause Fixer
        if len(raw_text.split()) < 5 or (("değiştirebilir" in text_lower or "saklı tutar" in text_lower) and len(raw_text.split()) < 8):
            risk_level = "BELİRSİZ (Gri Alan)"
            confidence = 0.45
            explanation = "Metin yetersiz veya çok muğlak. Kesin bir hukuki risk veya güvenli alan kararı verilemiyor."
            suggested_fix = "Sözleşme maddesi daha net ifadelerle yazılmalı; belirsiz kavramlar detaylandırılmalıdır."
            
        elif any(kw in text_lower for kw in low_risk_keywords) and not flagged_words:
            risk_level = "DÜŞÜK RİSK (Güvenli)"
            confidence = 0.92
            explanation = "Yasal mevzuata (KVKK) uyumluluk ve açık kullanıcı hakları tespit edildi."
            legal_citations.add("KVKK Madde 11 (İlgili Kişinin Hakları)")
            suggested_fix = "Mevcut madde kullanıcı haklarını korur niteliktedir, değişiklik gerekmez."
            
        elif flagged_words:
            risk_level = "YÜKSEK RİSK"
            confidence = 0.89
            explanation = "Tespit Edilen İhlaller: " + " ".join(detected_risks)
            suggested_fix = "Şirketimiz, kullanıcı verilerini yalnızca hizmetin ifası amacıyla ve ilgili mevzuata (KVKK) uygun olarak saklar. Kullanıcının açık rızası olmaksızın veriler üçüncü taraflarla paylaşılmaz veya süresiz aktarılamaz."
        else:
            risk_level = "ORTA RİSK / İNCELEME GEREKLİ"
            confidence = 0.65
            explanation = "Genel sözleşme maddesi. Özel bir ihlal tespit edilmedi ancak dikkatle incelenmelidir."
            suggested_fix = "Tarafların yükümlülüklerini daha açık ve şeffaf belirten ek maddeler eklenebilir."

        res = {
            "risk_level": risk_level,
            "confidence_score": confidence,
            "explanation": explanation,
            "flagged_words": list(set(flagged_words)),
            "legal_citations": list(legal_citations),
            "suggested_fix": suggested_fix
        }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(res, ensure_ascii=False).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

if __name__ == '__main__':
    print("ClauseMind TR Asistani baslatildi: http://localhost:5000")
    http.server.HTTPServer(('0.0.0.0', 5000), Handler).serve_forever()