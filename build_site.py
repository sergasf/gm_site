import os
import subprocess
import webbrowser
from PIL import Image

def update_exif_metadata(path):
    """Записывает авторскую метку в ImageDescription."""
    try:
        img = Image.open(path)
        exif = img.getexif()
        marker = "southbearstudio generated 2026"
        if not exif.get(0x010e) or marker not in str(exif.get(0x010e)):
            exif[0x010e] = marker
            img.save(path, exif=exif, quality=95, subsampling=0)
            print(f"   ✍️ EXIF обновлен: {os.path.basename(path)}")
    except Exception as e:
        print(f"   ⚠️ Ошибка EXIF для {os.path.basename(path)}: {e}")

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
    """Определение пропорций как в вашем примере."""
    ratio = width / height
    if 0.9 <= ratio <= 1.1: return "aspect-square"
    if ratio > 1.6: return "aspect-video"
    return "aspect-[3/4] lg:row-span-2" # Вертикальный формат

def generate():
    project_root = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.join(project_root, 'photos')
    
    translate = {
        'beds': 'Кровати', 'chairs': 'Кресла', 'interior': 'Интерьер',
        'kitchen': 'Кухни', 'materials': 'Материалы', 'sofas': 'Диваны', 
        'wardrobes': 'Шкафы', 'portfolio': 'Портфолио'
    }

    if not os.path.exists(base_dir):
        print(f"❌ Ошибка: Папка 'photos' не найдена!")
        return

    categories = sorted([d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d)) and not d.startswith('.')])

    css = """
    :root {
      --bg: #0e0e0e; --surface: #161616; --border: #2a2a2a;
      --text: #e8e2d9; --text-muted: #7a7570; --accent: #c8a96e;
    }
    html { scroll-behavior: smooth; }
    body { background: var(--bg); color: var(--text); font-family: 'Montserrat', sans-serif; font-weight: 300; margin: 0; }
    
    nav { position: fixed; top: 0; left: 0; right: 0; z-index: 100; display: flex; align-items: center; justify-content: space-between; padding: 18px 48px; background: rgba(14,14,14,0.95); backdrop-filter: blur(10px); border-bottom: 1px solid var(--border); }
    .nav-logo img { height: 28px; filter: invert(1); }
    .nav-links { display: flex; gap: 25px; list-style: none; margin: 0; padding: 0; }
    .nav-links a { color: var(--text-muted); text-decoration: none; font-size: 10px; letter-spacing: 0.15em; text-transform: uppercase; transition: 0.3s; }
    .nav-links a:hover { color: var(--accent); }

    /* Hero секция */
    .hero { min-height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 0 48px; background: var(--bg); }
    .hero-logo { width: min(450px, 85vw); filter: invert(1); margin-bottom: 30px; }
    .hero-tagline { font-family: 'Cormorant Garamond', serif; font-size: clamp(20px, 3vw, 28px); font-style: italic; color: var(--text-muted); margin: 0; }
    .hero-divider { width: 50px; height: 1px; background: var(--accent); margin: 30px auto; }
    .hero-sub { font-size: 11px; letter-spacing: 0.2em; text-transform: uppercase; color: var(--text-muted); margin: 0; }

    /* Контентные секции */
    .fade-in { opacity: 0; transform: translateY(20px); transition: all 0.8s ease-out; }
    .fade-in.visible { opacity: 1; transform: translateY(0); }
    
    .section-num { font-family: 'Cormorant Garamond', serif; font-size: 14px; color: var(--accent); }
    
    /* Стили карточек как в вашем запросе */
    .grid-card { position: relative; overflow: hidden; border-radius: 2.5rem; background: #1a1a1a; cursor: pointer; }
    .grid-card img, .grid-card video { width: 100%; height: 100%; object-fit: cover; transition: transform 2s; }
    .grid-card:hover img { transform: scale(1.1); }

    .lightbox { display: none; position: fixed; inset: 0; z-index: 200; background: rgba(0,0,0,0.98); align-items: center; justify-content: center; }
    .lightbox.open { display: flex; }
    .lightbox img { max-width: 95vw; max-height: 95vh; object-fit: contain; }

    .contact-section { text-align: center; padding: 120px 48px; border-top: 1px solid var(--border); }
    .contact-title { font-family: 'Cormorant Garamond', serif; font-size: 40px; font-weight: 300; margin-bottom: 30px; }
    .contact-link { display: inline-block; padding: 15px 45px; border: 1px solid var(--accent); color: var(--accent); text-decoration: none; font-size: 10px; letter-spacing: 0.2em; text-transform: uppercase; transition: 0.3s; }
    .contact-link:hover { background: var(--accent); color: var(--bg); }

    footer { padding: 40px 48px; border-top: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; font-size: 9px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 2px; }
    footer img { height: 18px; filter: invert(1) opacity(0.5); }
    
    @media (max-width: 768px) {
        nav { padding: 15px 20px; }
        .nav-links { display: none; }
        .hero-logo { width: 80vw; }
    }
    """

    nav_links = "".join([f'<li><a href="#{cat}">{translate.get(cat, cat).upper()}</a></li>' for cat in categories])

    html_start = f'''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>South Bear Studio</title>
    <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;1,300&family=Montserrat:wght@300;400&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <style>{css}</style>
</head>
<body>
    <div class="lightbox" id="lightbox" onclick="this.classList.remove('open')"><img id="lightbox-img"></div>
    <nav>
        <a class="nav-logo" href="#top"><img src="photos/logo.png" alt="Logo"></a>
        <ul class="nav-links">{nav_links}<li><a href="#contact">КОНТАКТЫ</a></li></ul>
    </nav>

    <div class="hero" id="top">
        <img class="hero-logo" src="photos/logo.png" alt="South Bear Studio">
        <p class="hero-tagline">Мебель и интерьеры под заказ</p>
        <div class="hero-divider"></div>
        <p class="hero-sub">Производство · Поставки · Проектирование</p>
    </div>
    <main class="container mx-auto px-6 py-32">'''

    sections_html = ""
    for idx, cat in enumerate(categories, 1):
        cat_path = os.path.join(base_dir, cat)
        files = sorted([f for f in os.listdir(cat_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.mp4'))])
        if not files: continue
        
        sections_html += f'''
        <section id="{cat}" class="mb-40 fade-in">
            <div class="mb-16">
                <h2 class="text-4xl font-light uppercase tracking-[0.4em] text-stone-200">{translate.get(cat, cat)}</h2>
                <div class="h-px w-24 bg-amber-800 mt-4 opacity-30"></div>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-10">'''
        
        for file in files:
            path = f"photos/{cat}/{file}"
            full_path = os.path.join(cat_path, file)
            is_video = file.lower().endswith('.mp4')
            if not is_video: update_exif_metadata(full_path)
            
            w, h = get_video_dimensions(full_path) if is_video else get_image_dimensions(full_path)
            cls = get_aspect_class(w, h)
            
            if is_video:
                sections_html += f'''
                <div class="grid-card {cls}">
                    <video autoplay muted loop playsinline class="w-full h-full object-cover">
                        <source src="{path}" type="video/mp4">
                    </video>
                </div>'''
            else:
                sections_html += f'''
                <div class="grid-card {cls}" onclick="openLightbox('{path}')">
                    <img src="{path}" loading="lazy" class="w-full h-full object-cover transition-transform duration-[2s] group-hover:scale-110">
                </div>'''
        
        sections_html += '</div></section>'

    html_end = '''
    </main>
    <div class="contact-section" id="contact">
        <h2 class="contact-title">Обсудим проект</h2>
        <a class="contact-link" href="mailto:info@southbearstudio.com">Написать нам</a>
    </div>
    <footer>
        <img src="photos/logo.png">
        <span>© 2026 South Bear Studio</span>
    </footer>
    <script>
        function openLightbox(src) {
            document.getElementById('lightbox-img').src = src;
            document.getElementById('lightbox').classList.add('open');
        }
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => { if (entry.isIntersecting) entry.target.classList.add('visible'); });
        }, { threshold: 0.1 });
        document.querySelectorAll('.fade-in').forEach(el => observer.observe(el));
    </script>
</body></html>'''

    output_path = os.path.join(project_root, 'index.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_start + sections_html + html_end)
    
    print(f"✨ Сборка завершена успешно.")
    webbrowser.open(f"file://{output_path}")

if __name__ == "__main__":
    generate()