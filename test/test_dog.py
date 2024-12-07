import pytest
from server.py.dog import Dog, GameState, GamePhase, RandomPlayer, Card, Action

def test_get_and_set_state():
    """Test get and set state"""
    # Initialize the game
    game = Dog()
    game.initialize_game()
    
    # Get the current state
    original_state = game.get_state()
    
    # Perform some operations on the game state
    original_state.cnt_round += 1  # Increment the round
    original_state.bool_card_exchanged = True  # Change a state property
    
    # Set the modified state
    game.set_state(original_state)
    
    # Retrieve the state again to verify
    modified_state = game.get_state()
    
    # Assert that the state has been correctly updated
    assert modified_state.cnt_round == original_state.cnt_round, "Round count did not update correctly."
    assert modified_state.bool_card_exchanged == original_state.bool_card_exchanged, "Card exchange flag did not update correctly."

def test_reshuffle_logic():
    """Test reshuffling logic when the draw pile is empty."""
    # Initialize the game
    game = Dog()
    game.initialize_game()
    
    # Simulate an empty draw pile and a populated discard pile
    state = game.get_state()
    state.list_card_discard = [Card(suit='♥', rank='A')] * 50  # Add 50 cards to the discard pile
    state.list_card_draw = []  # Empty the draw pile
    
    # Set the modified state
    game.set_state(state)
    
    # Call the reshuffling method
    game.reshuffle_discard_into_draw()
    
    # Verify the reshuffle logic
    state = game.get_state()  # Get the updated state after reshuffling
    assert len(state.list_card_draw) == 50, "Reshuffle failed: Draw pile does not have the correct number of cards."
    assert len(state.list_card_discard) == 0, "Reshuffle failed: Discard pile was not cleared."


def test_get_list_action_no_valid_kennel_moves():
    """Test get_list_action when all marbles are in the kennel and no valid cards are available."""
    # Initialize the game
    game = Dog()
    game.initialize_game()
    
    # Set up the game state
    player_idx = 0  # Test the first player
    game.state.idx_player_active = player_idx
    active_player = game.state.list_player[player_idx]

    # Place all marbles in the kennel for the active player
    kennels = {
        0: [64, 65, 66, 67],
        1: [72, 73, 74, 75],
        2: [80, 81, 82, 83],
        3: [88, 89, 90, 91]
    }
    for i, marble in enumerate(active_player.list_marble):
        marble.pos = kennels[player_idx][i]

    # Assign cards that cannot move marbles out of the kennel
    invalid_cards = [
        Card(suit='♠', rank='2'), 
        Card(suit='♥', rank='3'), 
        Card(suit='♦', rank='4'),
        Card(suit='♣', rank='5'), 
        Card(suit='♠', rank='6'), 
        Card(suit='♥', rank='8')
    ]
    active_player.list_card = invalid_cards

    # Call get_list_action and verify the result
    actions = game.get_list_action()

    # Assert that no actions are returned
    assert len(actions) == 0, f"Expected no actions, but found: {actions}"

    print("Test passed: No valid actions when all marbles are in the kennel and no valid cards are available.")


def test_move_out_of_kennel_two_cards():
    """Test: Move out of kennel without marble on the starting position."""
    
    # Initialize the game
    game = Dog()
    game.reset()
    
    # Set up the game state
    state = game.get_state()
    idx_player_active = 0
    state.cnt_round = 0
    state.idx_player_started = idx_player_active
    state.idx_player_active = idx_player_active
    state.bool_card_exchanged = True
    player = state.list_player[idx_player_active]

    # Assign player's cards and set all marbles in the kennel
    player.list_card = [Card(suit='♦', rank='A'), Card(suit='♣', rank='10')]
    kennels = [64, 65, 66, 67]  # Player 1's kennel positions
    for i, marble in enumerate(player.list_marble):
        marble.pos = kennels[i]

    # Update the game state
    game.set_state(state)

    # Log the initial state
    print("Initial State:")
    print(f"Player {player.name} cards: {[f'{card.rank} of {card.suit}' for card in player.list_card]}")
    print(f"Player {player.name} marbles: {[marble.pos for marble in player.list_marble]}")

    # Get and print all possible actions
    actions = game.get_list_action()
    print("Available Actions:")
    for idx, action in enumerate(actions):
        print(f"{idx}: Play {action.card.rank} of {action.card.suit} from {action.pos_from} to {action.pos_to}")

    # Apply the action to move marble out of the kennel
    action = Action(card=Card(suit='♦', rank='A'), pos_from=64, pos_to=0)
    game.apply_action(action)

    # Verify the resulting state
    state = game.get_state()
    player = state.list_player[idx_player_active]
    marble_found = any(marble.pos == 0 for marble in player.list_marble)
    marble_safe = any(marble.pos == 0 and marble.is_save for marble in player.list_marble)

    # Log the final state
    print("Final State:")
    print(f"Player {player.name} marbles: {[marble.pos for marble in player.list_marble]}")
    print(f"Player {player.name} marbles' safe status: {[marble.is_save for marble in player.list_marble]}")

    # Assertions
    assert marble_found, "Error: Player 1 must end with a marble at pos=0."
    assert marble_safe, 'Error: Status of marble at pos=0 must be "is_save"=True.'

