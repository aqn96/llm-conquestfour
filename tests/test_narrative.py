from ai.context_prompter import ContextAwarePrompter
from game.connect_four import ConnectFourGame


def test_narrative_generation():
    game = ConnectFourGame()
    # This will be a move for Player.ONE (the default first player)
    game.make_move(3)
    cap = ContextAwarePrompter()
    print('Narrative generation check:')
    try:
        print('Trying fantasy theme:')
        # The create_prompt method expects a game state object
        prompt = cap.create_prompt(game, "fantasy")
        print('Fantasy prompt generation: Success')
        print('Sample prompt:', 
              prompt[:100] + '...' if len(prompt) > 100 else prompt)
        
        print('\nTrying sci-fi theme:')
        prompt = cap.create_prompt(game, "scifi")
        print('Sci-fi prompt generation: Success')
        print('Sample prompt:', 
              prompt[:100] + '...' if len(prompt) > 100 else prompt)
        
        return True
    except Exception as e:
        print(f'Error: {e}')
        return False


if __name__ == "__main__":
    success = test_narrative_generation()
    print(f'\nTest {"passed" if success else "failed"}') 