import numpy as np
import json
import itertools
import matplotlib.pyplot as plt
from direct_transmission import GHZ_fid
from tqdm import tqdm
from graph_generator import three_star
from error_model_operators import measurement_rot_unitary
from lossfunctions import S_count_P_cond_loss



def get_perm(per, length):
    """
    Called in "get_configurations".
    :param per:
    :param length:
    :return:
    """
    list_per = itertools.permutations(per[0], length)
    list_per = list(list_per)
    clean_duplicates = []
    for p0 in list_per:
        count = 0
        for p1 in list_per:
            if p0 == p1:
                count += 1
        if p0 in clean_duplicates:
            continue
        else:
            clean_duplicates.append(p0)
    return clean_duplicates


def get_configuration(numb):
    """
    Caveman way of getting all the configurations for graphs up to 7-qubits( including the input qubit).
    Here "+" referes to no error and "-" to error.
    :param numb: number of qubits
    :return: all the configurations
    """
    permutation_three = [['++'], ['+-'], ['--']]
    permutation_four = [['+++'], ['++-'], ['+--'], ['---']]
    permutation_five = [['+++-'], ['++--'], ['+---'], ['----'], ['++++']]
    permutation_six = [['++++-'], ['+++--'], ['++---'], ['+----'], ['+++++'], ['-----']]
    permutation_seven = [['+++++-'], ['++++--'], ['+++---'], ['++----'], ['+-----'], ['++++++'], ['------']]
    permutation_eigth = [['++++++-'], ['+++++--'], ['++++---'], ['+++----'], ['++-----'], ['+------'], ['+++++++'], ['-------']]
    configurations = []
    if numb == 3:
        for per in permutation_three:
            new = get_perm(per, 2)
            configurations = configurations + new

    elif numb == 4:
        for per in permutation_four:
            new = get_perm(per, 3)
            configurations = configurations + new

    elif numb == 5:
        for per in permutation_five:
            new = get_perm(per, 4)
            configurations = configurations + new

    elif numb == 6:
        for per in permutation_six:
            new = get_perm(per, 5)
            configurations = configurations + new

    elif numb == 7:
        for per in permutation_seven:
            new = get_perm(per, 6)
            configurations = configurations + new

    elif numb == 8:
        for per in permutation_eigth:
            new = get_perm(per, 7)
            configurations = configurations + new

    return configurations

def prob_den(operator, den_matrix):
    projection = np.matmul(operator, np.matmul(den_matrix, np.conjugate(operator).transpose()))
    prob = np.trace(projection)
    projection = projection / prob
    return prob, projection




