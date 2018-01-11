import math
import pandas as pd
from generated_graph import ERGraph, EuclideanGraph, GeneratedGraph
import argparse
import os


def program_sequence_of_attacks(no_of_nodes):
    seq = {}
    seq2 = {}
    for i in range(1, 6):
        er = ERGraph(stat=math.log(no_of_nodes)/no_of_nodes, no_of_nodes=no_of_nodes)
        er.write_nodes_to_file()
        
        q = er.no_of_edges
        r = math.sqrt(q/math.pi/er.no_of_nodes/(er.no_of_nodes-1)*2)
        
        
        run_sequence_of_attacks(er, i, seq)
                   
        eucl = EuclideanGraph(stat = r, no_of_nodes=no_of_nodes)    
        eucl.write_nodes_to_file()
        
        run_sequence_of_attacks(eucl, i, seq2)   
    save_attacks(er.__class__.__name__, no_of_nodes, seq)
    save_attacks(eucl.__class__.__name__, no_of_nodes, seq2)
            
def run_sequence_of_attacks(graph, no_of_seq, seq_dict):
    att_dict = {}
    for j in range(1, 20):
        p = 0.05*j
        attacks = []
        succ_count = 0
        fail_count = 0
        avg_largest = 0
        for a in range(0, 1000):
            result = graph.make_an_attack(p)
            if result[3]:
                avg_largest += result[2]
                succ_count += 1
            else:
                fail_count += 1
            attacks.append(result)
            if fail_count > 10 and succ_count > 10 and a >= 100:
                break
        att_dict[str(p)] = {"non_attacked": graph.no_of_nodes - result[1],"size": graph.no_of_nodes,"no_of_attacks": a+1,  "no_of_success": succ_count, "avg_largest": float(avg_largest)/succ_count if succ_count>0 else "not succeeded", "attacked": result[1], "% of success": float(succ_count)/(a+1)}
    seq_dict[no_of_seq] = att_dict
    return seq_dict

def save_attacks(graph_name, no_of_nodes, x, directory = "attacks"):
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = graph_name+"_attacks_"+str(no_of_nodes)+".xls"
    path = os.path.join(directory, filename)
    pd.DataFrame.from_dict({(i,j): x[i][j]
                        for i in x.keys()
                        for j in x[i].keys()}).T.to_excel(path, float_format="%.2f")
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some options.')
    parser.add_argument("--no_of_nodes", action='store',
                        default=100, type=int,
                        help='default: 100')
    args = parser.parse_args()
    main = program_sequence_of_attacks(**vars(args))