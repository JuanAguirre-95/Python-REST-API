Instalar la ultima version de python.

Una ves instalado, abrir cmd, navegar hasta esta carpeta e instalar los paquetes necesarios con el comando

pip install -r requirements.txt

Para configurar la aplicacion dentro de la carpeta config hay un archivo settings.cfg donde estan los campos
configurables de la api. La parte de server conviene dejarla como esta, con el debug desactivado si va a estar 
la api en produccion.
En ese archivo se configura la ip de la base de datos mongo, el puerto donde corre, el nombre de la base de datos,
y los nombres de las 2 colecciones (tablas). Una tabla es para los usuarios y otra es para los items que se van a guardar

En la seccion [ROUTES] estan las rutas base que se pueden customizar

la seccion [ADMIN] tiene las credenciales para crear el usuario maestro de la api. Este es el usuario base
para poder crear otros usuarios desde la api. si no hay que crearlos manualmente por fuera de la api.

La seccion [LOGS] no sirve para nada poruqe todavia no esta implementada.

La seccion [SECURITY] contiene la llave de encripcion maestra con la cual se hashean y saltean las claves que se guardan
en la db para los usuarios y ademas se firman las cookies de sesion.

Para ejecutar el programa, abrir CMD, navegar hasta esta carpeta y usar el comando:

python app.py

lista de endpoints y lo que esperan recibir:

Autenticacion:

www.ejemplo.com/api/auth/login POST - HTML Form
www.ejemplo.com/api/auth/logout GET 
www.ejemplo.com/api/auth/register POST - HTML Form para registrar un usuario nuevo tiene que primero haber iniciado sesion

www.ejemplo.com/api/items/create POST - Html form con la info a cargar. Tiene que iniciar sesion
www.ejemplo.com/api/items/read/<id> GET - no recibe nada, se le pasa el ID del elemento en la url para buscarlo
www.ejemplo.com/api/items/update/<id> - PATCH - JSON object
www.ejemplo.com/api/items/delete/<id> - DELETE - pasa el id por la url y borra ese elemento
www.ejemplo.com/api/items/list - GET - Lista todos los items que estan en la base, si no esta logueado solo lista los visibles al publico

