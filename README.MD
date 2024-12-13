# Gestor de Tareas con Arquitectura Limpia

## Instalación y Ejecución

Sigue estos pasos para ejecutar la aplicación en tu entorno local:

1. **Clona este repositorio**:
   ```bash
   git clone https://github.com/abdielLopezpy/cleanAndTdd
   ```
2. **Navega al directorio del proyecto**:
   ```bash
   cd 
   ```
3. **Crea y activa un entorno virtual (opcional pero recomendado)**:
   ```bash
   python -m venv venv
   # En Windows
   venv\Scripts\activate
   # En Unix o MacOS
   source venv/bin/activate
   ```
4. **Instala las dependencias necesarias**:
   ```bash
   pip install -r requirements.txt
   ```
   Si no existe un archivo `requirements.txt`, las dependencias principales son:
   ```bash
   pip install tkinter
   ```
5. **Ejecuta la aplicación**:
   ```bash
   python main.py
   ```
   Al ejecutar la aplicación, se te pedirá que selecciones el tipo de almacenamiento:
   - **Memoria**: Las tareas se almacenarán temporalmente en memoria.
   - **SQLite**: Se almacenarán en una base de datos SQLite. Se te pedirá que indiques la ruta donde deseas guardar la base de datos.

6. **Opcional: Ejecutar pruebas unitarias**:
   Para ejecutar las pruebas, usa el siguiente comando:
   ```bash
   python main.py test
   ```

## Requisitos Previos

- Python 3.6 o superior.
- Si usas `tkinter`, asegúrate de que esté instalado. En algunas instalaciones de Python, `tkinter` no se incluye por defecto.

## Notas Adicionales

- Los registros de la aplicación se guardan en el archivo `task_manager.log`.
- Si encuentras algún problema, revisa los registros o abre un issue en el repositorio.

## Arquitectura Limpia

La aplicación está diseñada siguiendo los principios de la **Arquitectura Limpia**, lo que garantiza una separación clara de responsabilidades y facilita el mantenimiento y la escalabilidad del sistema. Las capas principales incluyen:

- **Entidades**: Representan los modelos de negocio y son independientes de cualquier framework o tecnología.
- **Casos de Uso**: Contienen la lógica específica de la aplicación y coordinan las interacciones entre las entidades y los repositorios.
- **Adaptadores de Interfaces**: Implementan las abstracciones definidas en los casos de uso, permitiendo la comunicación con tecnologías externas como bases de datos o interfaces de usuario.

## Desarrollo Guiado por Pruebas (TDD)

El proyecto adopta la metodología de **Desarrollo Guiado por Pruebas (TDD)** para asegurar la calidad y confiabilidad del código. Los pasos principales de TDD seguidos en este proyecto son:

1. **Escribir una prueba que falle**: Define una funcionalidad o mejora específica y crea una prueba que verifique su correcto funcionamiento.
2. **Desarrollar el código mínimo necesario para pasar la prueba**: Implementa únicamente lo necesario para que la prueba pase.
3. **Refactorizar el código**: Mejora la estructura del código sin cambiar su comportamiento, manteniendo las pruebas verdes.
4. **Repetir el ciclo**: Continúa con nuevas funcionalidades siguiendo el mismo proceso.

Este enfoque garantiza que cada componente del sistema esté adecuadamente probado y que el código sea mantenible y extensible.

