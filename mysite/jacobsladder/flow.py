import csv
import random
import math
import pygame
import colorsys

IN_FILE = "housedopbydivisiondownload-27966.csv"
SCREEN_WIDTH, SCREEN_HEIGHT = 700, 700
SHOW_FRACTION = 0.25
FRAMES = 60
HALF_WIDTH, HALF_HEIGHT = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2

pygame.init()


class Location(object):
    FONT = pygame.font.SysFont(pygame.font.get_default_font(), 30)
    RADIUS = 0

    def __init__(self):
        self.rpx = 0
        self.rpy = 0
        self.colour = (255, 255, 255)

    def etch_text(self, surface, column=None):
        text_surface = Location.FONT.render(str(self), True, (255, 255, 255))
        half_text_width = text_surface.get_width() / 2
        offset = 1.2 * text_surface.get_height()
        if column is None:
            y = self.py - self.__class__.RADIUS - offset
        else:
            y = column
        surface.blit(text_surface, (
            round(self.px - half_text_width),
            round(y)))

    @property
    def px(self):
        return self.rpx + HALF_HEIGHT

    @property
    def py(self):
        return self.rpy + HALF_HEIGHT

    def etch(self, surface, colour=None):
        if colour is None:
            colour = self.colour
        surface.set_at((round(self.px), round(self.py)), colour)


class Vote(Location):
    TOTAL_COUNT = 0

    def __init__(self, primary):
        Location.__init__(self)
        self.vx = 0
        self.vy = 0
        self.tpx = 0
        self.tpy = 0
        self.primary = primary
        self.candidate = primary
        Vote.TOTAL_COUNT += 1

    @property
    def px(self):
        return self.rpx + self.candidate.px

    @property
    def py(self):
        return self.rpy + self.candidate.py

    def __repr__(self):
        return str(self.primary).title()


class Candidate(Location):
    RADIUS = 80
    OUTER_RADIUS = 84
    SQUARE_RADIUS = RADIUS * RADIUS
    SIZE = math.pi * SQUARE_RADIUS

    def __init__(self, name):
        Location.__init__(self)
        self.name = name
        self.votes = None

    def __repr__(self):
        return self.name.title()

    def etch(self, surface, colour=None):
        if colour is None:
            circle_colour = (255, 255, 255)
        else:
            circle_colour = colour
        self.etch_text(surface)
        pygame.draw.circle(surface, circle_colour,
                           (round(self.px), round(self.py)),
                           Candidate.OUTER_RADIUS,
                           width=4)
        for vote in self.votes:
            vote.etch(surface, colour)


