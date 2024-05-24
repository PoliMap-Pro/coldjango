from django.db import models
from django.db.models import UniqueConstraint, Sum
from . import abstract_models, constants, names, people
from .abstract_models import Crown, Round, Transfer
from .format import keep_query
from .place import Booth, Seat
from .service import Contention, Representation


class HouseElection(abstract_models.Election):
    BYPASSES = {'primary_votes': 'aec_total'}
    DEFAULT_HOUSE_ELECTION_TEXT = "/AEC/Elections/House/"

    class ElectionType(models.TextChoices):
        BY_ELECTION = "by-election", "By-Election"
        REGULAR = "federal", "Regular"

    election_type = models.CharField(max_length=15,
                                     choices=ElectionType.choices)

    def get_contentions(self, party_abbreviation):
        return [Contention.objects.get(
            election=self, candidate=representation.person.candidate) for
            representation in Representation.objects.filter(
                election=self, party__abbreviation=party_abbreviation)]

    def result_by_place(self, party_set, place_set, places, parent, target,
                        sum_booths=False, return_format=constants.NEST_FORMAT):
        """
        Adds results to the election results dictionary for each of the places
        in a new place set generated from the representation set for this
        election and the party set.
        """
        representation_set = Representation.objects.filter(
            election=self, party__in=party_set).exclude(
            person__name__iexact=constants.INFORMAL_VOTER)





        contentions = service.Contention.objects.filter(
                election=election, seat=self,
                candidate=representation.person.candidate)
        place_set[0]











        elect_result, place_set = self.setup_place(
            party_set, place_set, places, representation_set, return_format,
            target, parent_result=parent)

        if isinstance(place_set[0], Seat):
            contention_set = Contention.objects.filter(
                election=self, seat__in=place_set)
        else:
            contention_set = Contention.objects.filter(
                election=self, seat__booth__in=place_set)
        persons = [contention.candidate.person for contention in contention_set]
        for place in place_set:
            subset = [rep for rep in representation_set if rep.person in persons]
            self.update_election_result(
                elect_result, subset, place, target,
                sum_booths, return_format=return_format)
        #[self.update_election_result(
        #    elect_result, representation_set, place, target,
        #    sum_booths, return_format=return_format) for place in place_set]
        self.format_result(elect_result, parent, return_format)

    def setup_election_result(
            self, p_set, representation_set, return_format, tally_attribute,
            house_elections_text=DEFAULT_HOUSE_ELECTION_TEXT,
            between_party_names=
            abstract_models.Election.DEFAULT_PARTY_NAME_SEPARATOR,
            add_to_end_of_name=
            abstract_models.Election.DEFAULT_AFTER_END_OF_NAME,
            between_parts_of_name=
            abstract_models.Election.DEFAULT_BETWEEN_PARTS_OF_NAME,
            parent_result=None):
        """
        Generates (or sends back) an election result that agrees with the
        return format.
        """
        if return_format == constants.TRANSACTION_FORMAT:
            return self.get_transaction_format_election_result(
                add_to_end_of_name, between_parts_of_name, between_party_names,
                house_elections_text, p_set, representation_set,
                tally_attribute)
        if return_format == constants.SPREADSHEET_FORMAT:
            self.set_top_level_entries_for_the_spreadsheet_format(
                add_to_end_of_name, between_parts_of_name, between_party_names,
                house_elections_text, p_set, parent_result, tally_attribute)
            return parent_result
        return {}

    def format_result(self, elect_result, result, return_format):
        if return_format == constants.TRANSACTION_FORMAT:
            result[self.election_date.year] = elect_result
        elif return_format == constants.SPREADSHEET_FORMAT:
            pass
        else:
            result[str(self)] = elect_result

    def booths_for_election(self, place_set, places):
        election_result = {}
        if not place_set:
            place_set = Booth.get_set(self, places)
        return election_result, place_set

    def new_dot_node(self, candidate):
        """
        Supply a HouseCandidate.
        Returns a dot node name and text for dot's label attribute for that
        candidate and the party they represented in the election.
        """
        node_name = str(candidate)
        try:
            rep = Representation.objects.get(person=candidate.person,
                                             election=self)
        except Representation.MultipleObjectsReturned:
            rep = Representation.objects.filter(person=candidate.person,
                                                election=self)[0]
        return (node_name, f"{node_name}\n{rep.party.name}"), node_name

    def set_top_level_entries_for_the_spreadsheet_format(
            self, add_to_end_of_name, between_parts_of_name,
            between_party_names, house_elections_text, p_set, parent_result,
            tally_attribute):
        """
        Adds empty lists for the series entry if they don't exist yet.
        If the names entry doesn't exist yet, tries to write it by tying
        together parts of the names of the supplied parties.
        """
        if constants.NAMES not in parent_result:
            parent_result[constants.NAMES] = [
                self.get_call_name(
                    add_to_end_of_name, between_parts_of_name,
                    between_party_names, house_elections_text, p_set,
                    tally_attribute), ]
        if constants.SERIES not in parent_result:
            parent_result[constants.SERIES] = [
                {constants.RETURN_NAME: name, constants.DATA: []} for name
                in constants.SPREADSHEET_NAMES]

    def get_transaction_format_election_result(self, add_to_end_of_name,
                                               between_parts_of_name,
                                               between_party_names,
                                               house_elections_text, p_set,
                                               representation_set,
                                               tally_attribute):
        return {constants.NAMES: [
            self.get_call_name(add_to_end_of_name, between_parts_of_name,
                               between_party_names, house_elections_text,
                               p_set, tally_attribute), ], constants.DATA: [],
                constants.QUERIES: [str(representation_set.query), ]}

    def update_election_result(self, election_result, representation_set,
                               place, tally_attribute, sum_booths=False,
                               return_format=constants.NEST_FORMAT):
        """
        Adds the results for the seats or the booths.
        """
        result = self.election_place_result(
            place, representation_set, tally_attribute, sum_booths,
            return_format=return_format)
        if return_format == constants.TRANSACTION_FORMAT:
            HouseElection.update_election_result_in_transaction_format(
                election_result, result, tally_attribute)
        elif return_format == constants.SPREADSHEET_FORMAT:
            [election_result[constants.SERIES][index][constants.DATA].extend(
                new_entries) for index, new_entries in self.get_result_entries(
                place, result, tally_attribute)]
        else:
            election_result[str(place)] = result

    def setup_place(self, p_set, place_set, places, standing,
                    return_format, tally_attribute, parent_result=None):
        """
        Starts a new election result. Fetches the place set if it doesn't
        exist yet.
        """
        elect_result, place_set = self.setup_query_sets(
            p_set, parent_result, place_set, places, standing, return_format,
            tally_attribute)
        HouseElection.setup_transaction_format(elect_result, place_set,
                                               return_format)
        return elect_result, place_set

    def results_highest_by_votes(self, election_result, how_many, location,
                                 representation_set, tally_attribute,
                                 sum_booths=False):
        all_parties = self.election_place_result(
            location, representation_set, tally_attribute, sum_booths)
        pairs = list(all_parties.items())
        pairs.sort(key=abstract_models.Election.by_votes)
        election_result[str(location)] = dict(pairs[:how_many])

    def get_result_entries(self, place, result, tally_attribute):
        """
        Returns result entries for the spreadsheet format
        """
        result_values = result.values()
        result_length = len(result_values)
        return ((constants.SPREADSHEET_FORMAT_YEAR_INDEX,
                 [self.election_date.year] * result_length),
                (constants.SPREADSHEET_FORMAT_PLACE_INDEX,
                 [str(place)] * result_length),
                (constants.SPREADSHEET_FORMAT_ATTRIBUTE_INDEX,
                 [tally_attribute] * result_length),
                (constants.SPREADSHEET_FORMAT_PARTY_INDEX, list(result.keys())),
                (constants.SPREADSHEET_FORMAT_VOTES_INDEX,
                 [value[constants.RETURN_VOTES] for value in result_values]),
                (constants.SPREADSHEET_FORMAT_PERCENT_INDEX,
                 [value[constants.RETURN_PERCENTAGE] for value in result_values
                  ]),)

    def setup_query_sets(self, p_set, parent_result, place_set, places,
                         representation_set, return_format, tally_attribute):
        """
        If the place set contains booths (instead of seats), captures the query
        used to fetch them. Starts a new election result.
        """
        elect_result = self.setup_election_result(
            p_set, representation_set, return_format, tally_attribute,
            parent_result=parent_result)
        if not place_set:
            place_set = Booth.get_set(self, places)
            keep_query(return_format, elect_result, place_set)
        return elect_result, place_set

    def election_place_result(self, place, representation_subset,
                              tally_attribute, sum_booths=False,
                              return_format=constants.NEST_FORMAT,
                              election_result=None,
                              name_of_informal_vote=constants.INFORMAL_VOTER,
                              check_for_informal=False):
        result, total = HouseElection.format_return(
            election_result, return_format, self.fetch_total(
                place, sum_booths, tally_attribute, return_format=return_format
            ))
        if check_for_informal:
            [place.update_place_result(
                self, representation, result, total, tally_attribute,
                return_format=return_format, election_result=election_result)
                for representation in representation_subset if
                representation.person.name.lower() != name_of_informal_vote]
        else:
            [place.update_place_result(
                self, representation, result, total, tally_attribute,
                return_format=return_format, election_result=election_result)
                for representation in representation_subset]
        return result

    def highest_by_votes(self, how_many, place_set, places, result,
                         tally_attribute, sum_booths=False):
        election_result, place_set = self.booths_for_election(place_set, places)
        representation_set = Representation.objects.filter(election=self)
        [self.results_highest_by_votes(
            election_result, how_many, location, representation_set,
            tally_attribute, sum_booths) for location in place_set]
        result[str(self)] = election_result

    def fetch_total(self, place, sum_booths, tally_attribute,
                    use_aggregate=True, return_format=constants.NEST_FORMAT):
        if sum_booths or isinstance(place, Booth):
            return place.total_attribute(self, tally_attribute,
                                         return_format=return_format)
        if use_aggregate:
            return self.fetch_total_aggregate_version(
                place, tally_attribute, return_format=return_format)
        print("LOOP!")
        return self.fetch_total_loop_version(place, tally_attribute)

    def fetch_total_loop_version(self, place, tally_attribute):
        total = 0
        for vote_tally in VoteTally.objects.filter(
                election=self, bypass=place):
            change = getattr(vote_tally, tally_attribute)
            if change and (change > 0):
                total += change
            else:
                total += getattr(vote_tally, HouseElection.BYPASSES[
                    tally_attribute]) or 0
        return total

    def fetch_total_aggregate_version(self, place, tally_attribute,
                                      return_format=constants.NEST_FORMAT):
        tallies = VoteTally.objects.filter(election=self, bypass=place)
        if tallies:
            if getattr(tallies[0], tally_attribute):
                attrib = tally_attribute
            else:
                attrib = HouseElection.BYPASSES[tally_attribute]
            aggregate = tallies.aggregate(Sum(attrib, default=0))
            if aggregate:
                if return_format == constants.TRANSACTION_FORMAT:
                    return aggregate.popitem()[1], tallies
                return aggregate.popitem()[1]
        if return_format == constants.TRANSACTION_FORMAT:
            return 0, tallies
        return 0

    @staticmethod
    def per(callback, *arguments, **keyword_arguments):
        for election in HouseElection.objects.all().order_by('election_date'):
            return callback(*arguments, election=election, **keyword_arguments)

    @staticmethod
    def format_return(election_result, return_format, total_returned):
        if return_format == constants.TRANSACTION_FORMAT:
            return HouseElection.format_return_for_transaction_format(
                election_result, total_returned)
        return {}, total_returned

    @staticmethod
    def setup_transaction_format(elect_result, place_set, return_format):
        if return_format == constants.TRANSACTION_FORMAT:
            divisions = {constants.RETURN_NAME: 'Division name',
                         constants.RETURN_VALUES: [divi.name for divi in place_set]}
            id_numbers = {constants.RETURN_NAME: 'id',
                          constants.RETURN_VALUES: [divi.id for divi in place_set]}
            elect_result[constants.DATA].append(divisions)
            elect_result[constants.DATA].append(id_numbers)


