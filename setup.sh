#!/bin/bash
# Instala Playwright y los navegadores necesarios en Streamlit Cloud

echo "🔧 Instalando Playwright y navegadores..."
pip install playwright

# Instala Chromium con todas las dependencias necesarias
playwright install chromium --with-deps

echo "✅ Playwright listo para usar."
