BOARD_SIZE = 9          
WIN_LENGTH = 4          
EMPTY  =  0
HUMAN  =  1   
AI     = -1  
DEFAULT_DEPTH = 3
NEIGHBOR_RANGE = 2

SCORE = {
    "WIN":          100_000,
    "FOUR_OPEN":     10_000,
    "FOUR_HALF":      5_000,
    "THREE_OPEN":     1_000,
    "THREE_HALF":       200,
    "TWO_OPEN":          50,
    "TWO_HALF":          10,
}


CELL_SIZE    = 64          
MARGIN       = 20   
PANEL_WIDTH  = 290

BOARD_PX  = BOARD_SIZE * CELL_SIZE + 2 * MARGIN
WINDOW_W  = BOARD_PX + PANEL_WIDTH
WINDOW_H  = BOARD_PX

C_BG         = ( 30,  30,  40) 
C_GRID       = ( 70,  70,  90)   
C_CELL_EVEN  = ( 35,  35,  48)   
C_CELL_ODD   = ( 42,  42,  58) 
C_HUMAN      = ( 99, 179, 255)   
C_AI         = (255, 107, 107)   
C_PANEL      = ( 22,  22,  32)   
C_TEXT       = (220, 220, 230)  
C_SUBTEXT    = (140, 140, 160)   
C_HIGHLIGHT  = (255, 210,  60) 
C_WIN_CELL   = ( 80, 220, 120)  
C_BTN        = ( 60,  90, 160)
C_BTN_HOVER  = ( 80, 120, 200)
C_BTN_TEXT   = (255, 255, 255)