# ⚡ IONOS Pseudocode - UMG

> **Aplicación web educativa para escribir, analizar y ejecutar pseudocódigo.**  
> Desarrollada con **Python** y **Flask**. La interfaz interactiva de usuario (HTML, CSS y JavaScript) se encuentra integrada directamente dentro de `app.py` mediante plantillas dinámicas.

---

## 🎓 Información Académica

* **🏛️ Universidad:** Universidad Mariano Gálvez de Guatemala (UMG)
* **🏫 Facultad:** Ingeniería en Sistemas de Información y Ciencias de la Computación
* **📍 Sede:** Retalhuleu
* **📚 Curso:** Autómatas y Lenguajes Formales
* **👨‍🏫 Catedrático:** Ing. Guillermo Alexander Pisqui Fuentes
* **👥 Integrantes:**
  * 👨‍💻 **Louis Neil Voyer García** — *(Carné: 2890-24-16741)*
  * 👨‍💻 **José Aimar López Bolaños** — *(Carné: 2890-24-12732)*

---

## 🚀 Funcionalidades Incluidas

* 📄 **Editor Web Interactivo:** Espacio para redactar y modificar pseudocódigo en tiempo real.
* 🔍 **Analizador Léxico (RF-3):** Escaneo y clasificación automática de tokens.
* ⚙️ **Diagnóstico y Análisis Sintáctico (RF-5):** Validación descriptiva de instrucciones con reporte detallado de errores.
* 📊 **Gestión de Tipos de Datos (RF-6):** Declaración e inicialización estricta de variables (`ENTERO`, `DECIMAL`, `TEXTO`).
* ⌨️ **Captura de Datos (RF-8):** Interacción dinámica por teclado mediante sentencias `LEER`.
* 🧮 **Asignación y Aritmética (RF-7):** Operaciones matemáticas jerárquicas con el operador `<-`.
* 🖥️ **Consola de Salida:** Muestra de resultados procesados con comandos `ESCRIBIR`.
* 📜 **Gramática GIC (RF-4):** Registro completo de derivaciones según la Gramática Independiente del Contexto.
* 🌳 **Árbol Sintáctico (RF-4):** Representación jerárquica visual del flujo sintáctico y procedimientos de ejecución.
* 💡 **Asistente e Instructor para Principiantes:** Manual integrado, presets rápidos y traducción segura de lenguaje natural.

> 📌 **Nota:** El código fuente contiene palabras reservadas adicionales como `SI`, `ENTONCES` y `SINO`, pero la ejecución de estructuras condicionales no está implementada en el intérprete actual. La sintaxis admitida debe seguir las normas del manual de la aplicación.

---

## 🛠️ Tecnologías y Herramientas Utilizadas

| Tecnología / Herramienta | Uso e Implementación Técnica |
| :--- | :--- |
| **🐍 Python 3** | Lenguaje principal del backend y motor del intérprete. |
| **🌶️ Flask** | Servidor web y API de rutas HTTP (`/` y `/run`). |
| **📄 Archivo `requirements.txt`** | Control de dependencias de librerías para instalación del entorno. |
| **🌐 HTML5** | Estructura semántica de la interfaz de usuario. |
| **🎨 CSS3** | Diseños visuales, animación y temas oscuros (*Dark Mode*). |
| **⚡ JavaScript (ES6+)** | Lógica de cliente, control de tabs, llamadas `fetch` e interactividad. |
| **🔍 Expresiones Regulares (`re`)** | Motor de reconocimiento, análisis léxico y tokenización. |
| **🐙 Git & GitHub** | Control de versiones y alojamiento remoto del repositorio. |
| **💻 VS Code** | Entorno de desarrollo integrado (IDE) recomendado. |

*La interfaz carga las fuentes **Inter** y **Fira Code** desde Google Fonts cuando hay conexión a Internet. Funciona normalmente sin conexión con tipografías del sistema.*

---

## 📌 Requisitos Previos

* **Python 3.10** o superior.
* **`pip`** (Administrador de paquetes de Python).
* Un navegador web actualizado.
* Conexión a Internet opcional (únicamente para cargar tipografías web).

---

## 💻 Instalación e Inicio Local

### 🪟 Windows (PowerShell o CMD)

1. **Clonar o descargar el repositorio:**
   ```bash
   git clone [https://github.com/lvoyerg-cloud/ionos-pseudocode.git](https://github.com/lvoyerg-cloud/ionos-pseudocode.git)
   cd ionos-pseudocode
Crear un entorno virtual:

PowerShell
python -m venv .venv
Activar el entorno virtual:

PowerShell:

PowerShell
.\.venv\Scripts\Activate.ps1
CMD:

DOS
.venv\Scripts\activate.bat
Instalar dependencias (requirements.txt):

PowerShell
pip install -r requirements.txt
Iniciar la aplicación:

PowerShell
python app.py
Acceso Web:

La aplicación abrirá automáticamente tu navegador. Si no sucede, ingresa a:

👉 http://127.0.0.1:5000/

🐧 🍎 Linux o macOS
Bash
# 1. Crear y activar entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar servidor
python app.py
Accede desde tu navegador a http://127.0.0.1:5000/.

Para detener el servidor en cualquier SO, presiona Ctrl + C en la terminal.

📂 Estructura del Repositorio
Plaintext
ionos-pseudocode/
├── app.py              # Aplicación principal, servidor Flask e interfaz
├── requirements.txt    # Lista de dependencias del proyecto (Flask, etc.)
├── README.md           # Documentación y manual del repositorio
└── .gitignore          # Filtros de archivos excluidos para Git
📖 Ejemplo de Pseudocódigo
Plaintext
INICIO
  DECIMAL subtotal
  DECIMAL bono
  DECIMAL total

  LEER subtotal
  LEER bono

  total <- subtotal + bono

  ESCRIBIR total
FIN
Al ejecutar este algoritmo, el sistema solicitará interactivamente los valores y desplegará los resultados en la consola con su respectivo formato monetario (Quetzales).

📜 Licencia y Uso
Proyecto realizado con fines académicos para el curso de Autómatas y Lenguajes Formales de la Universidad Mariano Gálvez de Guatemala.


4. Presiona el botón verde **"Commit changes..."** arriba a la derecha.
5. Vuelve a dar clic en **"Commit changes"** en la ventana emergente.

Haciéndolo así desde la web de GitHub queda actualizado al instante y te ahorras cualquier problema con el CMD.