def meas_projectors(B, theta, axis):
    """
    :param B: which basis to measure each qubit
    :return: the projectors corresponding to B. This is a list of lists, where the inner list contatins
    projector up and down.
    """
    U = measurement_rot_unitary(theta, axis, 0) # ZERO FOR PHI
    # B for bases :D
    identity = np.array([[1, 0, 0, 0],
                         [0, 1, 0, 0],
                         [0, 0, 1, 0],
                         [0, 0, 0, 1]], dtype=np.complex128)
    Z_up = np.array([0, 1, 0, 0], dtype=np.complex128)
    Z_down = np.array([0, 0, 1, 0], dtype=np.complex128)
    X_up = np.array([0, 1 / np.sqrt(2), 1 / np.sqrt(2), 0], dtype=np.complex128)
    X_down = np.array([0, 1 / np.sqrt(2), -1 / np.sqrt(2), 0], dtype=np.complex128)
    Y_up = np.array([0, 1 / np.sqrt(2), 1j / np.sqrt(2), 0], dtype=np.complex128)
    Y_down = np.array([0, 1 / np.sqrt(2), -1j / np.sqrt(2), 0], dtype=np.complex128)

    Z_up = np.outer(Z_up, Z_up.transpose())
    Z_up = np.matmul(np.matmul(U, Z_up), np.conjugate(U).transpose())
    Z_down = np.outer(Z_down, Z_down.transpose())
    Z_down = np.matmul(np.matmul(U, Z_down), np.conjugate(U).transpose())
    X_up = np.outer(X_up, X_up.transpose())
    X_up = np.matmul(np.matmul(U, X_up), np.conjugate(U).transpose())
    X_down = np.outer(X_down, X_down.transpose())
    X_down = np.matmul(np.matmul(U, X_down), np.conjugate(U).transpose())
    Y_up = np.outer(Y_up, np.conjugate(Y_up).transpose())
    Y_up = np.matmul(np.matmul(U, Y_up), np.conjugate(U).transpose())
    Y_down = np.outer(Y_down, np.conjugate(Y_down).transpose())
    Y_down = np.matmul(np.matmul(U, Y_down), np.conjugate(U).transpose())

    Z_up_spin = np.array([1, 0, 0, 0], dtype=np.complex128)
    Z_up_spin = np.outer(Z_up_spin, Z_up_spin.transpose())
    Z_down_spin = np.array([0, 1, 0, 0], dtype=np.complex128)
    Z_down_spin = np.outer(Z_down_spin, Z_down_spin.transpose())
    X_up_spin = np.array([1 / np.sqrt(2), 1 / np.sqrt(2), 0, 0], dtype=np.complex128)
    X_up_spin = np.outer(X_up_spin, X_up_spin.transpose())
    X_down_spin = np.array([1 / np.sqrt(2), -1 / np.sqrt(2), 0, 0], dtype=np.complex128)
    X_down_spin = np.outer(X_down_spin, X_down_spin.transpose())
    Y_up_spin = np.array([1 / np.sqrt(2), 1j / np.sqrt(2), 0, 0], dtype=np.complex128)
    Y_up_spin = np.outer(Y_up_spin, np.conjugate(Y_up_spin).transpose())
    Y_down_spin = np.array([1 / np.sqrt(2), -1j / np.sqrt(2), 0, 0], dtype=np.complex128)
    Y_down_spin = np.outer(Y_down_spin, np.conjugate(Y_down_spin).transpose())

    pattern = []
    for i in range(len(B)):
        print(i)
        if i == 0:
            if B[i] == 'X':
                op_up = X_up_spin
                op_dw = X_down_spin

            elif B[i] == 'Y':
                op_up = Y_up_spin
                op_dw = Y_down_spin

            else:
                op_up = Z_up_spin
                op_dw = Z_down_spin

        else:
            op_up = identity
            op_dw = identity
        for j in range(1, len(B)):
            if B[i] == 'X':
                if i == j:
                    op_up = np.kron(op_up, X_up)
                    op_dw = np.kron(op_dw, X_down)
                else:
                    op_up = np.kron(op_up, identity)
                    op_dw = np.kron(op_dw, identity)

            elif B[i] == 'Y':
                if i == j:
                    op_up = np.kron(op_up, Y_up)
                    op_dw = np.kron(op_dw, Y_down)
                else:
                    op_up = np.kron(op_up, identity)
                    op_dw = np.kron(op_dw, identity)

            else:
                if i == j:
                    op_up = np.kron(op_up, Z_up)
                    op_dw = np.kron(op_dw, Z_down)
                else:
                    op_up = np.kron(op_up, identity)
                    op_dw = np.kron(op_dw, identity)
        pattern.append([op_up, op_dw])

    return pattern


def get_B(S, M):
    """
    :param S: list of all stabilizers
    :return: A list of measurement basis for each qubit with qubit 0 being element 0, qubit 1 is element 1 etc.
    """
    B = []
    for i in range(len(S[0])):
        if i == 0:
            if M == 'Z':
                B.append('Z')
            elif M == 'X':
                B.append('X')
            elif M == 'Y':
                B.append('Y')
        else:
            B.append('I')

    for stab in S:
        for i in range(len(stab)):
            if B[i] == 'I' and stab[i] != 'I':
                del B[i]
                B.insert(i, stab[i])
    return B



def conditional_M_S(M, S):
    if M == -1:  # Currently only concerend with up in respective bases
        return 1
    else:
        return 0

