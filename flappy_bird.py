import pygame
import random
import sys

# Initialiseer pygame
pygame.init()

# --- Constanten ---
# Scherm instellingen
WIDTH = 400
HEIGHT = 600
FPS = 60

# Kleuren (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (135, 206, 235)  # Achtergrond lucht
GREEN = (0, 200, 0)     # Buizen
YELLOW = (255, 200, 0)  # Vogel
RED = (255, 50, 50)     # Game over tekst

# Spel instellingen
GRAVITY = 0.5
JUMP_STRENGTH = -8
PIPE_SPEED = 4
PIPE_WIDTH = 60
PIPE_GAP = 150

# Scherm aanmaken
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()

# Lettertypes
font_large = pygame.font.SysFont(None, 64)
font_medium = pygame.font.SysFont(None, 48)
font_small = pygame.font.SysFont(None, 32)

class Bird:
    def __init__(self):
        self.x = 50
        self.y = HEIGHT // 2
        self.radius = 15
        self.velocity = 1

    def jump(self):
        """Laat de vogel springen door de snelheid negatief te maken."""
        self.velocity = JUMP_STRENGTH

    def update(self):
        """Update de positie van de vogel op basis van zwaartekracht."""
        self.velocity += GRAVITY
        self.y += self.velocity

    def draw(self, surface):
        """Teken de vogel (een gele cirkel) op het scherm."""
        pygame.draw.circle(surface, YELLOW, (int(self.x), int(self.y)), self.radius)
        # Oogje toevoegen voor detail
        pygame.draw.circle(surface, BLACK, (int(self.x + 5), int(self.y - 5)), 3)

class Pipe:
    def __init__(self):
        self.x = WIDTH
        # Willekeurige hoogte voor de onderste buis, zorg voor minimale en maximale grootte
        self.bottom_height = random.randint(50, HEIGHT - PIPE_GAP - 50)
        self.top_height = HEIGHT - PIPE_GAP - self.bottom_height
        self.passed = False # Om bij te houden of we de score al hebben verhoogd

    def update(self):
        """Beweeg de buis naar links."""
        self.x -= PIPE_SPEED

    def draw(self, surface):
        """Teken de bovenste en onderste buis."""
        # Bovenste buis
        pygame.draw.rect(surface, GREEN, (self.x, 0, PIPE_WIDTH, self.top_height))
        # Onderste buis
        pygame.draw.rect(surface, GREEN, (self.x, HEIGHT - self.bottom_height, PIPE_WIDTH, self.bottom_height))

def check_collision(bird, pipes):
    """Controleer of de vogel een buis of de grond/plafond raakt."""
    # Controleer grond en plafond
    if bird.y + bird.radius >= HEIGHT or bird.y - bird.radius <= 0:
        return True

    for pipe in pipes:
        # Maak een onzichtbare rechthoek om de vogel voor de botsing-detectie
        bird_rect = pygame.Rect(bird.x - bird.radius, bird.y - bird.radius, bird.radius * 2, bird.radius * 2)
        
        # Bovenste buis rechthoek
        top_pipe_rect = pygame.Rect(pipe.x, 0, PIPE_WIDTH, pipe.top_height)
        # Onderste buis rechthoek
        bottom_pipe_rect = pygame.Rect(pipe.x, HEIGHT - pipe.bottom_height, PIPE_WIDTH, pipe.bottom_height)
        
        # Check botsing met een van de buizen
        if bird_rect.colliderect(top_pipe_rect) or bird_rect.colliderect(bottom_pipe_rect):
            return True
            
    return False

def draw_text(text, font, color, surface, x, y):
    """Hulpfunctie om tekst op het scherm te centreren en tekenen."""
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)

def main():
    bird = Bird()
    pipes = []
    score = 0
    game_over = False
    
    # Event timer voor het spawnen van nieuwe buizen
    SPAWNPIPE = pygame.USEREVENT
    pygame.time.set_timer(SPAWNPIPE, 1500) # Elke 1.5 seconden een event

    running = True
    while running:
        # 1. Event handling (Invoer van de gebruiker)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                # Spring met spatiebalk als we spelen
                if event.key == pygame.K_SPACE and not game_over:
                    bird.jump()
                
                # Herstart het spel als we af zijn en op 'R' drukken
                if event.key == pygame.K_r and game_over:
                    bird = Bird()
                    pipes.clear()
                    score = 0
                    game_over = False
                    
            # Spawn een nieuwe buis op het getimede event
            if event.type == SPAWNPIPE and not game_over:
                pipes.append(Pipe())

        # 2. Game logic updaten (Posities, scores, botsingen)
        if not game_over:
            bird.update()
            
            for pipe in pipes:
                pipe.update()
                
                # Check of de vogel de buis is gepasseerd (punt scoren)
                if pipe.x + PIPE_WIDTH < bird.x and not pipe.passed:
                    score += 1
                    pipe.passed = True
            
            # Verwijder buizen die helemaal buiten beeld aan de linkerkant zijn
            pipes = [pipe for pipe in pipes if pipe.x + PIPE_WIDTH > 0]
            
            # Controleer of we iets geraakt hebben
            if check_collision(bird, pipes):
                game_over = True

        # 3. Tekenen (Renderen naar het scherm)
        screen.fill(BLUE) # Blauwe lucht achtergrond
        
        # Teken alle buizen
        for pipe in pipes:
            pipe.draw(screen)
            
        # Teken de vogel
        bird.draw(screen)
        
        # Teken de score
        if not game_over:
            draw_text(str(score), font_large, WHITE, screen, WIDTH // 2, 50)
        
        # Teken Game Over scherm
        if game_over:
            # Een donkere overlay om de achtergrond minder zichtbaar te maken
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            screen.blit(overlay, (0,0))
            
            draw_text("GAME OVER", font_large, RED, screen, WIDTH // 2, HEIGHT // 2 - 60)
            draw_text(f"Score: {score}", font_medium, WHITE, screen, WIDTH // 2, HEIGHT // 2)
            draw_text("Druk op 'R' om te herstarten", font_small, YELLOW, screen, WIDTH // 2, HEIGHT // 2 + 50)

        # Update het beeldscherm en wacht tot de volgende frame
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

#test
# Hello world!
#33
