#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

import reda

basepath = os.path.dirname(__file__) + os.sep


def test_loading_normal():
    ert = reda.ERT()
    ert.import_syscal_bin(basepath + 'data_normal.bin')

    ert_txt = reda.ERT()
    ert_txt.import_syscal_txt(basepath + 'data_normal.txt')

def test_loading_reciprocal():
    ert = reda.ERT()
    ert.import_syscal_bin(
        basepath + 'data_reciprocal.bin',
        reciprocals=48,
    )

    ert_txt = reda.ERT()
    ert_txt.import_syscal_txt(
        basepath + 'data_reciprocal.txt',
        reciprocals=48,
    )