def corrected_conditional(P):
    return min(P, 1 - P)

def logical_error(P_dict, S_count, monte_steps):
    logical_err = 0
    no_corr_error = 0
    for the_key in P_dict.keys():
        if the_key == "0":
            logical_err += S_count[the_key] / monte_steps
            no_corr_error += logical_err
        else:
            P_err = P_dict[the_key] / S_count[the_key]
            P_err_corr = corrected_conditional(P_err)
            P_config = S_count[the_key] / monte_steps
            logical_err += P_config * P_err_corr
            no_corr_error += P_dict[the_key] / monte_steps
    return logical_err, no_corr_error



def gen_prob_dict(pattern, den_matrix, configurations, numb_photons):
    prob_dict = {}
    up = pattern[0][0]
    PP, den_matrix = prob_den(up, den_matrix)
    for config in configurations:
        root = 2 ** (numb_photons)
        value = root
        den_matrix_loop = den_matrix
        for i in range(len(config)):
            up, down = pattern[i + 1]
            if config[i] == "+":
                operator = up
                P_up, state_up = prob_den(operator, den_matrix_loop)
                P_down, state_down = prob_den(down, den_matrix_loop)
                norm = P_up + P_down
                P_up = P_up / norm
                den_matrix_loop = state_up
                value = value + root / (2 ** (i + 1))
                prob_dict[str(value)] = P_up

            else:
                operator = down
                P_down, state_down = prob_den(operator, den_matrix_loop)
                P_up, state_up = prob_den(up, den_matrix_loop)
                norm = P_up + P_down
                P_down = P_down / norm
                den_matrix_loop = state_down
                value = value - root / (2 ** (i + 1))
                prob_dict[str(value)] = P_down

    # up = pattern[0][1]
    # PP, den_matrix = prob_den(up, den_matrix_loop)
    # print(PP)

    return prob_dict




def get_logical_op(prob_dict, S, M, numb_photons):
    observables = [1 for i in range(numb_photons + 1)]
    root = 2 ** (numb_photons)
    value = root
    # Following loop generates the measurement outcome for each qubit and appends it to "observables"
    for i in range(1, numb_photons + 1):
        value_left = value - root / (2 ** (i))
        value_right = value + root / (2 ** (i))
        if prob_dict[str(value_right)] > np.random.uniform():
            # print(prob_dict[str(value_right)])
            value = value_right
            observables[i] = observables[i] * 1

        else:
            value = value_left
            observables[i] = observables[i] * (-1)
    S_measured = []
    M_measured = 1
    # Two following loops generate the measured value of each stabilizer and logical M
    for stab in S:
        s = 1
        for i in range(len(stab)):
            if stab[i] != 'I':
                s = s * observables[i]
        S_measured.append(s)
    for i in range(len(M)):
        if M[i] != 'I':
            M_measured = M_measured * observables[i]

    return M_measured, S_measured





def generate(S, M, theta, axis):
    """

    :param S: List of stabilizers
    :param M: Z, X or Y
    :return: meas. operators
    """
    B = get_B(S, M)
    pattern = meas_projectors(B, theta, axis)

    return pattern




def S_count_P_cond(prob_dict, S, M, numb_photons):
    S_measured = []
    S_count = {}
    P_dict = {}
    for i in range(monte_steps):  # Monte steps
        M_count, S_meas = get_logical_op(prob_dict, S, M, numb_photons)
        joined = ''.join(map(str, S_meas))
        if joined in S_measured:
            p_cond = conditional_M_S(M_count, S_meas)
            if p_cond == 1:
                P_dict[joined] = 1 + P_dict[joined]
            S_count[joined] = 1 + S_count[joined]
        else:
            S_measured.append(joined)
            p_cond = conditional_M_S(M_count, S_meas)
            if p_cond == 1:
                P_dict[joined] = 1
            else:
                P_dict[joined] = 0
            S_count[joined] = 1
    return P_dict, S_count





