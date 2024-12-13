import sqlite3
from abc import ABC, abstractmethod
from typing import List, Optional
import sys
import unittest
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog, ttk
import logging
from unittest.mock import MagicMock

# -------------------- Configuración de Logging --------------------

# Configuración básica de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("task_manager.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

# -------------------- Entidades --------------------

class Task:
    """
    Entidad que representa una tarea en la aplicación.

    En la Clean Architecture, las entidades son objetos de negocio que
    encapsulan las reglas de negocio más generales y son independientes
    de cualquier framework o tecnología externa.
    """

    def __init__(self, id: Optional[int], description: str):
        self.id: Optional[int] = id
        self.description: str = description

    def __str__(self):
        return f"{self.id}: {self.description}"


# -------------------- Casos de Uso --------------------

class TaskRepository(ABC):
    """
    Interfaz abstracta para el repositorio de tareas.

    Define los métodos que cualquier implementación de repositorio
    debe proporcionar. Esto permite que los casos de uso dependan
    de abstracciones en lugar de implementaciones concretas, siguiendo
    el principio de inversión de dependencias.
    """

    @abstractmethod
    def add_task(self, task: Task) -> None:
        """Agrega una nueva tarea al repositorio."""
        pass

    @abstractmethod
    def get_all_tasks(self) -> List[Task]:
        """Obtiene todas las tareas del repositorio."""
        pass

    @abstractmethod
    def delete_task(self, task_id: int) -> None:
        """Elimina una tarea del repositorio por su ID."""
        pass


class AddTaskUseCase:
    """
    Caso de uso para agregar una nueva tarea.

    Los casos de uso contienen la lógica específica de la aplicación y
    coordinan las interacciones entre las entidades y los repositorios.
    """

    def __init__(self, repository: TaskRepository):
        self.repository = repository

    def execute(self, description: str) -> None:
        """
        Ejecuta el caso de uso para agregar una tarea.

        :param description: Descripción de la nueva tarea.
        """
        task = Task(id=None, description=description)
        self.repository.add_task(task)
        logging.info(f'Tarea agregada: "{description}"')


class ListTasksUseCase:
    """
    Caso de uso para listar todas las tareas.
    """

    def __init__(self, repository: TaskRepository):
        self.repository = repository

    def execute(self) -> List[Task]:
        """
        Ejecuta el caso de uso para listar todas las tareas.

        :return: Lista de tareas.
        """
        tasks = self.repository.get_all_tasks()
        logging.info(f'Listado de tareas: {len(tasks)} encontradas')
        return tasks


class DeleteTaskUseCase:
    """
    Caso de uso para eliminar una tarea específica.
    """

    def __init__(self, repository: TaskRepository):
        self.repository = repository

    def execute(self, task_id: int) -> None:
        """
        Ejecuta el caso de uso para eliminar una tarea por su ID.

        :param task_id: ID de la tarea a eliminar.
        """
        self.repository.delete_task(task_id)
        logging.info(f'Tarea eliminada: ID {task_id}')


# -------------------- Adaptadores de Interfaces --------------------

class InMemoryTaskRepository(TaskRepository):
    """
    Implementación de TaskRepository que almacena las tareas en memoria.

    Útil para pruebas rápidas y entornos donde no se requiere persistencia.
    """

    def __init__(self):
        self.tasks: List[Task] = []
        logging.info("Repositorio en memoria inicializado.")

    def add_task(self, task: Task) -> None:
        if self.tasks:
            task.id = max(task.id for task in self.tasks if task.id is not None) + 1
        else:
            task.id = 1
        self.tasks.append(task)
        logging.debug(f'Tarea agregada en memoria: {task}')

    def get_all_tasks(self) -> List[Task]:
        return self.tasks.copy()

    def delete_task(self, task_id: int) -> None:
        original_length = len(self.tasks)
        self.tasks = [task for task in self.tasks if task.id != task_id]
        if len(self.tasks) < original_length:
            logging.debug(f'Tarea con ID {task_id} eliminada del repositorio en memoria.')


