import pygame
import sys
import random
import pickle
import time

pygame.init()

with open("mc_policy.pkl", "rb") as f:
    Q = pickle.load(f)

#window
width = 1000
height = 700
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Blackjack")

clock = pygame.time.Clock()

#table
wood = pygame.image.load("assets/wood_circle.png").convert_alpha()
felt = pygame.image.load("assets/felt_circle.png").convert_alpha()

card_width = 60
card_height = 80
card_spacing = 70

wood = pygame.transform.smoothscale(wood, (530, 530))
felt = pygame.transform.smoothscale(felt, (450, 450))

#cards
ranks = ["2","3","4","5","6","7","8","9","10","J","Q","K","A"]
suits = ["C","D","H","S"]

card_images = {}
for r in ranks:
    for s in suits:
        img = pygame.image.load(f"assets/Cards/{r}{s}.png").convert_alpha()
        img = pygame.transform.smoothscale(img, (card_width, card_height))
        card_images[f"{r}{s}"] = img

card_back = pygame.image.load("assets/Cards/BACK.png").convert_alpha()
card_back = pygame.transform.smoothscale(card_back, (card_width, card_height))

deck_pos = (width - 180, height//3)

#states
dealer_cards = []
player_cards = []
deck = []

game_phase = "dealing"
deal_sequence = []

round_over_time = 0

is_animating = False
animation_card = None
animation_target = None
animation_progress = 0
animation_speed = 0.02  

flip_progress = 0
dealer_revealed = False
results = ""

font = pygame.font.SysFont("arial", 28, bold=True)

ai_delay = 1.2            
decision_delay = 0.8      
last_ai_action = 0

ai_decision_text = ""    
decision_time = 0        

#functions
def calculate_total(hand):
    total = 0
    aces = 0

    for c in hand:
        rank = c[:-1]
        if rank in ["J","Q","K"]:
            total += 10
        elif rank == "A":
            total += 11
            aces += 1
        else:
            total += int(rank)

    while total > 21 and aces:
        total -= 10
        aces -= 1

    return total


def usable_ace(hand):
    total = 0
    aces = 0

    for c in hand:
        rank = c[:-1]
        if rank in ["J","Q","K"]:
            total += 10
        elif rank == "A":
            total += 11
            aces += 1
        else:
            total += int(rank)

    while total > 21 and aces:
        total -= 10
        aces -= 1

    return aces > 0 and total <= 21


def dealer_upcard_value():
    rank = dealer_cards[0][:-1]

    if rank in ["J","Q","K"]:
        return 10
    elif rank == "A":
        return 11
    else:
        return int(rank)


def reset_game():
    global deck, dealer_cards, player_cards
    global game_phase, deal_sequence
    global dealer_revealed, results, flip_progress
    global ai_decision_text   

    deck = list(card_images.keys())
    random.shuffle(deck)

    dealer_cards = []
    player_cards = []

    deal_sequence = ["player","dealer","player","dealer"]
    game_phase = "dealing"
    dealer_revealed = False
    results = ""
    flip_progress = 0
    ai_decision_text = "" 


def start_animation(target, card):
    global is_animating, animation_card, animation_target, animation_progress
    is_animating = True
    animation_card = card
    animation_target = target
    animation_progress = 0


reset_game()

#main loop
running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    current_time = time.time()

    #ai playing
    if game_phase == "playing" and not is_animating:

        player_total = calculate_total(player_cards)

        if player_total > 21:
            results = "AI Bust! Dealer Wins!"
            dealer_revealed = True
            game_phase = "round_over"
            round_over_time = current_time

        else:
            state = (player_total,
                     dealer_upcard_value(),
                     usable_ace(player_cards))

            if state in Q:
                action = Q[state].index(max(Q[state]))
            else:
                action = 0

            #show decision first
            if ai_decision_text == "":
                if action == 1:
                    ai_decision_text = "AI decides: HIT"
                else:
                    ai_decision_text = "AI decides: STAND"
                decision_time = current_time

            elif current_time - decision_time > decision_delay:
                if action == 1:
                    card = deck.pop()
                    start_animation("player", card)
                else:
                    game_phase = "dealer_reveal"
                    flip_progress = 0

                ai_decision_text = ""
                last_ai_action = current_time

    #initial deal
    if game_phase == "dealing" and not is_animating:
        if deal_sequence:
            target = deal_sequence[0]
            card = deck.pop()
            start_animation(target, card)

    #animation
    if is_animating:
        animation_progress += animation_speed

        if animation_progress >= 1:
            animation_progress = 1
            is_animating = False

            if animation_target == "player":
                player_cards.append(animation_card)
            else:
                dealer_cards.append(animation_card)

            if game_phase == "dealing":
                deal_sequence.pop(0)
                if not deal_sequence:
                    game_phase = "playing"

   #dealer reveal
    if game_phase == "dealer_reveal":
        flip_progress += 0.04   
        if flip_progress >= 1:
            flip_progress = 1
            dealer_revealed = True
            game_phase = "dealer_turn"

    #dealer turn
    if game_phase == "dealer_turn" and not is_animating:
        p = calculate_total(player_cards)
        d = calculate_total(dealer_cards)

        if d <= p and d <= 21:
            card = deck.pop()
            start_animation("dealer", card)
        else:
            if d > 21 or p > d:
                results = "AI Wins!"
            elif d > p:
                results = "Dealer Wins!"
            else:
                results = "Draw"

            game_phase = "round_over"
            round_over_time = current_time

   #auto reset
    if game_phase == "round_over":
        if current_time - round_over_time > 2:
            reset_game()
            # last_ai_action = current_time

    #drawing
    screen.fill((18,28,70))

    table_center_x = width//2
    table_center_y = height//3 + 60

    screen.blit(wood, wood.get_rect(center=(table_center_x, table_center_y)))
    screen.blit(felt, felt.get_rect(center=(table_center_x, table_center_y)))

    screen.blit(card_back, deck_pos)

    dealer_y = table_center_y - 100
    player_y = table_center_y + 100

    for i,c in enumerate(dealer_cards):
        x = table_center_x + (i - len(dealer_cards)/2)*card_spacing
        if i == 1 and not dealer_revealed:
            img = card_back
        else:
            img = card_images[c]
        screen.blit(img, img.get_rect(center=(x,dealer_y)))

    for i,c in enumerate(player_cards):
        x = table_center_x + (i - len(player_cards)/2)*card_spacing
        screen.blit(card_images[c], card_images[c].get_rect(center=(x,player_y)))

    if is_animating:
        start_x, start_y = deck_pos
        target_y = player_y if animation_target == "player" else dealer_y
        target_x = table_center_x

        current_x = start_x + (target_x - start_x) * animation_progress
        current_y = start_y + (target_y - start_y) * animation_progress

        screen.blit(card_images[animation_card],
                    card_images[animation_card].get_rect(center=(current_x,current_y)))


    if ai_decision_text != "":
        screen.blit(font.render(ai_decision_text, True, (255,255,255)),
                    (width//2 - 130, 90))

    player_total = calculate_total(player_cards)
    dealer_total = calculate_total(dealer_cards if dealer_revealed else dealer_cards[:1])

    screen.blit(font.render(f"AI TOTAL: {player_total}", True, (230,230,230)),
                (width//3 - 220, height-60))

    screen.blit(font.render(f"DEALER TOTAL: {dealer_total}", True, (230,230,230)),
                (2*width//3 + 40, height-60))

    if game_phase == "round_over":
        screen.blit(font.render(results, True, (255,215,0)),
                    (width//2 - 100, 40))

    pygame.display.flip()

pygame.quit()
sys.exit()