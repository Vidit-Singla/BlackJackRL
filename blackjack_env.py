import random

class BlackjackEnv:
    def __init__(self):
        self.ranks = ["2","3","4","5","6","7","8","9","10","J","Q","K","A"]
        self.suits = ["C","D","H","S"]
        self.reset()

    def _create_deck(self):
        deck = [r+s for r in self.ranks for s in self.suits]  
        random.shuffle(deck)
        return deck

    def _calculate_total(self, hand):
        total = 0
        aces = 0
        for c in hand:
            rank = c[:-1]
            if rank in ["J","K","Q"]:
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
    
    def _usable_ace(self, hand):
        total = 0
        aces = 0
        for c in hand:
            rank = c[:-1]
            if rank in ["J","K","Q"]:
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
    
    def reset(self):
        self.deck = self._create_deck()
        self.player = []
        self.dealer = []
        self.done = False

        self.player.append(self.deck.pop())
        self.dealer.append(self.deck.pop())
        self.player.append(self.deck.pop())
        self.dealer.append(self.deck.pop())

        return self._get_state()
    
    def step(self, action):
        """ 
        action:
            0 = stand
            1 = hit
        """
        if self.done:
            raise Exception("call reset()")
        
        if action == 1:
            self.player.append(self.deck.pop())

            if self._calculate_total(self.player) > 21:
                self.done = True
                return self._get_state(), -1, True
            
            return self._get_state(), 0, False
        
        elif action == 0:
            player_total = self._calculate_total(self.player)

            while True:
                dealer_total = self._calculate_total(self.dealer)

                if dealer_total > 21:
                    break
                if dealer_total > player_total:
                    break

                self.dealer.append(self.deck.pop())


            self.done = True

            
            dealer_total = self._calculate_total(self.dealer)

            if dealer_total > 21 or player_total > dealer_total:
                reward = 1
            elif dealer_total > player_total:
                reward = -1
            else:
                reward = 0

            return self._get_state(), reward, True
        
        else:
            raise ValueError("Invalid")
        
    def _get_state(self):
        player_total = self._calculate_total(self.player)
        dealer_upcard = self.dealer[0][:-1]

        if dealer_upcard in ["J","K","Q"]:
            dealer_value = 10
        elif dealer_upcard == "A":
            dealer_value = 11
        else:
            dealer_value = int(dealer_upcard)

        usable = self._usable_ace(self.player)
        return (player_total, dealer_value, usable)
        