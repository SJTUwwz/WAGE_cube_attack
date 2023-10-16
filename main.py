from gurobipy import *
import time
import json

Thread_number = 8
MAX = 200000000
# round constant of WAGE
RC = [(127, 63), (31, 15), (7, 3), (1, 64), (32, 16), (8, 4), (2, 65), (96, 48), (24, 12),
      (6, 67), (33, 80), (40, 20), (10, 69), (98, 113), (120, 60), (30, 79), (39, 19), (9, 68),
      (34, 81), (104, 52), (26, 77), (102, 115), (57, 92), (46, 87), (43, 21), (74, 101),
      (114, 121), (124, 62), (95, 47), (23, 11), (5, 66), (97, 112), (56, 28), (14, 71),
      (35, 17), (72, 36), (18, 73), (100, 50), (89, 108), (54, 91), (45, 86), (107, 53),
      (90, 109), (118, 123), (61, 94), (111, 55), (27, 13), (70, 99), (49, 88), (44, 22),
      (75, 37), (82, 105), (116, 58), (93, 110), (119, 59), (29, 78), (103, 51), (25, 76),
      (38, 83), (41, 84), (42, 85), (106, 117), (122, 125), (126, 127), (63, 31), (15, 7),
      (3, 1), (64, 32), (16, 8), (4, 2), (65, 96), (48, 24), (12, 6), (67, 33), (80, 40),
      (20, 10), (69, 98), (113, 120), (60, 30), (79, 39), (19, 9), (68, 34), (81, 104),
      (52, 26), (77, 102), (115, 57), (92, 46), (87, 43), (21, 74), (101, 114), (121, 124),
      (62, 95), (47, 23), (11, 5), (66, 97), (112, 56), (28, 14), (71, 35), (17, 72), (36, 18),
      (73, 100), (50, 89), (108, 54), (91, 45), (86, 107), (53, 90), (109, 118), (123, 61),
      (94, 111), (55, 27), (13, 70)]

# index of variables (for load() and extract())
K_index = [0, 1, 2, 3, 4, 5, 6, 133, 134, 135, 136, 137, 138, 139, 7, 8, 9, 10, 11, 12, 13,
           140, 141, 142, 143, 144, 145, 146, 14, 15, 16, 17, 18, 19, 20, 147, 148, 149, 150, 151, 152, 153,
           21, 22, 23, 24, 25, 26, 27, 154, 155, 156, 157, 158, 159, 160, 28, 29, 30, 31, 32, 33, 34,
           126, 161, 162, 163, 164, 165, 166, 167, 35, 36, 37, 38, 39, 40, 41, 168, 169, 170, 171, 172, 173, 174,
           42, 43, 44, 45, 46, 47, 48, 175, 176, 177, 178, 179, 180, 181, 49, 50, 51, 52, 53, 54, 55,
           182, 183, 184, 185, 186, 187, 188, 56, 57, 58, 59, 60, 61, 62, 189, 190, 191, 192, 193, 194, 195, 127]
N_index = [196, 197, 198, 199, 200, 201, 202, 63, 64, 65, 66, 67, 68, 69, 203, 204, 205, 206, 207, 208, 209,
           70, 71, 72, 73, 74, 75, 76, 210, 211, 212, 213, 214, 215, 216, 77, 78, 79, 80, 81, 82, 83,
           217, 218, 219, 220, 221, 222, 223, 84, 85, 86, 87, 88, 89, 90, 224, 225, 226, 227, 228, 229, 230, 128,
           91, 92, 93, 94, 95, 96, 97, 231, 232, 233, 234, 235, 236, 237, 98, 99, 100, 101, 102, 103, 104,
           238, 239, 240, 241, 242, 243, 244, 105, 106, 107, 108, 109, 110, 111, 245, 246, 247, 248, 249, 250, 251,
           119, 120, 121, 122, 123, 124, 125, 252, 253, 254, 255, 256, 257, 258, 112, 113, 114, 115, 116, 117, 118, 129]


