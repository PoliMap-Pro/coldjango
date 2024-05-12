import csv
import graphviz
from . import models, constants, folder_reader, people, house, place, service


class AECReader(object):
    # headers from csv files
    FIRST_NAME_HEADER = 'Surname'
    OTHER_NAMES_HEADER = 'GivenNm'
    SEAT_CODE_HEADER = 'DivisionID'
    SEAT_NAME_HEADER = 'DivisionNm'

    NODE_SHAPE = 'box'
    PREF = house.CandidatePreference.objects

    def add_one(self, filename, election, single_create_method,
                line_before_headers=True, two_header_years=None,
                election_year=None):
        with open(filename, "r") as in_file:
            reader = self.fetch_reader(filename, in_file,
                                       line_before_headers=line_before_headers,
                                       two_header_years=two_header_years,
                                       election_year=election_year)
            method = getattr(self.__class__, single_create_method)
            [method(election, row) for row in reader]

    @staticmethod
    def fetch_reader(filename, in_file, type_of_reader=csv.DictReader,
                     quiet=False, line_before_headers=True,
                     two_header_years=None, election_year=None):
        folder_reader.FolderReader.echo(quiet, filename, False)
        if line_before_headers or (two_header_years and election_year and
                                   (election_year in two_header_years)):
            next(in_file)
        return type_of_reader(in_file)

    @staticmethod
    def fetch_by_aec_code(model_attributes, model_objects, code_objects,
                          related_name, target):
        if model_objects.filter(**model_attributes).count() > 1:
            code_attributes = {'__'.join([related_name, key]): value for
                               key, value in model_attributes.items()}
            codes = [code for code in code_objects.filter(
                **code_attributes) if code.number == target]
            print("\t-filtered by code:", codes[0], codes[0].pk, related_name)
            return getattr(codes[0], related_name)
        try:
            return model_objects.get(**model_attributes)
        except Exception:
            new_model = model_objects.create(**model_attributes)
            new_attributes = {'number': target, related_name: new_model}
            new_code = code_objects.create(**new_attributes)
            return new_model

    @staticmethod
    def get_standard_beacon_attributes(row):
        return {'name': row[AECReader.SEAT_NAME_HEADER],
                'state': row[constants.STATE_ABBREVIATION_HEADER].lower(), }

    @classmethod
    def find_person(cls, candidate_objects, person_attributes, row,
                    group_abbreviation=None, election=None):
        try:
            person = cls.fetch_by_aec_code(
                person_attributes, people.Person.objects,
                people.PersonCode.objects, 'person', int(
                    row[constants.CANDIDATE_CODE_HEADER]))
        except KeyError:
            person, _ = people.Person.objects.get_or_create(**person_attributes)
        if group_abbreviation:
            group_abbreviation = group_abbreviation.strip()
            try:
                candidate = candidate_objects.get(
                        person=person, group__abbreviation=group_abbreviation)
            except models.SenateCandidate.DoesNotExist:
                if election:
                    group, _ = models.SenateGroup.objects.get_or_create(
                        abbreviation=group_abbreviation, election=election)
                    candidate, _ = candidate_objects.get_or_create(
                        person=person)
                    candidate.group = group
                    candidate.save()
        else:
            candidate, _ = candidate_objects.get_or_create(person=person)
        return candidate, person

    @staticmethod
    def get_standard_person_attributes(row):
        return {'name': row[AECReader.FIRST_NAME_HEADER],
                'other_names': row[AECReader.OTHER_NAMES_HEADER], }

    @staticmethod
    def find_candidate_for_seat(house_election, row):
        seat = AECReader.fetch_by_aec_code(
            AECReader.get_standard_beacon_attributes(row), place.Seat.objects,
            place.SeatCode.objects, 'seat', int(
                row[AECReader.SEAT_CODE_HEADER]))
        candidate = AECReader.pull_candidate(
            house_election, AECReader.get_standard_person_attributes(row), row,
            seat)
        return candidate, seat

    @staticmethod
    def pull_candidate(election, person_attributes, row, seat,
                       candidate_objects=house.HouseCandidate.objects):
        candidate, _ = AECReader.find_person(candidate_objects,
                                             person_attributes, row)
        contention, _ = service.Contention.objects.get_or_create(
            seat=seat, candidate=candidate, election=election)
        return candidate

    @staticmethod
    def add_source(candidate, current_round, house_election, pref_objects,
                   received, remaining, seat, transferred):
        preference_attributes = {'candidate': candidate,
                                 'election': house_election,
                                 'round': current_round,
                                 'votes_received': received,
                                 'votes_transferred': transferred,}
        try:
            AECReader.single_preference(current_round, house_election,
                                        pref_objects, preference_attributes,
                                        seat)
        except house.CandidatePreference.MultipleObjectsReturned:
            assert all([pref.source_candidate for pref in
                        pref_objects.filter(**preference_attributes)])

    @staticmethod
    def single_preference(current_round, house_election, pref_objects,
                          preference_attributes, seat):
        pref = pref_objects.get(**preference_attributes)
        pref.source_candidate = pref_objects.get(votes_received=0,
                                                 votes_transferred__lt=0,
                                                 round=current_round,
                                                 election=house_election,
                                                 seat=seat).candidate
        pref.save()

    @staticmethod
    def get_targets(election, seat, abbreviation=None, default=None):
        representing_candidates = [
            representation.person.candidate.pk for representation in
            service.Representation.objects.filter(
                election=election,
                party__abbreviation__iexact=abbreviation if abbreviation else
                default)]
        return list(house.PreferenceRound.objects.filter(
            election=election, seat=seat).order_by('round_number')), [
            contention.candidate for contention in
            service.Contention.objects.filter(election=election, seat=seat) if
            contention.candidate.pk in representing_candidates]

    @staticmethod
    def setup_pref(election, pref_rounds, round_index, seat, target):
        find_trail, round_obj = False, pref_rounds[round_index]
        pref_attributes = {'election': election, 'seat': seat,
                           'round': round_obj, 'candidate': target}
        return find_trail, pref_attributes, round_obj

    @staticmethod
    def setup_dot_file(seat, target, year):
        return graphviz.Digraph(
            f"{str(target)}_{seat.name}_{year}", format='png',
            comment='House preference flow',
            node_attr={'shape': AECReader.NODE_SHAPE},
            graph_attr={'labelloc': 't', 'label': f"{seat.name} {year}",
                        'mclimit': '10',},
            engine='dot'), [], []

    @staticmethod
    def setup_trail(election, last_pref, pref_rounds, round_obj, seat):
        trail_index = round_obj.round_number
        previous = AECReader.PREF.get(election=election, seat=seat,
                                      candidate=last_pref.candidate,
                                      round=pref_rounds[trail_index-1])
        trail = [(last_pref.candidate, last_pref.votes_received -
                  previous.votes_received, last_pref.round.round_number), ]
        return trail, trail_index
