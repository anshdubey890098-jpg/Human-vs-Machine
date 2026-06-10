import pygame
import random
import sys
import json
import os

pygame.init()
W, H = 720, 1280
screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()
FPS = 60

WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
BLUE = (50, 150, 255)
GREEN = (50, 255, 100)
RED = (255, 80, 80)
YELLOW = (255, 220, 0)
PURPLE = (180, 80, 255)
GRAY = (100, 100, 100)

font_big = pygame.font.SysFont('arial', 60, bold=True)
font_med = pygame.font.SysFont('arial', 40)
font_small = pygame.font.SysFont('arial', 30)

SAVE_FILE = "guessing_score.json"
def load_highscore():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, 'r') as f: return json.load(f).get('high', 999)
    return 999

def save_highscore(score):
    with open(SAVE_FILE, 'w') as f: json.dump({'high': score}, f)

class Button:
    def __init__(self, x, y, w, h, text, color):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        
    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=15)
        txt = font_med.render(self.text, True, WHITE)
        screen.blit(txt, (self.rect.centerx - txt.get_width()//2, 
                         self.rect.centery - txt.get_height()//2))
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class Game:
    def __init__(self):
        self.state = "menu"
        self.reset()
        self.highscore = load_highscore()
        self.buttons = [Button(W//2-100, 250+i*90, 200, 70, str(i+1), BLUE) for i in range(10)]
        self.feedback_btns = {
            'h': Button(W//2-200, H-300, 120, 80, "HIGH", RED),
            'l': Button(W//2+80, H-300, 120, 80, "LOW", GREEN),
            'c': Button(W//2-60, H-180, 120, 80, "OK", YELLOW)
        }
        self.play_btn = Button(W//2-150, H//2+100, 300, 80, "PLAY", GREEN)
        
    def reset(self):
        self.ai_number = random.randint(1, 10)
        self.user_attempts = 0
        self.ai_attempts = 0
        self.ai_low, self.ai_high = 1, 10
        self.ai_guess = 0
        self.timer = 30 * FPS
        self.message = ""
        self.message_timer = 0
        
    def draw_menu(self):
        screen.fill(BLACK)
        title = font_big.render("Number Battle 2D", True, PURPLE)
        screen.blit(title, (W//2 - title.get_width()//2, 150))
        
        high = font_med.render(f"Best Score: {self.highscore} tries", True, YELLOW)
        screen.blit(high, (W//2 - high.get_width()//2, 300))
        
        twist = font_small.render("Theme: Catch the Number Chor!", True, WHITE)
        screen.blit(twist, (W//2 - twist.get_width()//2, 380))
        
        self.play_btn.draw()
        
    def draw_user_turn(self):
        screen.fill(BLACK)
        title = font_big.render("Your Turn", True, BLUE)
        screen.blit(title, (W//2 - title.get_width()//2, 50))
        
        time_left = self.timer // FPS
        timer_txt = font_med.render(f"Time: {time_left}s", True, RED if time_left<10 else WHITE)
        screen.blit(timer_txt, (50, 50))
        
        score_txt = font_med.render(f"Tries: {self.user_attempts}", True, WHITE)
        screen.blit(score_txt, (W-200, 50))
        
        hint = font_small.render("AI ne 1-10 me number chupaya hai!", True, GRAY)
        screen.blit(hint, (W//2 - hint.get_width()//2, 150))
        
        for btn in self.buttons:
            btn.draw()
            
        if self.message_timer > 0:
            msg = font_med.render(self.message, True, YELLOW)
            screen.blit(msg, (W//2 - msg.get_width()//2, H-150))
            self.message_timer -= 1
    
    def draw_ai_turn(self):
        screen.fill(BLACK)
        title = font_big.render("AI's Turn", True, RED)
        screen.blit(title, (W//2 - title.get_width()//2, 50))
        
        if self.ai_guess == 0:
            self.ai_guess = (self.ai_low + self.ai_high) // 2
            self.ai_attempts += 1
            
        pygame.draw.circle(screen, PURPLE, (W//2, H//2-100), 120)
        guess_txt = font_big.render(str(self.ai_guess), True, WHITE)
        screen.blit(guess_txt, (W//2 - guess_txt.get_width()//2, H//2-130))
        
        ask = font_med.render("Tumhara number kaisa hai?", True, WHITE)
        screen.blit(ask, (W//2 - ask.get_width()//2, H//2+50))
        
        tries = font_small.render(f"AI Tries: {self.ai_attempts}", True, GRAY)
        screen.blit(tries, (W//2 - tries.get_width()//2, H//2+100))
        
        for btn in self.feedback_btns.values():
            btn.draw()
    
    def draw_result(self):
        screen.fill(BLACK)
        title = font_big.render("RESULT", True, YELLOW)
        screen.blit(title, (W//2 - title.get_width()//2, 100))
        
        user_txt = font_med.render(f"Tum: {self.user_attempts} tries", True, BLUE)
        ai_txt = font_med.render(f"AI: {self.ai_attempts} tries", True, RED)
        screen.blit(user_txt, (W//2 - user_txt.get_width()//2, 250))
        screen.blit(ai_txt, (W//2 - ai_txt.get_width()//2, 320))
        
        if self.user_attempts < self.ai_attempts:
            win = font_big.render("YOU WIN!", True, GREEN)
            if self.user_attempts < self.highscore:
                self.highscore = self.user_attempts
                save_highscore(self.highscore)
                new = font_med.render("NEW HIGHSCORE!", True, YELLOW)
                screen.blit(new, (W//2 - new.get_width()//2, 500))
        elif self.ai_attempts < self.user_attempts:
            win = font_big.render("AI WINS!", True, RED)
        else:
            win = font_big.render("DRAW!", True, WHITE)
            
        screen.blit(win, (W//2 - win.get_width()//2, 400))
        
        again = font_small.render("Tap to play again", True, GRAY)
        screen.blit(again, (W//2 - again.get_width()//2, H-100))
    
    def handle_click(self, pos):
        if self.state == "menu":
            if self.play_btn.is_clicked(pos):
                self.reset()
                self.state = "user_turn"
                
        elif self.state == "user_turn":
            for i, btn in enumerate(self.buttons):
                if btn.is_clicked(pos):
                    guess = i + 1
                    self.user_attempts += 1
                    
                    if guess < self.ai_number:
                        self.message = "Too Low! Chota hai"
                        self.message_timer = 60
                    elif guess > self.ai_number:
                        self.message = "Too High! Bada hai"
                        self.message_timer = 60
                    else:
                        self.message = "Correct! Pakad liya chor ko!"
                        self.message_timer = 60
                        pygame.time.wait(1000)
                        self.state = "ai_turn"
                        self.ai_guess = 0
                        
        elif self.state == "ai_turn":
            if self.feedback_btns['c'].is_clicked(pos):
                self.state = "result"
            elif self.feedback_btns['h'].is_clicked(pos):
                self.ai_low = self.ai_guess + 1
                self.ai_guess = 0
            elif self.feedback_btns['l'].is_clicked(pos):
                self.ai_high = self.ai_guess - 1
                self.ai_guess = 0
                
        elif self.state == "result":
            self.state = "menu"
    
    def update(self):
        if self.state == "user_turn":
            self.timer -= 1
            if self.timer <= 0:
                self.user_attempts = 99
                self.state = "ai_turn"
                self.ai_guess = 0

game = Game()
run = True

while run:
    clock.tick(FPS)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            game.handle_click(event.pos)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            run = False
    
    game.update()
    
    if game.state == "menu": game.draw_menu()
    elif game.state == "user_turn": game.draw_user_turn()
    elif game.state == "ai_turn": game.draw_ai_turn()
    elif game.state == "result": game.draw_result()
    
    pygame.display.flip()

pygame.quit()
sys.exit()
