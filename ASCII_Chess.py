"""
Chess Game (For A Terminal)
By: Monozide
-------------------------------------------------------------------
This programs lets you play a chess on a text interface terminal.
More practice with OOP and hopefully a first step in making a 
full-fledged chess game with AI.
"""
class Board():
    "Board containing an 8x8 two dimensional list"

    def __init__(self):
        self.positions = [
                            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '], 
                            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                         ]

    def coords_to_piece(self, coordinates):
        """
        Input: tuple containing two ints\n
        Output: object at the specified value on this board (either a str or Piece)
        """
        row = coordinates[0]
        column = coordinates[1]
        piece = self.positions[row][column]
        return piece
    
    def all_pieces_on_team(self, team):
        """
        Input: str == either 'black' or 'white'\n
        Output: list of Piece objects
        """
        pieces = []
        for x in range(len(self.positions)):
            for y in range(len(self.positions[0])):
                space = self.coords_to_piece((x, y))
                if isinstance(space, Piece):
                    selected_piece = space
                    if selected_piece.team == team:
                        pieces.append(selected_piece)
        return pieces

    def update(self, piece):
        """
        Input: Piece object\n
        Updates the board with this piece at the piece.position
        """
        move = piece.position
        index1 = move[0]
        index2 = move[1]
        self.positions[index1][index2] = piece
    
    def display(self):
        """
        Prints the board and all the pieces/spaces in it for the user to see
        """
        print('')
        print("   ---------------------------------")
        counter = 0
        for row in self.positions:
            counter += 1
            line = f'{counter}: |'
            for space in row:
                if isinstance(space, str):
                    line += f' {space} |'
                else:
                    line += f' {space.symbol} |'
            print(line)
            print("   ---------------------------------")
        print("   | A | B | C | D | E | F | G | H |\n")
    
    def update_all_spaces_threatened(self):
        """
        Loops through all the pieces on the board and makes them update
        their spaces threatened
        """
        spaces_threatened = []
        for row in self.positions:
            for space in row:
                if isinstance(space, Piece):
                    selected_piece = space
                    selected_piece.update_spaces_threatened()
        
        return spaces_threatened

    def spaces_threatened_by_team(self, team):
        """
        Input: str == either 'black' or 'white'\n
        Output: list of coordinates
        """
        spaces_threatened = []
        pieces = self.all_pieces_on_team(team)
        for piece in pieces:
            if piece.team == team:
                for threat in piece.spaces_threatened:
                    spaces_threatened.append(threat)
        
        return spaces_threatened

THE_BOARD = Board()


class Piece():
    "Parent class for all chess piece types"

    def __init__(self, team, position):
        # Current coordinates
        self.position = position

        # Team that the piece belongs to (white or black)
        self.team = team

        # Keeps track of if the piece has moved or not (for pawn or for castleing)
        self.has_moved = False

        # List of the spaces that the piece is currently threatening (for checks/checkmates/stalemates)
        self.spaces_threatened = []

        # Keeps track if this piece is currently threatening the enemy king.
        self.threatening_king = False

        # Keeps track of positions that this piece can move to while it's king is in check.
        self.possible_moves_during_check = []


