# arquivo: tres_corpos.py
import pygame
import math

# Inicializa o pygame
pygame.init()

# Constantes
LARGURA, ALTURA = 800, 800
G = 6.67430e-1  # Constante gravitacional ajustada para visualização

# Cores
PRETO = (0, 0, 0)
CORES = [(255, 0, 0), (0, 255, 0), (0, 128, 255)]

# Tela
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Simulação dos 3 Corpos")

# Classe do Corpo Celeste
class Corpo:
    def __init__(self, x, y, vx, vy, massa, cor):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.ax = 0
        self.ay = 0
        self.massa = massa
        self.cor = cor
        self.trilha = []

    def atrair(self, outros):
        self.ax = self.ay = 0
        for outro in outros:
            if outro == self:
                continue
            dx = outro.x - self.x
            dy = outro.y - self.y
            distancia = math.hypot(dx, dy)
            if distancia == 0:
                continue
            forca = G * self.massa * outro.massa / distancia**2
            angulo = math.atan2(dy, dx)
            self.ax += (forca / self.massa) * math.cos(angulo)
            self.ay += (forca / self.massa) * math.sin(angulo)

    def atualizar(self, dt):
        self.vx += self.ax * dt
        self.vy += self.ay * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        if len(self.trilha) > 300:
            self.trilha.pop(0)
        self.trilha.append((self.x, self.y))

# Funções de câmera
def centro_de_massa(corpos):
    x = sum(c.x * c.massa for c in corpos) / sum(c.massa for c in corpos)
    y = sum(c.y * c.massa for c in corpos) / sum(c.massa for c in corpos)
    return x, y

def calcular_zoom(corpos, margem=1.2):
    max_dist = max(
        math.hypot(c.x - camera_x, c.y - camera_y) for c in corpos
    )
    if max_dist == 0:
        return 1
    return min(LARGURA, ALTURA) / (2 * max_dist * margem)

def transformar(x, y, camera_x, camera_y, zoom):
    tela_x = int((x - camera_x) * zoom + LARGURA // 2)
    tela_y = int((y - camera_y) * zoom + ALTURA // 2)
    return tela_x, tela_y

# Inicializa corpos
corpos = [
    Corpo(400, 300, 0, 1.8, 1000, CORES[0]),
    Corpo(300, 500, -2, 0, 1000, CORES[1]),
    Corpo(500, 500, 2, -1, 1000, CORES[2])
]

# Loop principal
relogio = pygame.time.Clock()
rodando = True
while rodando:
    dt = relogio.tick(60) / 10  # controle da velocidade da simulação

    # Atualiza física
    for corpo in corpos:
        corpo.atrair(corpos)
    for corpo in corpos:
        corpo.atualizar(dt)

    # Câmera
    camera_x, camera_y = centro_de_massa(corpos)
    zoom = calcular_zoom(corpos)

    # Desenho
    tela.fill(PRETO)
    for corpo in corpos:
        # Desenha trilha
        for ponto in corpo.trilha:
            px, py = transformar(ponto[0], ponto[1], camera_x, camera_y, zoom)
            pygame.draw.circle(tela, corpo.cor, (px, py), 1)

        # Desenha corpo
        cx, cy = transformar(corpo.x, corpo.y, camera_x, camera_y, zoom)
        pygame.draw.circle(tela, corpo.cor, (cx, cy), 6)

    pygame.display.flip()

    # Eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

pygame.quit()
