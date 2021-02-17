import sys, math

print(
    """
    A
    |\\
    | \\
    |  \\
    |   \\
    |    \\
    |     \\
    |      \\
    |       \\M (Midpoint)
    |      / \\
    |     /   \\
    |    /     \\
    |   /       \\
    |  /         \\
    | /           \\
    |/ß)           \\
    B---------------C

    What is the angle of MBC?
    First parameter is AB, second is BC.
    """
    )

def midpoint(ab: int, bc: int) -> int:
    print(f'{int(round(math.degrees(math.atan2(ab,bc))))}°')

midpoint(int(input()),int(input()))