class Pawn(Piece):
    "Class that represents the pawn"

    def __init__(self, team, position):
        Piece.__init__(self, team, position)
    
        # Give the object it's own symbol and direction (movement up or down) based on it's team
        if team == 'white':
            self.symbol = '♙'
            self.direction = -1
        else:
            self.symbol = '♟'
            self.direction = 1

    def check_corners(self):
        """
        Output: list containing valid coordinates for pawn corner movement (list of tuples)

        If the corner spaces in the forward direction (depends on the team the pawn is on)
        are occupied by enemy pieces, the pawn can move to that space and capture the enemy.
        Use this function in conjunction with all_possible_moves().
        """
        current_row = self.position[0]
        current_column = self.position[1]

        occupied_corners = []

        # find the two corner spaces based on the current position
        corner1 = (current_row + 1 * self.direction, current_column - 1)
        corner2 = (current_row + 1 * self.direction, current_column + 1)

        # check the two corner spaces and see if there are enemy pieces on them
        # if there are enemy pieces, append the position to occupied_corners
        if is_within_bounds(corner1):
            if not isinstance(THE_BOARD.positions[corner1[0]][corner1[1]], str):
                if THE_BOARD.positions[corner1[0]][corner1[1]].team != self.team:
                    occupied_corners.append(corner1)
        
        if is_within_bounds(corner2):
            if not isinstance(THE_BOARD.positions[corner2[0]][corner2[1]], str):
                if THE_BOARD.positions[corner2[0]][corner2[1]].team != self.team:
                    occupied_corners.append(corner2)
        
        return occupied_corners

    def all_possible_moves(self):
        """
        Output: list containing all possible pawn movement options (list of tuples)

        Pawn can move forward (down or up based on which team it is on) and capture enemy pieces
        if they are in either adjacent diagonal space in front of the pawn. Cannot move forward
        if blocked by any piece and cannot capture pieces on the same team. 
        """
        possible_moves = []

        # Track current position in the form of row, column
        row = self.position[0]
        column = self.position[1]

        # If the space directly in front of the pawn is blocked, it cannot move forward at all
        # Otherwise, add moving forward 1 space and moving forward 2 spaces to list of possible moves
        if not is_space_occupied((row + 1 * self.direction, column)):
            possible_moves.append((row + 1 * self.direction, column))
            if not self.has_moved:
                if not is_space_occupied((row + 2 * self.direction, column)):
                    possible_moves.append((row + 2 * self.direction, column))

        # Add corner movement options if there are any (adjacent diagonal spaces containing an enemy)
        occupied_corners = self.check_corners()
        for move in occupied_corners:
            possible_moves.append(move)

        # Get rid of all movement options that take the piece off the board or leave the king in check
        possible_moves = [move for move in possible_moves if is_within_bounds(move)]
        possible_moves = remove_checks_from_possible_moves(self, possible_moves)
    
        return possible_moves
    
    def check_evolve(self):
        """
        Check if conditions are met to 'evolve'. If they are, perform the evolution
        """
        if self.team == 'white':
            if self.position[0] == 0:
                self.evolve()
        
        else:
            if self.position[0] == 7:
                self.evolve()
    
    def evolve(self):
        """
        Takes a user input and changes the pawn so that it becomes what the user chose
        """
        possible_evolutions = ["knight", "bishop", "rook", "queen"]
        evolution = input("Choose what your pawn will become: knight, bishop, rook, queen\n")
        if evolution == possible_evolutions[0]:
            evolution_piece = Knight(self.team, self.position)
            evolution_piece.update_spaces_threatened()
        elif evolution == possible_evolutions[1]:
            evolution_piece = Bishop(self.team, self.position)
            evolution_piece.update_spaces_threatened()
        elif evolution == possible_evolutions[2]:
            evolution_piece = Rook(self.team, self.position)
            evolution_piece.update_spaces_threatened()
        elif evolution == possible_evolutions[3]:
            evolution_piece = Queen(self.team, self.position)
            evolution_piece.update_spaces_threatened()

        # If evolution is not one of those choices, rerun the evolution input
        else:
            self.evolve()
        
        if evolution_piece:
            THE_BOARD.update(evolution_piece)
            THE_BOARD.update_all_spaces_threatened()
    
    def update_spaces_threatened(self):
        """
        Based on the piece's current position, update what spaces this piece threatens.
        In the instance of the pawn, the spaces threatened are always its forward facing corners
        """
        # The threatened spaces will always be it's corners
        current_row = self.position[0]
        current_column = self.position[1]
        corner1 = (current_row + 1 * self.direction, current_column - 1)
        corner2 = (current_row + 1 * self.direction, current_column + 1)
        current_spaces_threatened = [corner1, corner2]
        self.spaces_threatened = current_spaces_threatened
        update_threatening_king(self)


