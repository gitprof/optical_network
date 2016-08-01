# optical_network





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

* perftest unit:
file: src/test/process_iperf_res.p

this is a perftest runs All2All on the currently running MN topo.
it uses pickled host list, as produced by the OpticalNetwork object.
thus you must use it after executing MN via test mode interactive.
just open a shell (different than the one that running MN) and run w/o params
(this unit is used by mn test)
