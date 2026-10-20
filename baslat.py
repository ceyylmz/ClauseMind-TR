import http.server
import json

HTML_CONTENT = """<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ClauseMind TR - YC RFS 2026 Compliance Agent</title>
    <style>
        :root {
            --bordo: #722F37;
            --bordo-hover: #521420;
            --antrasit: #2B2D37;
            --antrasit-light: #4A4D5C;
            --arkaplan: #F4F4F6;
            --beyaz: #FFFFFF;
            --kirmizi-vurgu: #D9534F;
            --yesil-vurgu: #2E7D32;
        }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: var(--arkaplan); color: var(--antrasit); max-width: 900px; margin: 30px auto; padding: 0 20px; }
        .container { background-color: var(--beyaz); padding: 40px; border-radius: 16px; box-shadow: 0 10px 30px rgba(43, 45, 55, 0.08); border-top: 6px solid var(--bordo); }
        .header-tag { font-size: 11px; font-weight: 700; color: var(--bordo); text-transform: uppercase; letter-spacing: 1.2px; margin-bottom: 8px; }
        h2 { color: var(--antrasit); margin-top: 0; font-size: 28px; margin-bottom: 5px; }
        p.subtitle { color: #666; font-size: 14px; margin-bottom: 25px; line-height: 1.5; }
        
        .workspace { display: grid; grid-template-columns: 1fr; gap: 20px; }
        textarea { width: 100%; height: 160px; padding: 16px; box-sizing: border-box; border-radius: 10px; border: 1px solid #D1D1D6; font-size: 14px; background-color: #FAFAFC; resize: vertical; font-family: inherit; }
        textarea:focus { outline: none; border-color: var(--bordo); background-color: var(--beyaz); box-shadow: 0 0 0 3px rgba(114, 47, 55, 0.1); }
        
        .actions-row { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; }
        button { background-color: var(--bordo); color: var(--beyaz); border: none; padding: 12px 28px; font-size: 15px; font-weight: 600; cursor: pointer; border-radius: 8px; transition: background-color 0.2s, transform 0.1s; }
        button:hover { background-color: var(--bordo-hover); }
        button:active { transform: scale(0.98); }
        
        .preset-buttons { display: flex; gap: 8px; flex-wrap: wrap; }
        .preset-btn { background-color: #EFEFF1; color: var(--antrasit); border: 1px solid #D1D1D6; padding: 6px 12px; font-size: 12px; border-radius: 6px; cursor: pointer; font-weight: 500; }
        .preset-btn:hover { background-color: #E2E2E6; }

        .meta-badges { display: flex; gap: 10px; margin-top: 20px; font-size: 12px; color: #555; flex-wrap: wrap; border-top: 1px solid #eee; padding-top: 15px; }
        .badge { background: #EFEFF1; padding: 4px 10px; border-radius: 4px; font-weight: 600; color: var(--antrasit-light); }

        #result { margin-top: 25px; padding: 25px; background-color: #FAFAFC; border-radius: 12px; border: 1px solid #E4E4E9; display: none; }
        .card { background: white; padding: 18px; border-radius: 8px; border: 1px solid #E0E0E0; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.02); }
        .card-title { font-size: 12px; font-weight: 700; text-transform: uppercase; color: var(--antrasit-light); letter-spacing: 0.5px; margin-bottom: 8px; }
        .highlighted-box { padding: 14px; background: #FFF; border: 1px dashed #CCC; border-radius: 6px; line-height: 1.6; font-size: 14px; }
        .flag { background-color: #FFCDD2; color: #B71C1C; font-weight: bold; padding: 2px 6px; border-radius: 4px; }
        .badge-cite { display: inline-block; background: #E8EAF6; color: #1A237E; padding: 5px 10px; border-radius: 6px; font-size: 12px; margin: 3px; font-weight: 600; }
        .fix-box { background-color: #E8F5E9; border-left: 4px solid var(--yesil-vurgu); padding: 14px; color: #1B5E20; font-size: 14px; border-radius: 6px; line-height: 1.5; }
        #riskLevel { font-weight: bold; padding: 6px 12px; border-radius: 6px; font-size: 13px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header-tag">YC RFS 2026 • Autonomous Regulatory AI Agent</div>
        <h2>ClauseMind TR</h2>
        <p class="subtitle">Türkiye Hukuku (KVKK, ETK, TKHK, TBK) Odaklı Akıllı Sözleşme Denetim ve Revizyon Platformu</p>
        
        <div class="workspace">
            <textarea id="tosText" placeholder="Analiz edilecek sözleşme veya aydınlatma metnini buraya yapıştırın ya da aşağıdaki hazır senaryolardan birini seçin..."></textarea>
            
            <div class="actions-row">
                <div class="preset-buttons">
                    <span style="font-size: 12px; color: #666; align-self: center; font-weight: 600;">Hazır Test:</span>
                    <button class="preset-btn" onclick="loadPreset(1)">Yüksek Risk (Veri Aktarımı)</button>
                    <button class="preset-btn" onclick="loadPreset(2)">Düşük Risk (KVKK Uyumlu)</button>
                    <button class="preset-btn" onclick="loadPreset(3)">Muğlak / Kısa Metin</button>
                </div>
                <button onclick="analyzeText()">Metni Denetle & Analiz Et</button>
            </div>
        </div>

        <div class="meta-badges">
            <span>Desteklenen Standartlar:</span>
            <span class="badge">KVKK (6698)</span>
            <span class="badge">ETK (6563)</span>
            <span class="badge">TKHK (6502)</span>
            <span class="badge">Borçlar Kanunu</span>
        </div>

        <div id="result">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h3 style="margin:0; font-size: 18px;">Denetim & Analiz Raporu</h3>
                <div><strong>Risk Düzeyi:</strong> <span id="riskLevel"></span></div>
            </div>
            <div class="card">
                <div class="card-title">🚩 Kırmızı Bayrak (Red-Flag) Vurguları</div>
                <div id="highlightedText" class="highlighted-box"></div>
            </div>
            <div class="card">
                <div class="card-title">⚖️ İlgili Mevzuat & Yasal Atıflar</div>
                <div id="legalCitations"></div>
            </div>
            <div class="card">
                <div class="card-title">📝 Risk ve Uyum Değerlendirmesi</div>
                <div id="explanation" style="font-size:14px; color:#333; line-height: 1.5;"></div>
            </div>
            <div class="card" style="border:none; padding:0; margin-bottom:0;">
                <div class="card-title">💡 Clause Fixer: Tavsiye Edilen Adil Madde</div>
                <div id="suggestedFix" class="fix-box"></div>
            </div>
        </div>
    </div>

    <script>
        const presets = {
            1: "Şirketimiz, üyelerin site üzerinde gerçekleştirdiği kişisel ve ticari verileri, pazarlama ve reklam faaliyetleri amacıyla yurt dışındaki üçüncü taraf iş ortaklarımızla süresiz olarak paylaşma ve aktarma hakkına sahiptir.",
            2: "Kişisel verileriniz, 6698 sayılı KVKK kapsamındaki yasal yükümlülüklerin yerine getirilmesi amacıyla saklanır. İlgili kişi dilediği zaman veri silme talebinde bulunabilir.",
            3: "Şartlar değiştirilebilir."
        };

        function loadPreset(id) {
            document.getElementById('tosText').value = presets[id];
        }

        async function analyzeText() {
            const rawText = document.getElementById('tosText').value.trim();
            if (!rawText) { alert('Lütfen analiz için bir metin girin!'); return; }
            try {
                const response = await fetch('/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: rawText })
                });
                const data = await response.json();
                const riskSpan = document.getElementById('riskLevel');
                riskSpan.innerText = data.risk_level + ` (%${Math.round(data.confidence_score * 100)})`;
                
                if (data.risk_level.includes("YÜKSEK")) {
                    riskSpan.style.color = "#D9534F"; riskSpan.style.backgroundColor = "#FDF2F2";
                } else if (data.risk_level.includes("DÜŞÜK")) {
                    riskSpan.style.color = "#2E7D32"; riskSpan.style.backgroundColor = "#E8F5E9";
                } else {
                    riskSpan.style.color = "#8A6D3B"; riskSpan.style.backgroundColor = "#FCF8E3";
                }

                let formattedText = rawText;
                if (data.flagged_words && data.flagged_words.length > 0) {
                    data.flagged_words.forEach(word => {
                        const regex = new RegExp(`(${word})`, 'gi');
                        formattedText = formattedText.replace(regex, `<span class="flag">$1</span>`);
                    });
                } else {
                    formattedText = "<em>Metinde kısıtlayıcı veya riskli anahtar kelime bulunamadı.</em>";
                }
                document.getElementById('highlightedText').innerHTML = formattedText;
                
                const citeDiv = document.getElementById('legalCitations');
                if (data.legal_citations && data.legal_citations.length > 0) {
                    citeDiv.innerHTML = data.legal_citations.map(c => `<span class="badge-cite">${c}</span>`).join(' ');
                } else {
                    citeDiv.innerHTML = "<span style='font-size:13px; color:#777;'>Eşleşen kanun maddesi yok.</span>";
                }
                
                document.getElementById('explanation').innerText = data.explanation;
                document.getElementById('suggestedFix').innerText = data.suggested_fix;
                document.getElementById('result').style.display = 'block';
            } catch (error) {
                alert('Sunucuya bağlanırken hata oluştu!');
            }
        }
    </script>
</body>
</html>
"""

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_CONTENT.encode('utf-8'))
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
        
        high_risk_map = {
            "süresiz": ("Kullanıcı verisi zaman sınırlaması olmaksızın işlenemez ve saklanamaz.", "KVKK Madde 4 (Amaçla Sınırlılık)"),
            "üçüncü taraf": ("Verilerin üçüncü taraflarla paylaşılması açık rıza ve net bilgilendirme gerektirir.", "KVKK Madde 8 (Veri Aktarımı)"),
            "reklam": ("Pazarlama ve ticari ileti gönderimi için ayrı açık rıza şarttır.", "6563 Sayılı ETK Madde 6"),
            "aktar": ("Yurt dışına veya ilişkili şirketlere veri aktarımı sıkı yasal şartlara tabidir.", "KVKK Madde 9 (Yurt Dışına Aktarım)"),
            "devredil": ("Fikri hakların veya içerik haklarının münhasıran devri haksız şart niteliğindedir.", "TKHK Madde 5 & TTK"),
            "otomatik": ("Otomatik yenileme ve karttan çekim öncesi açık bilgilendirme yapılmalıdır.", "TKHK Madde 52 (Abonelikler)"),
            "feragat": ("Kullanıcı yasal haklarından veya tazminat talep hakkından önceden feragat ettirilemez.", "TBK Madde 115 (Sorumsuzluk Anlaşması)"),
            "değiştirebilir": ("Tek taraflı sözleşme değiştirme yetkisi haksız şart niteliğindedir.", "Tüketici Sözleşmelerindeki Haksız Şartlar Yönetmeliği")
        }
        low_risk_keywords = ["kvkk", "yasal yükümlülük", "silme", "güncelleme", "onay", "6698", "açık rıza"]
        
        flagged_words = []
        legal_citations = set()
        detected_risks = []

        for word, (desc, cite) in high_risk_map.items():
            if word in text_lower:
                flagged_words.append(word)
                legal_citations.add(cite)
                detected_risks.append(desc)

        if len(raw_text.split()) < 5:
            risk_level = "BELİRSİZ (Yetersiz Metin)"
            confidence = 0.40
            explanation = "Metin karar vermek için çok kısa veya muğlak. Hukuki değerlendirme yapılamadı."
            suggested_fix = "Lütfen değerlendirmek istediğiniz sözleşme maddesini tam ve eksiksiz olarak girin."
        elif any(kw in text_lower for kw in low_risk_keywords) and not flagged_words:
            risk_level = "DÜŞÜK RİSK (Güvenli)"
            confidence = 0.94
            explanation = "Yasal mevzuata (KVKK) uyumluluk ve ilgili kişi hakları tespit edildi."
            legal_citations.add("KVKK Madde 11 (İlgili Kişinin Hakları)")
            suggested_fix = "Mevcut madde kullanıcı haklarını ve mevzuatı korur niteliktedir, revize gerekmez."
        elif flagged_words:
            risk_level = "YÜKSEK RİSK"
            confidence = 0.89
            explanation = "Tespit Edilen İhlaller: " + " ".join(detected_risks)
            suggested_fix = "Şirketimiz, kullanıcı verilerini yalnızca hizmetin ifası amacıyla ve KVKK'ya uygun olarak saklar. Kullanıcının açık rızası olmaksızın veriler üçüncü taraflarla paylaşılmaz veya süresiz aktarılamaz."
        else:
            risk_level = "ORTA RİSK / İNCELEME GEREKLİ"
            confidence = 0.60
            explanation = "Genel sözleşme maddesi. Doğrudan bir ihlal saptanmadı ancak muğlak ifadeler barındırıyor."
            suggested_fix = "Tarafların hak ve yükümlülüklerini daha net belirten ifadeler eklenmesi önerilir."

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
        self.end_headers()

if __name__ == '__main__':
    print("ClauseMind TR (YC RFS 2026 Agent) baslatildi: http://localhost:5000")
    http.server.HTTPServer(('0.0.0.0', 5000), Handler).serve_forever()