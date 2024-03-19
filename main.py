"""System Bibliotheken."""
import sys
from random import randint, uniform
from pygame.locals import MOUSEBUTTONDOWN, QUIT
import pygame
import pygame.math


# Konstante Variable für die Breite und Höher
WINDOW_WIDTH = 1380

#WINDOW_HEIGHT = 750
WINDOW_HEIGHT = 850


class Person(pygame.sprite.Sprite):
    """
     Person erbt alle Attribute und Methoden der "Sprite"
     Klasse und kann auch ihre eigenen Attribute und Methoden definieren.
    """

    def __init__(self, groups, window_width, window_height):

        # Die Elternklasse wurde initieren
        super().__init__(groups)
        # Schriftart wurde ausgewählt und de große wurde bestimmt
        self.schrift_art = pygame.font.Font('Schrift.ttf',
                                            50)

        # Clock bietet eine Möglichkeit, die Zeit zu verfolgen,
        # und kann verwendet werden, um die Bildrate
        # zu steuern, die verstrichene Zeit zu messen
        # und die Geschwindigkeit der Spielschleife zu begrenzen.

        self.zeit_steuerung = pygame.time.Clock()
        self.time = 0

        # Kämferperson Foto wurde geladen, um die zu verwenden
        self.image = pygame.image.load('Artz (1).png').convert_alpha()

        # Rechteck darstellt den Bereich und die Position des Bildes
        self.rect = self.image.get_rect(center=(window_width / 2,
                                                window_height / 2))

        #Die Maske wird verwendet, um Operationen,
        # die Transparenz beinhalten,
        # wie zum Beispiel Kollisionserkennung, durchzuführen.

        self.mask = pygame.mask.from_surface(self.image)

        # timer
        self.schiessen_breit = True
        self.schiessen_time = None

    def impfstoff_timer(self):
        """organisiert der Rate des Schießens des Impfstoffs"""
        if not self.schiessen_breit:
            aktuelle_uhrzeit = pygame.time.get_ticks()
            if aktuelle_uhrzeit - self.schiessen_time > 500:
                self.schiessen_breit = True

    def input_position(self):
        """Festlegung von Position des Mouses"""
        position = pygame.mouse.get_pos()
        self.rect.center = position

    def impfstoff_schiessen(self, impfstoff_group):
        """schießt Impfstoff ab"""
        # sound
        self.impfstoff_sound = pygame.mixer.Sound('wurf.WAV')
        if pygame.mouse.get_pressed()[0] and self.schiessen_breit:
            self.schiessen_breit = False
            self.schiessen_time = pygame.time.get_ticks()
            Impfstoff(self.rect.midtop, impfstoff_group)
            self.impfstoff_sound.play()

    def display(self, display_surface, window_width, window_height):
        """Hier werden die Sachen, die auf dem Display gezeigt werden, definiert.Z.B die Zeit """

        # Clock.tick() gibt zurück, wie viele
        # Millisekunden seit dem letzten Aufruf vergangen sind,
        # also zeigt, wie lange die While -Schleife dauert

        milli = self.zeit_steuerung.tick()
        seconds = milli / 1000
        self.time += seconds
        score_text = f'Time: {self.time:.0f}'
        text_surf = self.schrift_art.render(score_text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(midbottom=(window_width / 2, window_height - 80))
        display_surface.blit(text_surf, text_rect)
        pygame.draw.rect(
            display_surface,
            (255, 255, 255),
            text_rect.inflate(30, 30),
            width=8,
            border_radius=5
        )

    def person_collision(self, virus_group, background_surf_statr_and_ende, display_surface,
                         font, window_height, titel_schrift):
        """wenn Person mit dem Virus collidert"""
        if pygame.sprite.spritecollide(self, virus_group, False, pygame.sprite.collide_mask):
            end_menu(background_surf_statr_and_ende,
                     display_surface, font, window_height, titel_schrift)
            main_loop(False)

    def update(self, impfstoff_group, virus_group, background_surf_statr_and_ende, display_surface,
               schrift, window_height, window_width, titel_schrift):
        """Updatet die Positionen der Person bzw. Frames"""
        self.impfstoff_timer()
        self.impfstoff_schiessen(impfstoff_group)
        self.input_position()
        self.display(display_surface, window_height,
                     window_width)
        self.person_collision(virus_group, background_surf_statr_and_ende,
                              display_surface, schrift, WINDOW_WIDTH, titel_schrift)


class Impfstoff(pygame.sprite.Sprite):
    """Erzeugt die von Person abgeschoßene Impfstoffe """
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.score1 = 0
        self.font = pygame.font.Font('Schrift.ttf', 50)
        self.image = pygame.image.load('Impfstoff (1).png').convert_alpha()
        self.rect = self.image.get_rect(midbottom=pos)
        self.mask = pygame.mask.from_surface(self.image)

        '''Float basierte Position'''
        self.position = pygame.math.Vector2(self.rect.topleft)
        self.direction = pygame.math.Vector2(0, -1)
        self.speed = 1000

        # sound
        self.impfung_sound = pygame.mixer.Sound('treffen.wav')

    def virus_collision(self, virus_group):
        """wenn abgeschoßene Impfstoff mit Virus collidert"""
        if pygame.sprite.spritecollide(self, virus_group, True, pygame.sprite.collide_mask):
            self.kill()
            self.impfung_sound.play()


    def update(self, dalta, angreifer_virus_group, display_surface, window_height, window_width):
        """Updatet die Positionen des Impfstoffs bzw. Frames"""
        self.position += self.direction * self.speed * dalta
        self.rect.topleft = (round(self.position.x), round(self.position.y))
        if self.rect.bottom < 0:
            self.kill()

        if pygame.sprite.spritecollide(self, angreifer_virus_group,
                                       False, pygame.sprite.collide_mask):
            self.score1 += 1
            self.virus_collision(angreifer_virus_group)


class AngreiferVirus(pygame.sprite.Sprite):
    """Erzeugt Virenobjekte"""
    def __init__(self, pos, groups):
        # Basic setup
        super().__init__(groups)
        virus_surf = pygame.image.load('Virus.png').convert_alpha()
        virus_size = pygame.math.Vector2(virus_surf.get_size()) * uniform(0.5, 1.5)
        self.scaled_surf = pygame.transform.scale(virus_surf, virus_size)
        self.image = self.scaled_surf
        self.rect = self.image.get_rect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)

        # Float-basierte Positionierung
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.direction = pygame.math.Vector2(uniform(-0.5, 0.5), 1)
        self.speed = randint(200, 300)

        # Rotation logic
        self.rotation = 0
        self.rotation_speed = randint(20, 50)

    def rotate(self, dalta):
        """Die Objekte werden mehrmals erzeugt """
        self.rotation += self.rotation_speed * dalta
        rotated_surf = pygame.transform.rotozoom(self.scaled_surf, self.rotation, 1)
        self.image = rotated_surf
        self.rect = self.image.get_rect(center=self.rect.center)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dalta, window_height):
        """Updatet die Positionen der Viren bzw. Frames"""
        self.pos += self.direction * self.speed * dalta
        self.rect.topleft = (round(self.pos.x), round(self.pos.y))
        self.rotate(dalta)

        if self.rect.top > window_height:
            self.kill()



