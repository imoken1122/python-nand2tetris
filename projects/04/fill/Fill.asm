// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.
  @R0 // this is flag that whather black or white draw 
  M = 0
  @8192
  D = A
  @num_pixel //32*256
  M = D 

(KEY_LOOP)
  @KBD
  D = M
  @PUSH_KEY
  D;JNE 

(NONPUSH_KEY)
  @R0
  D = M
  @KEY_LOOP
  D;JEQ // R0 == 0
  
  @FILL_WHITE
  D;JNE

(PUSH_KEY) 
  @R0
  D=M
  @FILL_BLACK
  D;JEQ // R1=0 
  
(FILL_BLACK)
  @R0
  M = 1 // R1 = 1
  @color
  M = -1 //-1の2の補数は全て１なので16bit全て1にできる
  @DEFINE
  0;JMP

(FILL_WHITE)
  @R0
  M = 0
  @color
  M = 0

(DEFINE)
  @SCREEN //16348
  D = A
  @pos
  M = D // pos = 16348(SCREEN)
  @cnt
  M = 0

(FILL_LOOP)
  @cnt
  D = M //D = cnt
  @num_pixel
  D = D - M // cnt - num_pixel
  @FILL_LOOP_END
  D;JEQ
  
  @color
  D = M // D=color
  @pos
  A = M
  M = D // M[pos] = color
  
  @cnt
  M = M+1 // cnt++
  @pos
  M = M + 1 //pos++
  @FILL_LOOP
  0;JMP
(FILL_LOOP_END)
  @KEY_LOOP
  0;JMP
