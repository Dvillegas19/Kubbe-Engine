=============================================================
 PROYECTO: Kubbe - Un lenguaje basado en juegos de ladrillos
=============================================================

Kubbe es un lenguaje de programación simple diseñado con un enfoque en el análisis y abstracción de este, de manera que su principal objetivo está centrado en definir e implementar dicha abstracción para la ejecución de juegos basados en ladrillos, más específicamente los juegos conocidos como snake y Tetris.

Este proyecto incluye el compilador que traduce el codigo Kubbe a un formato que la computadora entiende, y el motor de juego que lo ejecuta.

Adicionalmente, el runtime fue implementado para Windows con Python 2.7

-------------------------------------------------------------
                      COMO JUGAR
-------------------------------------------------------------

Si bien los pasos a seguir para ejecutar correctamente los juegos de tetris y snake programados en Kubbe son sencillos, aun así, vale la pena dejarlos claros para lograr la  ejecución de los programas correctamente evitando cualquier posible inconveniente. Dichos pasos por seguir son los siguientes: 

1. Descargar el archivo llamado “Proyecto Práctico TLP Entregable 3.ZIP” 

2. Descomprimir este archivo y entrar a la carpeta resultante.

3. Copiar la ruta de la carpeta descomprimida “Proyecto Práctico TLP Entregable 3”.

4. Abrir una terminal de comandos (CMD), para luego escribir en ella el comando “cd” seguido de un espacio en blanco, y posterior a este pegar la ruta de la carpeta “Proyecto Práctico TLP Entregable 3”, una vez hecho esto solo queda pulsar la tecla enter.
	
	EJEMPLO: cd C:\Ussers\Usuario\Documents\UNAL\TLP\Proyecto Práctico TLP Entregable 3

5. Escribir el comando "jugar" seguido del nombre del juego deseado, únicamente el nombre del juego, es decir sin la extensión .brick

	EJEMPLO PARA JUGAR SNAKE:
		jugar snake

	EJEMPLO PARA JUGAR TETRIS:
		jugar Tetris

Nota: si se está ejecutando desde Windows PowerShell, el comando debe ser “.\jugar” y el respectivo juego que se quiere ejecutar.  

Mediante todas estas instrucciones el script primero compilara el archivo .brick correspondiente. Si la compilacion es exitosa, el juego se iniciara automaticamente.

Para salir del juego, presiona la tecla 'q', y para pausarlo, presiona la tecla 'p'.


-------------------------------------------------------------
                 SINTAXIS DE KUBBE
-------------------------------------------------------------

A continuación, se verá un breve listado de la sintaxis para aspectos principales que resultan imprescindibles para la correcta implementación y ejecución en los archivos “.brick”: 

--- COMANDOS GENERALES ---

* nombre~juego ASSIGN ´<nombre>´
    Este comando se encarga de definir el nombre visible del juego.
	Ejemplo: nombre~juego ASSIGN ´Snake Moderno´
 
* tablero~moderno ASSIGN {ANCHO; ALTO}
    Mediante este comando se establece el tamaño del tablero jugable.
	Ejemplo: tablero~moderno ASSIGN {10; 20} 

* velocidad ASSIGN <valor>
    Con este comando se indica la velocidad inicial del jugador o piezas.
		Ejemplo: velocidad ASSIGN 6.0
 
--- DEFINICIÓN DE VARIABLES ---

Para la definición de las variables existente en el lenguaje de programación Kubbe, se estableció lo siguiente: 

* ASSIGN
	La palabra reservada “ASSIGN” se utiliza para indicar que a una variable se le asigna un valor.

* !!
	Para indicar que el valor asignado a una variable es una acción se utilizará “!!”.

* String
	Mediante el uso de “´´” se indicará que el valor de una variable es solamente texto.
	
--- DEFINICIÓN DE VARIABLES ---

Para la definición de listas en el lenguaje de programación Kubbe, se utilizarán los operadores “{}”. Por otro lado, para la creación de listas anidadas o listas dentro de listas, se hará uso del operador “;” como separador.

Ejemplo: lista ASSIGN {elementos}
	 Puntos ASSIGN {1; 2; 3}
	 Rotar ASSIGN { {90; 30; 50; 80}; {90; 30; 50; 80}; {90; 30; 50; 80} }

Por otro lado, para los bloques de código se usan las palabras clave “BEGIN” y “END” en mayúscula, además, las palabras reservadas “BEGIN” y “END” no pueden ser usadas para declarar variables. 

Ejemplo: 
	 vidas ASSIGN 3 
	 reglas ASSIGN BEGIN 
	 |	colision ASSIGN !terminar! 
	 END

--- COMENTARIOS ---

Para comentar una línea de código no ejecutable en Kubbe, se utilizará el operador “//” al inicio del comentario que se quiere hacer. Del mismo modo, se utilizará indentación con el fin de tener un código comprensible para las personas que busquen leer o interpretar el código.

Ejemplo: //Reglas generales del juego

--- SINTAXIS PARA TETRIS ---

Eventos disponibles: puntuacion~dinamica, fin~juego~bloques, bloques~disponibles.

Acciones comunes:
* completar ASSIGN !linea completa!
* accion ASSIGN !eliminar linea!
* mover~izquierda
* mover~derecha
* acelerar~abajo
* caida
* rotación
* pausar

--- SINTAXIS PARA SNAKE ---

Eventos disponibles: aparicion~comida; aparicion~aleatoria, probabilidad~normal, probabilidad~dorada, probabilidad~veneno.

Acciones comunes:
* mover~arriba
* mover~abajo
* mover~izquierda
* mover~derecha
* pausar