def draw_text(text, knopf_schrift, farbe, surface, laenge, breite):
    """Schreibt und drückt texte, wo die Methode benutzt wird"""
    textobj = knopf_schrift.render(text, 1, farbe)
    textrect = textobj.get_rect()
    textrect.topleft = (laenge, breite)
    surface.blit(textobj, textrect)


def main_menu(display_surface, knopf_schrift,
              background_surf_statr_and_ende, window_width, titel_schrift):
    """Erzeugt die Startseite"""
    bg_music = pygame.mixer.Sound('Hintergrund_sound.wav')
    bg_music.play(loops=-1)
    click = False
    while True:

        display_surface.blit(background_surf_statr_and_ende,
                             (0, 0))
        draw_text('VIREN KÄMPFEN SPIEL', titel_schrift, (0, 0, 0),
                  display_surface, (window_width / 2) / 1.8, 40)
        mouse_x_posi, mouse_y_posi = pygame.mouse.get_pos()

        # Creating buttons
        button_1 = pygame.Rect(980, 500, 200, 50)
        button_2 = pygame.Rect(980, 565, 200, 50)

        # Definition von Funktionen, wenn eine bestimmte Taste gedrückt wird
        if button_1.collidepoint((mouse_x_posi, mouse_y_posi)):
            if click:
                return True
        if button_2.collidepoint((mouse_x_posi, mouse_y_posi)):
            if click:
                pygame.quit()
                sys.exit()
        pygame.draw.rect(display_surface, (199, 21, 133), button_1)
        pygame.draw.rect(display_surface, (199, 21, 133), button_2)

        # writing text on top of button
        draw_text('PLAY', knopf_schrift, (0, 0, 0), display_surface, 1054, 515)
        draw_text('Exit', knopf_schrift, (0, 0, 0), display_surface, 1059, 580)

        click = False
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            # if event.type == KEYDOWN:
            # if event.key == K_ESCAPE:
            # sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
        pygame.display.update()

