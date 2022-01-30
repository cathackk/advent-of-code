from common.chain import Circle


def game(players_count: int, last_marble: int, log_each: int = 1_000_000) -> int:
    """
    >>> game(players_count=9, last_marble=25)
    32
    >>> game(players_count=10, last_marble=1618)
    8317
    >>> game(players_count=13, last_marble=7999)
    146373
    >>> game(players_count=17, last_marble=1104)
    2764
    >>> game(players_count=21, last_marble=6111)
    54718
    >>> game(players_count=30, last_marble=5807)
    37305
    """
    player_scores = {p: 0 for p in range(players_count)}

    marbles = Circle([0])
    current_player = 0

    for turn in range(1, last_marble + 1):
        # Each Elf takes a turn placing the lowest-numbered remaining marble into the circle
        new_marble = turn
        if new_marble % 23 != 0:
            # ... between the marbles that are 1 and 2 marbles clockwise of the current marble.
            marbles.insert(+1, new_marble)
        else:
            # However, if the marble that is about to be placed has a number
            # which is a multiple of 23, something entirely different happens.
            # First, the current player keeps the marble they would have placed,
            # adding it to their score.
            player_scores[current_player] += new_marble
            # In addition, the marble 7 marbles counter-clockwise from the current marble
            # is removed from the circle ...
            removed_marble = marbles.pop(-7)
            # ... and also added to the current player's score.
            player_scores[current_player] += removed_marble

        current_player = (current_player + 1) % players_count

        if log_each > 0 and turn % log_each == 0:
            print(f"... {turn} / {last_marble} ({turn / last_marble:.2%})")

    # return high score
    high_score = max(player_scores.values())
    # print(f"game(player_count={players_count}, last_marble={last_marble}) -> {high_score}")
    return high_score


if __name__ == '__main__':
    PLAYERS_COUNT_ = 426
    LAST_MARBLE_ = 72058
    high_score_1 = game(PLAYERS_COUNT_, LAST_MARBLE_)
    print(f"part 1: high score is {high_score_1}")
    high_score_2 = game(PLAYERS_COUNT_, LAST_MARBLE_ * 100)
    print(f"part 2: high score is {high_score_2}")
