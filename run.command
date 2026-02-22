#!/bin/bash
cd "$(dirname "$0")"

# 1. Проверка окружения
if [ ! -d "venv" ]; then
    echo "📦 Создаю venv..."
    python3 -m venv venv
fi

source venv/bin/activate

# 2. Установка Pillow (быстро)
pip install Pillow --quiet

# 3. Запуск
python3 build_site.py

deactivate