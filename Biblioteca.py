#Gestor de prestamos en biblioteca 

import os
import sqlite3
import random
import uuid
import datetime
import pandas as pd
import openpyxl
import bcrypt 
import requests
import json

#variables para factura
libroCurrent = 0

#variables para el inicio de sesión
PasswordTest = 0
PaswordTry = 0
UserTry = ' '
UserCurrent = 0

#Variable para analisis
rank = 0

#Creacion DB
def Create_DataBase():
    conn = sqlite3.connect('bibliotecaDB.db')
    conn.commit()
    conn.close()

#Generador de Ids unicas 
def generar_uuid():
    return str(uuid.uuid4())


#Creación menú
def Menu():
    print("Bienvenido a la biblioteca central\n")
    login()

#función para crear la tabla de usuarios de la base de datos 
def createTableUsers():
    conn = sqlite3.connect("bibliotecaDB.db")
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS USERS (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            user text,
            password integer
            )"""
    )
    conn.commit()
    conn.close()

#función para cargar los usuarios
def addData(user, password): 
    conn = None
    try:
        conn = sqlite3.connect("bibliotecaDB.db")
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(ID) FROM USERS")
        max_id = cursor.fetchone()[0]
        if max_id is None:
            new_id = 1  
        else:
            new_id = max_id + 1  
        cursor.execute("INSERT INTO USERS (ID, user, password) VALUES (?, ?, ?)", (new_id, user, password))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error al agregar usuario: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
    
    
#Creador de usuario 
def UserCreator():
    global UserTry
    os.system("cls")
    while True:
        print("Ingrese el nombre de usuario que desea guardar (máximo 12 letras): ")
        New_User = input().strip()
        if len(New_User) > 12:
            print("Error: El nombre de usuario no debe superar 12 letras. Intente nuevamente.")
        elif not New_User:
            print("Error: El nombre de usuario no puede estar vacío. Intente nuevamente.")
        else:
            break

    while True:
        print("Ingrese la contraseña que desea guardar (solo números): ")
        New_Password = input().strip()
        if New_Password.isdigit():  
            break
        else:
            print("Error: La contraseña debe ser un número. Intente nuevamente.")

    addData(New_User, int(New_Password)) 
    UserTry = New_User
    os.system("pause")
    print("Su usuario ha sido creado, ingrese para tener acceso a los libros")
    login()
    
#función para comparar el nombre y contraseña del usuario con los guardados
def comparer():
    conn = None
    try:
        conn = sqlite3.connect("bibliotecaDB.db")
        cursor = conn.cursor()
        carga = "SELECT password FROM USERS WHERE user = ?"
        cursor.execute(carga, (UserTry,))
        passCom = cursor.fetchone()
        if passCom:
            global PasswordTest
            PasswordTest = passCom[0]
        else:
            print("El usuario no existe.")
            os.system("pause")
            login()
    except sqlite3.Error as e:
        print(f"Error de SQLite: {e}")
    finally:
        if conn:
            conn.close()

#función para iniciar sesión en la DB    (Recordatorio, REVISAR FUNCION DEL CURRENT USER)
def InicioSesion():
    os.system("cls")
    print("Ingrese su nombre de usuario: \n")
    user = input().strip()
    if not user:
        print("El nombre de usuario no puede estar vacío.")
        os.system("pause")
        return InicioSesion()

    global UserTry
    UserTry = str(user)
    try:
        print("Ingrese la contraseña de su usuario\n")
        password = int(input())
    except ValueError:
        print("La contraseña debe ser un número.")
        os.system("pause")
        return InicioSesion()

    comparer()
    global PaswordTry
    global UserCurrent
    PaswordTry = password
    if PasswordTest == PaswordTry:
        print("WELCOME")
        conn = sqlite3.connect("bibliotecaDB.db")
        cursor = conn.cursor()
        carga = f"SELECT ID FROM USERS WHERE user ='{UserTry}'"
        cursor.execute(carga)
        result = cursor.fetchone()
        UserCurrent = result[0] if result else None  
        conn.commit()
        conn.close()
        OpcUser()
    else:
        print("Usuario o contraseña no válidos.")
        os.system("pause")
        return InicioSesion()

#Selector de opciones para inicio de sesión
def login():
    while True:
        print("\nSeleccione una opción:")
        print("1) Iniciar sesión")
        print("2) Crear usuario")
        print("3) Admin")
        print("4) Salir")
        try:
            opc = int(input("Ingrese el número de la opción: "))
            if opc == 1:
                os.system("cls")
                InicioSesion()
                break
            elif opc == 2:
                os.system("cls")
                print("Crear usuario")
                UserCreator()
                break
            elif opc == 3:
                os.system("cls")
                print("Admin")
                admin()
                break
            elif opc == 4:
                os.system("cls")
                raise SystemExit('Cerrando programa')
            else:
                print("Opción no válida. Intente de nuevo.")
        except ValueError:
            print("Por favor, ingrese un número válido.")
            Menu()

#Control SUDO
def admin():
    print("1)Modificar libros\n2)Modificar usuarios")
    opc = int(input())
    if opc == 1:
        print("Carga de libros ")
        cargaLibros()
    elif opc == 2: 
        print("Modificación de usuarios")
    else:
        print("Error")
        os.system("pause")
        admin()

#funcion de carga de libros
def Carga_libros():
    print("1)Cargar libro\n2)Salir")
    opc = int(input())
    if opc == 1: 
        Carga_libros()
    elif opc == 2:
        admin()
    else:
        print("Error")
        login()
        
                
            
#Creación de tablas de generos Y carga de la misma
def Generos():
    conn = sqlite3.connect("bibliotecaDB.db")
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS GENDERS(
            ID_GENDER INTEGER PRIMARY KEY AUTOINCREMENT,
            GENDER TEXT UNIQUE
        )
        """
    )
    conn.commit()
    GENDERS = ['Suspenso', 'Horror', 'Ciencia Ficción', 'Educación', 'Acción', 
               'Drama', 'Comedia', 'Romance', 'Fantasía', 'Biografía', 'Otro']

    for GENDER in GENDERS:
        try:
            cursor.execute("SELECT COUNT(*) FROM GENDERS WHERE GENDER = ?", (GENDER,))
            existe = cursor.fetchone()[0]
            if existe == 0:
                cursor.execute("INSERT INTO GENDERS (GENDER) VALUES (?)", (GENDER,))
        except sqlite3.Error as e:
            print(f"Error al insertar género '{GENDER}': {e}")

    conn.commit()
    conn.close()
    