class Rook(Piece):
    "Class that represents the rook"

    def __init__(self, team, position):
        Piece.__init__(self, team, position)
    
        if team == 'white':
            self.symbol = '♖'
        else:
            self.symbol = '♜'
    
    def all_possible_moves(self, list_of_directional_threats=False, return_spaces_threatened=False):
        """
        Inputs: 2 Optional Booleans which affect the output\n
        Output:
                If all inputs == False; a list of all possible moves,
                if list_of_directional_threats; a list of a list of threats. list of threats seperated by direction
                if return_spaces_threatened; a list of all spaces threatened by this piece

        The rook can move to any space in a straight line, i.e. all spaces on it's current row or column
        if a space is blocked on the path (a piece is in the way), the rook cannot move past it.
        if the blocking piece is on the enemy team, the rook can move there, otherwise, it cannot
        """
        threatened_spaces = []
        # There are 4 directions the rook influences.
        # Checking outward from the current position in those directions:
        threatened_spaces_n = check_threats_in_one_straight_direction(self, "column", -1)
        threatened_spaces_s = check_threats_in_one_straight_direction(self, "column", 1)
        threatened_spaces_e = check_threats_in_one_straight_direction(self, "row", 1)
        threatened_spaces_w = check_threats_in_one_straight_direction(self, "row", -1)
        list_of_list_of_threats = [threatened_spaces_n, threatened_spaces_s, threatened_spaces_e, threatened_spaces_w]
        if list_of_directional_threats:
            return list_of_list_of_threats

        for lst in list_of_list_of_threats:
            threatened_spaces.extend(lst)
        if return_spaces_threatened:
            return threatened_spaces
        
        # Possible moves are just threatened spaces where the space threatened is not occupied by a team member
        possible_moves = convert_threats_to_possible_moves(self, threatened_spaces)
        possible_moves = remove_checks_from_possible_moves(self, possible_moves)
        
        return possible_moves
    
    def update_spaces_threatened(self):
        """
        Based on the piece's current position, update what spaces this piece threatens.\n
        In the instance of the rook, the spaces threatened are always along the row+column it occupies,
        including the space that a piece that is blocking the rest of the path occupies, regardless of team
        """
        # Spaces threatened are all the spaces it can move to + guarding an ally at the end of a path
        self.spaces_threatened = self.all_possible_moves(return_spaces_threatened=True)
        update_threatening_king(self)
    
    def spaces_threatened_towards_king(self, list_of_directional_spaces_threatened):
        """
        ONLY CALL THIS FUNCTION IF YOU KNOW THE PIECE IS THREATENING THE KING\n
        Input: list of list of spaces. Each list is seperated by direction\n
        This function scans through every space provided. If the king is found,
        the directional list containing the space is returned
        """
        for lst in list_of_directional_spaces_threatened:
            for move in lst:
                if isinstance(THE_BOARD.coords_to_piece(move), King):
                    return(lst)
        
        raise Exception(f"{self.symbol} not threatening the enemy king")


class Knight(Piece):
    "Class that represents the knight"

    def __init__(self, team, position):
        Piece.__init__(self, team, position)
    
        if team == 'white':
            self.symbol = '♘'
        else:
            self.symbol = '♞'

    def all_possible_moves(self, return_spaces_threatened=False):
        """
        Inputs: 1 Optional Boolean which affects the output\n
        Output:
                If all inputs == False; a list of all possible moves,
                if return_spaces_threatened; a list of all spaces threatened by this piece

        The knight can move to any space that is (current row +-2, current column +-1) and (current row +-1, current column +-2),
        as long as there is not a piece on the space that is on the same team as the knight
        """
        row = self.position[0]
        column = self.position[1]

        threat1 = (row+2, column+1)
        threat2 = (row+2, column-1)
        threat3 = (row-2, column+1)
        threat4 = (row-2, column-1)
        threat5 = (row+1, column+2)
        threat6 = (row+1, column-2)
        threat7 = (row-1, column+2)
        threat8 = (row-1, column-2)

        threatened_spaces = [threat1, threat2, threat3, threat4, threat5, threat6, threat7, threat8]
        threatened_spaces = [move for move in threatened_spaces if is_within_bounds(move)]
        if return_spaces_threatened:
            return threatened_spaces
            
        possible_moves = convert_threats_to_possible_moves(self, threatened_spaces)
        possible_moves = remove_checks_from_possible_moves(self, possible_moves)
        return possible_moves
    
    def update_spaces_threatened(self):
        """
        Based on the piece's current position, update what spaces this piece threatens.\n
        In the instance of the knight, it is everywhere it can move to, regardless of the piece that is in the destination
        """
        self.spaces_threatened = self.all_possible_moves(return_spaces_threatened=True)
        update_threatening_king(self)


