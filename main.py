import turtle

t = turtle.Turtle()
t.speed(5)
t.pensize(5)

def draw_ring(x, y, color):
    t.penup()
    t.goto(x, y - 50)
    t.pendown()
    t.color(color)
    t.circle(50)

draw_ring(-110, 0, "blue")
draw_ring(0, 0, "black")
draw_ring(110, 0, "red")

draw_ring(-55, -60, "yellow")
draw_ring(55, -60, "green")

t.hideturtle()
turtle.exitonclick()
