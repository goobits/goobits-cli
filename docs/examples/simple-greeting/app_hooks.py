"""
Hook functions for Simple Greeting CLI - Python version
"""

def on_hello(name, style="casual", repeat=1, verbose=False, **kwargs):
    """Say hello to someone with specified style"""
    
    if verbose:
        print(f"Greeting {name} with {style} style, repeating {repeat} times")
    
    # Define greeting styles
    greetings = {
        "casual": f"Hey {name}! 👋",
        "formal": f"Good day, {name}.",
        "enthusiastic": f"🎉 HELLO {name.upper()}! 🎉"
    }
    
    greeting = greetings.get(style, greetings["casual"])
    
    # Repeat greeting
    for i in range(repeat):
        if repeat > 1:
            print(f"[{i+1}] {greeting}")
        else:
            print(greeting)
    
    return 0


def on_goodbye(name, polite=False, verbose=False, **kwargs):
    """Say goodbye to someone"""
    
    if verbose:
        print(f"Saying goodbye to {name}, polite={polite}")
    
    if polite:
        print(f"It was a pleasure meeting you, {name}. Have a wonderful day!")
    else:
        print(f"See you later, {name}! 👋")
    
    return 0


def on_introduce(name, role="friend", verbose=False, **kwargs):
    """Introduce yourself"""
    
    if verbose:
        print(f"Introducing as {name} ({role})")
    
    print(f"Hello! My name is {name} and I'm your {role}. Nice to meet you!")
    return 0