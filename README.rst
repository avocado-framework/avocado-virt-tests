Avocado Virt Tests
==================

These are sample tests written with the avocado virt plugin [1].

Provided that you have avocado and its virt plugin installed, you can run the
tests like the following::

    $ avocado run qemu/boot.py 
    JOB ID    : d808c7b3cd28455fe500a0911b792e40ea88a21c
    JOB LOG   : /home/lmr/avocado/job-results/job-2014-09-02T23.49-d808c7b/job.log
    TESTS     : 1
    (1/1) qemu/boot.py: PASS (7.51 s)
    PASS      : 1
    ERROR     : 0
    FAIL      : 0
    SKIP      : 0
    WARN      : 0
    NOT FOUND : 0
    TIME      : 7.51 s

[1] https://github.com/avocado-framework/avocado-virt
