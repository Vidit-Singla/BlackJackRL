import pygame
import sys
import random

pygame.init()

#main window
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

wood = pygame.transform.smoothscale(wood, (530, 530))
felt = pygame.transform.smoothscale(felt, (450, 450))

#load cards
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

#player variables
dealer_cards = []
player_cards = []
deck = []

game_phase = "dealing"
deal_sequence = []

is_animating = False
animation_card = None
animation_target = None
animation_progress = 0
animation_speed = 0.033

flip_progress = 0
dealer_revealed = False
results = ""

font = pygame.font.SysFont("arial", 28, bold=True)
card_spacing = 70

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


def reset_game():
    global deck, dealer_cards, player_cards
    global game_phase, deal_sequence
    global dealer_revealed, results

    deck = list(card_images.keys())
    random.shuffle(deck)

    dealer_cards = []
    player_cards = []

    deal_sequence = ["player","dealer","player","dealer"]
    game_phase = "dealing"
    dealer_revealed = False
    results = ""


def start_animation(target, card):
    global is_animating, animation_card, animation_target, animation_progress
    is_animating = True
    animation_card = card
    animation_target = target
    animation_progress = 0


reset_game()

#main
running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_r:
                reset_game()

            if game_phase == "playing":

                if event.key == pygame.K_h and not is_animating:
                    card = deck.pop()
                    start_animation("player", card)

                if event.key == pygame.K_s:
                    game_phase = "dealer_reveal"
                    flip_progress = 0

    #animation
    if is_animating:
        animation_progress += animation_speed

        if animation_progress >= 1:
            animation_progress = 1
            is_animating = False

            if animation_target == "player":
                player_cards.append(animation_card)

                # Player Bust
                if calculate_total(player_cards) > 21:
                    results = "You Bust! Dealer Wins!"
                    dealer_revealed = True
                    game_phase = "round_over"

            else:
                dealer_cards.append(animation_card)

            #Finish initial deal
            if game_phase == "dealing":
                if deal_sequence:
                    deal_sequence.pop(0)
                if not deal_sequence:
                    game_phase = "playing"

            #Dealer draw loop
            if game_phase == "dealer_turn" and not is_animating:
                if calculate_total(dealer_cards) <= player_total and dealer_total <= 21:
                    card = deck.pop()
                    start_animation("dealer", card)
                else:
                    p = calculate_total(player_cards)
                    d = calculate_total(dealer_cards)

                    if d > 21 or p > d:
                        results = "You Win!"
                    elif d > p:
                        results = "Dealer Wins!"
                    else:
                        results = "Draw"

                    game_phase = "round_over"

    #initial deal
    if game_phase == "dealing" and not is_animating:
        if deal_sequence:
            target = deal_sequence[0]
            card = deck.pop()
            start_animation(target, card)

    #dealer reveal
    if game_phase == "dealer_reveal":
        flip_progress += 0.08

        if flip_progress >= 1:
            flip_progress = 1
            dealer_revealed = True

            
            if calculate_total(dealer_cards) < 17:
                game_phase = "dealer_turn"
                card = deck.pop()
                start_animation("dealer", card)
            else:
                p = calculate_total(player_cards)
                d = calculate_total(dealer_cards)

                if d > 21 or p > d:
                    results = "You Win!"
                elif d > p:
                    results = "Dealer Wins!"
                else:
                    results = "Draw"

                game_phase = "round_over"

    #drawing
    screen.fill((18,28,70))

    table_center_x = width//2
    table_center_y = height//3 + 60

    screen.blit(wood, wood.get_rect(center=(table_center_x, table_center_y)))
    screen.blit(felt, felt.get_rect(center=(table_center_x, table_center_y)))

    #Deck stack
    screen.blit(card_back, deck_pos)

    #Dealer cards
    dealer_y = table_center_y - 100
    for i,c in enumerate(dealer_cards):
        x = table_center_x + (i - len(dealer_cards)/2)*card_spacing
        if i == 1 and not dealer_revealed:
            img = card_back
        else:
            img = card_images[c]
        screen.blit(img, img.get_rect(center=(x,dealer_y)))

    #Player cards
    player_y = table_center_y + 100
    for i,c in enumerate(player_cards):
        x = table_center_x + (i - len(player_cards)/2)*card_spacing
        screen.blit(card_images[c], card_images[c].get_rect(center=(x,player_y)))

    #Sliding animation
    if is_animating:
        start_x, start_y = deck_pos

        if animation_target == "player":
            target_y = player_y
        else:
            target_y = dealer_y

        target_x = table_center_x

        current_x = start_x + (target_x - start_x) * animation_progress
        current_y = start_y + (target_y - start_y) * animation_progress

        screen.blit(card_images[animation_card],
                    card_images[animation_card].get_rect(center=(current_x,current_y)))

    #Flip animation
    if game_phase == "dealer_reveal" and len(dealer_cards) > 1:
        hidden_card = dealer_cards[1]
        scale = abs(1 - flip_progress*2)
        scaled_width = max(1, int(card_width * scale))
        img = card_back if flip_progress < 0.5 else card_images[hidden_card]
        scaled_img = pygame.transform.scale(img, (scaled_width, card_height))
        x = table_center_x + (1 - len(dealer_cards)/2)*card_spacing
        screen.blit(scaled_img, scaled_img.get_rect(center=(x,dealer_y)))

    #Totals
    player_total = calculate_total(player_cards)
    dealer_total = calculate_total(dealer_cards if dealer_revealed else dealer_cards[:1])

    screen.blit(font.render(f"YOUR TOTAL: {player_total}", True, (230,230,230)),
                (width//3 - 220, height-60))

    screen.blit(font.render(f"DEALER TOTAL: {dealer_total}", True, (230,230,230)),
                (2*width//3 + 40, height-60))

    #Result
    if game_phase == "round_over":
        screen.blit(font.render(results, True, (255,215,0)),
                    (width//2 - 100, 40))

    pygame.display.flip()

pygame.quit()
sys.exit()
