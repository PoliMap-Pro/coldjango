import os

import graphviz
from datetime import datetime
from django.core.management.base import BaseCommand
from ... import models


class Command(BaseCommand):
    N = 200
    #YEARS = (2022, 2016, )
    YEARS = (2022, 2019, 2016, 2013, 2010, 2007, 2004,)
    PARTY_ABBREVIATION = 'GRN'
    NODE_SHAPE = 'box'
    RESULTS_DIRECTORY = os.path.join(".", "test_case_4_results")
    PREF = models.CandidatePreference.objects

    help = "Look at these N seats. How do preferences flow from the Libs to " \
           "ALP/Greens in the 2016 election, and how about 2022 (where the " \
           "Lib recommendation was different?)\n\n"

    def handle(self, *arguments, **keywordarguments):
        print(Command.help)
        seat_list = list(models.Seat.objects.all().order_by('name'))[:Command.N]
        for year in Command.YEARS:
            election = models.HouseElection.objects.get(
                election_date=datetime(year=year, month=1, day=1))
            print(election)
            print()
            for seat in seat_list:
                print(seat)
                print()
                pref_rounds = list(models.PreferenceRound.objects.filter(
                    election=election, seat=seat).order_by('round_number'))
                representing_candidates = [
                    representation.person.candidate.pk for representation in
                    models.Representation.objects.filter(
                        election=election,
                        party__abbreviation__iexact=Command.PARTY_ABBREVIATION)]
                targets = [contention.candidate for contention in
                           models.Contention.objects.filter(
                               election=election, seat=seat
                           ) if contention.candidate.pk in
                           representing_candidates]
                if targets:
                    target = targets[0]
                    dot = graphviz.Digraph(
                        f"{str(target)}_{seat.name}_{year}", format='png',
                        comment='House preference flow',
                        node_attr={'shape': Command.NODE_SHAPE},
                        graph_attr={'labelloc': 't',
                                    'label': f"{seat.name} {year}",
                                    'mclimit': '10', },
                        engine='dot')
                    edges = []
                    nodes = []
                    queue = [targets[0]]
                    while queue:
                        target = queue.pop()
                        new_targets = Command.add_candidate(
                            edges, election, nodes, pref_rounds, seat, target)
                        if new_targets:
                            queue += new_targets
                    [dot.node(*node) for node in nodes]
                    [dot.edge(*edge) for edge in edges]
                    dot.render(directory=Command.RESULTS_DIRECTORY)

    @staticmethod
    def add_candidate(edges, election, nodes, pref_rounds, seat, target):
        last_round = -1
        result = []
        while last_round > -len(pref_rounds):
            round_obj = None
            for round_index in range(last_round,
                                     -len(pref_rounds) - 1, -1):
                find_trail = False
                round_obj = pref_rounds[round_index]
                pref_attributes = {
                    'election': election, 'seat': seat,
                    'round': round_obj, 'candidate': target}
                if Command.PREF.filter(**pref_attributes).exists():
                    last_pref = Command.PREF.get(**pref_attributes)
                    if last_pref.votes_received > 0:
                        find_trail = True
                        last_round = round_index - 1
                        break
                last_round -= 1
            if find_trail:
                trail_index = round_obj.round_number
                previous = Command.PREF.get(
                    election=election, seat=seat,
                    candidate=last_pref.candidate,
                    round=pref_rounds[trail_index - 1])
                trail = [(last_pref.candidate,
                          last_pref.votes_received -
                          previous.votes_received,
                          last_pref.round.round_number), ]
                while last_pref.source_candidate:
                    trail_index -= 1
                    previous = Command.PREF.get(
                        election=election, seat=seat,
                        candidate=last_pref.source_candidate,
                        round=pref_rounds[trail_index - 1]
                    )
                    last_pref = Command.PREF.get(
                        election=election, seat=seat,
                        candidate=last_pref.source_candidate,
                        round=pref_rounds[trail_index])
                    proximate = last_pref.votes_received - \
                        previous.votes_received
                    trail.append((last_pref.candidate,
                                  proximate,
                                  last_pref.round.round_number), )
                last_candidate = None
                for n, (candidate, a, b) in enumerate(trail):
                    if (candidate != target) and (candidate not in result):
                        result.append(candidate)
                    node_name = str(candidate)
                    new_node = node_name, node_name
                    try:
                        rep = models.Representation.objects.get(
                            person=candidate.person, election=election)
                    except models.Representation.MultipleObjectsReturned:
                        rep = models.Representation.objects.filter(
                            person=candidate.person, election=election)[0]
                    if new_node not in nodes:
                        nodes.append((node_name,
                                      f"{node_name}\n{rep.party.name}"), )
                    if last_candidate:
                        new_edge = node_name, last_candidate, \
                                   str(trail[n - 1][1])
                        if new_edge not in edges:
                            edges.append(new_edge)
                    last_candidate = node_name
                print(trail)
        return result









