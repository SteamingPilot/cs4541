
import subprocess
import os

# NOTE: Make sure to have csim-ref and cache_sim executables in the same directory as this file
# All references to ./test2 are to ./cache_sim

# ./test2 -v -s 1 -E 2 -b 4 -t wmucachelab2/traces/yi.trace
# ./csim-ref -v -s 1 -E 2 -b 4 -t ./traces/yi.trace 



# Test s
# yi.trace
# E = 1
# while E < 5:
#     s = 1
#     while s < 5:
#         b = 1
#         while b < 5:
#             os.system(f"./test2 -v -s {s} -E {E} -b {b} -t wmucachelab2/traces/yi.trace > ./unittest/unittest_my.txt")
#             os.system(f"./wmucachelab2/csim-ref -v -s {s} -E {E} -b {b} -t ./wmucachelab2/traces/yi.trace > ./unittest/unittest_ref.txt")


#             file_my = open("./unittest/unittest_my.txt", "r")
#             file_ref = open("./unittest/unittest_ref.txt", "r")

#             my_lines = file_my.readlines()
#             ref_lines = file_ref.readlines()

#             print(f"E={E} s={s} b={b}", end=" ")
#             isError = False
#             for i in range(len(my_lines)):
#                 if(my_lines[i] != ref_lines[i]):
#                     print("Error")
#                     isError = True
#                     break
                
#             if not isError:
#                 print("Success")

#             b += 1
#         s += 1
#     E += 1


# Test: dave.trace
# E = 1
# while E < 5:
#     s = 1
#     while s < 5:
#         b = 1
#         while b < 5:
#             os.system(f"./test2 -v -s {s} -E {E} -b {b} -t wmucachelab2/traces/dave.trace > ./unittest/unittest_my.txt")
#             os.system(f"./wmucachelab2/csim-ref -v -s {s} -E {E} -b {b} -t ./wmucachelab2/traces/dave.trace > ./unittest/unittest_ref.txt")


#             file_my = open("./unittest/unittest_my.txt", "r")
#             file_ref = open("./unittest/unittest_ref.txt", "r")

#             my_lines = file_my.readlines()
#             ref_lines = file_ref.readlines()

#             print(f"E={E} s={s} b={b}", end=" ")
#             isError = False
#             for i in range(len(my_lines)):
#                 if(my_lines[i] != ref_lines[i]):
#                     print("Error")
#                     isError = True
#                     break
                
#             if not isError:
#                 print("Success")

#             b += 1
#         s += 1
#     E += 1


# Test: trans.trace
# E = 1
# while E < 5:
#     s = 1
#     while s < 5:
#         b = 1
#         while b < 5:
#             os.system(f"./test2 -v -s {s} -E {E} -b {b} -t wmucachelab2/traces/trans.trace > ./unittest/unittest_my.txt")
#             os.system(f"./wmucachelab2/csim-ref -v -s {s} -E {E} -b {b} -t ./wmucachelab2/traces/trans.trace > ./unittest/unittest_ref.txt")


#             file_my = open("./unittest/unittest_my.txt", "r")
#             file_ref = open("./unittest/unittest_ref.txt", "r")

#             my_lines = file_my.readlines()
#             ref_lines = file_ref.readlines()

#             print(f"E={E} s={s} b={b}", end=" ")
#             isError = False
#             for i in range(len(my_lines)):
#                 if(my_lines[i] != ref_lines[i]):
#                     print(f"Line: {i}, my: {my_lines[i]}, ref: {ref_lines[i]}")
#                     print("Error")
#                     isError = True
#                     break
                
#             if not isError:
#                 print("Success")

#             b += 1
#         s += 1
#     E += 1



s = 1
E = 1
b = 1
fname = "yi2.trace"

def test(s, E, b, fname):
    os.system(f"./cache_sim -s {s} -E {E} -b {b} -t wmucachelab2/traces/{fname} > ./unittest/unittest_my.txt")
    os.system(f"./wmucachelab2/csim-ref -s {s} -E {E} -b {b} -t ./wmucachelab2/traces/{fname} > ./unittest/unittest_ref.txt")


    file_my = open("./unittest/unittest_my.txt", "r")
    file_ref = open("./unittest/unittest_ref.txt", "r")

    my_lines = file_my.readlines()
    ref_lines = file_ref.readlines()

    print(f"E={E} s={s} b={b}", end=" ")
    isError = False
    for i in range(len(my_lines)):
        if(my_lines[i] != ref_lines[i]):
            print(f"Line: {i}, my: {my_lines[i]}, ref: {ref_lines[i]}")
            print("Error")
            isError = True
            break

    if not isError:
        print("Success")



test(s=1, E=1, b=1, fname="yi2.trace")
test(s=4, E=2, b=4, fname="yi.trace")
test(s=2, E=1, b=4, fname="dave.trace")
test(s=2, E=1, b=3, fname="trans.trace")

test(s=2, E=2, b=3, fname="trans.trace")
test(s=2, E=4, b=3, fname="trans.trace")
test(s=2, E=4, b=3, fname="trans.trace")
test(s=5, E=1, b=5, fname="trans.trace")

test(s=5, E=1, b=5, fname="long.trace")





