import os
import subprocess
from PIL import Image

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
    if 0.9 <= ratio <= 1.1: return "aspect-square"
    if ratio < 0.9: return "aspect-[3/4] lg:row-span-2"
    return "aspect-video"

def generate():
    project_root = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.join(project_root, 'photos')
    
    # Словарь для перевода разделов на русский
    translate = {
        'beds': 'Кровати',
        'chairs': 'Кресла',
        'interior': 'Интерьер',
        'kitchen': 'Кухни',
        'materials': 'Материалы',
        'sofas': 'Диваны',
        'wardrobes': 'Шкафы',
        'portfolio': 'Портфолио'
    }

    if not os.path.exists(base_dir):
        print(f"❌ Папка 'photos' не найдена!")
        return

    categories = sorted([d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d)) and not d.startswith('.')])

    # 1. Навигация и Шапка (Hero)
    nav_links = "".join([f'<li><a href="#{cat}" class="hover:text-amber-700 transition-colors">{translate.get(cat, cat).upper()}</a></li>' for cat in categories])

    html_start = f'''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SOUTH BEAR STUDIO | Дизайн и Технологии</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@100;300;400;600&display=swap');
        body {{ font-family: 'Inter', sans-serif; background: #faf9f6; scroll-behavior: smooth; }}
        .fade-in {{ opacity: 0; transform: translateY(20px); transition: all 0.9s ease-out; }}
        .fade-in.visible {{ opacity: 1; transform: translateY(0); }}
    </style>
</head>
<body class="text-stone-900">
    <nav class="fixed top-0 z-50 w-full bg-white/80 backdrop-blur-md border-b border-stone-100 py-5 px-10 flex justify-between items-center">
        <div class="flex items-center gap-3">
            <img src="photos/logo.png" class="h-8 opacity-90" alt="Logo">
            <span class="font-bold tracking-[0.3em] text-[10px] uppercase">South Bear Studio</span>
        </div>
        <ul class="hidden md:flex space-x-8 text-[10px] font-medium tracking-widest text-stone-400">
            {nav_links}
        </ul>
    </nav>

    <header class="relative h-screen flex items-center justify-center bg-stone-950 overflow-hidden">
        <div class="absolute inset-0 grid grid-cols-2 opacity-40">
            <img src="photos/interoir/interior.webp" class="w-full h-full object-cover" alt="Hero 1">
            <img src="photos/interoir/interior2.jpg" class="w-full h-full object-cover" alt="Hero 2">
        </div>
        <div class="absolute inset-0 bg-black/20"></div>
        <div class="relative text-center px-6">
            <h1 class="text-6xl md:text-9xl font-thin text-white mb-6 tracking-tighter uppercase">South Bear</h1>
            <p class="text-amber-500/80 text-[10px] md:text-xs uppercase tracking-[0.8em] font-light">Архитектурные решения для жизни</p>
        </div>
    </header>

    <main class="container mx-auto px-6 py-32">'''

    # 2. Контент
    sections_html = ""
    for cat in categories:
        cat_path = os.path.join(base_dir, cat)
        files = sorted([f for f in os.listdir(cat_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.mp4')) and not f.startswith('.')])
        if not files: continue
        
        sections_html += f'''
        <section id="{cat}" class="mb-40 fade-in">
            <div class="mb-16">
                <h2 class="text-4xl font-light uppercase tracking-[0.4em] text-stone-800">{translate.get(cat, cat)}</h2>
                <div class="h-px w-24 bg-amber-800 mt-4 opacity-30"></div>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-10">'''
        
        for file in files:
            html_path = f"photos/{cat}/{file}"
            full_path = os.path.join(cat_path, file)
            is_video = file.lower().endswith('.mp4')
            w, h = get_video_dimensions(full_path) if is_video else get_image_dimensions(full_path)
            aspect_class = get_aspect_class(w, h)
            
            card_wrap = f'<div class="relative overflow-hidden rounded-[2.5rem] bg-stone-200 shadow-sm group {aspect_class}">'
            if is_video:
                media = f'<video autoplay muted loop playsinline class="w-full h-full object-cover"><source src="{html_path}" type="video/mp4"></video>'
            else:
                media = f'<img src="{html_path}" loading="lazy" class="w-full h-full object-cover transition-transform duration-[2s] group-hover:scale-110">'
            sections_html += f'{card_wrap}{media}</div>'
        
        sections_html += '</div></section>'

    # 3. Подвал с формой
    html_end = '''
    </main>

    <footer class="bg-stone-950 text-white py-32">
        <div class="container mx-auto px-6 grid grid-cols-1 lg:grid-cols-2 gap-24">
            <div class="space-y-8">
                <h2 class="text-4xl font-extralight tracking-widest uppercase">Обсудить проект</h2>
                <p class="text-stone-500 font-light leading-loose max-w-md">
                    Мы создаем пространства в Гуанчжоу и по всему миру. Оставьте заявку, чтобы получить консультацию нашего ведущего дизайнера.
                </p>
                <div class="text-xs tracking-[0.3em] text-stone-600 uppercase">
                    &copy; 2026 South Bear Studio • Design • Tech
                </div>
            </div>
            <form class="space-y-6">
                <input type="text" placeholder="ИМЯ" class="w-full bg-transparent border-b border-stone-800 py-4 outline-none focus:border-amber-800 transition-colors text-xs tracking-widest uppercase">
                <input type="email" placeholder="EMAIL / WECHAT" class="w-full bg-transparent border-b border-stone-800 py-4 outline-none focus:border-amber-800 transition-colors text-xs tracking-widest uppercase">
                <textarea placeholder="ОПИСАНИЕ ЗАДАЧИ" rows="4" class="w-full bg-transparent border-b border-stone-800 py-4 outline-none focus:border-amber-800 transition-colors text-xs tracking-widest uppercase resize-none"></textarea>
                <button class="bg-white text-black px-12 py-4 text-[10px] tracking-[0.4em] uppercase hover:bg-amber-800 hover:text-white transition-all">ОТПРАВИТЬ</button>
            </form>
        </div>
    </footer>

    <script>
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => { if (entry.isIntersecting) entry.target.classList.add('visible'); });
        }, { threshold: 0.1 });
        document.querySelectorAll('.fade-in').forEach(el => observer.observe(el));
    </script>
</body>
</html>'''

    output_path = os.path.join(project_root, 'index.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_start + sections_html + html_end)
    print(f"✅ Готово! Секций переведено: {len(categories)}")

if __name__ == "__main__":
    generate()