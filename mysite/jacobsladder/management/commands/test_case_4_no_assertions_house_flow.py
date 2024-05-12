import os
from datetime import datetime
from django.core.management.base import BaseCommand
from ... import models, aec_readers


class Command(BaseCommand, aec_readers.AECReader):
    N = 3
    YEARS = (2022, 2016, )
    PARTY_ABBREVIATION = 'GRN'
    RESULTS_DIRECTORY = os.path.join(".", "test_case_4_results")
    PREF = models.CandidatePreference.objects

    help = "Look at these N seats. How do preferences flow from the Libs to " \
           "ALP/Greens in the 2016 election, and how about 2022 (where the " \
           "Lib recommendation was different?)\n\n"

    def handle(self, *arguments, **keywordarguments):
        print(Command.help)
        seat_list = list(models.Seat.objects.all().order_by('name'))[:
                                                                     Command.N]
        [Command.year_flow(seat_list, year) for year in Command.YEARS]

    @staticmethod
    def year_flow(seat_list, year, abbreviation=None):
        election = Command.get_election(year)
        [Command.seat_flow(election, seat, year, abbreviation) for seat
         in seat_list]

    @staticmethod
    def seat_flow(election, seat, year, abbreviation=None):
        print(seat)
        print()
        pref_rounds, targets = Command.get_targets(
            election, seat, abbreviation, default=Command.PARTY_ABBREVIATION)
        if targets:
            Command.get_flow(election, pref_rounds, seat, targets, year)

    @staticmethod
    def get_flow(election, pref_rounds, seat, targets, year):
        dot, edges, nodes, queue = Command.setup_queue(seat, targets, year)
        while queue:
            queue = Command.one_target(edges, election, nodes, pref_rounds,
                                       queue, seat)
        Command.render_dot_file(dot, edges, nodes)

    @staticmethod
    def setup_queue(seat, targets, year):
        target = targets[0]
        dot, edges, nodes = Command.setup_dot_file(seat, target, year)
        return dot, edges, nodes, [targets[0], ]

    @staticmethod
    def render_dot_file(dot, edges, nodes):
        [dot.node(*node) for node in nodes]
        [dot.edge(*edge) for edge in edges]
        dot.render(directory=Command.RESULTS_DIRECTORY)

    @staticmethod
    def one_target(edges, election, nodes, pref_rounds, queue, seat):
        target = queue.pop()
        new_targets = Command.add_candidate(
            edges, election, nodes, pref_rounds, seat, target)
        if new_targets:
            queue += new_targets
        return queue

    @staticmethod
    def get_election(year):
        election = models.HouseElection.objects.get(
            election_date=datetime(year=year, month=1, day=1))
        print(election)
        print()
        return election

    @staticmethod
    def add_candidate(edges, election, nodes, pref_rounds, seat, target):
        last_round, result = -1, []
        while last_round > -len(pref_rounds):
            find_trail, last_pref, last_round, round_obj = \
                Command.trail_search(election, last_round, pref_rounds,
                                     seat, target)
            if find_trail:
                Command.new_trail(edges, election, last_pref, nodes,
                                  pref_rounds, result, round_obj, seat, target)
        return result

    @staticmethod
    def new_trail(edges, election, last_pref, nodes, pref_rounds, result,
                  round_obj, seat, target):
        trail = Command.add_trail(election, last_pref, pref_rounds, round_obj,
                                  seat)
        last_candidate = None
        for n, (candidate, _, _) in enumerate(trail):
            last_candidate = Command.update_candidate(
                candidate, edges, election, last_candidate, n, nodes,
                result, target, trail)
        print(trail)

    @staticmethod
    def update_candidate(candidate, edges, election, last_candidate, n, nodes,
                         result, target, trail):
        if (candidate != target) and (candidate not in result):
            result.append(candidate)
        new_node, node_name = Command.new_dot_node(candidate, election)
        if new_node not in nodes:
            nodes.append(new_node, )
        if last_candidate:
            new_edge = node_name, last_candidate, str(trail[n-1][1])
            if new_edge not in edges:
                edges.append(new_edge)
        return node_name

    @staticmethod
    def new_dot_node(candidate, election):
        node_name = str(candidate)
        try:
            rep = models.Representation.objects.get(person=candidate.person,
                                                    election=election)
        except models.Representation.MultipleObjectsReturned:
            rep = models.Representation.objects.filter(person=candidate.person,
                                                       election=election)[0]
        return (node_name, f"{node_name}\n{rep.party.name}"), node_name

    @staticmethod
    def trail_search(election, last_round, pref_rounds, seat, target):
        round_obj, find_trail = None, False
        for round_index in range(last_round, -len(pref_rounds) - 1, -1):
            find_trail, pref_attributes, round_obj = Command.setup_pref(
                election, pref_rounds, round_index, seat, target)
            if Command.PREF.filter(**pref_attributes).exists():
                last_pref = Command.PREF.get(**pref_attributes)
                if last_pref.votes_received > 0:
                    find_trail, last_round = True, round_index - 1
                    break
            last_round -= 1
        return find_trail, last_pref, last_round, round_obj

    @staticmethod
    def add_trail(election, last_pref, pref_rounds, round_obj, seat):
        trail, trail_index = Command.setup_trail(election, last_pref,
                                                 pref_rounds, round_obj, seat)
        while last_pref.source_candidate:
            trail_index -= 1
            last_pref = Command.add_candidate_source(
                election, last_pref, pref_rounds, seat, trail, trail_index)
        return trail

    @staticmethod
    def add_candidate_source(election, last_pref, pref_rounds, seat, trail,
                             trail_index):
        last_pref, previous = seat.setup_source(election, last_pref,
                                                pref_rounds, trail_index)
        proximate = last_pref.votes_received - previous.votes_received
        trail.append((last_pref.candidate, proximate,
                      last_pref.round.round_number), )
        return last_pref

    #@staticmethod
    #def setup_source(election, last_pref, pref_rounds, seat, trail_index):
    #    return seat.setup_source(election, last_pref, pref_rounds, trail_index)
        #return Command.PREF.get(
        #    election=election, seat=seat, candidate=last_pref.source_candidate,
        #    round=pref_rounds[trail_index]), Command.PREF.get(
        #    election=election, seat=seat, candidate=last_pref.source_candidate,
        #    round=pref_rounds[trail_index-1])

    @staticmethod
    def setup_trail(election, last_pref, pref_rounds, round_obj, seat):
        trail_index = round_obj.round_number
        previous = Command.PREF.get(election=election, seat=seat,
                                    candidate=last_pref.candidate,
                                    round=pref_rounds[trail_index-1])
        trail = [(last_pref.candidate, last_pref.votes_received -
                  previous.votes_received, last_pref.round.round_number), ]
        return trail, trail_index
