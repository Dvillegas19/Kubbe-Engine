@echo off
REM 

cls

REM 
if "%1"=="" (
    echo.
    echo  Uso: jugar [nombre_del_juego]
    echo  Ejemplo: jugar snake
    echo  Ejemplo: jugar tetris
    echo.
    goto :eof
)

REM 
echo Compilando el juego: %1...
echo ----------------------------------

REM 
py -2.7 .\compiler.py .\games\%1.brick

if errorlevel 1 (
    echo.
    echo !!! Ocurrio un error durante la compilacion. !!!
    pause
    goto :eof
)

echo.
echo Compilacion exitosa. Iniciando el juego...
echo ----------------------------------
REM 
timeout /t 2 >nul 2>&1 || pause

REM 
REM 
py -2.7 .\runtime.py .\games\%1.json

echo.
echo Juego terminado. Presiona cualquier tecla para cerrar esta ventana.
pause