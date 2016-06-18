

import imp
import os
from mininet.topo import Topo

running_script_dir = os.path.dirname(os.path.abspath(__file__))
global_dir = os.path.join(os.path.split(running_script_dir)[0], 'main')
Global  = imp.load_source('Global', os.path.join(global_dir, 'Global.py'))
from Global import *
OptNet  = imp.load_source('OpticalNetwork', os.path.join(MAIN_DIR, 'OpticalNetwork.py'))
MmSrlg  = imp.load_source('MM_SRLG',        os.path.join(MAIN_DIR, 'MM_SRLG.py'))
MNInterface = imp.load_source('mn_interface',        os.path.join(BASE_DIR, 'mininet', 'mn_interface.py'))


def mn_test():
    optNet = MNInterface.get_running_opt_net()
    print(optNet.nodes())
    print(optNet.get_logical_nodes())
    print(optNet.physical_links())
    mmSrlg = MmSrlg.MM_SRLG_solver()
    optNet.l_net = mmSrlg.mm_srlg(optNet)
    mn_intf = MininetInterface()
    topo = mn_intf.optical_network_to_mn_topo(optNet)
    print(optNet.l_net.get_paths())


def run_tests():
    mn_test()

if "__main__" == __name__:
    run_tests()