def read_ineq(file_name):
    ineqs = []
    f = open(file_name, "r")
    all_lines = f.readlines()
    for line in all_lines:
        test_line = line.rstrip('\n')
        index1 = test_line.find("[")
        index2 = test_line.find("]")
        test_line = test_line[index1:index2+1]
        # print(test_line)
        # print(type(json.loads(test_line)))
        ineqs.append(json.loads(test_line))
    # print(len(ineqs))
    f.close()
    return ineqs


Sbox_ineqs = read_ineq("inequality/WAGE_SB_DP_IG_GREEDY2.txt")
WGP_ineqs = read_ineq("inequality/WAGE_WGP_DP_IG_MILP2.txt")


# some functions for better readability of result
def normal_expression(state):
    result_poly = ""
    for i in range(259):
        if state[i] == 1:
            result_poly += ("a"+str(i))
    return result_poly


def key_nonce_expression(state):
    result_poly = ""
    for i in range(128):
        if state[K_index[i]] == 1:
            result_poly += ("k"+str(i))
    for i in range(128):
        if state[N_index[i]] == 1:
            result_poly += ("n"+str(i))
    return result_poly


def key_expression(state):
    result_poly = ""
    for i in range(128):
        if state[K_index[i]] == 1:
            result_poly += ("k"+str(i))
    return result_poly


def nonce_expression(state):
    result_poly = ""
    for i in range(128):
        if state[N_index[i]] == 1:
            result_poly += ("n"+str(i))
    return result_poly


# return the index of stage (S_ )
def return_stage_key(key_index):
    stage_index = []
    for index in key_index:
        cor_s = K_index[index] // 7
        if cor_s not in stage_index:
            stage_index.append(cor_s)
    return stage_index


def return_stage_nonce(nonce_index):
    stage_index = []
    for index in nonce_index:
        cor_s = N_index[index] // 7
        if cor_s not in stage_index:
            stage_index.append(cor_s)
    return stage_index


# model for each simple operation: SB, WGP, COPY, XOR
def Sbox_op(model, X):
    after_sbox = [model.addVar(lb=0, ub=1, vtype=GRB.BINARY) for i in range(len(X))]
    for ineq in Sbox_ineqs:
        expr = ineq[0]
        for i in range(7):
            expr += ineq[i+1]*X[i]
            expr += ineq[i+8]*after_sbox[i]
        model.addConstr(expr >= 0)
    return after_sbox


def WGP_op(model, X):
    after_WGP = [model.addVar(lb=0, ub=1, vtype=GRB.BINARY) for i in range(len(X))]
    for ineq in WGP_ineqs:
        expr = ineq[0]
        for i in range(7):
            expr += ineq[i+1]*X[i]
            expr += ineq[i+8]*after_WGP[i]
        model.addConstr(expr >= 0)
    return after_WGP


def COPY_op(model, X):
    Xcopy1 = [model.addVar(lb=0, ub=1, vtype=GRB.BINARY) for i in range(len(X))]
    Xcopy2 = [model.addVar(lb=0, ub=1, vtype=GRB.BINARY) for i in range(len(X))]
    for i in range(len(X)):
        model.addConstr(X[i] == Xcopy1[i] + Xcopy2[i])
    return Xcopy1, Xcopy2


def SB_and_xor(model, X1, X2):
    result_vector = [model.addVar(lb=0, ub=1, vtype=GRB.BINARY) for i in range(7)]
    X2copy1, X2copy2 = COPY_op(model, X2)
    SX2 = Sbox_op(model, X2copy1)
    for i in range(7):
        model.addConstr(result_vector[i] == X1[i] + SX2[i])
    return result_vector, X2copy2


def WGP_and_xor(model, X1, X2):
    result_vector = [model.addVar(lb=0, ub=1, vtype=GRB.BINARY) for i in range(7)]
    X2copy1, X2copy2 = COPY_op(model, X2)
    WX2 = WGP_op(model, X2copy1)
    for i in range(7):
        model.addConstr(result_vector[i] == X1[i] + WX2[i])
    return result_vector, X2copy2


