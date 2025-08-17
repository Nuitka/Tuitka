import sys

PYTHON_VERSION = f"{sys.version_info.major}.{sys.version_info.minor}"

sss_snek = r"""
    ____                  
       / . .\                
       \  ---<     Sss...    
    \  /              
     ___/ /                
    <_____/               
"""
happy_snek_2 = r"""
        ____
       / o o\ 
      \_ v _>   Hisss...
        \   /
  ______/  /
 <_______/
"""


snek_1 = r"""
    _   
     /. .\___
    (   ---<
     \  /
   ___\/_____
  <_________/
"""


face_snek = r"""
       ____     ____     ____     ____     ____     ____    
     / . . \  / . . \  / . . \  / . . \  / . . \  / . . \    
     \  ---<  \  ---<  \  ---<  \  ---<  \  ---<  \  ---<    
      \  /      \  /      \  /      \  /      \  /      \   
______/ /______/ /______/ /______/ /______/ /______/ /_____
<_______/<_______/<_______/<_______/<_______/<_______/<_____/
"""

mythical_snek = r"""
    /^\/^\
    _|__|  O|
  \/~     \_/ \
    \_______  \ \
                `\   \_\      
                  |     |      
                  /      /       
                /     /         
              /      /          
              /     /           
            (      (        
            \      ~-_
              ~-_     ~-_
                  ~--___-~

"""

SNAKE_ARTS = [sss_snek, happy_snek_2, snek_1, face_snek, mythical_snek]
SNAKE_FACTS = [
    "Did you know? Python was created as a Christmas hobby project in December 1989!",
    "Fun fact: Python's name comes from Monty Python's Flying Circus—not the snake!",
    "Easter egg: 'import antigravity'",
    "Run `python -m __hello__` for a surprise.",
    "Try `from __future__ import braces`",
    "Enable FLUFL: `from __future__ import barry_as_FLUFL`",
    "Hashing infinity isn't boring: `hash(float('inf'))` == 314159 (π digits).",
    "Declare `__peg_parser__ = ...` in REPL and Python says: 'SyntaxError: You found it!'",
    "Python supports fancy loop syntax: 'else' runs if no `break` in loop.",
    "Odd bug (pre-Python 3.5): `time(0,0,0)` evaluated to False. Not anymore!",
    "Python's `__debug__` is True by default, but can be set to False with `-O` flag.",
    "try `import this` for the Zen of Python, a collection of guiding principles.",
    "Nuitka is short for Annuitka, which is the nickname Nuitka's author uses for his wife Anna.",
]

SPLASHSCREEN_LINKS = (
    "\n\nNuitka Github: \n\n[#fbdd58 underline]https://github.com/Nuitka/Nuitka[/]\n\n"
    "Tuitka Github: \n\n[#fbdd58 underline]https://github.com/KRRT7/tuitka[/]"
)