def end_menu(background_surf_statr_and_ende, display_surface,
             knopf_schrift, window_width, titel_end_schrift):
    """Erzeugt die Endseite, die nach dem Verlieren des Spiels gezeigt wird"""
    click = False
    while True:

        display_surface.blit(
            background_surf_statr_and_ende, (0, 0))
        draw_text('GAME OVER !', titel_end_schrift,
                  (0, 0, 0), display_surface,
                  (window_width / 2) / 1.4, 200)

        mouse_x_posi, mouse_y_posi = pygame.mouse.get_pos()

        # buttons erstellen
        button_1 = pygame.Rect((window_width / 5) * 1.6, 400, 200, 50)
        button_2 = pygame.Rect((window_width / 5) * 2.7, 400, 200, 50)

        # Definition von Funktionen, wenn eine bestimmte Taste gedrückt wird
        if button_1.collidepoint((mouse_x_posi, mouse_y_posi)):
            if click:
                return True
        if button_2.collidepoint((mouse_x_posi, mouse_y_posi)):
            if click:
                pygame.quit()
                sys.exit()
        pygame.draw.rect(display_surface, (199, 21, 133), button_1)
        pygame.draw.rect(display_surface, (199, 21, 133), button_2)
        # writing text on top of button
        draw_text('Replay', knopf_schrift, (0, 0, 0),
                  display_surface, (window_width / 4.9) * 1.8, 413)
        draw_text('Exit', knopf_schrift, (0, 0, 0),
                  display_surface, (window_width / 4.9) * 2.9, 413)

        click = False
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True

        pygame.display.update()

# game loop
def main_loop(test=True):
    """Die Main Methode, wo die Schleife des Spiels sich befindet"""
    # basic setup
    pygame.init()

    display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Viren Kämpfer ')
    clock = pygame.time.Clock()

    # hintergrund
    background_surf = pygame.image.load('Coronavirus_background.jpg').convert()
    background_surf_statr_and_ende = pygame.image.load('Hintergrund1.png').convert()

    # sprite groups
    person_group = pygame.sprite.GroupSingle()
    impfstoff_grupe = pygame.sprite.Group()
    virus_group = pygame.sprite.Group()

    # sprite creation
    Person(person_group, WINDOW_WIDTH, WINDOW_HEIGHT)

    # timer
    virus_timer = pygame.event.custom_type()
    pygame.time.set_timer(virus_timer, 200)

    knopf_schrift = pygame.font.SysFont(None, 30)
    titel_start_schrift = pygame.font.SysFont(None, 80)

    while True:
        start_game = True
        if test:
            start_game = main_menu(display_surface,
                                   knopf_schrift,
                                   background_surf_statr_and_ende, WINDOW_WIDTH,
                                   titel_start_schrift)

        while start_game:

            # event loop
            for event in pygame.event.get():
                if event.type == QUIT:
                    sys.exit()
                if event.type == virus_timer:
                    virus_y_pos = randint(-150, -50)
                    virus_x_pos = randint(-100, WINDOW_WIDTH + 100)
                    AngreiferVirus((virus_x_pos, virus_y_pos), groups=virus_group)

            # delta time
            delta_zeit = clock.tick() / 1000

            # hintergrund
            display_surface.blit(
                background_surf, (0, 0))
            # update

            person_group.update(impfstoff_grupe, virus_group,
                                background_surf_statr_and_ende,
                                display_surface, knopf_schrift,
                                WINDOW_WIDTH,
                                WINDOW_HEIGHT,
                                titel_start_schrift)
            impfstoff_grupe.update(delta_zeit, virus_group,
                                   display_surface, WINDOW_WIDTH, WINDOW_HEIGHT)
            virus_group.update(delta_zeit, WINDOW_HEIGHT)

            # graphics
            person_group.draw(display_surface)
            impfstoff_grupe.draw(display_surface)
            virus_group.draw(display_surface)

            # draw the frame
            pygame.display.update()

main_loop()

#Quellen:
    #1. https://www.pygame.org/docs/
    #2. https://www.farb-tabelle.de/de/rgb2hex.htm?q=199%2C21%2C133
    #3. https://www.flaticon.com/search?word=bullet
    #4. https://www.resizepixel.com/de/download
    #5. https://www.pexels.com/de-de/suche/gaming/
    #6. https://mixkit.co/free-sound-effects/game/