# Secret variables evaluation method
# input: cube (list), rounds (int), output_index(int)
# output: poly_var (list)
# Model status: 2-OPTIMAL, 3-INFEASIBLE, 9-TIME_LIMIT. For more information, please refer to the REFERENCE MANUAL.
# Algorithm 1, original method for evaluating secret variables
def SuperPoly_var(cube, rounds, output_index):
    env = Env(empty=True)
    env.setParam(GRB.Param.LogToConsole, 0)
    env.setParam(GRB.Param.Threads, Thread_number)
    env.setParam(GRB.Param.TimeLimit, 18000)
    env.start()
    m = Model(env=env)

    initial_state = [m.addVar(lb=0, ub=1, vtype=GRB.BINARY) for i in range(259)]
    state = initial_state.copy()

    # cube_constraint
    for i in range(128):
        if i in cube:
            m.addConstr(state[N_index[i]] == 1)
        else:
            m.addConstr(state[N_index[i]] == 0)

    # constant constraint
    for i in range(7*18+4, 7*19):
        m.addConstr(state[i]==0)

    # k unit vector
    nv = 0
    for i in range(9*7):
        nv += initial_state[i]
    nv += initial_state[18*7]
    nv += initial_state[18*7+1]
    for i in range(19*7, 28*7):
        nv += initial_state[i]
    m.addConstr(nv == 1)

    for r in range(rounds):
        # fb = S31 + S30 + S26 + S24 + S19 + S13 + S12 + S8 + S6 + wS0
        xor_indexs = [6, 8, 12, 13, 19, 24, 26, 30, 31]
        x6copy = [m.addVar(lb=0, ub=1, vtype=GRB.BINARY) for i in range(4)]
        m.addConstr(x6copy[0] + x6copy[1] + x6copy[2] + x6copy[3] == state[6])
        w_mul = [x6copy[3]] + [m.addVar(lb=0, ub=1, vtype=GRB.BINARY) for i in range(3)] + state[3:6]
        for i in range(3):
            m.addConstr(w_mul[i+1] == state[i] + x6copy[i])

        add_var = [w_mul]
        for index in xor_indexs:
            tmp_copy1, tmp_copy2 = COPY_op(m, state[7*index:7*(index+1)])
            state[7*index:7*(index+1)] = tmp_copy1
            add_var.append(tmp_copy2)

        fb = [m.addVar(lb=0, ub=1, vtype=GRB.BINARY) for i in range(7)]
        for i in range(7):
            xor_expr = 0
            for j in range(len(add_var)):
                xor_expr += add_var[j][i]
            m.addConstr(fb[i] == xor_expr)

        # nonlinear operation
        SandC_indexs = [(5, 8), (11, 15), (24, 27), (30, 34)]
        for index in SandC_indexs:
            state[7*index[0]:7*(index[0]+1)], state[7*index[1]:7*(index[1]+1)] = SB_and_xor(m, state[7*index[0]:7*(index[0]+1)], state[7*index[1]:7*(index[1]+1)])

        state[7*19:7*(19+1)], state[7*18:7*(18+1)] = WGP_and_xor(m, state[7*19:7*(19+1)], state[7*18:7*(18+1)])
        fb, state[7*36:7*(36+1)] = WGP_and_xor(m, fb, state[7*36:7*(36+1)])

        # linear layer
        state = state[7:]+fb

    for i in range(259):
        if i == output_index:
            m.addConstr(state[i] == 1)
        else:
            m.addConstr(state[i] == 0)

    m.update()
    poly_var = []
    while True:
        m.optimize()
        # print("M status:", m.Status)
        if m.Status != 2:
            print("M status:", m.Status)
            break
        else:
            for i in range(128):
                xvalue = initial_state[K_index[i]].getAttr(GRB.Attr.X)
                if round(xvalue) == 1:
                    poly_var.append(i)
                    m.addConstr(initial_state[K_index[i]] == 0)
            m.update()
            print("|I| = ", len(poly_var), "and Current Variables: I = ", poly_var)
        poly_var.sort()
    print("|I| = ", len(poly_var), "and Current Variables: I = ", poly_var)
    env.close()
    return poly_var