class HouseCandidate(models.Model):
    person = models.OneToOneField(people.Person, on_delete=models.CASCADE,
                                  related_name='candidate')
    seat = models.ManyToManyField(Seat, through="Contention")

    def __str__(self):
        return str(self.person)


class VoteTally(models.Model):
    class Meta:
        verbose_name_plural = "Vote Tallies"
        constraints = [UniqueConstraint(
            fields=['booth', 'bypass', 'election', 'candidate', ],
            name='booth_bypass_election_candidate')]

    booth = models.ForeignKey(Booth, on_delete=models.CASCADE, null=True)
    bypass = models.ForeignKey(Seat, on_delete=models.CASCADE, null=True)
    election = models.ForeignKey(HouseElection, on_delete=models.CASCADE)
    candidate = models.ForeignKey(HouseCandidate, on_delete=models.CASCADE)
    tcp_votes = models.IntegerField(null=True, blank=True)
    primary_votes = models.IntegerField(null=True, blank=True)
    absent_votes = models.PositiveIntegerField(default=0)
    provisional_votes = models.PositiveIntegerField(default=0)
    declaration_pre_poll_votes = models.PositiveIntegerField(default=0)
    postal_votes = models.PositiveIntegerField(default=0)
    aec_ordinary = models.PositiveIntegerField(default=0)
    aec_total = models.PositiveIntegerField(default=0)
    aec_swing = models.DecimalField(max_digits=8, decimal_places=4, default=0)
    created = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def via_representation(election, party_abbreviation, seat, booth,
                           found_callback=None, not_found_callback=None):
        """
        Supply a HouseElection.
        Supply a party abbreviation as a string.
        Supply a Seat.
        Supply a Booth.
        Returns the VoteTally for the candidate representing that party in
        that booth in that seat in that election.
        """
        representation = Representation.objects.get(
            election=election, party__abbreviation__iexact=party_abbreviation,
            person__candidate__contention__seat=seat,
            person__candidate__contention__election=election
        )
        try:
            vote_tally = VoteTally.objects.get(
                booth=booth, election=election,
                candidate=representation.person.candidate
            )
            if found_callback:
                found_callback(booth, party_abbreviation, vote_tally)
            return vote_tally
        except VoteTally.DoesNotExist:
            if not_found_callback:
                not_found_callback(booth, party_abbreviation)
            return False

    @staticmethod
    def per(callback, *arguments, **keyword_arguments):
        def wrapper(booth, seat, election):
            return [callback(*arguments, election=election, seat=seat,
                             booth=booth, vote_tally=vote_tally,
                             **keyword_arguments) for vote_tally in
                    VoteTally.objects.filter(booth=booth, election=election)]
        return wrapper

    def __str__(self):
        return str(f"{self.primary_votes or self.aec_total} for "
                   f"{self.candidate} at {self.booth or self.bypass} in "
                   f"{self.election} ({self.pk})")