#Creación de tabla de editoriales
def Editoriales():
    conn = sqlite3.connect("bibliotecaDB.db")
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS EDITORIALES(
            ID_EDITORIAL INTEGER PRIMARY KEY AUTOINCREMENT,
            EDITORIAL TEXT
        )
        """
    )
    conn.commit()
    conn.close()          

#Carga de editoriales
def AddEditorial(Edit): 
    conn = None
    try:
        conn = sqlite3.connect("bibliotecaDB.db")
        cursor = conn.cursor()

        consulta = "SELECT COUNT(*) FROM EDITORIALES WHERE EDITORIAL = ?"
        cursor.execute(consulta, (Edit,))
        existe = cursor.fetchone()[0]
        
        if existe == 0:
            carga = "INSERT INTO EDITORIALES (EDITORIAL) VALUES (?)"
            cursor.execute(carga, (Edit,))
            conn.commit()
            print(f"Editorial '{Edit}' agregada exitosamente.")
        else:
            print(f"La editorial '{Edit}' ya existe en la base de datos.")
    except sqlite3.Error as e:
        print(f"Error al agregar la editorial: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
    
#Creación de tabla de autores
def Autores():
    conn = sqlite3.connect("bibliotecaDB.db")
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS AUTORES(
            ID_AUTOR INTEGER PRIMARY KEY AUTOINCREMENT,
            AUTOR TEXT
        )
        """
    )
    conn.commit()
    conn.close()    

