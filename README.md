# ⚡ IONOS PSEUDOCODE - UMG

> **Compilador, Intérprete y Entorno de Desarrollo para Pseudocódigo Interactivo**  
> Proyecto desarrollado para la cátedra de *Autómatas y Lenguajes Formales* de la Universidad Mariano Gálvez de Guatemala.

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

## 🛠️ Tecnologías y Herramientas Utilizadas

El desarrollo del proyecto combina un backend enfocado en el procesamiento del lenguaje y un frontend moderno responsivo:

* **🐍 Python 3.8+:** Lenguaje base para el desarrollo del backend, motor de análisis y servidor de la aplicación.
* **🌶️ Flask:** Framework web ligero utilizado para la gestión de rutas HTTP, APIs REST y renderizado dinámico de la interfaz.
* **🔍 Módulo `re` (Regex):** Motor de Expresiones Regulares para la implementación del Analizador Léxico y extracción de Tokens.
* **🌳 Estrategias AST & GIC:** Construcción manual del Árbol Sintáctico (AST) y logs de derivación basados en Gramáticas Libres de Contexto (GIC).
* **🌐 HTML5 & CSS3:** Interfaz con diseño *Dark Theme* moderno, variables CSS, animaciones y componentes estructurados.
* **⚡ JavaScript ES6+:** Lógica de cliente para la gestión de eventos, manipulado interactivo de tabs, llamadas asíncronas (`fetch`) y generador inteligente para principiantes.
* **🌐 Webbrowser & Threading:** Módulos de Python para la apertura automática e independiente del navegador web al iniciar el servidor local.

---

## 🚀 Requerimientos Funcionales Implementados (RF)

* 📄 **Editor de Pseudocódigo (`RF-1`):** Área de texto interactiva para redacción y edición del algoritmo.
* 🔤 **Definición del Lenguaje (`RF-2`):** Soporte de palabras clave (`INICIO`, `FIN`, `LEER`, `ESCRIBIR`, `SI`, `ENTONCES`, `SINO`, `FINSI`).
* 🔍 **Analizador Léxico (`RF-3`):** Escáner léxico por Regex y generación de la Tabla de Tokens formal.
* 🌳 **Árbol Sintáctico (`RF-4`):** Representación jerárquica visual del flujo sintáctico y reglas de producción aplicadas.
* ⚙️ **Parser Sintáctico (`RF-5`):** Validación gramatical y reporte de errores descriptivos paso a paso por línea.
* 📊 **Tipos de Datos (`RF-6`):** Soporte y control estricto de variables `ENTERO`, `DECIMAL` y `TEXTO`.
* 🧮 **Operaciones Aritméticas (`RF-7`):** Evaluación de expresiones matemáticas (`+`, `-`, `*`, `/`) respetando precedencia.
* 🖥️ **Entrada y Salida (`RF-8`):** Captura de datos mediante prompts intermedios y formato monetario en Quetzales (Q) para números.
* 🛡️ **Ejecución Segura (`RF-10`):** Control de excepciones (bloqueo de división entre cero y referencias nulas).
* 🌱 **Asistente Inteligente:** Motor seguro que traduce lenguaje natural a identificadores válidos en compilación.

---

## 💻 Instrucciones para Iniciar el Proyecto

Sigue estos pasos sencillos para descargar, configurar e iniciar la aplicación en tu equipo local:

### 1. Prerrequisitos
Asegúrate de contar con **Python 3.8** o superior instalado en tu equipo. Puedes verificarlo abriendo la terminal y ejecutando:
```bash
python --version
