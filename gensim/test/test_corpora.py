#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 Radim Rehurek <radimrehurek@seznam.cz>
# Licensed under the GNU LGPL v2.1 - http://www.gnu.org/licenses/lgpl.html

"""
Automated tests for checking corpus I/O formats (the corpora package).
"""

import logging
import os.path
import unittest
import tempfile

from gensim.corpora import (bleicorpus, mmcorpus, lowcorpus, svmlightcorpus,
                            ucicorpus, malletcorpus, textcorpus)


module_path = os.path.dirname(__file__) # needed because sample data files are located in the same folder
datapath = lambda fname: os.path.join(module_path, 'test_data', fname)


def testfile():
    # temporary data will be stored to this file
    return os.path.join(tempfile.gettempdir(), 'gensim_corpus.tst')


class CorpusTesterABC(object):
    TEST_CORPUS = [[(1, 1.0)], [], [(0, 0.5), (2, 1.0)], []]

    def __init__(self):
        raise NotImplementedError("cannot instantiate Abstract Base Class")
        self.corpus_class = None # to be overridden with a particular class
        self.file_extension = None # file 'testcorpus.fileExtension' must exist and be in the format of corpusClass

    def test_load(self):
        fname = datapath('testcorpus.' + self.file_extension.lstrip('.'))
        corpus = self.corpus_class(fname)
        docs = list(corpus)
        self.assertEqual(len(docs), 9) # the deerwester corpus always has nine documents, no matter what format

    def test_empty_input(self):
        fname = testfile() + '.empty'
        with open(fname, 'w') as f:
            f.write('')

        # a couple of the subclasses rely on vocab files existing.
        with open(fname + '.vocab', 'w') as f:
            f.write('')

        corpus = self.corpus_class(fname)
        self.assertEqual(len(corpus), 0)

        docs = list(corpus)
        self.assertEqual(len(docs), 0)

    def test_save(self):
        corpus = self.TEST_CORPUS

        # make sure the corpus can be saved
        self.corpus_class.save_corpus(testfile(), corpus)

        # and loaded back, resulting in exactly the same corpus
        corpus2 = list(self.corpus_class(testfile()))
        self.assertEqual(corpus, corpus2)

        # delete the temporary file
        os.remove(testfile())

    def test_serialize(self):
        corpus = self.TEST_CORPUS

        # make sure the corpus can be saved
        self.corpus_class.serialize(testfile(), corpus)

        # and loaded back, resulting in exactly the same corpus
        corpus2 = self.corpus_class(testfile())
        self.assertEqual(corpus, list(corpus2))

        # make sure the indexing corpus[i] works
        for i in range(len(corpus)):
            self.assertEqual(corpus[i], corpus2[i])

        # delete the temporary file
        os.remove(testfile())

    def test_serialize_compressed(self):
        corpus = self.TEST_CORPUS

        for extension in ['.gz', '.bz2']:
            fname = testfile() + extension
            # make sure the corpus can be saved
            self.corpus_class.serialize(fname, corpus)

            # and loaded back, resulting in exactly the same corpus
            corpus2 = self.corpus_class(fname)
            self.assertEqual(corpus, list(corpus2))

            # make sure the indexing `corpus[i]` syntax works
            for i in range(len(corpus)):
                self.assertEqual(corpus[i], corpus2[i])

            # delete the temporary file
            os.remove(fname)

# endclass CorpusTesterABC


class TestMmCorpus(unittest.TestCase, CorpusTesterABC):
    def setUp(self):
        self.corpus_class = mmcorpus.MmCorpus
        self.file_extension = '.mm'

    def test_serialize_compressed(self):
        # MmCorpus needs file write with seek => doesn't support compressed output (only input)
        pass

# endclass TestMmCorpus


class TestSvmLightCorpus(unittest.TestCase, CorpusTesterABC):
    def setUp(self):
        self.corpus_class = svmlightcorpus.SvmLightCorpus
        self.file_extension = '.svmlight'

# endclass TestSvmLightCorpus


class TestBleiCorpus(unittest.TestCase, CorpusTesterABC):
    def setUp(self):
        self.corpus_class = bleicorpus.BleiCorpus
        self.file_extension = '.blei'

# endclass TestBleiCorpus


class TestLowCorpus(unittest.TestCase, CorpusTesterABC):
    TEST_CORPUS = [[(1, 1)], [], [(0, 2), (2, 1)], []]

    def setUp(self):
        self.corpus_class = lowcorpus.LowCorpus
        self.file_extension = '.low'

# endclass TestLowCorpus


class TestUciCorpus(unittest.TestCase, CorpusTesterABC):
    TEST_CORPUS = [[(1, 1)], [], [(0, 2), (2, 1)], []]

    def setUp(self):
        self.corpus_class = ucicorpus.UciCorpus
        self.file_extension = '.uci'

    def test_serialize_compressed(self):
        # UciCorpus needs file write with seek => doesn't support compressed output (only input)
        pass

# endclass TestUciCorpus


class TestMalletCorpus(unittest.TestCase, CorpusTesterABC):
    TEST_CORPUS = [[(1, 1)], [], [(0, 2), (2, 1)], []]

    def setUp(self):
        self.corpus_class = malletcorpus.MalletCorpus
        self.file_extension = '.mallet'

    def test_load_with_metadata(self):
        fname = datapath('testcorpus.' + self.file_extension.lstrip('.'))
        corpus = self.corpus_class(fname)
        corpus.metadata = True
        docs = list(corpus)
        self.assertEqual(len(docs), 9) # the deerwester corpus always has nine documents, no matter what format
        for i, docmeta in enumerate(docs):
            doc, metadata = docmeta

            self.assertEqual(metadata[0], str(i + 1))
            self.assertEqual(metadata[1], 'en')

# endclass TestMalletCorpus


class TestTextCorpus(unittest.TestCase):

    def setUp(self):
        self.corpus_class = textcorpus.TextCorpus
        self.file_extension = '.txt'

    def test_empty_input(self):
        fname = testfile()
        with open(fname, 'w') as f:
            f.write('')
        corpus = self.corpus_class(fname)
        docs = list(corpus)
        self.assertEqual(len(docs), 0)
        self.assertEqual(len(corpus), 0)

    def test_load_with_metadata(self):
        fname = datapath('testcorpus.' + self.file_extension.lstrip('.'))
        corpus = self.corpus_class(fname)
        corpus.metadata = True
        docs = list(corpus)
        self.assertEqual(len(docs), 9) # the deerwester corpus always has nine documents, no matter what format
        for i, docmeta in enumerate(docs):
            doc, metadata = docmeta

            self.assertEqual(metadata[0], i)

    def test_load(self):
        fname = datapath('testcorpus.' + self.file_extension.lstrip('.'))
        corpus = self.corpus_class(fname)
        docs = list(corpus)
        self.assertEqual(len(docs), 9) # the deerwester corpus always has nine documents, no matter what format
#endclass TestTextCorpus


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