#Carga de autores
def AddAutor(Autor): 
    conn = None
    try:
        conn = sqlite3.connect("bibliotecaDB.db")
        cursor = conn.cursor()

        consulta = "SELECT COUNT(*) FROM AUTORES WHERE AUTOR = ?"
        cursor.execute(consulta, (Autor,))
        existe = cursor.fetchone()[0]
        
        if existe == 0:
            carga = "INSERT INTO AUTORES (AUTOR) VALUES (?)"
            cursor.execute(carga, (Autor,))
            conn.commit()
            print(f"Autor '{Autor}' agregado exitosamente.")
        else:
            print(f"El autor '{Autor}' ya existe en la base de datos.")
    except sqlite3.Error as e:
        print(f"Error al agregar el autor: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
    
    
#Creación de tabla de libros
def Libros():
    conn = sqlite3.connect("bibliotecaDB.db")
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS LIBROS(
            ID_LIBRO INTEGER PRIMARY KEY AUTOINCREMENT,
            LIBRO TEXT,
            DISPONIBLE INTEGER,
            ID_GENERO INTEGER,
            ID_AUTOR INTEGER,
            ID_EDITORIAL INTEGER,
            RANK INTEGER DEFAULT 0,
            SINOPSIS TEXT DEFAULT NULL,
            FOREIGN KEY (ID_EDITORIAL) REFERENCES EDITORIALES(ID_EDITORIAL),
            FOREIGN KEY (ID_AUTOR) REFERENCES AUTORES(ID_AUTOR),
            FOREIGN KEY (ID_GENERO) REFERENCES GENDERS(ID_GENDER)
        )
        """
    )
    conn.commit()
    conn.close()
     
#Carga de libros en el sistema 
def AddBooks(Book, disp, gen, aut, edit):
    conn = None
    try:
        conn = sqlite3.connect("bibliotecaDB.db")
        cursor = conn.cursor()
        consulta = """
            SELECT COUNT(*) FROM LIBROS 
            WHERE LIBRO = ? AND ID_GENERO = ? AND ID_AUTOR = ? AND ID_EDITORIAL = ?
        """
        cursor.execute(consulta, (Book, gen, aut, edit))
        existe = cursor.fetchone()[0]
        if existe > 0:
            print(f"El libro '{Book}' ya existe en la base de datos. No se cargará nuevamente.")
            return
        carga = """
            INSERT INTO LIBROS (LIBRO, DISPONIBLE, ID_GENERO, ID_AUTOR, ID_EDITORIAL) 
            VALUES (?, ?, ?, ?, ?)
        """
        cursor.execute(carga, (Book, disp, gen, aut, edit))
        conn.commit()
        print(f"Libro '{Book}' agregado exitosamente.")
    except sqlite3.Error as e:
        print(f"Error al agregar el libro: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

# Función para cargar autores desde el archivo Excel
def cargaAutoresExcel():
    file_path = "LibrosDB.xlsx"
    try:
        df = pd.read_excel(file_path)
        print("Encabezados del archivo:", df.columns.tolist()) 
        for index, row in df.iterrows():
            AUTOR = row['Autor']
            AddAutor(AUTOR)  
        print("Autores cargados exitosamente.")
    except Exception as e:
        print(f"Error al cargar los autores: {e}")

# Función para cargar editoriales desde el archivo Excel
def cargaEditorialesExcel():
    file_path = "LibrosDB.xlsx"
    try:
        df = pd.read_excel(file_path)
        print("Encabezados del archivo:", df.columns.tolist()) 
        for index, row in df.iterrows():
            EDITORIAL = row['Editorial']
            AddEditorial(EDITORIAL)  
        print("Editoriales cargadas exitosamente.")
    except Exception as e:
        print(f"Error al cargar las editoriales: {e}")

# Función para cargar libros desde el archivo Excel
def cargaLibrosExcel():
    file_path = "LibrosDB.xlsx"
    try:
        df = pd.read_excel(file_path)
        print("Encabezados del archivo:", df.columns.tolist())  
        for index, row in df.iterrows():
            LIBRO = row['Libro']
            AUTOR = row['Autor']
            EDITORIAL = row['Editorial']
            GENERO = row['Genero']

            id_autor = obtener_id_autor(AUTOR)
            if not id_autor:
                continue

            id_genero = obtener_id_genero(GENERO)
            if not id_genero:
                continue

            id_editorial = obtener_id_editorial(EDITORIAL)
            if not id_editorial:
                continue

            AddBooks(LIBRO, 1, id_genero, id_autor, id_editorial)
        print("Libros cargados exitosamente.")
    except Exception as e:
        print(f"Error al cargar los libros: {e}")

# Función para obtener el ID del autor desde la tabla AUTORES
def obtener_id_autor(autor):
    conn = sqlite3.connect("bibliotecaDB.db")
    cursor = conn.cursor()
    consulta = "SELECT ID_AUTOR FROM AUTORES WHERE AUTOR = ?"
    cursor.execute(consulta, (autor,))
    id_autor = cursor.fetchone()
    conn.close()
    if id_autor:
        return id_autor[0]
    else:
        print(f"Error: No se encontró el autor '{autor}' en la tabla AUTORES.")
        return None

# Función para obtener el ID del género desde la tabla GENDERS
def obtener_id_genero(genero):
    conn = sqlite3.connect("bibliotecaDB.db")
    cursor = conn.cursor()
    consulta = "SELECT ID_GENDER FROM GENDERS WHERE GENDER = ?"
    cursor.execute(consulta, (genero,))
    id_genero = cursor.fetchone()
    conn.close()
    if id_genero:
        return id_genero[0]
    else:
        print(f"Error: No se encontró el género '{genero}' en la tabla GENDERS.")
        return None

# Función para obtener el ID de la editorial desde la tabla EDITORIALES
def obtener_id_editorial(editorial):
    conn = sqlite3.connect("bibliotecaDB.db")
    cursor = conn.cursor()
    consulta = "SELECT ID_EDITORIAL FROM EDITORIALES WHERE EDITORIAL = ?"
    cursor.execute(consulta, (editorial,))
    id_editorial = cursor.fetchone()
    conn.close()
    if id_editorial:
        return id_editorial[0]
    else:
        print(f"Error: No se encontró la editorial '{editorial}' en la tabla EDITORIALES.")
        return None
        
#Carga de libros por parte del admin
def cargaLibros():
    print("Bienvenido a la carga de libros, aquí podrá agregar libros nuevos a nuestra biblioteca")
    gen = ' '
    disp = 1
    book = input(print("Introduzca el nombre del libro: "))
    genSelector = int(input(print("Seleccione genero\n1)para suspenso\n2)para horror\n3)para ciencia ficcion\n4)para educacion")))
    if genSelector == 1:    
        gen = 'Suspenso'
    elif genSelector == 2:
        gen = 'Horror'
    elif genSelector == 3:
        gen = 'Ciencia_FIccion'
    elif genSelector == 4: 
        gen = 'Educacion'
    elif genSelector == 5:
        gen = 'Accion'
    elif genSelector == 6:
        gen = 'Drama'
    elif genSelector == 7:  
        gen = 'Comedia'
    elif genSelector == 8:
        gen = 'Romance'
    elif genSelector == 9:
        gen = 'Fantasia'
    elif genSelector == 10:
        gen = 'Biografia'
    elif genSelector == 11: 
        gen = 'Otro'
    else:
        print("Error")
        Carga_libros()
        
    #extraccion id de genero
    conn = sqlite3.connect("bibliotecaDB.db")
    cursor = conn.cursor()
    Dato = gen
    columnaDat0 = 'GENDER'
    consulta = f"SELECT ID_GENDER FROM GENDERS WHERE {columnaDat0} = ?"
    cursor.execute(consulta, (Dato,))
    iD_Ref = cursor.fetchone()
    id_refdef = iD_Ref[0]
    
    #peticion de autor
    print("Escriba el autor del libro: ")
    autor = input()
    AddAutor(autor)
    conn.commit() 
    conn.close()  
    
    #peticion de editorial
    conn = sqlite3.connect("bibliotecaDB.db")
    cursor = conn.cursor()
    print("Escriba la editorial del libro: ")
    editorial = input()
    AddEditorial(editorial)
    conn.commit()
    conn.close()
    
    #extraccion id de editorial
    conn = sqlite3.connect("bibliotecaDB.db")   
    cursor = conn.cursor()
    DatoE = editorial
    columnaDat1 = 'EDITORIAL'
    consulta = f"SELECT ID_EDITORIAL FROM EDITORIALES WHERE {columnaDat1} = ?" 
    cursor.execute(consulta, (DatoE,))
    iD_RefE = cursor.fetchone()
    id_refdefE = iD_RefE[0]
    conn.commit()
    conn.close()   
    
    #extraccion id de autor
    conn = sqlite3.connect("bibliotecaDB.db")
    cursor = conn.cursor()   
    DatoA = autor
    columnaDat2 = 'AUTOR'   
    consulta = f"SELECT ID_AUTOR FROM AUTORES WHERE {columnaDat2} = ?"
    cursor.execute(consulta, (DatoA,))
    iD_RefA = cursor.fetchone()
    id_refdefA = iD_RefA[0]
    conn.commit()
    conn.close()
    

    AddBooks(book,disp,id_refdef,id_refdefA,id_refdefE)
    opc = int(input(print("Presione 1 para agregar y cualquier otra letra para salir al menú de administrador")))
    if opc == 1:
        os.system("cls")
        cargaLibros()
    else: 
        admin()

#Creacion de tabla para renta
def TablaRenta():
    conn = sqlite3.connect("bibliotecaDB.db")
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS RENTA (
            ID TEXT PRIMARY KEY,
            ID_USER INTEGER,
            ID_LIBRO INTEGER,
            FECHA_DESDE TEXT,
            FECHA_HASTA TEXT,
            COSTO TEXT,
            FOREIGN KEY(ID_USER) REFERENCES USERS(ID),
            FOREIGN KEY(ID_LIBRO) REFERENCES LIBROS(ID_LIBRO)
            )"""
    )
    conn.commit()
    conn.close()

