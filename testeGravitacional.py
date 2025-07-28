import pygame
import math
from datetime import datetime
import matplotlib.pyplot as plt

# Inicialização
pygame.init()

# Constantes
PRETO = (0, 0, 0)
FPS = 60
G = 6.67430e-11
ESCALA = 1e9
RAIO = 5

# Tela cheia
info = pygame.display.Info()
LARGURA, ALTURA = info.current_w, info.current_h
tela = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Simulação dos Três Corpos com Rastros")
relogio = pygame.time.Clock()

# Log de dados
nome_arquivo = datetime.now().strftime("simulacao_%Y%m%d_%H%M%S.txt")
arquivo_log = open(nome_arquivo, "w")

# Classe Corpo
class Corpo:
    def __init__(self, x, y, vx, vy, massa, cor, nome):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.ax = 0
        self.ay = 0
        self.massa = massa
        self.cor = cor
        self.nome = nome
        self.rastro = []

    def atracao(self, outros):
        self.ax = self.ay = 0
        for outro in outros:
            if outro == self:
                continue
            dx = outro.x - self.x
            dy = outro.y - self.y
            dist_sq = dx**2 + dy**2
            if dist_sq == 0:
                continue
            forca = G * outro.massa / dist_sq
            dist = math.sqrt(dist_sq)
            self.ax += forca * dx / dist
            self.ay += forca * dy / dist

    def atualizar(self, dt):
        self.vx += self.ax * dt
        self.vy += self.ay * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.rastro.append((self.x, self.y))

    def desenhar(self, tela, cx, cy):
        px = int(cx + self.x / ESCALA)
        py = int(cy + self.y / ESCALA)
        pygame.draw.circle(tela, self.cor, (px, py), RAIO)

        if len(self.rastro) > 2:
            pontos = [(int(cx + x / ESCALA), int(cy + y / ESCALA)) for x, y in self.rastro]
            pygame.draw.lines(tela, self.cor, False, pontos, 1)

    def log_estado(self, tempo):
        arquivo_log.write(f"{tempo:.2f}s | {self.nome} | "
                          f"Pos: ({self.x:.2e}, {self.y:.2e}) | "
                          f"Vel: ({self.vx:.2e}, {self.vy:.2e}) | "
                          f"Acel: ({self.ax:.2e}, {self.ay:.2e})\n")

# Corpos
corpos = [
    Corpo(-3.1e11, 0, 0, 20000, 4e30, (255, 0, 0), "Vermelho"),
    Corpo(1e11, 2e3, 0, 20000, 3e30, (0, 255, 0), "Verde"),
    Corpo(3e1, 1e11, -25000, 0, 2e30, (0, 0, 255), "Azul"),
]

# Loop
rodando = True
pausado = False
tempo_simulado = 0
dt = 7200  # 2 horas por frame

while rodando:
    relogio.tick(FPS)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                rodando = False
            if evento.key == pygame.K_p:
                pausado = not pausado  # Pausar/resumir

    if not pausado:
        # Atualizar física
        for corpo in corpos:
            corpo.atracao(corpos)

        for corpo in corpos:
            corpo.atualizar(dt)
            corpo.log_estado(tempo_simulado)

        tempo_simulado += dt

    # Centralizar
    media_x = sum(c.x for c in corpos) / len(corpos)
    media_y = sum(c.y for c in corpos) / len(corpos)

    tela.fill(PRETO)
    for corpo in corpos:
        corpo.desenhar(tela, LARGURA // 2 - media_x / ESCALA, ALTURA // 2 - media_y / ESCALA)

    pygame.display.flip()

# Encerrar
arquivo_log.close()
pygame.quit()


# Após fechar a simulação, gerar gráfico
plt.figure(figsize=(10, 10))
for corpo in corpos:
    x_vals = [p[0] / ESCALA for p in corpo.rastro]
    y_vals = [p[1] / ESCALA for p in corpo.rastro]
    cor_normalizada = tuple(c / 255 for c in corpo.cor)
    plt.plot(x_vals, y_vals, color=cor_normalizada, label=corpo.nome)

plt.xlabel("X (bilhões de metros)")
plt.ylabel("Y (bilhões de metros)")
plt.title("Rotas dos Corpos Celestes")
plt.legend()
plt.grid(True)
plt.axis('equal')

# Salva com nome baseado no horário da simulação
nome_grafico = nome_arquivo.replace(".txt", ".png")
plt.savefig(nome_grafico, dpi=300)
print(f"Gráfico salvo como {nome_grafico}")
