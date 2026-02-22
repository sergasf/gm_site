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
    
    print(f"--- СТАРТ ГЕНЕРАЦИИ (БЕЗ ШАБЛОНА) ---")

    if not os.path.exists(base_dir):
        print(f"❌ Ошибка: Папка 'photos' не найдена!")
        return

    # Получаем список категорий
    categories = sorted([
        d for d in os.listdir(base_dir) 
        if os.path.isdir(os.path.join(base_dir, d)) and not d.startswith('.')
    ])

    # 1. Генерируем Навигацию
    nav_links = "".join([f'<li><a href="#{cat}" class="hover:text-black transition-colors">{cat.upper()}</a></li>' for cat in categories])

    # 2. Начало HTML-документа
    html_start = f'''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SOUTH BEAR STUDIO | CATALOG</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@200;300;400;600&display=swap');
        body {{ font-family: 'Inter', sans-serif; background: #fafafa; scroll-behavior: smooth; }}
        .fade-in {{ opacity: 0; transform: translateY(20px); transition: all 0.8s ease-out; }}
        .fade-in.visible {{ opacity: 1; transform: translateY(0); }}
    </style>
</head>
<body class="text-stone-800">
    <nav class="fixed top-0 z-50 w-full bg-white/90 backdrop-blur-md border-b border-stone-100 py-6 px-10 flex justify-between items-center">
        <span class="font-bold tracking-[0.4em] text-sm">SOUTH BEAR STUDIO</span>
        <ul class="hidden md:flex space-x-8 text-[11px] font-medium tracking-widest text-stone-400">
            {nav_links}
        </ul>
    </nav>
    <main class="container mx-auto px-6 pt-32 pb-20">'''

    sections_html = ""

    # 3. Генерация секций с контентом
    for cat in categories:
        cat_path = os.path.join(base_dir, cat)
        files = sorted([
            f for f in os.listdir(cat_path) 
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.mp4')) 
            and not f.startswith('.')
        ])
        
        if not files: continue
        print(f"👉 Обработка: {cat}")

        sections_html += f'''
        <section id="{cat}" class="mb-32 fade-in">
            <h2 class="text-4xl font-extralight uppercase tracking-[0.5em] mb-12 border-b border-stone-100 pb-8">{cat}</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">'''
        
        for file in files:
            html_path = f"photos/{cat}/{file}"
            full_path = os.path.join(cat_path, file)
            is_video = file.lower().endswith('.mp4')
            
            w, h = get_video_dimensions(full_path) if is_video else get_image_dimensions(full_path)
            aspect_class = get_aspect_class(w, h)
            
            common_wrap = f'<div class="relative overflow-hidden rounded-[1.5rem] bg-stone-100 group {aspect_class}">'
            
            if is_video:
                content = f'<video autoplay muted loop playsinline class="w-full h-full object-cover"><source src="{html_path}" type="video/mp4"></video>'
            else:
                content = f'<img src="{html_path}" alt="{file}" loading="lazy" class="w-full h-full object-cover transition-transform duration-[1.5s] group-hover:scale-110">'
            
            sections_html += f'{common_wrap}{content}</div>'
        
        sections_html += '</div></section>'

    # 4. Конец документа
    html_end = '''
    </main>
    <script>
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => { if (entry.isIntersecting) entry.target.classList.add('visible'); });
        }, { threshold: 0.1 });
        document.querySelectorAll('.fade-in').forEach(el => observer.observe(el));
    </script>
</body>
</html>'''

    # Запись итогового файла
    try:
        output_path = os.path.join(project_root, 'index.html')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_start + sections_html + html_end)
        
        final_size = os.path.getsize(output_path) / 1024
        print(f"---")
        print(f"✅ Сборка завершена успешно!")
        print(f"📂 Файл: {output_path}")
        print(f"📊 Итоговый размер: {final_size:.2f} KB")
    except Exception as e:
        print(f"❌ Ошибка записи: {e}")

if __name__ == "__main__":
    generate()