#CARGA DE LA FUNCION RENTA
def AddRenta(ID_USER, ID_LIBRO, FECHA_D, FECHA_H, COSTO): 
    if not all([ID_USER, ID_LIBRO, FECHA_D, FECHA_H, COSTO]):
        print("Error: Todos los campos son obligatorios para registrar una renta.")
        print(f"ID_USER: {ID_USER}, ID_LIBRO: {ID_LIBRO}, FECHA_D: {FECHA_D}, FECHA_H: {FECHA_H}, COSTO: {COSTO}")
        return

    conn = None
    try:
        conn = sqlite3.connect("bibliotecaDB.db", timeout=10)
        cursor = conn.cursor()
        nueva_id = str(generar_uuid())
        carga = """
            INSERT INTO RENTA (ID, ID_USER, ID_LIBRO, FECHA_DESDE, FECHA_HASTA, COSTO) 
            VALUES (?, ?, ?, ?, ?, ?)
        """
        cursor.execute(carga, (nueva_id, ID_USER, ID_LIBRO, FECHA_D, FECHA_H, COSTO))
        actualizar_disponibilidad = """
            UPDATE LIBROS
            SET DISPONIBLE = 0
            WHERE ID_LIBRO = ?
        """
        cursor.execute(actualizar_disponibilidad, (ID_LIBRO,))
        
        conn.commit()
        print("Renta agregada con éxito y disponibilidad del libro actualizada.")
    except sqlite3.Error as e:
        print(f"Error de base de datos al agregar renta: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

#FUNCION PARA CARGAR LA RENTA (rentar)
def Rentar():
    print("1)Buscar libro por su nombre\n2)Buscar libro por su genero\n3)Buscar libro por su autor\n4)Buscar libro por su editorial\n5)Regresar")
    opc = int(input())
    if opc == 1:
        os.system("cls")
        print("Buscando libro por su nombre\n")        
        BusquedaxNombre()
        print("¿Por cuantos días desea rentar el libro?")
        Días = int(input())
        Calculador_de_fecha(Días)
  
    elif opc == 2:
        os.system("cls")
        print("Buscando libro por su genero\n")
        BusquedaxGenero()
        print("¿Por cuantos días desea rentar el libro?")
        Días = int(input())
        Calculador_de_fecha(Días)
    
    elif opc == 3:
        os.system("cls")
        print("Buscando libro por su autor\n")
        BusquedaxAutor()
        print("¿Por cuantos días desea rentar el libro?")
        Días = int(input())
        Calculador_de_fecha(Días)
        
    elif opc == 4:  
        os.system("cls")
        print("Buscando libro por su editorial\n")
        BusquedaxEditorial()
        print("¿Por cuantos días desea rentar el libro?")
        Días = int(input())
        Calculador_de_fecha(Días)
        
    elif opc == 5:  
        os.system("cls")
        print("Regresando al menú principal")
        login()
    else:
        print("Error, opción no válida")
        os.system("pause")
        Rentar()


#Busqueda por nombre
def BusquedaxNombre():
    global libroCurrent
    print("Escriba el nombre del libro que desea rentar: ")
    NombreAprox = input().strip()
    
    if not NombreAprox:
        print("El nombre del libro no puede estar vacío. Intente nuevamente.")
        os.system("pause")
        return Rentar()
    try:
        conn = sqlite3.connect("bibliotecaDB.db")
        cursor = conn.cursor()
        consulta = "SELECT ID_LIBRO, LIBRO FROM LIBROS WHERE LIBRO LIKE ?"
        cursor.execute(consulta, (f"%{NombreAprox}%",)) 
        resultados = cursor.fetchall()
        
        if resultados:
            print("Libros encontrados:")
            for libro in resultados:
                print(f"ID: {libro[0]}, Título: {libro[1]}")
            print("Ingrese el ID del libro que desea rentar:")
            try:
                libro_id = int(input())
                libro_encontrado = next((libro for libro in resultados if libro[0] == libro_id), None)
                if libro_encontrado:
                    libroCurrent = libro_id
                    print(f"Libro seleccionado: {libro_encontrado[1]}")
                else:
                    print("ID no válido. Intente nuevamente.")
                    return BusquedaxNombre()
            except ValueError:
                print("Entrada no válida. Intente nuevamente.")
                return BusquedaxNombre()
        else:
            print("No se encontró ningún libro con ese nombre.")
            os.system("pause")
            return Rentar()
    except sqlite3.Error as e:
        print(f"Error de SQLite: {e}")
    finally:
        if conn:
            conn.close()
        
        

#Busqueda por genero 
def BusquedaxGenero():
    libros_encontrados = []
    print("Escriba el genero del libro: ")
    GeneroAprox = input()
    conn = None  
    try:
        conn = sqlite3.connect("bibliotecaDB.db")
        cursor = conn.cursor()
        consulta_genero = "SELECT ID_GENDER FROM GENDERS WHERE GENDER LIKE ?"
        cursor.execute(consulta_genero, (f"%{GeneroAprox}%",))
        IdGenTemp = cursor.fetchone()
        print(IdGenTemp)
        if IdGenTemp:
            id_genero = IdGenTemp[0]
            consulta_libros = "SELECT LIBRO FROM LIBROS WHERE ID_GENERO = ?"
            cursor.execute(consulta_libros, (id_genero,))
            Libros_genero = cursor.fetchall()
            for libro in Libros_genero:
                libros_encontrados.append(libro[0])

        else:
            print(f"No se encontró ningún género similar a '{GeneroAprox}'.")
            cursor.execute("SELECT GENDER FROM GENDERS")
            print("Los géneros disponibles son:")
            generos_disponibles = cursor.fetchall()
            for genero in generos_disponibles:
                print(f"- {genero[0]}")
            Rentar()

    except sqlite3.Error as e:
        print(f"Error de SQLite: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

    print(libros_encontrados)
    BusquedaxNombre()

#Busqueda por autor
def BusquedaxAutor():
    global libroCurrent
    print("Escriba el autor del libro que desea rentar: ")
    AutorAprox = input().strip()

    if not AutorAprox:
        print("El nombre del autor no puede estar vacío. Intente nuevamente.")
        os.system("pause")
        return Rentar()

    conn = None
    try:
        conn = sqlite3.connect("bibliotecaDB.db")
        cursor = conn.cursor()
        consulta_autor = "SELECT ID_AUTOR FROM AUTORES WHERE AUTOR LIKE ?"
        cursor.execute(consulta_autor, (f"%{AutorAprox}%",))
        IdAutTemp = cursor.fetchone()

        if IdAutTemp:
            id_autor = IdAutTemp[0]
            consulta_libros = "SELECT ID_LIBRO, LIBRO FROM LIBROS WHERE ID_AUTOR = ?"
            cursor.execute(consulta_libros, (id_autor,))
            Libros_autor = cursor.fetchall()

            if Libros_autor:
                print("Libros encontrados:")
                for libro in Libros_autor:
                    print(f"ID: {libro[0]}, Título: {libro[1]}")
                print("Ingrese el ID del libro que desea rentar:")
                try:
                    libro_id = int(input())
                    libro_encontrado = next((libro for libro in Libros_autor if libro[0] == libro_id), None)
                    if libro_encontrado:
                        libroCurrent = libro_id
                        print(f"Libro seleccionado: {libro_encontrado[1]}")
                    else:
                        print("ID no válido. Intente nuevamente.")
                        return BusquedaxAutor()
                except ValueError:
                    print("Entrada no válida. Intente nuevamente.")
                    return BusquedaxAutor()
            else:
                print(f"No se encontraron libros asociados al autor '{AutorAprox}'.")
                os.system("pause")
                return Rentar()
        else:
            print(f"No se encontró ningún autor similar a '{AutorAprox}'.")
            cursor.execute("SELECT AUTOR FROM AUTORES")
            print("Los autores disponibles son:")
            autores_disponibles = cursor.fetchall()
            for autor in autores_disponibles:
                print(f"- {autor[0]}")
            os.system("pause")
            return Rentar()

    except sqlite3.Error as e:
        print(f"Error de SQLite: {e}")
    finally:
        if conn:
            conn.close()
    
#Busqueda por editorial
def BusquedaxEditorial():
    global libroCurrent
    print("Escriba la editorial del libro que desea rentar: ")
    EditorialAprox = input().strip()

    if not EditorialAprox:
        print("El nombre de la editorial no puede estar vacío. Intente nuevamente.")
        os.system("pause")
        return Rentar()

    conn = None
    try:
        conn = sqlite3.connect("bibliotecaDB.db")
        cursor = conn.cursor()
        consulta_editorial = "SELECT ID_EDITORIAL FROM EDITORIALES WHERE EDITORIAL LIKE ?"
        cursor.execute(consulta_editorial, (f"%{EditorialAprox}%",))
        IdEditTemp = cursor.fetchone()

        if IdEditTemp:
            id_editorial = IdEditTemp[0]
            consulta_libros = "SELECT ID_LIBRO, LIBRO FROM LIBROS WHERE ID_EDITORIAL = ?"
            cursor.execute(consulta_libros, (id_editorial,))
            Libros_editorial = cursor.fetchall()

            if Libros_editorial:
                print("Libros encontrados:")
                for libro in Libros_editorial:
                    print(f"ID: {libro[0]}, Título: {libro[1]}")
                print("Ingrese el ID del libro que desea rentar:")
                try:
                    libro_id = int(input())
                    libro_encontrado = next((libro for libro in Libros_editorial if libro[0] == libro_id), None)
                    if libro_encontrado:
                        libroCurrent = libro_id
                        print(f"Libro seleccionado: {libro_encontrado[1]}")
                    else:
                        print("ID no válido. Intente nuevamente.")
                        return BusquedaxEditorial()
                except ValueError:
                    print("Entrada no válida. Intente nuevamente.")
                    return BusquedaxEditorial()
            else:
                print(f"No se encontraron libros asociados a la editorial '{EditorialAprox}'.")
                os.system("pause")
                return Rentar()
        else:
            print(f"No se encontró ninguna editorial similar a '{EditorialAprox}'.")
            cursor.execute("SELECT EDITORIAL FROM EDITORIALES")
            print("Las editoriales disponibles son:")
            editoriales_disponibles = cursor.fetchall()
            for editorial in editoriales_disponibles:
                print(f"- {editorial[0]}")
            os.system("pause")
            return Rentar()

    except sqlite3.Error as e:
        print(f"Error de SQLite: {e}")
    finally:
        if conn:
            conn.close()

#Opciones para usuarios
def OpcUser():
    try:
        print("Seleccione 1 si desea rentar\n Seleccione 2 si desea devolver el libro:\n")
        opc = int(input()) 
        if opc == 1:
            print("renta")
            Rentar()
        elif opc == 2:
            print("Devolucion")   
            Devolucion()
        else :
            os.system("cls")
            OpcUser()  
    except ValueError:    
        OpcUser()

#Calculador de fecha de devolución + costo
def Calculador_de_fecha(Días):
    if Días <= 0:
        print("Error: El número de días debe ser mayor a 0.")
        return
    global UserCurrent
    global libroCurrent
    if UserCurrent is None or libroCurrent is None:
        print("Error: No se pudo determinar el usuario o el libro actual.")
        return

    conn = None
    try:
        conn = sqlite3.connect("bibliotecaDB.db")
        cursor = conn.cursor()
        fecha_actual = datetime.date.today()
        fecha_futura = fecha_actual + datetime.timedelta(days=Días)
        Costo = max(Días * 1.2, 6)
        print("El día de devolución sería el: ", fecha_futura, "y tendría un costo de", Costo)
        print("¿Presione 1 para continuar o 2 para regresar?")
        Costo = str(Costo)
        opc = int(input())
        if opc == 1:
            fecha_actual = fecha_actual.isoformat()
            fecha_futura = fecha_futura.isoformat()
            AddRenta(UserCurrent, libroCurrent, fecha_actual, fecha_futura, Costo)
    except sqlite3.Error as e:
        print(f"Error de SQLite: {e}")
    finally:
        if conn:
            conn.close()
        elif opc == 2:
            os.system("cls")
            Calculador_de_fecha(Días)
        else:
            os.system("cls")
            print("Dato inválido")
            Calculador_de_fecha(Días)

#Funcion para gestionar la devolución de libros
def Devolucion():
    os.system("cls")
    print("Ingrese el número de factura de la renta: ")
    factura = input().strip()

    conn = None
    try:
        conn = sqlite3.connect("bibliotecaDB.db")
        cursor = conn.cursor()
        consulta = "SELECT ID_LIBRO, ID_USER FROM RENTA WHERE ID = ?"
        cursor.execute(consulta, (factura,))
        resultado = cursor.fetchone()

        if resultado:
            id_libro, id_user = resultado
            if id_user != UserCurrent:
                print("Error: Solo el usuario que realizó la renta puede devolver el libro.")
                return

            actualizar_disponibilidad = """
                UPDATE LIBROS
                SET DISPONIBLE = 1
                WHERE ID_LIBRO = ?
            """
            cursor.execute(actualizar_disponibilidad, (id_libro,))

            eliminar_renta = "DELETE FROM RENTA WHERE ID = ?"
            cursor.execute(eliminar_renta, (factura,))

            conn.commit()
            print(f"Devolución realizada con éxito. El libro con ID {id_libro} ahora está disponible.")
        else:
            print("Error: No se encontró ninguna renta con el número de factura proporcionado.")
    except sqlite3.Error as e:
        print(f"Error de SQLite al procesar la devolución: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
    

#Función para obtener sinopsis de un libro usando la API de Google Books
def obtener_sinopsis_libro(nombre_libro, autor, api_key=None):
    """
    Busca la sinopsis de un libro usando la API de Google Books.
    
    Args:
        nombre_libro (str): El nombre del libro a buscar.
        autor (str): El autor del libro a buscar.
        api_key (str): La clave de la API de Google Books (opcional).
    
    Returns:
        dict: Un diccionario con la información del libro, incluyendo la sinopsis si está disponible.
    """
    try:
        # Construir la URL de la API
        base_url = "https://www.googleapis.com/books/v1/volumes"
        # Incluir tanto el nombre del libro como el autor en la consulta
        params = {"q": f"{nombre_libro} {autor}"}
        if api_key:
            params["key"] = api_key

        # Realizar la solicitud a la API
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Lanza una excepción si ocurre un error HTTP

        # Procesar los datos de la respuesta
        data = response.json()
        if "items" in data and len(data["items"]) > 0:
            # Tomar el primer resultado
            libro = data["items"][0]
            sinopsis = libro["volumeInfo"].get("description", None)
            return {"sinopsis": sinopsis}
        else:
            return None
    except requests.RequestException as e:
        print(f"Error al conectar con la API de Google Books: {e}")
        return None

#Función para acrtualizar sinopsis de un libro usando la API de Google Books
def actualizar_sinopsis_libros(api_key=None):
    """
    Actualiza la columna SINOPSIS de la tabla LIBROS con información obtenida de la API de Google Books.
    Solo se procesan libros que no tienen sinopsis.
    """
    conn = None
    try:
        conn = sqlite3.connect("bibliotecaDB.db")
        cursor = conn.cursor()

        # Obtener todos los libros que no tienen sinopsis
        consulta = """
            SELECT L.ID_LIBRO, L.LIBRO, A.AUTOR 
            FROM LIBROS L
            JOIN AUTORES A ON L.ID_AUTOR = A.ID_AUTOR
            WHERE L.SINOPSIS IS NULL OR TRIM(L.SINOPSIS) = ''
        """
        cursor.execute(consulta)
        libros_sin_sinopsis = cursor.fetchall()

        if not libros_sin_sinopsis:
            print("Todos los libros ya tienen sinopsis.")
            return

        for libro in libros_sin_sinopsis:
            id_libro, nombre_libro, autor = libro
            print(f"Buscando sinopsis para el libro: {nombre_libro} por {autor}")

            # Obtener sinopsis desde la API
            info_libro = obtener_sinopsis_libro(nombre_libro, autor, api_key=api_key)
            if info_libro and "sinopsis" in info_libro:
                sinopsis = info_libro["sinopsis"]
                if sinopsis:  # Verificar que la sinopsis no esté vacía
                    # Actualizar la sinopsis en la base de datos
                    actualizacion = "UPDATE LIBROS SET SINOPSIS = ? WHERE ID_LIBRO = ?"
                    cursor.execute(actualizacion, (sinopsis, id_libro))
                    print(f"Sinopsis actualizada para el libro '{nombre_libro}'.")
                else:
                    print(f"No se encontró una sinopsis válida para el libro '{nombre_libro}'.")
            else:
                print(f"No se encontró sinopsis para el libro '{nombre_libro}'.")

        conn.commit()
        print("Actualización de sinopsis completada.")
    except sqlite3.Error as e:
        print(f"Error de SQLite: {e}")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"Error inesperado: {e}")
    finally:
        if conn:
            conn.close()
            
#Ejecutar funciones iniciales

Create_DataBase()
createTableUsers()
Generos()
Autores()
Editoriales()
cargaEditorialesExcel()
cargaAutoresExcel()
Libros()
cargaLibrosExcel()
TablaRenta()
actualizar_sinopsis_libros(api_key="AIzaSyCmAvfCbTPX-7dqeHkEWXN1zFEjrTVBPEo")
Menu()