class PreferenceRound(Crown, Round):
    class Meta:
        constraints = [UniqueConstraint(
            fields=['seat', 'election', 'round_number',],
            name='unique_combination_of_seat_election_round_number')]

    def __str__(self):
        return f"Round {self.round_number} of {self.seat} in {self.election}"


class CandidatePreference(Transfer):
    class Meta:
        constraints = [UniqueConstraint(
            fields=['candidate', 'round', 'seat', 'election'],
            name='unique_combination_of_candidate_round_seat_election')]

    election = models.ForeignKey(HouseElection, on_delete=models.CASCADE,
                                 null=True, blank=True)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE,
                             null=True, blank=True)
    candidate = models.ForeignKey(HouseCandidate, on_delete=models.CASCADE,
                                  related_name="target_preference")
    source_candidate = models.ForeignKey(HouseCandidate,
                                         on_delete=models.SET_NULL,
                                         related_name="source_preference",
                                         null=True, blank=True)
    round = models.ForeignKey(PreferenceRound, on_delete=models.CASCADE)
    votes_received = models.IntegerField()
    votes_remaining = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.candidate} in {self.round} ({self.pk})"


class Enrollment(Crown):
    class Meta:
        constraints = [UniqueConstraint(fields=['seat', 'election',],
                                        name='unique_seat_for_election')]

    number_enrolled = models.PositiveIntegerField(default=0)

    def __str__(self):
        return str(f"{self.number_enrolled} to vote in "
                   f"{self.seat} in {self.election} ({self.pk})")


class HouseAlliance(names.TrackedName):
    election = models.ForeignKey(HouseElection, on_delete=models.CASCADE)

    def __str__(self):
        return str(f"{self.name} at {self.election} ({self.pk})")


