# optical_network


---- OpticalNetwork ------
for syncing this project with mininet environment, use a RYU app controller that set a static routing paths between
    pairs of end-points (hosts).
a suitable app is located at:
https://github.com/gitprof/ryu

 Instructions:
 clone this repo and RYU repo into the same dir.
 use one of the familiar graph formats to initialize the object. see OpticalNetwork relevant code.


----- Mininet Interface ------
file: src/mn/mn_interface.py
This module provide the OpticalNetwork layer, and the mininet environment.
it provides various of functionalities for initializing, monitoring, benchmarking and testing of a given topology
and an algorithm for routing over it.



------ Tests -------
* dry tests:
file: src/test/AlgoTester.py
this is a generic test for checking performance of routing algorithms.
the test initialize OpticalNetwork object with a given graph file, execute a given algorithm
for producing logical paths, check connectivity theoretical estimatated BW for each link failure

* mn tests:
file: src/test/mn_test.py
initialize OpticalNetwork and deploy it on Mininet environemnt, using a certain routing algorithm for each test.
most of the tests are resillience tests for checking and comparing algorithm's performance (to each other, or over different topologies)
run with --help for options info.
see src/main/Global.py file for list of all pathing algorithms, graphs and more.

 --- HELP output ---
$ sudo python src/test/mn_test.py --help
usage: mn_test.py [-h]
                  [--test_mode {INTERACTIVE,GRAPH_CMP,ALGO_CMP,REGRESSION,MN_EXAMPLES}]
                  [--graph GRAPH] [--algo {MM_SRLG,MM_SRLG_VAR,DP}]
                  [--debug_mod {0,1,2,3,4}]

--- Generic Mininet Test ---
Execute Mininet, run different perftests and produce results statistics and diagrams.

optional arguments:
  -h, --help            show this help message and exit
  --test_mode {INTERACTIVE,GRAPH_CMP,ALGO_CMP,REGRESSION,MN_EXAMPLES}
                        test mode.
                        interactive: run mn and execute mn shell.
                        graph_cmp:   run the given algorithm on different graphs.
                        algo_cmp:    run different algorithms on the given graph.
                        regression:  runs all algorithms on each graphs, produce results per graphs, and total summary.
                        mn_examples: run some basic mn examples.
                        # default is INTERACTIVE
                        # see src/mainGlobal.py file for list of all pathing algorithms and graphs
  --graph GRAPH         graph file name. the file should be located in the 'graphs' dir, and should be of a familiar format. see documentation for gen_grid_graph() method of OpticalNetwork for details.
                        available only for test_mode interactive or algo_comparison. default test8.g.
  --algo {MM_SRLG,MM_SRLG_VAR,DP}
                        routing algorithm. available only for test_mode interactive or graph_comparison. default MM_SRLG
  --debug_mod {0,1,2,3,4}
                        debug_mod: 0 - debug. 1 - info. 2 - warnings. 3 - errors. 4 - silent

 ----------------

* perftest unit:
file: src/test/process_iperf_res.p
this is a perftest runs All2All on the currently running MN topo.
it uses pickled host list, as produced by the OpticalNetwork object.
thus you must use it after executing MN via test mode interactive.
just open a shell (different than the one that running MN) and run w/o params
(this unit is used by mn test)
