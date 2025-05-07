from random import choice

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
    ___
   /. .\___     
  (   ---<`     
   \  /           
 ___\/_____      
<_________/
"""

happy_snek = r"""
            /^\/^\
          _|__|  O|
  \/     /~     \_/ \
  \____|__________/  \
          \_______      \
                  `\     \                 \
                    |     |                  \
                  /      /                    \
                  /     /                       \
                /      /                         \ \
              /     /                            \  \
            /     /             _----_            \   \
            /     /           _-~      ~-_         |   |
          (      (        _-~    _--_    ~-_     _/   |
            \      ~-____-~    _-~    ~-_    ~-_-~    /
              ~-_           _-~          ~-_       _-~
                ~--______-~                ~-___-~
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

flavor_of_snek = choice(
    [
        sss_snek,
        happy_snek_2,
        snek_1,
        happy_snek,
        face_snek,
        mythical_snek,
    ]
)
SPLASHSCREEN_TEXT = rf"""
{flavor_of_snek}

Nuitka Github
[#fbdd58 underline]https://github.com/Nuitka/Nuitka[/]


Tuitka Github
[#fbdd58 underline]https://github.com/KRRT7/tuitka[/]

"""