# Algorithm 2, evaluate each secret variables individually
def SuperPoly_varv2(cube, rounds, output_index):
    env = Env(empty=True)
    env.setParam(GRB.Param.LogToConsole, 0)
    env.setParam(GRB.Param.Threads, Thread_number)
    env.setParam(GRB.Param.TimeLimit, 18000)
    env.start()
    m = Model(env=env)

    initial_state = [m.addVar(lb=0, ub=1, vtype=GRB.BINARY) for i in range(259)]
    state = initial_state.copy()

    # cube_constraint
    for i in range(128):
        if i in cube:
            m.addConstr(state[N_index[i]] == 1)
        else:
            m.addConstr(state[N_index[i]] == 0)

    # constant constraint
    for i in range(7*18+4, 7*19):
        m.addConstr(state[i]==0)

    for r in range(rounds):
        # fb = S31 + S30 + S26 + S24 + S19 + S13 + S12 + S8 + S6 + wS0
        xor_indexs = [6, 8, 12, 13, 19, 24, 26, 30, 31]
        x6copy = [m.addVar(lb=0, ub=1, vtype=GRB.BINARY) for i in range(4)]
        m.addConstr(x6copy[0] + x6copy[1] + x6copy[2] + x6copy[3] == state[6])
        w_mul = [x6copy[3]] + [m.addVar(lb=0, ub=1, vtype=GRB.BINARY) for i in range(3)] + state[3:6]
        for i in range(3):
            m.addConstr(w_mul[i+1] == state[i] + x6copy[i])

        add_var = [w_mul]
        for index in xor_indexs:
            tmp_copy1, tmp_copy2 = COPY_op(m, state[7*index:7*(index+1)])
            state[7*index:7*(index+1)] = tmp_copy1
            add_var.append(tmp_copy2)

        fb = [m.addVar(lb=0, ub=1, vtype=GRB.BINARY) for i in range(7)]
        for i in range(7):
            xor_expr = 0
            for j in range(len(add_var)):
                xor_expr += add_var[j][i]
            m.addConstr(fb[i] == xor_expr)

        # nonlinear operation
        SandC_indexs = [(5, 8), (11, 15), (24, 27), (30, 34)]
        for index in SandC_indexs:
            state[7*index[0]:7*(index[0]+1)], state[7*index[1]:7*(index[1]+1)] = SB_and_xor(m, state[7*index[0]:7*(index[0]+1)], state[7*index[1]:7*(index[1]+1)])

        state[7*19:7*(19+1)], state[7*18:7*(18+1)] = WGP_and_xor(m, state[7*19:7*(19+1)], state[7*18:7*(18+1)])
        fb, state[7*36:7*(36+1)] = WGP_and_xor(m, fb, state[7*36:7*(36+1)])

        # linear layer
        state = state[7:]+fb

    for i in range(259):
        if i == output_index:
            m.addConstr(state[i] == 1)
        else:
            m.addConstr(state[i] == 0)

    # k unit vector
    nv = 0
    for i in range(9*7):
        nv += initial_state[i]
    nv += initial_state[18*7]
    nv += initial_state[18*7+1]
    for i in range(19*7, 28*7):
        nv += initial_state[i]
    m.addConstr(nv == 1)

    m.addConstr(initial_state[K_index[0]] == 1, name="cons"+str(0))
    m.update()
    poly_var = []
    tmp1t = time.time()
    for i in range(1, 128):
        m.optimize()
        tmp2t = time.time()
        # print("var:", i-1, "Status:", m.Status, "Time:", tmp2t-tmp1t)
        tmp1t = tmp2t
        if m.Status == 2:
            poly_var.append(i-1)
        m.remove(m.getConstrByName("cons"+str(i-1)))
        m.addConstr(initial_state[K_index[i]] == 1, name="cons" + str(i))
        m.update()
    m.optimize()
    tmp2t = time.time()
    # print("var:", 127, "Status:", m.Status, "Time:", tmp2t-tmp1t)
    if m.Status == 2:
        poly_var.append(127)
    env.close()
    return poly_var


