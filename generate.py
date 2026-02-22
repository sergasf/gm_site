import os
import subprocess
import webbrowser
from PIL import Image

def update_exif_metadata(path):
    """Добавляет авторскую метку в EXIF метаданные изображения, если её там нет."""
    try:
        # Открываем изображение
        img = Image.open(path)
        exif = img.getexif()
        
        # 0x010e — это стандартный тег ImageDescription (Описание изображения)
        description = exif.get(0x010e)
        marker = "southbearstudio generated 2026"
        
        if not description or marker not in str(description):
            exif[0x010e] = marker
            # Сохраняем изображение с обновленным EXIF (перезаписывает оригинал)
            img.save(path, exif=exif, quality=95, subsampling=0)
            print(f"   ✍️ Метаданные обновлены: {os.path.basename(path)}")
    except Exception as e:
        print(f"   ⚠️ Не удалось обновить EXIF для {os.path.basename(path)}: {e}")

def get_video_dimensions(path):
    try:
        w = subprocess.check_output(f"mdls -name kMDItemPixelWidth -raw '{path}'", shell=True).decode()
        h = subprocess.check_output(f"mdls -name kMDItemPixelHeight -raw '{path}'", shell=True).decode()
        return int(w), int(h)
    except:
        return 1280, 720

def get_image_dimensions(path):
    try:
        with Image.open(path) as img:
            return img.size
    except:
        return 800, 600

def get_aspect_class(width, height):
    ratio = width / height
    if 0.9 <= ratio <= 1.1: return "gallery-item--square"
    if ratio < 0.9: return "" # Портрет
    if ratio > 1.6: return "gallery-item--wide"
    return ""