class Bishop(Piece):
    "Class that represents the bishop"

    def __init__(self, team, position):
        Piece.__init__(self, team, position)
    
        if team == 'white':
            self.symbol = '♗'
        else:
            self.symbol = '♝'

    def all_possible_moves(self, list_of_directional_threats=False, return_spaces_threatened=False):
        """
        Inputs: 2 Optional Booleans which affect the output\n
        Output:
                If all inputs == False; a list of all possible moves,
                if list_of_directional_threats; a list of a list of threats. list of threats seperated by direction
                if return_spaces_threatened; a list of all spaces threatened by this piece

        The bishop can move to any space in a diagonal line, i.e. all spaces (current row +- 1*n, current column +- 1*n)
        if a space is blocked on the path (a piece is in the way), the bishop cannot move past it.
        if the blocking piece is on the enemy team, the bishop can move there, otherwise, it cannot
        """
        threatened_spaces = []
        threatened_spaces_ne = check_threats_in_one_diagonal_direction(self, -1, 1)
        threatened_spaces_nw = check_threats_in_one_diagonal_direction(self, -1, -1)
        threatened_spaces_sw = check_threats_in_one_diagonal_direction(self, 1, -1)
        threatened_spaces_se = check_threats_in_one_diagonal_direction(self, 1, 1)
        list_of_list_of_threats = [threatened_spaces_ne, threatened_spaces_nw, threatened_spaces_sw, threatened_spaces_se]
        if list_of_directional_threats:
            return list_of_list_of_threats

        for lst in list_of_list_of_threats:
            threatened_spaces.extend(lst)
        if return_spaces_threatened:
            return threatened_spaces
        
        possible_moves = convert_threats_to_possible_moves(self, threatened_spaces)
        possible_moves = remove_checks_from_possible_moves(self, possible_moves)
        return possible_moves
    
    def update_spaces_threatened(self):
        """
        Based on the piece's current position, update what spaces this piece threatens.\n
        In the instance of the bishop, the spaces threatened are always along the diagonal paths from its position,
        including the space that a piece that is blocking the rest of the path occupies, regardless of team
        """
        # Spaces threatened are all the spaces it can move to + guarding an ally at the end of a path
        self.spaces_threatened = self.all_possible_moves(return_spaces_threatened=True)
        update_threatening_king(self)
    
    def spaces_threatened_towards_king(self, list_of_directional_spaces_threatened):
        """
        ONLY CALL THIS FUNCTION IF YOU KNOW THE PIECE IS THREATENING THE KING\n
        Input: list of list of spaces. Each list is seperated by direction\n
        This function scans through every space provided. If the king is found,
        the directional list containing the space is returned
        """
        for lst in list_of_directional_spaces_threatened:
            for move in lst:
                if isinstance(THE_BOARD.coords_to_piece(move), King):
                    return(lst)
        
        raise Exception(f"{self.symbol} not threatening the enemy king")


class Queen(Piece):
    "Class that represents the queen"

    def __init__(self, team, position):
        Piece.__init__(self, team, position)
    
        if team == 'white':
            self.symbol = '♕'
        else:
            self.symbol = '♛'

    def all_possible_moves(self, list_of_directional_threats=False, return_spaces_threatened=False):
        """
        Inputs: 2 Optional Booleans which affect the output\n
        Output:
                If all inputs == False; a list of all possible moves,
                if list_of_directional_threats; a list of a list of threats. list of threats seperated by direction
                if return_spaces_threatened; a list of all spaces threatened by this piece

        The queen can move to any space a bishop or rook can in the same position
        """
        threatened_spaces = []
        threatened_spaces_n = check_threats_in_one_straight_direction(self, "column", -1)
        threatened_spaces_s = check_threats_in_one_straight_direction(self, "column", 1)
        threatened_spaces_e = check_threats_in_one_straight_direction(self, "row", 1)
        threatened_spaces_w = check_threats_in_one_straight_direction(self, "row", -1)
        threatened_spaces_ne = check_threats_in_one_diagonal_direction(self, -1, 1)
        threatened_spaces_nw = check_threats_in_one_diagonal_direction(self, -1, -1)
        threatened_spaces_sw = check_threats_in_one_diagonal_direction(self, 1, -1)
        threatened_spaces_se = check_threats_in_one_diagonal_direction(self, 1, 1)
        list_of_list_of_threats = [
                                  threatened_spaces_n, threatened_spaces_s, threatened_spaces_e, threatened_spaces_w,
                                  threatened_spaces_ne, threatened_spaces_nw, threatened_spaces_sw, threatened_spaces_se
                                ]
        if list_of_directional_threats:
            return list_of_list_of_threats

        for lst in list_of_list_of_threats:
            threatened_spaces.extend(lst)
        if return_spaces_threatened:
            return threatened_spaces
        
        possible_moves = convert_threats_to_possible_moves(self, threatened_spaces)
        possible_moves = remove_checks_from_possible_moves(self, possible_moves)
        return possible_moves
    
    def update_spaces_threatened(self):
        """
        Based on the piece's current position, update what spaces this piece threatens.\n
        In the instance of the queen, the spaces threatened are always along the row+column it from its position,
        and the diagonals from its position, including the space that a piece that is blocking the rest of the path occupies,
        regardless of team
        """
        # Spaces threatened are all the spaces it can move to + guarding an ally at the end of a path
        self.spaces_threatened = self.all_possible_moves(return_spaces_threatened=True)
        update_threatening_king(self)
    
    def spaces_threatened_towards_king(self, list_of_directional_spaces_threatened):
        """
        ONLY CALL THIS FUNCTION IF YOU KNOW THE PIECE IS THREATENING THE KING\n
        Input: list of list of spaces. Each list is seperated by direction\n
        This function scans through every space provided. If the king is found,
        the directional list containing the space is returned
        """
        for lst in list_of_directional_spaces_threatened:
            for move in lst:
                if isinstance(THE_BOARD.coords_to_piece(move), King):
                    return(lst)
        
        raise Exception(f"{self.symbol} not threatening the enemy king")


