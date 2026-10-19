# 🎵 YT to MP3 Converter

Aplicación de escritorio para Windows que permite convertir videos de YouTube en archivos MP3, incorporando automáticamente metadatos y carátulas cuando están disponibles.

Incluye una interfaz gráfica moderna desarrollada con **Python y PyQt6**, procesamiento mediante una cola de descargas, seguimiento del progreso y herramientas para gestionar la conversión de audio.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![PyQt6](https://img.shields.io/badge/PyQt6-6.7-green)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📋 Tabla de contenido

- [Características](#-características)
- [Tecnologías utilizadas](#️-tecnologías-utilizadas)
- [Requisitos previos](#-requisitos-previos)
- [Instalación](#-instalación-desde-código-fuente)
- [Instalación de FFmpeg](#-instalación-de-ffmpeg)
- [Uso de la aplicación](#-uso-de-la-aplicación)
- [Compilar a ejecutable](#-compilar-a-ejecutable-exe)
- [Estructura del proyecto](#-estructura-del-proyecto)
- [Solución de problemas](#-solución-de-problemas)
- [Consideraciones legales](#️-consideraciones-legales)
- [Licencia](#-licencia)
- [Autor](#-autor)

---

## ✨ Características

- 🚀 **Descargas optimizadas:** soporte para `yt-dlp` y, si está configurado, `aria2c`.
- 📥 **Cola de descargas:** permite procesar varias URL y consultar el estado de cada tarea.
- 🏷️ **Metadatos de audio:** permite incorporar título, artista, álbum y otros campos disponibles.
- 🖼️ **Carátulas:** integración de imágenes en los archivos MP3 cuando se dispone de ellas.
- ⚙️ **Conversión de audio:** procesamiento mediante FFmpeg.
- 🎨 **Interfaz gráfica:** aplicación desarrollada con PyQt6.
- 🧵 **Procesamiento en segundo plano:** uso de hilos de trabajo para mantener la interfaz receptiva.
- ❌ **Gestión de tareas:** controles para detener o cancelar el procesamiento según la implementación disponible.
- 📂 **Carpeta de destino configurable:** selección de la ubicación de los archivos generados.

---

## 🛠️ Tecnologías utilizadas

| Tecnología | Función |
|---|---|
| Python 3.10+ | Lenguaje principal |
| PyQt6 | Interfaz gráfica |
| yt-dlp | Obtención de información y descarga de contenido compatible |
| FFmpeg | Conversión y procesamiento de audio |
| mutagen | Lectura y escritura de metadatos ID3 |
| Pillow | Procesamiento de imágenes |
| PyInstaller | Generación del ejecutable para Windows |
| aria2c | Descargas concurrentes opcionales, si está configurado |

---

## 💻 Requisitos previos

Antes de instalar el proyecto, asegúrate de tener:

- Windows 10 o superior.
- Python 3.10 o superior.
- Git.
- FFmpeg instalado y accesible para la aplicación.
- Una conexión a Internet para obtener el contenido autorizado.

Puedes comprobar las instalaciones desde PowerShell:

```powershell
python --version
git --version
```

---

## 📦 Instalación desde código fuente

### 1. Clonar el repositorio

Reemplaza `TU_USUARIO` por el nombre de usuario o la organización propietaria del repositorio.

```powershell
git clone https://github.com/TU_USUARIO/youtube_to_mp3.git
cd youtube_to_mp3
```

### 2. Crear el entorno virtual

```powershell
python -m venv venv
```

### 3. Activar el entorno virtual

En Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Si PowerShell bloquea la activación del entorno, puedes permitirla temporalmente para la sesión actual:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

### 4. Instalar las dependencias

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Instalar FFmpeg

Sigue las instrucciones de la siguiente sección antes de iniciar la aplicación.

### 6. Ejecutar el programa

Desde la carpeta raíz del proyecto:

```powershell
python main.py
```

---

## ⬇️ Instalación de FFmpeg

**FFmpeg es un requisito para la conversión de audio.** No se incluye directamente en este repositorio debido a su tamaño.

### Opción A: descarga automática mediante PowerShell

Ejecuta los siguientes comandos desde la carpeta raíz del proyecto:

```powershell
New-Item -ItemType Directory -Force -Path "ffmpeg" | Out-Null

Invoke-WebRequest `
    -Uri "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip" `
    -OutFile "ffmpeg\ffmpeg.zip"

Expand-Archive `
    -Path "ffmpeg\ffmpeg.zip" `
    -DestinationPath "ffmpeg" `
    -Force

Remove-Item "ffmpeg\ffmpeg.zip"
```

El archivo ZIP puede extraerse en una subcarpeta. Por ello, comprueba dónde quedaron los ejecutables:

```powershell
Get-ChildItem .\ffmpeg -Recurse -Filter ffmpeg.exe
Get-ChildItem .\ffmpeg -Recurse -Filter ffprobe.exe
```

La aplicación o su configuración debe apuntar a la ubicación real de `ffmpeg.exe`. Si el programa utiliza `ffprobe`, también debe poder localizarlo.

Puedes verificar una instalación de FFmpeg agregada al `PATH` con:

```powershell
ffmpeg -version
```

> **Importante:** descargar y extraer FFmpeg no garantiza que la aplicación lo encuentre automáticamente. La ubicación debe coincidir con la configuración utilizada por el proyecto.

### Opción B: instalación manual

1. Visita [FFmpeg Builds de Gyan](https://www.gyan.dev/ffmpeg/builds/).
2. Descarga una compilación adecuada para Windows.
3. Extrae el archivo descargado.
4. Localiza `ffmpeg.exe` y, si corresponde, `ffprobe.exe`.
5. Configura sus rutas según la implementación de la aplicación.

---

## ▶️ Uso de la aplicación

1. Inicia la aplicación con `python main.py` o abre el ejecutable generado.
2. Introduce una o varias URL compatibles, una por línea.
3. Selecciona la carpeta de destino.
4. Añade las tareas a la cola.
5. Inicia el procesamiento.
6. Espera a que finalicen las tareas y comprueba los archivos generados.

Los metadatos y las carátulas dependen de la información y las imágenes disponibles para cada contenido.

---

## 🏗️ Compilar a ejecutable (.exe)

Puedes empaquetar la aplicación para Windows utilizando PyInstaller.

### 1. Instalar PyInstaller

Activa el entorno virtual e instala la herramienta:

```powershell
pip install pyinstaller
```

### 2. Generar el ejecutable

Si el proyecto incluye `build.spec`, utiliza:

```powershell
pyinstaller build.spec
```

Si el archivo de especificación no existe, puedes generar una compilación básica con:

```powershell
pyinstaller --noconfirm --windowed --name YouTubeToMP3 main.py
```

Este último comando es una alternativa básica; puede requerir ajustes para incluir recursos, módulos, archivos de configuración y FFmpeg.

### 3. Localizar el resultado

El ejecutable normalmente se encontrará en:

```text
dist/
```

Por ejemplo:

```text
dist/YouTubeToMP3.exe
```

**Nota:** la existencia de `build.spec` no garantiza que FFmpeg quede incluido correctamente. Revisa su configuración y prueba el ejecutable en un equipo que no tenga Python instalado.

---

## 📁 Estructura del proyecto

La siguiente estructura es una referencia basada en la organización prevista del repositorio. Ajusta los nombres si tu estructura real es diferente.

```text
youtube_to_mp3/
├── main.py
├── config.py
├── build.spec
├── requirements.txt
├── README.md
├── LICENSE
├── .gitignore
├── core/
│   ├── youtube.py
│   ├── downloader.py
│   ├── metadata.py
│   └── queue.py
├── ui/
│   ├── main_window.py
│   ├── widgets.py
│   └── queue_view.py
├── utils/
│   ├── validators.py
│   └── file_utils.py
├── ffmpeg/                 # Dependencia local, no incluida en Git
└── dist/                   # Archivos compilados, normalmente ignorados
```

---

## 🧰 Solución de problemas

### FFmpeg no encontrado

Comprueba que `ffmpeg.exe` exista y que la aplicación esté configurada para localizarlo. Si se utiliza `ffprobe`, verifica también su ruta.

### Error al instalar dependencias

Comprueba la versión de Python y vuelve a ejecutar:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### La aplicación no inicia

Activa el entorno virtual y ejecuta el programa desde PowerShell para consultar el mensaje de error:

```powershell
python main.py
```

### El ejecutable no funciona en otro equipo

Comprueba las dependencias incluidas, las rutas de los recursos y la configuración de PyInstaller. Prueba la compilación en un entorno limpio.

---

## ⚖️ Consideraciones legales

Este proyecto es una herramienta de software para el procesamiento de audio. El usuario es responsable de utilizarla de acuerdo con la legislación aplicable, los derechos de autor y los términos de servicio de las plataformas de origen.

Descarga o convierte únicamente contenido para el que tengas autorización o cuyo uso esté permitido legalmente.

Este proyecto no está afiliado, patrocinado ni respaldado por YouTube.

---

## 📄 Licencia

Este proyecto se distribuye bajo la licencia **MIT**, siempre que el repositorio incluya el archivo `LICENSE` correspondiente.

Consulta el archivo `LICENSE` para conocer los términos completos de uso, modificación y distribución.

---

## 👨‍💻 Autor

**Jose Rivera**

Proyecto desarrollado con fines académicos y de aprendizaje en desarrollo de software.

---

⭐ Si este proyecto te resulta útil, puedes darle una estrella al repositorio en GitHub.