def simulate_monte(S_M_dict, monte_steps, kappas, T2, keys, logical_op, theta, axis, I, numb_photons, loss):
    for key in keys:
        M = S_M_dict[key][0]
        S = S_M_dict[key][1]
        print(M)
        print(S)
        ind_direct = logical_op
        configurations = get_configuration(numb_photons + 1)
        xval = []
        error = []
        xvalGHZ = []
        error_GHZ_list = []
        corr_val = []
        corr_error = []
        t2 = T2
        t = theta
        kappa = kappas
        if logical_op == "Z":
            graph = "star-middle"
        elif logical_op == "Y":
            graph = "fully"
        else:
            graph = "star-leaf"
        for l in loss:
        # for kappa in kappas:
        # for t2 in T2:
        # for t in theta:
            pattern_X = generate(S, ind_direct, t, axis)
            log_error_list = []
            no_error_list = []
            the_list = [i for i in range(10)]
            # for i in range(1000):
            for i in tqdm(the_list):
                den_matrix = three_star(I, kappa, t2, numb_photons, graph)
                prob_dict = gen_prob_dict(pattern_X, den_matrix, configurations, numb_photons)
                # P_dict, S_count = S_count_P_cond(prob_dict, S, M, numb_photons)
                P_dict, S_count, steps = S_count_P_cond_loss(prob_dict, numb_photons, l, graph, logical_op, monte_steps)
                print(P_dict, S_count)
                logical_err, no_corr_error = logical_error(P_dict, S_count, steps)
                log_error_list.append(logical_err)
                no_error_list.append(no_corr_error)
            GHZ_error, GHZ_error_error = GHZ_fid(kappa, 'Z', t2, t, axis, I, l)
            xval.append(np.mean(log_error_list))
            error.append(np.std(log_error_list))
            xvalGHZ.append(GHZ_error)
            error_GHZ_list.append(GHZ_error_error)
            corr_val.append(np.mean(no_error_list))
            corr_error.append(np.std(no_error_list))
            print("GHZ error {} with standard deviation {}".format(GHZ_error, GHZ_error_error))
            print("Logical error {} with standard deviation {}".format(np.mean(log_error_list), np.std(log_error_list)))
            print("No correction error {} with standard deviation {}".format(np.mean(no_error_list), np.std(no_error_list)))
    plt.errorbar(loss, xval, yerr=error, label="logical-encoded-corrected")
    plt.errorbar(loss, xvalGHZ, yerr=error_GHZ_list, label="direct-transmission")
    # plt.errorbar(kappas, corr_val, yerr=corr_error, label="logical-encoded-no-correction")
    # plt.xscale('log')
    # plt.xlabel("$\kappa$")
    # plt.xlabel("$\u03B8$")
    # plt.xlabel("$T_2^*$")
    plt.xlabel("$p_{loss}$")
    plt.ylabel("$\epsilon_{L}$")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    path_codes = r"C:\Users\Admin\final_iter_dict.json"
    # path_codes = r"C:\Users\Admin\now_with_lc_5_qubit.json"
    f = open(path_codes)
    the_dict = json.load(f)
    # path_stabs = r"C:\Users\Admin\stab_and_logical_op_5_qubit.json"
    path_stabs = r"C:\Users\Admin\stab_and_logical_Y_4_qubit.json"
    f = open(path_stabs)
    S_M_dict = json.load(f)
    # Few parameters

    # kappas = np.linspace(0.00021, 0.021, 5)
    kappas = 0.021
    monte_steps = 20000
    inputs = list(S_M_dict.keys())
    logical_op = "Y"
    input = ["5"]
    # T2 = np.linspace(60, 10, 5)
    T2 = 23.2
    # theta = np.linspace(0, np.pi / 4, 5)
    theta = 0.05
    axis = "all"
    I = 0.947
    numb_photons = 3
    loss = np.linspace(0, 0.8, 6)
    # Run the simulation given the parameters and the given graphs
    simulate_monte(S_M_dict, monte_steps, kappas, T2, input, logical_op, theta, axis, I, numb_photons, loss)