class King(Piece):
    "Class that represents the king"

    def __init__(self, team, position):
        Piece.__init__(self, team, position)
    
        if team == 'white':
            self.symbol = '♔'
        else:
            self.symbol = '♚'
        
    def all_possible_moves(self, return_spaces_threatened=False):
        """
        Inputs: 1 Optional Boolean which affects the output\n
        Output:
                If all inputs == False; a list of all possible moves,
                if return_spaces_threatened; a list of all spaces threatened by this piece

        The king can move to any adjacent space, for a maximum total of 8 possible moves. If one of those
        spaces is occupied, the king can move there if the occupant is from the enemy team
        """
        threatened_spaces = []
        current_row = self.position[0]
        current_column = self.position[1]

        threatened_spaces.append((current_row+1, current_column))
        threatened_spaces.append((current_row-1, current_column))
        threatened_spaces.append((current_row, current_column+1))
        threatened_spaces.append((current_row, current_column-1))
        threatened_spaces.append((current_row-1, current_column-1))
        threatened_spaces.append((current_row-1, current_column+1))
        threatened_spaces.append((current_row+1, current_column-1))
        threatened_spaces.append((current_row+1, current_column+1))

        threatened_spaces = [move for move in threatened_spaces if is_within_bounds(move)]
        if return_spaces_threatened:
            return threatened_spaces

        possible_moves = convert_threats_to_possible_moves(self, threatened_spaces)
        possible_moves = remove_checks_from_possible_moves(self, possible_moves)
        return possible_moves
    
    def update_spaces_threatened(self):
        """
        Based on the piece's current position, update what spaces this piece threatens.\n
        In the instance of the king, the spaces threatened are all its adjacent spaces, regardless of what lies in those spaces
        """
        self.spaces_threatened = self.all_possible_moves(return_spaces_threatened=True)
        update_threatening_king(self)
        

def initialize_board():
    """
    Initializes the chess board with all 32 pieces
    """
    # Wipe current board
    for x in range(len(THE_BOARD.positions)):
        for y in range(len(THE_BOARD.positions)):
            THE_BOARD.positions[x][y] = ' '

    all_pieces = []

    # Pawns
    white_pawns = [Pawn('white', (6, i)) for i in range(len(THE_BOARD.positions[6]))]
    black_pawns = [Pawn('black', (1, i)) for i in range(len(THE_BOARD.positions[1]))]
    all_pieces.extend(white_pawns)
    all_pieces.extend(black_pawns)

    # Rooks
    rook1 = Rook('black', (0, 0))
    all_pieces.append(rook1)
    rook2 = Rook('black', (0, 7))
    all_pieces.append(rook2)
    rook3 = Rook('white', (7, 0))
    all_pieces.append(rook3)
    rook4 = Rook('white', (7, 7))
    all_pieces.append(rook4)

    # Knights
    knight1 = Knight('black', (0, 1))
    all_pieces.append(knight1)
    knight2 = Knight('black', (0, 6))
    all_pieces.append(knight2)
    knight3 = Knight('white', (7, 1))
    all_pieces.append(knight3)
    knight4 = Knight('white', (7, 6))
    all_pieces.append(knight4)

    # Bishops
    bishop1 = Bishop('black', (0, 2))
    all_pieces.append(bishop1)
    bishop2 = Bishop('black', (0, 5))
    all_pieces.append(bishop2)
    bishop3 = Bishop('white', (7, 2))
    all_pieces.append(bishop3)
    bishop4 = Bishop('white', (7, 5))
    all_pieces.append(bishop4)

    # King and Queen
    queen1 = Queen('black', (0, 4))
    all_pieces.append(queen1)
    queen2 = Queen('white', (7, 4))
    all_pieces.append(queen2)
    king1 = King('black', (0, 3))
    all_pieces.append(king1)
    king2 = King('white', (7, 3))
    all_pieces.append(king2)

    # Add every single piece to the board. Only then can they update their spaces threatened
    for piece in all_pieces:
        THE_BOARD.update(piece)
    THE_BOARD.update_all_spaces_threatened()


def is_space_occupied(coordinates):
    """
    Input: tuple with two ints. both ints must be within the board i.e. 0 <= int <= 7\n
    Output: Boolean\n
    Given coordinates, checks the board at that position. returns False if empty, True if occupied
    """
    if isinstance(THE_BOARD.positions[coordinates[0]][coordinates[1]], str):
        return False
    else:
        return True


def is_within_bounds(coordinates):
    """
    Input: tuple pair of two ints\n
    Output: Boolean
    """
    coordinate_x = coordinates[0]
    coordinate_y = coordinates[1]
    if coordinate_x <= 7 and coordinate_x >= 0:
        if coordinate_y <= 7 and coordinate_y >= 0:
            return True
    return False


