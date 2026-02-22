import os
from PIL import Image # pip install Pillow

def get_files():
    structure = {}
    base_path = 'photos'
    for root, dirs, files in os.walk(base_path):
        category = os.path.basename(root)
        if category == 'photos' or category.startswith('.'): continue
        
        valid_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.mp4'))]
        if valid_files:
            structure[category] = [os.path.join(root, f) for f in valid_files]
    return structure

def generate_html(data):
    # Здесь мы создаем блоки для каждой папки динамически
    sections_html = ""
    for category, files in data.items():
        sections_html += f'<section class="py-20 fade-in"><h2 class="text-3xl uppercase mb-10">{category}</h2>'
        sections_html += '<div class="grid grid-cols-2 md:grid-cols-4 gap-4">'
        
        for file in files:
            if file.endswith('.mp4'):
                sections_html += f'''
                <div class="video-wrapper">
                    <video controls><source src="{file}" type="video/mp4"></video>
                </div>'''
            else:
                sections_html += f'<div class="rounded-xl overflow-hidden"><img src="{file}" class="gallery-img"></div>'
        
        sections_html += '</div></section>'
    
    # Читаем шаблон и заменяем метку на сгенерированный код
    with open('template.html', 'r') as f:
        template = f.read()
    
    final_html = template.replace('', sections_html)
    with open('index.html', 'w') as f:
        f.write(final_html)

if __name__ == "__main__":
    data = get_files()
    generate_html(data)