def test_get_list_action_no_valid_kennel_moves():
    """Test get_list_action when all marbles are in the kennel and no valid cards are available."""
    game = Dog()
    game.initialize_game()

    player_idx = 0
    game.state.idx_player_active = player_idx
    active_player = game.state.list_player[player_idx]

    kennels = game.KENNEL_POSITIONS
    for i, marble in enumerate(active_player.list_marble):
        marble.pos = kennels[player_idx][i]

    invalid_cards = [Card(suit='♠', rank='2'), Card(suit='♠', rank='3')]
    active_player.list_card = invalid_cards

    game.state.bool_card_exchanged = True
    actions = game.get_list_action()

    assert len(actions) == 0, "Expected no actions when marbles are in the kennel and no valid cards."


def test_collision_sends_opponent_marble_to_kennel():
    """Test that a marble colliding with another player's marble sends it to the kennel."""
    game = Dog()
    game.initialize_game()

    player_idx = 0
    opponent_idx = 1
    state = game.get_state()

    opponent = state.list_player[opponent_idx]
    opponent.list_marble[0].pos = 5
    active_player = state.list_player[player_idx]
    active_player.list_marble[0].pos = 3

    # Use valid card from the deck
    card_to_play = state.list_card_draw.pop()
    card_to_play.rank = '2'
    active_player.list_card = [card_to_play]

    game.set_state(state)
    action = Action(card=card_to_play, pos_from=3, pos_to=5)
    game.apply_action(action)

    opponent_positions = [marble.pos for marble in opponent.list_marble]
    assert any(pos in game.KENNEL_POSITIONS[opponent_idx] for pos in opponent_positions)


def test_joker_card_as_wildcard():
    """Test that the Joker card can be used as a wildcard for any valid move."""
    game = Dog()
    game.initialize_game()

    player_idx = 0
    state = game.get_state()
    active_player = state.list_player[player_idx]

    joker_card = next(card for card in state.list_card_draw if card.rank == 'JKR')
    state.list_card_draw.remove(joker_card)
    active_player.list_card = [joker_card]
    active_player.list_marble[0].pos = 4

    game.set_state(state)
    action = Action(card=joker_card, pos_from=4, pos_to=10)
    game.apply_action(action)

    new_pos = active_player.list_marble[0].pos
    assert new_pos == 10, "Joker card did not move marble to position 10."


def test_no_valid_actions_with_empty_hand():
    """Test that no actions are available when a player has no cards."""
    game = Dog()
    game.initialize_game()

    player_idx = 0
    state = game.get_state()
    active_player = state.list_player[player_idx]
    active_player.list_card = []

    game.set_state(state)
    actions = game.get_list_action()

    assert len(actions) == 0, "Expected no valid actions when player has no cards."


def test_reshuffle_when_deck_runs_out():
    """Test reshuffling discard pile into draw pile when no cards are left."""
    game = Dog()
    game.initialize_game()

    state = game.get_state()
    state.list_card_draw = []
    state.list_card_discard = GameState.LIST_CARD.copy()

    game.set_state(state)
    game.deal_cards()

    updated_state = game.get_state()
    assert len(updated_state.list_card_draw) > 0, "Reshuffle failed: Draw pile is still empty."
    assert len(updated_state.list_card_discard) == 0, "Reshuffle failed: Discard pile was not cleared."


def test_marble_moves_into_safe_space():
    """Test that a marble correctly enters the safe space when moving the exact steps."""
    game = Dog()
    game.initialize_game()

    player_idx = 0
    state = game.get_state()
    active_player = state.list_player[player_idx]

    entry_point = Dog.SAFE_SPACES[player_idx][0] - 1
    active_player.list_marble[0].pos = entry_point

    card_to_play = state.list_card_draw.pop()
    card_to_play.rank = '1'
    active_player.list_card = [card_to_play]

    game.set_state(state)
    action = Action(card=card_to_play, pos_from=entry_point, pos_to=Dog.SAFE_SPACES[player_idx][0])
    game.apply_action(action)

    marble_pos = active_player.list_marble[0].pos
    assert marble_pos == Dog.SAFE_SPACES[player_idx][0], "Marble did not enter the safe space correctly."


def test_move_out_of_kennel_two_cards():
    """Test: Move out of kennel without marble on the starting position."""
    game = Dog()
    game.reset()

    state = game.get_state()
    idx_player_active = 0
    state.cnt_round = 0
    state.idx_player_active = idx_player_active
    state.bool_card_exchanged = True

    player = state.list_player[idx_player_active]
    player.list_card = [Card(suit='♦', rank='A')]
    kennels = game.KENNEL_POSITIONS[idx_player_active]
    for i, marble in enumerate(player.list_marble):
        marble.pos = kennels[i]

    game.set_state(state)
    action = Action(card=Card(suit='♦', rank='A'), pos_from=kennels[0], pos_to=0)
    game.apply_action(action)

    state = game.get_state()
    marble_pos = state.list_player[idx_player_active].list_marble[0].pos
    assert marble_pos == 0, "Marble did not move out of the kennel correctly."