# Algorithm 3, Our improved method
def SuperPoly_varv3(cube, rounds, output_index):
    env = Env(empty=True)
    env.setParam(GRB.Param.LogToConsole, 0)
    env.setParam(GRB.Param.Threads, Thread_number)
    env.setParam(GRB.Param.TimeLimit, 2000)
    env.start()
    m = Model(env=env)

    initial_state = [m.addVar(lb=0, ub=1, vtype=GRB.BINARY) for i in range(259)]
    state = initial_state.copy()

    # cube_constraint
    for i in range(128):
        if i in cube:
            m.addConstr(state[N_index[i]] == 1)
        else:
            m.addConstr(state[N_index[i]] == 0)

    # constant constraint
    for i in range(7*18+4, 7*19):
        m.addConstr(state[i]==0)

    # k unit vector
    nv = 0
    for i in range(9*7):
        nv += initial_state[i]
    nv += initial_state[18*7]
    nv += initial_state[18*7+1]
    for i in range(19*7, 28*7):
        nv += initial_state[i]
    m.addConstr(nv == 1)

    for r in range(rounds):
        # fb = S31 + S30 + S26 + S24 + S19 + S13 + S12 + S8 + S6 + wS0
        xor_indexs = [6, 8, 12, 13, 19, 24, 26, 30, 31]
        x6copy = [m.addVar(lb=0, ub=1, vtype=GRB.BINARY) for i in range(4)]
        m.addConstr(x6copy[0] + x6copy[1] + x6copy[2] + x6copy[3] == state[6])
        w_mul = [x6copy[3]] + [m.addVar(lb=0, ub=1, vtype=GRB.BINARY) for i in range(3)] + state[3:6]
        for i in range(3):
            m.addConstr(w_mul[i+1] == state[i] + x6copy[i])

        add_var = [w_mul]
        for index in xor_indexs:
            tmp_copy1, tmp_copy2 = COPY_op(m, state[7*index:7*(index+1)])
            state[7*index:7*(index+1)] = tmp_copy1
            add_var.append(tmp_copy2)

        fb = [m.addVar(lb=0, ub=1, vtype=GRB.BINARY) for i in range(7)]
        for i in range(7):
            xor_expr = 0
            for j in range(len(add_var)):
                xor_expr += add_var[j][i]
            m.addConstr(fb[i] == xor_expr)

        # nonlinear operation
        SandC_indexs = [(5, 8), (11, 15), (24, 27), (30, 34)]
        for index in SandC_indexs:
            state[7*index[0]:7*(index[0]+1)], state[7*index[1]:7*(index[1]+1)] = SB_and_xor(m, state[7*index[0]:7*(index[0]+1)], state[7*index[1]:7*(index[1]+1)])

        state[7*19:7*(19+1)], state[7*18:7*(18+1)] = WGP_and_xor(m, state[7*19:7*(19+1)], state[7*18:7*(18+1)])
        fb, state[7*36:7*(36+1)] = WGP_and_xor(m, fb, state[7*36:7*(36+1)])

        # linear layer
        state = state[7:]+fb

    for i in range(259):
        if i == output_index:
            m.addConstr(state[i] == 1)
        else:
            m.addConstr(state[i] == 0)

    m.update()
    poly_var = []
    while True:
        m.optimize()
        # print("M status:", m.Status)
        if m.Status != 2:
            print("M status:", m.Status)
            break
        else:
            for i in range(128):
                xvalue = initial_state[K_index[i]].getAttr(GRB.Attr.X)
                if round(xvalue) == 1:
                    poly_var.append(i)
                    m.addConstr(initial_state[K_index[i]] == 0)
            m.update()
        poly_var.sort()
    if m.Status == 9:
        index_to_test = []
        for i in range(128):
            if i not in poly_var:
                index_to_test.append(i)
        print("Need to test:", len(index_to_test))
        tmpt = time.time()
        for i in range(len(index_to_test)):
            m.addConstr(initial_state[K_index[index_to_test[i]]] == 1, name="cons" + str(i))
            m.update()
            m.optimize()
            if m.Status == 2:
                poly_var.append(index_to_test[i])
            m.remove(m.getConstrByName("cons" + str(i)))
        # print("Time for testing:", time.time()-tmpt)
    env.close()
    poly_var.sort()
    return poly_var