def check_threats_in_one_straight_direction(selected_piece, row_or_column, direction):
    """
    Inputs: Piece (Rook or Queen), string ("row" or "column"), int (1 for up or right, -1 for down or left)\n
    Output: List of coordinates in specified direction\n
    This function is a helper function for Rook or Queen movement 
    """
    possible_moves = []
    current_row = selected_piece.position[0]
    current_column = selected_piece.position[1]

    if row_or_column == "column":
        counter = 0
        while True:
            counter += 1
            move = (current_row, current_column + counter * direction)
            if is_within_bounds(move):
                if is_space_occupied(move):
                    possible_moves.append(move)
                    break
                else:
                    possible_moves.append(move)

            else:
                break
                
    elif row_or_column == "row":
        counter = 0
        while True:
            counter += 1
            move = (current_row + counter * direction, current_column)
            if is_within_bounds(move):
                if is_space_occupied(move):
                    possible_moves.append(move)
                    break
                else:
                    possible_moves.append(move)

            else:
                break
    
    return possible_moves


def check_threats_in_one_diagonal_direction(selected_piece, up_down_direction, left_right_direction):
    """
    Inputs: Piece (Bishop or Queen), int (-1 or 1. up or down), int (-1 or 1. left or right)\n
    Output: List of coordinates in specified direction\n
    This function is a helper function for Bishop or Queen movement 
    """
    possible_moves = []
    current_row = selected_piece.position[0]
    current_column = selected_piece.position[1]

    counter = 0
    while True:
        counter += 1
        move = (current_row + counter * left_right_direction, current_column + counter * up_down_direction)

        if is_within_bounds(move):
                if is_space_occupied(move):
                    possible_moves.append(move)
                    break
                else:
                    possible_moves.append(move)
        
        else:
            break
    
    return possible_moves


def convert_threats_to_possible_moves(piece, list_of_threats):
    """
    Inputs: Piece object and a list containing the spaces the Piece threatens\n
    Output: list of possible moves (list of coordinates)\n
    Helper function for each piece's all_possible_moves() function. Takes a list of threats and if an ally
    is on a threatened space, remove the space from possible moves
    """

    possible_moves = []

    for space in list_of_threats:
        selected_piece = THE_BOARD.coords_to_piece(space)
        if isinstance(selected_piece, Piece):
            if selected_piece.team == piece.team:
                pass
            else:
                possible_moves.append(space)
        else:
            possible_moves.append(space)

    return possible_moves


def remove_checks_from_possible_moves(self, possible_moves):
    """
    Inputs: List of possible moves\n
    Output: Updated list of possible moves
    Helper function each piece's all_possible_moves() function
    """
    # Get rid of all movement options that leaves the king in check
    new_possible_moves = []
    old_position = self.position

    for move in possible_moves:
        # Move the piece to the potential destination and see if the king is in check
        piece_in_destination = THE_BOARD.coords_to_piece(move)
        self.position = move
        THE_BOARD.positions[old_position[0]][old_position[1]] = ' '
        THE_BOARD.update(self)
        THE_BOARD.update_all_spaces_threatened()
        if not is_my_king_in_check(self.team):
            new_possible_moves.append(move)
        # Reset the board state
        self.position = old_position
        THE_BOARD.positions[move[0]][move[1]] = piece_in_destination
        THE_BOARD.update(self)
        THE_BOARD.update_all_spaces_threatened()

    return new_possible_moves


def letter_to_num(letter):
    """
    Input: string - lower case letter in the english alphabet\n
    Output: int - a number corresponding to the letter (a = 0, b = 1, c = 2, ...)\n
    Helper function for function convert_input_to_coords()
    """
    counter = 0
    letter = letter.lower()
    for l in 'abcdefghijklmnopqrstuvwxyz':
        if l == letter:
            break
        counter += 1
    return counter


def convert_input_to_coords(player_input):
    """
    Input: string - formatted as 'LetterNumber to LetterNumber' (i.e. a1 to a2)\n
    Output: if incorrect player input; False. Otherwise it will be a tuple pair of the two sets of coordinates (tuple pair within a tuple pair)
    """
    # Try to perform the operation; if thrown an exception, the input was incorrect
    try:
        # Isolate the 'a1' and 'a2' from 'a1 to a2'
        split_text = player_input.split(' ')
        coord1= split_text[0]
        coord2 = split_text[2]

        # Convert the letter/number pairs into coordinates
        coord1_y = letter_to_num(coord1[0])
        coord1_x = int(coord1[1]) - 1
        coord2_y = letter_to_num(coord2[0])
        coord2_x = int(coord2[1]) - 1

        # Combine the coordinate pairs
        selected_position = (coord1_x, coord1_y)
        destination_position = (coord2_x, coord2_y)
        
        # Check if the two coordinate pairs are within bounds
        if not is_within_bounds(selected_position) or not is_within_bounds(destination_position):
            print("inputted coords are not within bounds")
            return False
        else:
            return selected_position, destination_position 
    
    except:
        print("error converting input into coordinates")
        return False