class SQLiteTaskRepository(TaskRepository):
    """
    Implementación de TaskRepository que usa SQLite para almacenar las tareas.

    Permite persistencia de datos entre ejecuciones de la aplicación.
    """

    def __init__(self, db_path: str = "tasks.db"):
        """
        Inicializa la conexión a la base de datos.

        :param db_path: Ruta al archivo de la base de datos SQLite.
                        Por defecto, usa "tasks.db" en el directorio actual.
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self._create_table()
        logging.info(f"Repositorio SQLite inicializado en {self.db_path}")

    def _create_table(self):
        """
        Crea la tabla de tareas si no existe.
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL
            )
        ''')
        self.conn.commit()
        logging.debug("Tabla 'tasks' asegurada en la base de datos SQLite.")

    def add_task(self, task: Task) -> None:
        """
        Agrega una nueva tarea a la base de datos.

        :param task: Instancia de Task a agregar.
        """
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO tasks (description) VALUES (?)', (task.description,))
        self.conn.commit()
        task.id = cursor.lastrowid
        logging.debug(f'Tarea agregada a SQLite: {task}')

    def get_all_tasks(self) -> List[Task]:
        """
        Obtiene todas las tareas almacenadas en la base de datos.

        :return: Lista de instancias de Task.
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, description FROM tasks')
        rows = cursor.fetchall()
        tasks = [Task(id=row[0], description=row[1]) for row in rows]
        logging.debug(f'Obtenidas {len(tasks)} tareas de SQLite.')
        return tasks

    def delete_task(self, task_id: int) -> None:
        """
        Elimina una tarea de la base de datos por su ID.

        :param task_id: ID de la tarea a eliminar.
        """
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        self.conn.commit()
        logging.debug(f'Tarea con ID {task_id} eliminada de SQLite.')

    def close(self):
        """
        Cierra la conexión a la base de datos.
        """
        self.conn.close()
        logging.info("Conexión a SQLite cerrada.")


# -------------------- Interfaz Gráfica --------------------

class TaskManagerGUI:
    """
    Interfaz gráfica para gestionar tareas utilizando Tkinter.

    Este componente actúa como el controlador de la interfaz de usuario,
    interactuando con los casos de uso para realizar operaciones.
    """

    def __init__(self, root, repository: TaskRepository):
        self.root = root
        self.root.title("Gestor de Tareas")
        self.root.geometry("500x400")

        self.repository = repository
        self.add_task_use_case = AddTaskUseCase(self.repository)
        self.list_tasks_use_case = ListTasksUseCase(self.repository)
        self.delete_task_use_case = DeleteTaskUseCase(self.repository)

        self.create_widgets()
        self.refresh_task_list()

    def create_widgets(self):
        """
        Crea los componentes de la interfaz gráfica.
        """
        # Frame para agregar tareas
        add_frame = tk.Frame(self.root)
        add_frame.pack(pady=10, padx=10, fill=tk.X)

        self.task_description_var = tk.StringVar()
        tk.Entry(add_frame, textvariable=self.task_description_var, width=50).pack(side=tk.LEFT, padx=5)
        tk.Button(add_frame, text="Agregar Tarea", command=self.add_task).pack(side=tk.LEFT)

        # Lista de tareas usando Treeview
        columns = ('ID', 'Descripción')
        self.tasks_tree = ttk.Treeview(self.root, columns=columns, show='headings')
        self.tasks_tree.heading('ID', text='ID')
        self.tasks_tree.heading('Descripción', text='Descripción')
        self.tasks_tree.column('ID', width=50, anchor=tk.CENTER)
        self.tasks_tree.column('Descripción', width=400, anchor=tk.W)
        self.tasks_tree.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Scrollbar para Treeview
        scrollbar = ttk.Scrollbar(self.tasks_tree, orient=tk.VERTICAL, command=self.tasks_tree.yview)
        self.tasks_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Botón para eliminar tareas
        tk.Button(self.root, text="Eliminar Tarea", command=self.delete_task).pack(pady=5)

    def add_task(self):
        """
        Agrega una nueva tarea utilizando el caso de uso correspondiente.
        """
        try:
            description = self.task_description_var.get().strip()
            if description:
                self.add_task_use_case.execute(description)
                self.task_description_var.set("")  # Limpiar el campo de entrada
                self.refresh_task_list()
                messagebox.showinfo("Éxito", f'Tarea agregada: "{description}"')
            else:
                messagebox.showwarning("Advertencia", "La descripción de la tarea no puede estar vacía.")
        except Exception as e:
            logging.error(f"Error al agregar tarea: {e}")
            messagebox.showerror("Error", f"Se produjo un error al agregar la tarea: {e}")

    def refresh_task_list(self):
        """
        Actualiza la lista de tareas en la interfaz.
        """
        self.tasks_tree.delete(*self.tasks_tree.get_children())
        tasks = self.list_tasks_use_case.execute()
        for task in tasks:
            self.tasks_tree.insert('', tk.END, values=(task.id, task.description))

    def delete_task(self):
        """
        Elimina la tarea seleccionada en la lista.
        """
        selected = self.tasks_tree.selection()
        if selected:
            task_id, description = self.tasks_tree.item(selected[0], 'values')
            confirm = messagebox.askyesno("Confirmar Eliminación", f"¿Está seguro de eliminar la tarea: '{description}'?")
            if confirm:
                try:
                    self.delete_task_use_case.execute(int(task_id))
                    self.refresh_task_list()
                    messagebox.showinfo("Éxito", f'Tarea eliminada: ID {task_id}')
                except Exception as e:
                    logging.error(f"Error al eliminar tarea: {e}")
                    messagebox.showerror("Error", f"Se produjo un error al eliminar la tarea: {e}")
        else:
            messagebox.showwarning("Advertencia", "No se ha seleccionado ninguna tarea para eliminar.")


class StorageSelectionDialog:
    """
    Diálogo para seleccionar el tipo de almacenamiento al iniciar la aplicación.
    """

    def __init__(self, root):
        self.root = root
        self.selected_storage: Optional[str] = None
        self.db_path: str = "tasks.db"  # Ruta por defecto para SQLite

        self.create_widgets()

    def create_widgets(self):
        """
        Crea los componentes del diálogo de selección de almacenamiento.
        """
        self.top = tk.Toplevel(self.root)
        self.top.title("Seleccionar Almacenamiento")
        self.top.geometry("300x150")
        self.top.grab_set()  # Bloquear interacción con otras ventanas

        tk.Label(self.top, text="Seleccione el tipo de almacenamiento:", font=("Arial", 12)).pack(pady=10)

        btn_frame = tk.Frame(self.top)
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="Memoria", width=15, command=self.select_memory).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="SQLite", width=15, command=self.select_sqlite).pack(side=tk.LEFT, padx=5)

        tk.Button(self.top, text="Salir", command=self.top.destroy).pack(pady=10)

    def select_memory(self):
        """
        Selecciona el almacenamiento en memoria.
        """
        self.selected_storage = 'memory'
        self.top.destroy()

    def select_sqlite(self):
        """
        Selecciona el almacenamiento en SQLite y permite al usuario elegir la ruta de la base de datos.
        """
        db_path = filedialog.asksaveasfilename(
            parent=self.top,
            defaultextension=".db",
            filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")],
            title="Seleccione la ruta para la base de datos SQLite"
        )
        if db_path:
            self.selected_storage = 'sqlite'
            self.db_path = db_path
            self.top.destroy()
        else:
            messagebox.showwarning("Advertencia", "No se ha seleccionado una ruta para la base de datos.")

    def get_selection(self) -> (Optional[str], str):
        """
        Retorna el tipo de almacenamiento seleccionado y la ruta de la base de datos si es SQLite.

        :return: Tuple con el tipo de almacenamiento y la ruta de la base de datos.
        """
        self.root.wait_window(self.top)
        return self.selected_storage, self.db_path


# -------------------- Pruebas Unitarias --------------------

class TestInMemoryTaskRepository(unittest.TestCase):
    """
    Pruebas unitarias para InMemoryTaskRepository.

    Asegura que las operaciones de agregar, obtener y eliminar tareas funcionen correctamente.
    """

    def setUp(self):
        self.repo = InMemoryTaskRepository()

    def test_add_and_get_tasks(self):
        task = Task(1, 'Test tarea')
        self.repo.add_task(task)
        tasks = self.repo.get_all_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].description, 'Test tarea')

    def test_delete_task(self):
        self.repo.add_task(Task(1, 'Tarea 1'))
        self.repo.add_task(Task(2, 'Tarea 2'))
        self.repo.delete_task(1)
        tasks = self.repo.get_all_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].id, 2)


class TestSQLiteTaskRepository(unittest.TestCase):
    """
    Pruebas unitarias para SQLiteTaskRepository.

    Utiliza una base de datos en memoria para evitar efectos secundarios y
    asegura que las operaciones de agregar, obtener y eliminar tareas funcionen correctamente.
    """

    def setUp(self):
        # Usa una base de datos en memoria para pruebas rápidas y aisladas
        self.repo = SQLiteTaskRepository(":memory:")

    def test_add_and_get_tasks(self):
        task = Task(id=None, description='Test tarea SQLite')
        self.repo.add_task(task)
        tasks = self.repo.get_all_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].description, 'Test tarea SQLite')
        self.assertIsNotNone(tasks[0].id)

    def test_delete_task(self):
        task1 = Task(id=None, description='Tarea 1 SQLite')
        task2 = Task(id=None, description='Tarea 2 SQLite')
        self.repo.add_task(task1)
        self.repo.add_task(task2)
        tasks = self.repo.get_all_tasks()
        self.repo.delete_task(tasks[0].id)
        tasks_after_deletion = self.repo.get_all_tasks()
        self.assertEqual(len(tasks_after_deletion), 1)
        self.assertEqual(tasks_after_deletion[0].id, tasks[1].id)

    def tearDown(self):
        self.repo.close()


class TestUseCases(unittest.TestCase):
    """
    Pruebas unitarias para los casos de uso.

    Verifica que los casos de uso interactúan correctamente con el repositorio.
    """

    def setUp(self):
        self.repo = InMemoryTaskRepository()
        self.add_use_case = AddTaskUseCase(self.repo)
        self.list_use_case = ListTasksUseCase(self.repo)
        self.delete_use_case = DeleteTaskUseCase(self.repo)

    def test_add_use_case(self):
        self.add_use_case.execute('Nueva tarea')
        tasks = self.list_use_case.execute()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].description, 'Nueva tarea')

    def test_delete_use_case(self):
        self.add_use_case.execute('Tarea a eliminar')
        tasks = self.list_use_case.execute()
        self.assertEqual(len(tasks), 1)
        self.delete_use_case.execute(tasks[0].id)
        tasks_after_deletion = self.list_use_case.execute()
        self.assertEqual(len(tasks_after_deletion), 0)


class TestAddTaskUseCaseWithMock(unittest.TestCase):
    """
    Prueba del caso de uso AddTaskUseCase utilizando un mock para el repositorio.
    """

    def setUp(self):
        self.mock_repo = MagicMock(spec=TaskRepository)
        self.add_use_case = AddTaskUseCase(self.mock_repo)

    def test_execute_calls_add_task(self):
        description = 'Nueva tarea con mock'
        self.add_use_case.execute(description)
        self.mock_repo.add_task.assert_called_once()
        args, kwargs = self.mock_repo.add_task.call_args
        self.assertEqual(args[0].description, description)


# -------------------- Función Principal --------------------

def main():
    """
    Función principal que configura y ejecuta la aplicación.

    Permite al usuario elegir entre ejecutar pruebas o iniciar la interfaz gráfica.
    """
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        # Ejecutar pruebas si el primer argumento es 'test'
        unittest.main(argv=[sys.argv[0]])
    else:
        # Iniciar la interfaz gráfica
        root = tk.Tk()
        root.withdraw()  # Ocultar la ventana principal mientras se selecciona el almacenamiento

        # Mostrar el diálogo de selección de almacenamiento
        storage_dialog = StorageSelectionDialog(root)
        selected_storage, db_path = storage_dialog.get_selection()

        if selected_storage is None:
            # Si el usuario cerró el diálogo sin seleccionar, salir
            logging.info("Aplicación cerrada por el usuario sin seleccionar almacenamiento.")
            sys.exit(0)

        # Seleccionar el repositorio según la selección del usuario
        if selected_storage == 'memory':
            repository = InMemoryTaskRepository()
        else:
            repository = SQLiteTaskRepository(db_path)

        # Mostrar la ventana principal
        root.deiconify()
        app = TaskManagerGUI(root, repository)
        try:
            root.mainloop()
        finally:
            if isinstance(repository, SQLiteTaskRepository):
                repository.close()


if __name__ == '__main__':
    main()
