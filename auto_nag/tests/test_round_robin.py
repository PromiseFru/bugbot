# coding: utf-8

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import unittest

from auto_nag.round_robin import RoundRobin


class TestRoundRobin(unittest.TestCase):

    config = {
        'doc': 'The triagers need to have a \'Fallback\' entry.',
        'triagers': {
            'A B': {'bzmail': 'ab@mozilla.com', 'nick': 'ab'},
            'C D': {'bzmail': 'cd@mozilla.com', 'nick': 'cd'},
            'E F': {'bzmail': 'ef@mozilla.com', 'nick': 'ef'},
            'Fallback': {'bzmail': 'gh@mozilla.com', 'nick': 'gh'},
        },
        'components': {'P1::C1': 'default', 'P2::C2': 'default', 'P3::C3': 'special'},
        'default': {
            'doc': 'All the dates are the duty end dates.',
            '2019-02-21': 'A B',
            '2019-02-28': 'C D',
            '2019-03-07': 'E F',
        },
        'special': {
            'doc': 'All the dates are the duty end dates.',
            '2019-02-21': 'E F',
            '2019-02-28': 'A B',
            '2019-03-07': 'C D',
        },
    }

    def mk_bug(self, pc):
        p, c = pc.split('::')
        return {
            'product': p,
            'component': c,
            'triage_owner': 'ij@mozilla.com',
            'triage_owner_detail': {'nick': 'ij'},
        }

    def test_get(self):
        rr = RoundRobin(rr={'team': TestRoundRobin.config})

        assert rr.get(self.mk_bug('P1::C1'), '2019-02-17') == ('ab@mozilla.com', 'ab')
        assert rr.get(self.mk_bug('P2::C2'), '2019-02-17') == ('ab@mozilla.com', 'ab')
        assert rr.get(self.mk_bug('P3::C3'), '2019-02-17') == ('ef@mozilla.com', 'ef')

        assert rr.get(self.mk_bug('P1::C1'), '2019-02-24') == ('cd@mozilla.com', 'cd')
        assert rr.get(self.mk_bug('P2::C2'), '2019-02-24') == ('cd@mozilla.com', 'cd')
        assert rr.get(self.mk_bug('P3::C3'), '2019-02-24') == ('ab@mozilla.com', 'ab')

        assert rr.get(self.mk_bug('P1::C1'), '2019-02-28') == ('cd@mozilla.com', 'cd')
        assert rr.get(self.mk_bug('P2::C2'), '2019-02-28') == ('cd@mozilla.com', 'cd')
        assert rr.get(self.mk_bug('P3::C3'), '2019-02-28') == ('ab@mozilla.com', 'ab')

        assert rr.get(self.mk_bug('P1::C1'), '2019-03-05') == ('ef@mozilla.com', 'ef')
        assert rr.get(self.mk_bug('P2::C2'), '2019-03-05') == ('ef@mozilla.com', 'ef')
        assert rr.get(self.mk_bug('P3::C3'), '2019-03-05') == ('cd@mozilla.com', 'cd')

        assert rr.get(self.mk_bug('P1::C1'), '2019-03-08') == ('gh@mozilla.com', 'gh')
        assert rr.get(self.mk_bug('P2::C2'), '2019-03-08') == ('gh@mozilla.com', 'gh')
        assert rr.get(self.mk_bug('P3::C3'), '2019-03-08') == ('gh@mozilla.com', 'gh')

        assert rr.get(self.mk_bug('Foo::Bar'), '2019-03-01') == ('ij@mozilla.com', 'ij')