def check_then_move(selected_position, destination_position, player):
    """
    Inputs: coordinates, coordinates, string == 'white' or 'black'\n
    Output: Boolean\n
    This is the main function that handles all player movement
    """
    selected_piece = THE_BOARD.coords_to_piece(selected_position)
    if not isinstance(selected_piece, Piece):
        print("space selected is empty")
        return False
    if selected_piece.team != player:
        print("selected piece is on the opposite team")
        return False
    else:
        possible_moves = selected_piece.all_possible_moves()
        if destination_position in possible_moves:
            old_position = selected_piece.position
            selected_piece.position = destination_position
            THE_BOARD.positions[old_position[0]][old_position[1]] = ' '
            THE_BOARD.update(selected_piece)
            THE_BOARD.update_all_spaces_threatened()
            selected_piece.has_moved = True
            return True
        else:
            print("invalid destination")
            return False


def pawn_evolution_check():
    """
    Checks to see if a pawn made it to the other side
    """
    for x in range(len(THE_BOARD.positions)):
        for y in range(len(THE_BOARD.positions[x])):
            selected_piece = THE_BOARD.positions[x][y]

            # Check if pawn made it to opposite side
            if isinstance(selected_piece, Pawn):
                selected_piece.check_evolve()


def is_my_king_in_check(player):
    """
    Input: str == "white" or "black"\n
    Output: King object or False\n
    """
    for x in range(len(THE_BOARD.positions)):
        for y in range(len(THE_BOARD.positions[x])):
            selected_piece = THE_BOARD.positions[x][y]

            # Check if king is in check and if it is checkmate
            if isinstance(selected_piece, King):
                if selected_piece.team == "white":
                    opposite_team = "black"
                else:
                    opposite_team = "white"

                # Make sure the king belongs to the inputted player
                if selected_piece.team == player:
                    # All threatened spaces do not include the spaces that are threatened by pieces on the same team
                    spaces_threatened = THE_BOARD.spaces_threatened_by_team(opposite_team)
        
                    if (x, y) in spaces_threatened:
                        king_in_check = selected_piece
                        return king_in_check
    
    return False


def check_stalemate(player):
    """
    Input: str == "white" or "black"\n
    Output: Boolean\n
    Check's all the possible moves a player has; if there are none; return True
    """
    pieces = THE_BOARD.all_pieces_on_team(player)
    for piece in pieces:
        if len(piece.all_possible_moves()) > 0:
            return False
    return True


def update_threatening_king(piece):
    """
    Input: Piece object\n
    Helper function to be used by every piece when determining the spaces they threaten
    """
    if piece.team == 'white':
        opposite_team = 'black'
    else:
        opposite_team = 'white'

    for space in piece.spaces_threatened:
        if is_within_bounds(space):
            selected_piece = THE_BOARD.coords_to_piece(space)
            if isinstance(selected_piece, King):
                # This piece of code isn't needed because when determining possible moves/threats,
                # Spaces containing pieces on the same team are not added to the list
                if selected_piece.team == opposite_team:
                    piece.threatening_king = True
                    return None

            piece.threatening_king = False