# degree estimation method (help to construct cube)
def Superpoly_degree_estimation(cube, rounds, output_index):
    env = Env(empty=True)
    env.setParam(GRB.Param.LogToConsole, 0)
    env.setParam(GRB.Param.Threads, Thread_number)
    env.start()
    m = Model(env=env)

    initial_state = [m.addVar(lb=0, ub=1, vtype=GRB.BINARY) for i in range(259)]
    state = initial_state.copy()

    # cube_constraint
    for i in range(128):
        if i in cube:
            m.addConstr(state[N_index[i]] == 1)
        else:
            m.addConstr(state[N_index[i]] == 0)

    # constant constraint
    for i in range(7*18+4, 7*19):
        m.addConstr(state[i]==0)

    for r in range(rounds):
        # fb = S31 + S30 + S26 + S24 + S19 + S13 + S12 + S8 + S6 + wS0
        xor_indexs = [6, 8, 12, 13, 19, 24, 26, 30, 31]
        x6copy = [m.addVar(lb=0, ub=1, vtype=GRB.BINARY) for i in range(4)]
        m.addConstr(x6copy[0] + x6copy[1] + x6copy[2] + x6copy[3] == state[6])
        w_mul = [x6copy[3]] + [m.addVar(lb=0, ub=1, vtype=GRB.BINARY) for i in range(3)] + state[3:6]
        for i in range(3):
            m.addConstr(w_mul[i+1] == state[i] + x6copy[i])

        add_var = [w_mul]
        for index in xor_indexs:
            tmp_copy1, tmp_copy2 = COPY_op(m, state[7*index:7*(index+1)])
            state[7*index:7*(index+1)] = tmp_copy1
            add_var.append(tmp_copy2)

        fb = [m.addVar(lb=0, ub=1, vtype=GRB.BINARY) for i in range(7)]
        for i in range(7):
            xor_expr = 0
            for j in range(len(add_var)):
                xor_expr += add_var[j][i]
            m.addConstr(fb[i] == xor_expr)

        # nonlinear operation
        SandC_indexs = [(5, 8), (11, 15), (24, 27), (30, 34)]
        for index in SandC_indexs:
            state[7*index[0]:7*(index[0]+1)], state[7*index[1]:7*(index[1]+1)] = SB_and_xor(m, state[7*index[0]:7*(index[0]+1)], state[7*index[1]:7*(index[1]+1)])

        state[7*19:7*(19+1)], state[7*18:7*(18+1)] = WGP_and_xor(m, state[7*19:7*(19+1)], state[7*18:7*(18+1)])
        fb, state[7*36:7*(36+1)] = WGP_and_xor(m, fb, state[7*36:7*(36+1)])

        # linear layer
        state = state[7:]+fb

    for i in range(259):
        if i == output_index:
            m.addConstr(state[i] == 1)
        else:
            m.addConstr(state[i] == 0)

    # k unit vector
    nv = 0
    for i in range(9*7):
        nv += initial_state[i]
    nv += initial_state[18*7]
    nv += initial_state[18*7+1]
    for i in range(19*7, 28*7):
        nv += initial_state[i]

    m.setObjective(nv, GRB.MAXIMIZE)

    m.update()
    m.optimize()

    if m.getAttr(GRB.Attr.Status) == GRB.OPTIMAL:
        return round(m.getObjective().getValue()), tuple([round(initial_state[j].Xn) for j in range(259)])
    else:
        return 0, []


