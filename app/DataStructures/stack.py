from typing import Dict, Optional, List

class Stack:
    def __init__(self, s):
        self.size = s
        self.data = [0] * self.size
        self.top = -1
    
    def is_full(self):
        return self.top == self.size - 1
    
    def is_empty(self):
        return self.top == -1
    
    def push(self, x):
        if self.is_full():
            print("Stack is full")
            return
        self.top += 1
        self.data[self.top] = x
    
    def pop(self):
        if self.is_empty():
            print("Stack is empty")
            return None
        element = self.data[self.top]
        self.top -= 1
        return element
    
    def peek(self):
        if self.is_empty():
            print("Stack is empty")
            return None
        return self.data[self.top]
    
    def display_list(self):
        if self.is_empty():
            print("Stack is empty")
            return
        for i in range(self.top, -1, -1):
            print(self.data[i], end=" ")
        print()


class RideHistoryStack:
    """Dynamic stack for storing user ride history"""
    
    def __init__(self):
        self.rides: List[Dict] = []
    
    def push(self, ride: Dict) -> None:
        """Push a completed ride onto the stack"""
        self.rides.append(ride)
    
    def pop(self) -> Optional[Dict]:
        """Remove and return the most recent ride"""
        if self.is_empty():
            return None
        return self.rides.pop()
    
    def peek(self) -> Optional[Dict]:
        """View the most recent ride without removing"""
        if self.is_empty():
            return None
        return self.rides[-1]
    
    def is_empty(self) -> bool:
        """Check if stack is empty"""
        return len(self.rides) == 0
    
    def size(self) -> int:
        """Get number of rides in history"""
        return len(self.rides)
    
    def get_all(self) -> List[Dict]:
        """Get all rides (most recent first)"""
        return list(reversed(self.rides))
    
    def get_recent(self, count: int = 5) -> List[Dict]:
        """Get the most recent 'count' rides"""
        return list(reversed(self.rides[-count:]))
    
    def clear(self) -> None:
        """Clear all history"""
        self.rides = []


class UserRideHistoryManager:
    """Manages ride history stacks for multiple users"""
    
    def __init__(self):
        self.user_histories: Dict[str, RideHistoryStack] = {}
    
    def get_user_stack(self, user_email: str) -> RideHistoryStack:
        """Get or create a history stack for a user"""
        if user_email not in self.user_histories:
            self.user_histories[user_email] = RideHistoryStack()
        return self.user_histories[user_email]
    
    def add_completed_ride(self, user_email: str, ride: Dict) -> None:
        """Add a completed ride to user's history"""
        stack = self.get_user_stack(user_email)
        stack.push(ride)
    
    def get_user_history(self, user_email: str, count: int = None) -> List[Dict]:
        """Get user's ride history"""
        stack = self.get_user_stack(user_email)
        if count:
            return stack.get_recent(count)
        return stack.get_all()
    
    def get_last_ride(self, user_email: str) -> Optional[Dict]:
        """Get user's most recent ride"""
        stack = self.get_user_stack(user_email)
        return stack.peek()