def count_possible_moves_when_in_check(king_in_check):
    """
    Input: King object\n
    Output: Number of possible moves (int)\n
    This function counts the number of moves possible when a king is in check.\n
    FUTURE USE: It also keeps track of those moves by saving a list of possible destinations 
    for each piece that can make a move in piece.possible_moves_during_check
    """
    num_of_possible_moves = 0

    if king_in_check.team == "white":
        opposite_team = "black"
    else:
        opposite_team = "white"

    # King moves out of check
    king_in_check.possible_moves_during_check = king_in_check.all_possible_moves()

    # Remove or block the piece placing you in check (If piece > 1, king has to move)
    pieces_threatening_king = [i for i in THE_BOARD.all_pieces_on_team(opposite_team) if i.threatening_king]
    for threat in pieces_threatening_king:
        print(f'{threat.symbol}: threatening the king\n')

    if len(pieces_threatening_king) == 1:
        # Identify the piece that is threatening the king and all the space it is influencing
        threat = pieces_threatening_king[0]
        threat_space = threat.position

        # Update the possible moves of the king's allies in this instance of check
        possible_saviors = THE_BOARD.all_pieces_on_team(king_in_check.team)
        possible_saviors.remove(king_in_check)

        # The king might be the final piece remaining
        if possible_saviors:
            # Reset the possible moves that could have existed during the last check
            for piece in possible_saviors:
                piece.possible_moves_during_check = []

            # If the threat is a knight or pawn, they do not have a 'path' they follow; they cannot be blocked
            if isinstance(threat, Pawn) or isinstance(threat, Knight):
                for piece in possible_saviors:
                    if threat_space in piece.all_possible_moves():
                        piece.possible_moves_during_check.append(threat_space)
                        num_of_possible_moves += 1
                    
                    """
                    # Debugging
                    if piece.possible_moves_during_check:
                        print(f"Potential Move: {piece.symbol}  on {piece.position} can move to {piece.possible_moves_during_check}")
                    """
            
            # If the threat is a bishop or rook or queen, they have a blockable 'path' that can be occupied
            elif isinstance(threat, Queen) or isinstance(threat, Bishop) or isinstance(threat, Rook):
                path = threat.spaces_threatened_towards_king(threat.all_possible_moves(list_of_directional_threats=True))
                path.append(threat_space)
                for piece in possible_saviors:
                    for space in path:
                        if space in piece.all_possible_moves():
                            piece.possible_moves_during_check.append(space)
                            num_of_possible_moves += 1

                    """
                    # Debugging
                    if piece.possible_moves_during_check:
                        print(f"Potential Move: {piece.symbol}  on {piece.position} can move to {piece.possible_moves_during_check}")
                    """
        
    # Return the number of possible moves
    num_of_possible_moves += len(king_in_check.possible_moves_during_check)

    """
    # Debugging
    print("num moves possible:", num_of_possible_moves)
    print("num moves king can do:", len(king_in_check.possible_moves_during_check))
    print(king_in_check.possible_moves_during_check)
    """

    return num_of_possible_moves
 

def main():
    "Runs the game loop"
    """
    # Debugging
    test_queen1 = Queen('white', (7, 0))
    test_rook1 = Rook('black', (0, 0))
    test_rook2 = Rook('white', (7, 7))
    test_king1 = King('black', (0, 4))
    test_king2 = King('white', (7, 4))
    test_pieces = [test_queen1, test_rook1, test_rook2, test_king1, test_king2]
    for test in test_pieces:
        THE_BOARD.update(test)
    for test in test_pieces:
        test.update_spaces_threatened()
    """
    
    initialize_board()

    # Variable that keeps the game loop going
    game = True
    # Turn Counter
    turn = 0
    stalemate = False

    print("Welcome to Chess! State your moves in the form: a2 to a4")
    THE_BOARD.display()

    while game:

        if turn % 2 == 0:
            player = "white"
            player_move_completed = False
            my_king = is_my_king_in_check(player)
            if my_king:
                print(f"{(player).upper()} KING IN CHECK")
                if count_possible_moves_when_in_check(my_king) < 1:
                    loser = player
                    break
            
            stalemate = check_stalemate(player)
            if stalemate:
                break

            while not player_move_completed:
                print("")
                move = input("WHITE TO MOVE:\n")

                coordinates = convert_input_to_coords(move)
                # Checks to see if coordinates are valid (True if valid)
                if coordinates:
                    selected_position = coordinates[0]
                    destination_position = coordinates[1]

                    # If the piece is succesfully moved, the player's turn is over
                    # Otherwise, completion remains False
                    player_move_completed = check_then_move(selected_position, destination_position, player)
                    pawn_evolution_check()
            
            THE_BOARD.display()
            turn += 1

        else:
            player = "black"
            player_move_completed = False
            my_king = is_my_king_in_check(player)
            if my_king:
                print(f"{player.upper()} KING IN CHECK")
                if count_possible_moves_when_in_check(my_king) < 1:
                    loser = player
                    break
            
            stalemate = check_stalemate(player)
            if stalemate:
                break

            while not player_move_completed:
                move = input("BLACK TO MOVE:\n")

                coordinates = convert_input_to_coords(move)
                # Checks to see if coordinates are valid (True if valid)
                if coordinates:
                    selected_position = coordinates[0]
                    destination_position = coordinates[1]

                    # If the piece is succesfully moved, the player's turn is over
                    # Otherwise, completion remains False
                    player_move_completed = check_then_move(selected_position, destination_position, player)
                    pawn_evolution_check()
            
            THE_BOARD.display()
            turn += 1

    if stalemate:
        print(f"STALEMATE. TIE GAME")
    else:
        print(f"CHECKMATE. {loser.upper()} LOSES")

    again = input("Do you wanna play again?")
    if (again.lower())[0] == 'y':
        main()
    else:
        print("Thanks for playing!")


if __name__ == "__main__":
    main()