def generate():
    project_root = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.join(project_root, 'photos')
    
    translate = {
        'beds': 'Кровати', 'chairs': 'Кресла', 'interior': 'Интерьер',
        'kitchen': 'Кухни', 'materials': 'Материалы', 'sofas': 'Диваны', 
        'wardrobes': 'Шкафы'
    }

    if not os.path.exists(base_dir):
        print(f"❌ Папка 'photos' не найдена!")
        return

    categories = sorted([d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d)) and not d.startswith('.')])

    # Стилизация и Lightbox
    css = """
    :root {
      --bg: #0e0e0e; --surface: #161616; --border: #2a2a2a;
      --text: #e8e2d9; --text-muted: #7a7570; --accent: #c8a96e;
    }
    html { scroll-behavior: smooth; }
    body { background: var(--bg); color: var(--text); font-family: 'Montserrat', sans-serif; font-weight: 300; line-height: 1.7; margin: 0; }
    
    nav { position: fixed; top: 0; left: 0; right: 0; z-index: 100; display: flex; align-items: center; justify-content: space-between; padding: 18px 48px; background: rgba(14,14,14,0.92); backdrop-filter: blur(12px); border-bottom: 1px solid var(--border); }
    .nav-logo img { height: 32px; filter: invert(1) brightness(0.9); }
    .nav-links { display: flex; gap: 28px; list-style: none; }
    .nav-links a { color: var(--text-muted); text-decoration: none; font-size: 11px; letter-spacing: 0.12em; text-transform: uppercase; transition: color 0.3s; }
    .nav-links a:hover { color: var(--accent); }

    .hero { min-height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 120px 48px; position: relative; }
    .hero-logo { width: min(420px, 80vw); filter: invert(1) brightness(0.95); margin-bottom: 40px; }
    .hero-tagline { font-family: 'Cormorant Garamond', serif; font-size: clamp(18px, 2.5vw, 26px); font-style: italic; color: var(--text-muted); letter-spacing: 0.04em; }
    .hero-divider { width: 60px; height: 1px; background: var(--accent); margin: 32px auto; }
    .hero-sub { font-size: 12px; letter-spacing: 0.18em; text-transform: uppercase; color: var(--text-muted); }

    .section-wrap { padding: 100px 48px; max-width: 1280px; margin: 0 auto; }
    .section-header { display: flex; align-items: baseline; gap: 24px; margin-bottom: 60px; border-bottom: 1px solid var(--border); padding-bottom: 24px; }
    .section-num { font-family: 'Cormorant Garamond', serif; font-size: 13px; color: var(--accent); }
    .section-title { font-family: 'Cormorant Garamond', serif; font-size: clamp(32px, 4vw, 52px); font-weight: 300; flex: 1; }

    .gallery { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 4px; }
    .gallery-item { aspect-ratio: 3/4; overflow: hidden; background: var(--surface); cursor: pointer; }
    .gallery-item--wide { aspect-ratio: 2/1; grid-column: span 2; }
    .gallery-item--square { aspect-ratio: 1/1; }
    .gallery-item img, .gallery-item video { width: 100%; height: 100%; object-fit: cover; transition: transform 0.6s ease; display: block; }
    .gallery-item:hover img { transform: scale(1.05); }

    /* Lightbox */
    .lightbox { display: none; position: fixed; inset: 0; z-index: 200; background: rgba(0,0,0,0.95); align-items: center; justify-content: center; cursor: zoom-out; }
    .lightbox.open { display: flex; }
    .lightbox img { max-width: 90vw; max-height: 90vh; object-fit: contain; }

    .contact-section { text-align: center; padding: 120px 48px; border-top: 1px solid var(--border); }
    .contact-title { font-family: 'Cormorant Garamond', serif; font-size: clamp(28px, 3.5vw, 44px); font-weight: 300; margin-bottom: 40px; }
    .contact-link { display: inline-block; padding: 14px 40px; border: 1px solid var(--accent); color: var(--accent); text-decoration: none; font-size: 11px; letter-spacing: 0.16em; text-transform: uppercase; transition: 0.3s; }
    .contact-link:hover { background: var(--accent); color: var(--bg); }
    
    footer { padding: 40px 48px; border-top: 1px solid var(--border); display: flex; justify-content: space-between; font-size: 10px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 2px; }
    footer img { height: 20px; filter: invert(1) brightness(0.5); }
    @media (max-width: 600px) { .nav-links { display: none; } .section-wrap { padding: 60px 20px; } }
    """

    nav_links = "".join([f'<li><a href="#{cat}">{translate.get(cat, cat)}</a></li>' for cat in categories])

    html_start = f'''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>South Bear Studio</title>
    <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;1,300&family=Montserrat:wght@300;400&display=swap" rel="stylesheet">
    <style>{css}</style>
</head>
<body>
    <div class="lightbox" id="lightbox" onclick="this.classList.remove('open')">
        <img id="lightbox-img" src="">
    </div>

    <nav>
        <a class="nav-logo" href="#"><img src="photos/logo.png" alt="Logo"></a>
        <ul class="nav-links">{nav_links}<li><a href="#contact">Контакты</a></li></ul>
    </nav>

    <div class="hero">
        <img class="hero-logo" src="photos/logo.png" alt="South Bear Studio">
        <p class="hero-tagline">Интерьеры и мебель под заказ</p>
        <div class="hero-divider"></div>
        <p class="hero-sub">Гуанчжоу · Проектирование · Поставки</p>
    </div>
    <main>'''

    sections_html = ""
    for idx, cat in enumerate(categories, 1):
        cat_path = os.path.join(base_dir, cat)
        files = sorted([f for f in os.listdir(cat_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.mp4'))])
        if not files: continue
        
        print(f"👉 Обработка раздела: {cat}")
        sections_html += f'''
        <div class="section-wrap" id="{cat}">
            <div class="section-header">
                <span class="section-num">{idx:02d}</span>
                <h2 class="section-title">{translate.get(cat, cat)}</h2>
            </div>
            <div class="gallery">'''
        
        for file in files:
            path = f"photos/{cat}/{file}"
            full_path = os.path.join(cat_path, file)
            is_video = file.lower().endswith('.mp4')
            
            # Обновляем EXIF для изображений
            if not is_video:
                update_exif_metadata(full_path)
            
            w, h = get_video_dimensions(full_path) if is_video else get_image_dimensions(full_path)
            cls = get_aspect_class(w, h)
            
            if is_video:
                sections_html += f'<div class="gallery-item {cls}"><video autoplay muted loop playsinline><source src="{path}" type="video/mp4"></video></div>'
            else:
                sections_html += f'''
                <div class="gallery-item {cls}" onclick="openLightbox('{path}')">
                    <img src="{path}" alt="" loading="lazy">
                </div>'''
        
        sections_html += '</div></div>'

    html_end = '''
    </main>
    <div class="contact-section" id="contact">
        <h2 class="contact-title">Обсудим ваш проект?</h2>
        <a class="contact-link" href="mailto:info@southbearstudio.com">Написать нам</a>
    </div>
    <footer>
        <img src="photos/logo.png" alt="">
        <span>© 2026 South Bear Studio</span>
    </footer>
    <script>
        function openLightbox(src) {
            document.getElementById('lightbox-img').src = src;
            document.getElementById('lightbox').classList.add('open');
        }
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') document.getElementById('lightbox').classList.remove('open');
        });
    </script>
</body></html>'''

    output_path = os.path.join(project_root, 'index.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_start + sections_html + html_end)
    
    print(f"✅ Готово. Обновленный сайт: {output_path}")
    webbrowser.open(f"file://{output_path}")

if __name__ == "__main__":
    generate()