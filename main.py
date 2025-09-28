
print ('Hello! This is a simple calculator')
# Step 1 Take the numbers from user
a = int(input('Enter first number: '))
b = int(input('Enter second number: '))

# Step 2 Ask for operation from the user
c = input ('Enter the operation (+,-,/,*): ')
# Perform the opration

if c == '+': # addition
    print ('Result', a + b)
elif c == '-': # subraction
    print ('Result', a - b)
elif c == '/': # division
    print ('Result', a / b)
elif c == '*':
    print ('Result', a * b)
else : print ('Error Please enter a valid operation')


input("Press Enter to exit...")
