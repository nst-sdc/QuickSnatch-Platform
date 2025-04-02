import random
from typing import Dict, List, Tuple

# Database of riddles with their answers and hints
RIDDLES: List[Dict[str, str]] = [
    {
        "riddle": "I speak without a mouth and hear without ears. I have no body, but I come alive with wind. What am I?",
        "answer": "echo",
        "hint": "Listen carefully to nature's reply"
    },
    {
        "riddle": "The more you take, the more you leave behind. What am I?",
        "answer": "footsteps",
        "hint": "Think about walking"
    },
    {
        "riddle": "What has keys, but no locks; space, but no room; and you can enter, but not go in?",
        "answer": "keyboard",
        "hint": "You use it to type"
    },
    {
        "riddle": "I am not alive, but I grow; I don't have lungs, but I need air; I don't have a mouth, but water kills me. What am I?",
        "answer": "fire",
        "hint": "I bring light and warmth"
    },
    {
        "riddle": "What is always in front of you but can't be seen?",
        "answer": "future",
        "hint": "Time moves towards it"
    },
    {
        "riddle": "I have cities, but no houses. I have mountains, but no trees. I have water, but no fish. I have roads, but no cars. What am I?",
        "answer": "map",
        "hint": "I help you navigate"
    },
    {
        "riddle": "What can travel around the world while staying in a corner?",
        "answer": "stamp",
        "hint": "I help letters reach their destination"
    },
    {
        "riddle": "The person who makes it, sells it. The person who buys it never uses it. The person who uses it doesn't know they are. What is it?",
        "answer": "coffin",
        "hint": "Think about final rest"
    },
    {
        "riddle": "What has a head and a tail but no body?",
        "answer": "coin",
        "hint": "It's in your pocket"
    },
    {
        "riddle": "I am taken from a mine and shut up in a wooden case, from which I am never released, and yet I am used by everyone. What am I?",
        "answer": "pencil",
        "hint": "I help you write"
    },
    {
        "riddle": "What starts with 'e', ends with 'e', and contains one letter?",
        "answer": "envelope",
        "hint": "Mail needs me"
    },
    {
        "riddle": "What has legs, but doesn't walk?",
        "answer": "table",
        "hint": "You eat on me"
    },
    {
        "riddle": "What gets wetter and wetter the more it dries?",
        "answer": "towel",
        "hint": "Use me after a shower"
    },
    {
        "riddle": "I am always hungry; I must always be fed. The finger I touch, will soon turn red. What am I?",
        "answer": "fire",
        "hint": "I consume everything in my path"
    },
    {
        "riddle": "What can fill a room but takes up no space?",
        "answer": "light",
        "hint": "Switch me on to see"
    }
]

class RiddleManager:
    def __init__(self):
        self.user_riddles: Dict[str, Dict] = {}  # Maps user_id to their current riddle
        
    def assign_riddle(self, user_id: str, level: int) -> Dict[str, str]:
        """Assign a random riddle to a user for a specific level."""
        # Get riddles not yet used by this user
        used_riddles = self.user_riddles.get(user_id, {}).get('used_riddles', set())
        available_riddles = [r for i, r in enumerate(RIDDLES) if i not in used_riddles]
        
        # If all riddles used, reset the used riddles
        if not available_riddles:
            used_riddles = set()
            available_riddles = RIDDLES.copy()  # Get a fresh copy of all riddles
        
        # Select a random riddle
        riddle = random.choice(available_riddles)
        riddle_index = RIDDLES.index(riddle)
        
        # Store the riddle for this user
        self.user_riddles[user_id] = {
            'current_riddle': riddle,
            'level': level,
            'used_riddles': used_riddles | {riddle_index}
        }
        
        return {
            'riddle': riddle['riddle'],
            'hint': riddle['hint']
        }
    
    def check_answer(self, user_id: str, answer: str) -> bool:
        """Check if the provided answer matches the user's current riddle."""
        if user_id not in self.user_riddles:
            return False
            
        current_riddle = self.user_riddles[user_id]['current_riddle']
        return answer.lower().strip() == current_riddle['answer'].lower()
    
    def get_hint(self, user_id: str) -> str:
        """Get the hint for the user's current riddle."""
        if user_id not in self.user_riddles:
            return "No riddle assigned"
            
        return self.user_riddles[user_id]['current_riddle']['hint']
    
    def clear_riddle(self, user_id: str):
        """Clear the current riddle for a user (called after level completion)."""
        if user_id in self.user_riddles:
            used_riddles = self.user_riddles[user_id].get('used_riddles', set())
            self.user_riddles[user_id] = {'used_riddles': used_riddles}

# Create a global instance of the riddle manager
riddle_manager = RiddleManager()
