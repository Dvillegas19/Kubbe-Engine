# -*- coding: utf-8 -*-
import sys
import json
import random
import re
import Tkinter as tk
import tkMessageBox
import io
import winsound
import os
import ctypes

class Juego:
    def __init__(self, datos_juego):
        self.datos_juego = datos_juego
        nombre = datos_juego.get("nombre~juego", "").lower()
        
        if "snake" in nombre:
            self.tipo_juego = "SNAKE"
        else:
            self.tipo_juego = "TETRIS"
            
        tablero = datos_juego.get("tablero~moderno", [20, 20])
        self.cols = int(tablero[0])
        self.rows = int(tablero[1])
        self.cell_size = 25
        
        self.root = tk.Tk()
        self.root.title("KUBBE ENGINE - " + self.tipo_juego)
        self.root.resizable(False, False)
        self.root.bind("<Key>", self.manejar_input)
        
        self.canvas_width = self.cols * self.cell_size
        self.panel_width = 220
        total_width = self.canvas_width + self.panel_width
        total_height = self.rows * self.cell_size
        
        self.canvas = tk.Canvas(self.root, width=total_width, height=total_height, bg="#111111")
        self.canvas.pack()
        
        self.juego_terminado = False
        self.pausado = False
        self.puntuacion = int(datos_juego.get("puntos", 0))
        self.velocidad = float(datos_juego.get("velocidad", 4.0))
        self.timer_gravedad = 0
        self.contador_comidas = 0
        
        self.key_map = {}
        self.cargar_controles()

        self.color_map = {
            "cian": "#00FFFF", "amarillo": "#FFFF00", "magenta": "#FF00FF",
            "naranja": "#FFA500", "azul": "#0000FF", "verde": "#00FF00",
            "rojo": "#FF0000", "marron": "#8B4513", "beige": "#F5F5DC",
            "rosado": "#FFC0CB", "blanco": "#FFFFFF", "gris": "#808080"
        }

        self.grid = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        
        self.reproducir_musica()
        
        try:
            if os.path.exists("icon.ico"):
                self.root.iconbitmap("icon.ico")
        except Exception:
            pass

        if self.tipo_juego == "SNAKE":
            self.vidas = int(datos_juego.get("vidas~iniciales", 2))
            self.serpiente_cuerpo = []
            self.serpiente_direccion = (1, 0)
            self.longitud_inicial = int(datos_juego.get("longitud", 3))
            self.velocidad_gravedad = 1000.0 / self.velocidad
            self.comida_actual = None
            self.snake_spawn_jugador()
            self.snake_spawn_comida()
            
        elif self.tipo_juego == "TETRIS":
            self.piezas = self.cargar_piezas()
            self.pieza_actual = None
            self.pieza_x = 0
            self.pieza_y = 0
            self.pieza_rotacion = 0
            self.velocidad_gravedad = 400
            self.lineas_completadas = 0
            self.tetris_spawn_pieza()

    def reproducir_musica(self):
        try:
            ruta_musica = "games\\music.wav"
            winsound.PlaySound(ruta_musica, winsound.SND_ASYNC | winsound.SND_LOOP)
        except Exception:
            pass

    def detener_musica(self):
        try:
            winsound.PlaySound(None, 0)
        except Exception:
            pass

    def cargar_controles(self):
        ctrls = self.datos_juego.get("controles", {})
        for accion, tecla in ctrls.items():
            if isinstance(tecla, unicode) or isinstance(tecla, str):
                t = tecla.lower()
                self.key_map[t] = accion

    def run(self):
        self.game_loop()
        self.root.mainloop()
        
    def game_loop(self):
        if self.juego_terminado or self.pausado:
            self.root.after(100, self.game_loop)
            return
            
        if self.tipo_juego == "SNAKE":
            delay = int(self.velocidad_gravedad)
            self.ejecutar_evento("ON_TICK")
        else:
            delay = 50
            self.timer_gravedad += 50
            if self.timer_gravedad >= self.velocidad_gravedad:
                self.ejecutar_evento("ON_TICK")
                self.timer_gravedad = 0
            
        self.dibujar()
        self.root.after(delay, self.game_loop)

    def manejar_input(self, event):
        key = event.keysym.lower()
        
        if key == "q":
            self.detener_musica()
            self.root.destroy()
            sys.exit(0)
            
        accion = self.key_map.get(key)
        
        if accion == "pausar" or key == "p":
            self.pausado = not self.pausado
            if self.pausado:
                tkMessageBox.showinfo("PAUSA", "Juego Pausado")
                self.pausado = False
            return

        if self.juego_terminado or self.pausado:
            return
            
        if self.tipo_juego == "SNAKE":
            if accion == "mover~arriba": self.snake_cambiar_direccion("UP")
            elif accion == "mover~abajo": self.snake_cambiar_direccion("DOWN")
            elif accion == "mover~izquierda": self.snake_cambiar_direccion("LEFT")
            elif accion == "mover~derecha": self.snake_cambiar_direccion("RIGHT")
        else:
            if accion == "mover~derecha": self.tetris_mover(1, 0)
            elif accion == "mover~izquierda": self.tetris_mover(-1, 0)
            elif accion == "acelerar~abajo": self.tetris_bajar()
            elif accion == "rotacion": self.tetris_rotar()
            elif accion == "caida": self.tetris_caida_instantanea()
            
    def dibujar(self):
        self.canvas.delete("all")
        
        self.canvas.create_rectangle(self.canvas_width, 0, 
                                   self.canvas_width + self.panel_width, self.rows * self.cell_size, 
                                   fill="#1A1A1A", outline="")
                                   
        ix = self.canvas_width + 10
        self.canvas.create_text(ix, 20, text="PUNTUACION", fill="white", anchor="nw", font=("Arial", 10, "bold"))
        self.canvas.create_text(ix, 40, text=str(self.puntuacion), fill="#00FF00", anchor="nw", font=("Arial", 16, "bold"))
        
        self.canvas.create_text(ix, 70, text="VELOCIDAD", fill="white", anchor="nw", font=("Arial", 8))
        self.canvas.create_text(ix, 85, text="{:.1f}".format(self.velocidad), fill="yellow", anchor="nw", font=("Arial", 10))

        # --- SECCION DE CONTROLES MANUALES ---
        self.canvas.create_text(ix, 170, text="CONTROLES:", fill="gray", anchor="nw", font=("Arial", 10, "bold"))
        
        # Aqui agregamos las teclas globales P y Q
        self.canvas.create_text(ix, 195, text="P: Pausar", fill="white", anchor="nw", font=("Arial", 9))
        self.canvas.create_text(ix, 215, text="Q: Salir", fill="white", anchor="nw", font=("Arial", 9))
        
        base_y = 245 # Bajamos un poco mas para dejar espacio a P y Q

        if self.tipo_juego == "SNAKE":
            self.canvas.create_text(ix, 110, text="VIDAS", fill="white", anchor="nw", font=("Arial", 10, "bold"))
            self.canvas.create_text(ix, 130, text=str(self.vidas), fill="red", anchor="nw", font=("Arial", 14, "bold"))
            
            # Dibujar controles del Snake desde el JSON
            for k, v in self.key_map.items():
                if k not in ['p', 'q']:
                    lbl = k.upper() + ": " + v.replace("mover~", "")
                    self.canvas.create_text(ix, base_y, text=lbl, fill="white", anchor="nw", font=("Arial", 9))
                    base_y += 20
            
            # Leyenda de Comidas
            leg_y = base_y + 20
            self.canvas.create_text(ix, leg_y, text="COMIDAS:", fill="gray", anchor="nw", font=("Arial", 10, "bold"))
            
            def draw_legend_item(y, color, text):
                self.canvas.create_oval(ix, y, ix+15, y+15, fill=color, outline="white")
                self.canvas.create_text(ix+25, y, text=text, fill="white", anchor="nw", font=("Arial", 9))
                
            draw_legend_item(leg_y + 25, "#00FF00", "Normal (+100)")
            draw_legend_item(leg_y + 50, "gold", "Dorada (+500)")
            draw_legend_item(leg_y + 75, "purple", "Veneno (-200)")
            
        else:
            self.canvas.create_text(ix, 110, text="LINEAS", fill="white", anchor="nw", font=("Arial", 10, "bold"))
            self.canvas.create_text(ix, 130, text=str(self.lineas_completadas), fill="cyan", anchor="nw", font=("Arial", 14, "bold"))
            
            # Dibujar controles del Tetris desde el JSON
            for k, v in self.key_map.items():
                if k not in ['p', 'q']:
                    lbl = k.upper() + ": " + v.replace("mover~", "").replace("acelerar~", "")
                    self.canvas.create_text(ix, base_y, text=lbl, fill="white", anchor="nw", font=("Arial", 9))
                    base_y += 20
        
        for y in range(self.rows):
            for x in range(self.cols):
                color = self.grid[y][x]
                if color:
                    self.dibujar_celda(x, y, color)
                else:
                    x1 = x * self.cell_size
                    y1 = y * self.cell_size
                    x2 = x1 + self.cell_size
                    y2 = y1 + self.cell_size
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="#222222")

        if self.tipo_juego == "SNAKE":
            for i, (sx, sy) in enumerate(self.serpiente_cuerpo):
                color = "#00FF00" if i == 0 else "#008800"
                self.dibujar_celda(sx, sy, color)
                
            if self.comida_actual:
                cx, cy = self.comida_actual["pos"]
                tipo = self.comida_actual["tipo"]
                color = "#00FF00"
                if tipo == "comida~dorada": color = "gold"
                elif tipo == "comida~veneno": color = "purple"
                self.dibujar_celda(cx, cy, color, is_circle=True)
                
        elif self.tipo_juego == "TETRIS":
            if self.pieza_actual:
                color_pieza = self.color_map.get(self.pieza_actual['color'], "white")
                for y, fila in enumerate(self.pieza_actual['rotaciones'][self.pieza_rotacion]):
                    for x, celda in enumerate(fila):
                        if celda:
                            self.dibujar_celda(self.pieza_x + x, self.pieza_y + y, color_pieza)

    def dibujar_celda(self, x, y, color, is_circle=False):
        x1 = x * self.cell_size
        y1 = y * self.cell_size
        x2 = x1 + self.cell_size
        y2 = y1 + self.cell_size
        if is_circle:
            self.canvas.create_oval(x1+2, y1+2, x2-2, y2-2, fill=color, outline="")
        else:
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")

    def ejecutar_evento(self, tipo_evento, datos=None):
        if self.tipo_juego == "SNAKE":
            if tipo_evento == "ON_TICK": self.snake_mover_jugador()
        elif self.tipo_juego == "TETRIS":
            if tipo_evento == "ON_TICK": self.tetris_bajar()

    def cargar_piezas(self):
        piezas = {}
        for clave, valor in self.datos_juego.items():
            if clave.startswith("bloque~"):
                nombre = clave.split("~")[1].upper()
                rotaciones_raw = valor.get("rotaciones", [])
                color = valor.get("color", "blanco")
                rotaciones = []
                for rot in rotaciones_raw:
                    matriz = []
                    for fila in rot:
                        if isinstance(fila, list):
                            matriz.append([int(x) for x in fila])
                    rotaciones.append(matriz)
                piezas[nombre] = {'rotaciones': rotaciones, 'color': color}
        return piezas

    def tetris_spawn_pieza(self):
        nombre = random.choice(list(self.piezas.keys()))
        self.pieza_actual = self.piezas[nombre]
        self.pieza_x = self.cols // 2 - len(self.pieza_actual['rotaciones'][0][0]) // 2
        self.pieza_y = 0
        self.pieza_rotacion = 0
        if self.tetris_colision(self.pieza_x, self.pieza_y, self.pieza_rotacion):
            self.game_over()

    def tetris_mover(self, dx, dy):
        if not self.tetris_colision(self.pieza_x + dx, self.pieza_y + dy, self.pieza_rotacion):
            self.pieza_x += dx
            self.pieza_y += dy
        elif dy > 0:
            self.tetris_fijar_pieza()
            self.tetris_limpiar_lineas()
            self.tetris_spawn_pieza()

    def tetris_bajar(self):
        self.tetris_mover(0, 1)

    def tetris_rotar(self):
        nueva = (self.pieza_rotacion + 1) % len(self.pieza_actual['rotaciones'])
        if not self.tetris_colision(self.pieza_x, self.pieza_y, nueva):
            self.pieza_rotacion = nueva

    def tetris_colision(self, x, y, rot):
        forma = self.pieza_actual['rotaciones'][rot]
        for j, fila in enumerate(forma):
            for i, celda in enumerate(fila):
                if celda:
                    px = x + i
                    py = y + j
                    if px < 0 or px >= self.cols or py >= self.rows: return True
                    if py >= 0 and self.grid[py][px]: return True
        return False

    def tetris_fijar_pieza(self):
        forma = self.pieza_actual['rotaciones'][self.pieza_rotacion]
        color = self.color_map.get(self.pieza_actual['color'], "gris")
        for j, fila in enumerate(forma):
            for i, celda in enumerate(fila):
                if celda:
                    px = self.pieza_x + i
                    py = self.pieza_y + j
                    if 0 <= py < self.rows and 0 <= px < self.cols:
                        self.grid[py][px] = color

    def tetris_limpiar_lineas(self):
        nuevas = [fila for fila in self.grid if not all(fila)]
        limpias = self.rows - len(nuevas)
        if limpias > 0:
            for _ in range(limpias): nuevas.insert(0, [None] * self.cols)
            self.grid = nuevas
            self.puntuacion += limpias * 100
            self.lineas_completadas += limpias

    def tetris_caida_instantanea(self):
        if not self.pieza_actual: return
        while not self.tetris_colision(self.pieza_x, self.pieza_y + 1, self.pieza_rotacion):
            self.pieza_y += 1
        self.tetris_fijar_pieza()
        self.tetris_limpiar_lineas()
        self.tetris_spawn_pieza()

    def snake_spawn_jugador(self):
        ix = self.cols // 2
        iy = self.rows // 2
        self.serpiente_cuerpo = [(ix - i, iy) for i in range(self.longitud_inicial)]
        self.serpiente_direccion = (1, 0)

    def snake_spawn_comida(self):
        regla = self.datos_juego.get("regla~aparicion~comida", {})
        pn = float(regla.get("probabilidad~normal", 0.6))
        pd = float(regla.get("probabilidad~dorada", 0.1))
        r = random.random()
        if r < pn: tipo = "comida~normal"
        elif r < pn + pd: tipo = "comida~dorada"
        else: tipo = "comida~veneno"
        
        while True:
            x, y = random.randint(0, self.cols - 1), random.randint(0, self.rows - 1)
            if (x, y) not in self.serpiente_cuerpo:
                self.comida_actual = {"pos": (x, y), "tipo": tipo}
                break

    def snake_mover_jugador(self):
        head = self.serpiente_cuerpo[0]
        dx, dy = self.serpiente_direccion
        new_head = (head[0] + dx, head[1] + dy)
        
        if not (0 <= new_head[0] < self.cols and 0 <= new_head[1] < self.rows):
            self.perder_vida()
            return

        if new_head in self.serpiente_cuerpo:
            self.perder_vida()
            return

        self.serpiente_cuerpo.insert(0, new_head)
        
        if self.comida_actual and new_head == self.comida_actual["pos"]:
            self.aplicar_regla_comida(self.comida_actual)
            self.snake_spawn_comida()
        else:
            self.serpiente_cuerpo.pop()

    def perder_vida(self):
        self.vidas -= 1
        if self.vidas <= 0:
            self.game_over()
        else:
            self.snake_spawn_jugador()

    def snake_cambiar_direccion(self, d):
        dx, dy = self.serpiente_direccion
        if d == "UP" and dy != 1: self.serpiente_direccion = (0, -1)
        elif d == "DOWN" and dy != -1: self.serpiente_direccion = (0, 1)
        elif d == "LEFT" and dx != 1: self.serpiente_direccion = (-1, 0)
        elif d == "RIGHT" and dx != -1: self.serpiente_direccion = (1, 0)

    def aplicar_regla_comida(self, datos):
        tipo = datos.get("tipo", "comida~normal")
        reglas = self.datos_juego.get("reglas~comida", {})
        regla = reglas.get(tipo, [1, 100])
        if not isinstance(regla, list): regla = [1, 100]
        
        crecimiento = int(regla[0])
        puntos = int(regla[1])
        
        self.puntuacion += puntos
        if self.puntuacion < 0: self.puntuacion = 0
        
        for _ in range(crecimiento):
            self.serpiente_cuerpo.append(self.serpiente_cuerpo[-1])
            
        if crecimiento == 0:
            if len(self.serpiente_cuerpo) > 3:
                self.serpiente_cuerpo.pop()
                
        self.contador_comidas += 1
        
        vr = self.datos_juego.get("reglas~velocidad", {})
        cond = vr.get("condicion", "")
        if "cada" in cond:
            nums = re.findall(r'\d+', cond)
            if nums:
                n = int(nums[0])
                if self.contador_comidas % n == 0:
                    if "aumentar" in str(vr.get("efecto", "")):
                        self.velocidad += 0.2
                        self.velocidad_gravedad = 1000.0 / self.velocidad
        
        if self.velocidad > 12.0:
            self.velocidad = 12.0
            self.velocidad_gravedad = 1000.0 / self.velocidad

    def game_over(self):
        self.detener_musica()
        self.juego_terminado = True
        msg = "Puntuacion Final: " + str(self.puntuacion)
        tkMessageBox.showinfo("GAME OVER", msg)
        self.root.destroy()
        sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(1)
    fpath = sys.argv[1]
    try:
        with io.open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
        app = Juego(data)
        app.run()
    except Exception:
        sys.exit(1)