class Stage(Location):
    RADIUS = 240
    ALL_STAGES = []
    ELIMINATED = []

    def __init__(self, number, division):
        Location.__init__(self)
        self.number = number
        self.division = division
        self.candidates = {}
        self.rows = []
        self.rpx = 0
        self.rpy = 0

    def etch(self, surface, colour=None):
        self.etch_text(surface, HALF_HEIGHT)
        for surname, candidate in self.candidates.items():
            candidate.etch(surface, colour)

    def transfer_votes(self, surface):
        pool = []
        for row in self.rows:
            if row['Surname'] not in Stage.ELIMINATED:
                if row['CalculationType'] == 'Preference Count':
                    if int(row['CalculationValue']) == 0:
                        pool = self.candidates[row['Surname']].votes
                        Stage.ELIMINATED.append(row['Surname'])
                        del self.candidates[row['Surname']]
        random.shuffle(pool)
        for row in self.rows:
            if row['Surname'] not in Stage.ELIMINATED:
                if row['CalculationType'] == 'Preference Count':
                    num_votes = int(int(row['CalculationValue']) * SHOW_FRACTION)
                    if num_votes > 0:
                        extra = num_votes - len(self.candidates[row['Surname']].votes)
                        for x, y in Stage.random_position(Candidate.RADIUS, extra, len(self.candidates[row['Surname']].votes)):
                            try:
                                vote = pool.pop()
                                x_off, y_off = vote.candidate.px, vote.candidate.py
                                vote.candidate = self.candidates[row['Surname']]
                                vote.rpx += x_off - vote.candidate.px
                                vote.rpy += y_off - vote.candidate.py
                                #vote.tpx, vote.tpy = Stage.random_position(Candidate.RADIUS)
                                vote.tpx, vote.tpy = x, y
                                vote.vx = (vote.tpx + vote.candidate.px - vote.px) / FRAMES
                                vote.vy = (vote.tpy + vote.candidate.py - vote.py) / FRAMES
                                self.candidates[row['Surname']].votes.append(vote)
                            except IndexError:
                                break
        if self.number == 0:
            self.etch(surface)
        else:
            stage_clock = pygame.time.Clock()
            for frame in range(FRAMES):
                surface.fill([0, 0, 0])
                for candidate in self.candidates.values():
                    for vote in candidate.votes:
                        vote.rpx += vote.vx
                        vote.rpy += vote.vy
                self.etch(surface)
                pygame.display.flip()
                stage_clock.tick(60)
            for candidate in self.candidates.values():
                for vote in candidate.votes:
                    vote.vx = 0
                    vote.vy = 0

    def populate(self):
        if self.number > 0:
            self.candidates = Stage.ALL_STAGES[self.number - 1].candidates
        else:
            for row in self.rows:
                if row['Surname'] not in self.candidates:
                    self.candidates[row['Surname']] = Candidate(row['Surname'])
                if row['CalculationType'] == 'Preference Count':
                    num_votes = int(int(row['CalculationValue']) * SHOW_FRACTION)
                    self.candidates[row['Surname']].votes = None
                    self.candidates[row['Surname']].votes = []
                    self.candidates[row['Surname']].num_votes = num_votes
                    for x, y in Stage.random_position(Candidate.RADIUS, num_votes):
                        new_vote = Vote(self.candidates[row['Surname']])
                        new_vote.rpx, new_vote.rpy = x, y
                        new_vote.tpx, new_vote.tpy = new_vote.rpx, new_vote.rpy
                        self.candidates[row['Surname']].votes.append(new_vote)
                separation = 2.0 * math.pi / len(self.candidates)
                proportion = 1.0 / len(self.candidates)
                for n, candidate in enumerate(self.candidates.values()):
                    r = Stage.RADIUS
                    angle = separation * n
                    hsv = (n * proportion, 1.0, 1.0)
                    candidate.colour = [round(255.0 * norm) for norm in colorsys.hsv_to_rgb(*hsv)]
                    for vote in candidate.votes:
                        vote.colour = candidate.colour
                    candidate.rpx = r * math.cos(angle)
                    candidate.rpy = r * math.sin(angle)

    @staticmethod
    def random_position(steps, num_votes, old_total=0):
        counter = 0
        target = old_total + num_votes
        for row in range(-steps, steps):
            right_column = int(math.sqrt(Candidate.SQUARE_RADIUS - (row * row)))
            for column in range(-right_column, right_column):
                if old_total < counter < target:
                    yield column, row
                counter += 1

    def __repr__(self):
        return f"{self.division.upper()} ROUND {self.number}"


if __name__ == '__main__':
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT),)
    clock = pygame.time.Clock()
    old_division_name = None
    with open(IN_FILE, "r") as in_file:
        next(in_file)
        reader = csv.DictReader(in_file)
        for row in reader:
            try:
                division_name = row['DivisionNm']
                if (old_division_name is not None) and (row['DivisionNm'] != old_division_name):
                    screen.fill([0, 0, 0])
                    for stage in Stage.ALL_STAGES:
                        stage.populate()
                        stage.transfer_votes(screen)
                        pygame.display.flip()
                        pygame.time.wait(2000)
                    Stage.ALL_STAGES = []
                old_division_name = row['DivisionNm']
                stage_number = int(row['CountNumber'])
                if len(Stage.ALL_STAGES) <= stage_number:
                    new_stage = Stage(stage_number, division_name)
                    Stage.ALL_STAGES.append(new_stage)
                Stage.ALL_STAGES[stage_number].rows.append(row)
            except KeyError:
                pass