# degree estimation method (help to construct cube)
def UpBound(rounds, start, output_index, var_type):
    env = Env(empty=True)
    env.setParam(GRB.Param.LogToConsole, 0)
    env.setParam(GRB.Param.Threads, Thread_number)
    env.start()
    m = Model(env=env)

    initial_state = [m.addVar(lb=0, ub=1, vtype=GRB.BINARY) for i in range(259)]
    state = initial_state.copy()

    for i in range(7*18+4, 7*19):
        m.addConstr(state[i] == 0)

    for r in range(rounds):
        # fb = S31 + S30 + S26 + S24 + S19 + S13 + S12 + S8 + S6 + wS0
        xor_indexs = [6, 8, 12, 13, 19, 24, 26, 30, 31]
        x6copy = [m.addVar(lb=0, ub=1, vtype=GRB.BINARY) for i in range(4)]
        m.addConstr(x6copy[0] + x6copy[1] + x6copy[2] + x6copy[3] == state[6])
        w_mul = [x6copy[3]] + [m.addVar(lb=0, ub=1, vtype=GRB.BINARY) for i in range(3)] + state[3:6]
        for i in range(3):
            m.addConstr(w_mul[i+1] == state[i] + x6copy[i])

        add_var = [w_mul]
        for index in xor_indexs:
            tmp_copy1, tmp_copy2 = COPY_op(m, state[7*index:7*(index+1)])
            state[7*index:7*(index+1)] = tmp_copy1
            add_var.append(tmp_copy2)

        fb = [m.addVar(lb=0, ub=1, vtype=GRB.BINARY) for i in range(7)]
        for i in range(7):
            xor_expr = 0
            for j in range(len(add_var)):
                xor_expr += add_var[j][i]
            m.addConstr(fb[i] == xor_expr)

        # nonlinear operation
        SandC_indexs = [(5, 8), (11, 15), (24, 27), (30, 34)]
        for index in SandC_indexs:
            state[7*index[0]:7*(index[0]+1)], state[7*index[1]:7*(index[1]+1)] = SB_and_xor(m, state[7*index[0]:7*(index[0]+1)], state[7*index[1]:7*(index[1]+1)])

        state[7*19:7*(19+1)], state[7*18:7*(18+1)] = WGP_and_xor(m, state[7*19:7*(19+1)], state[7*18:7*(18+1)])
        fb, state[7*36:7*(36+1)] = WGP_and_xor(m, fb, state[7*36:7*(36+1)])

        # linear layer
        state = state[7:]+fb

    for i in range(259):
        if i == output_index:
            m.addConstr(state[i] == 1)
        else:
            m.addConstr(state[i] == 0)

    if var_type == 0:
        nv = 0
        for i in range(9*7, 18*7):
            nv += initial_state[i]
        nv += initial_state[18*7+2]
        nv += initial_state[18*7+3]
        for i in range(28*7, 259):
            nv += initial_state[i]
    elif var_type == 1:
        nv = 0
        for i in range(9*7):
            nv += initial_state[i]
        nv += initial_state[18*7]
        nv += initial_state[18*7+1]
        for i in range(19*7, 28*7):
            nv += initial_state[i]
    else:
        nv = sum(initial_state)

    m.setObjective(nv, GRB.MAXIMIZE)

    m.update()
    m.optimize()

    if m.getAttr(GRB.Attr.Status) == GRB.OPTIMAL:
        for i in range(259):
            start[i] = round(initial_state[i].Xn)

        return round(m.getObjective().getValue())
    else:
        return 0


if __name__ == "__main__":
    # prepare cube (here show S_9-16 as example)
    # S_9-15,17 corresponds to [1, 3, 5, 7, 9, 11, 13, 15]
    new_test_cube = []
    for index in [1, 3, 5, 7, 9, 11, 13, 17]:
        if index < 9:
            new_test_cube += [i for i in range(7 * index, 7 * (index + 1))]
        else:
            new_test_cube += [i for i in range(7 * index + 1, 7 * (index + 1) + 1)]

    # search for S_8 (24 round)
    for i in range(56, 63):
        tmpt = time.time()
        print("output index:", i)
        vars = SuperPoly_varv3(new_test_cube, 24, i)
        print(len(vars), vars)
        print("Time for this index is ", time.time() - tmpt)

    # search for S_8 (24 round)
    for i in range(7):
        tmpt = time.time()
        print("output index:", i)
        vars = SuperPoly_varv3(new_test_cube, 29, i)
        print(len(vars), vars)
        print("Time for this index is ", time.time() - tmpt)




