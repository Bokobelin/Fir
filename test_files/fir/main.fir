using include_test.fir

push(5)
push(3)
add
dump
push(10)
sub
dump
print(Hello, world!)
str(ax, 5)
print($ax)
exec(ls -l)
push(1.3)
dump
str(bx, 5 ^ 2)
print($bx)
equ(ax, bx)
print($ax)